import { createHash } from 'node:crypto';
import Database from 'better-sqlite3';
import { evaluatePolicy, type RiskLevel, type TaskPolicyRequest } from '@cockpit/policy';

export type CommandStatus = 'queued' | 'pending_approval' | 'denied' | 'running' | 'succeeded' | 'failed' | 'cancelled';
export type CommandAction = TaskPolicyRequest['action'];

export interface CommandInput {
  readonly requestedBy: string;
  readonly principalRole?: TaskPolicyRequest['principal']['role'];
  readonly action: CommandAction;
  readonly target: string;
  readonly risk: RiskLevel;
  readonly payload?: unknown;
}

export interface CommandRecord extends CommandInput {
  readonly id: string;
  readonly status: CommandStatus;
  readonly policyDecision: string;
  readonly policyReason: string;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface ApprovalInput {
  readonly commandId: string;
  readonly approvedBy: string;
  readonly reason: string;
}

export interface AuditEvent {
  readonly id: number;
  readonly createdAt: string;
  readonly kind: string;
  readonly actor: string;
  readonly subject: string;
  readonly payloadJson: string;
  readonly previousHash: string;
  readonly eventHash: string;
}

export interface CockpitStore {
  readonly dbPath: string;
  close(): void;
  appendAuditEvent(kind: string, actor: string, subject: string, payload: unknown): AuditEvent;
  listAuditEvents(limit?: number): AuditEvent[];
  verifyAuditChain(): boolean;
  submitCommand(input: CommandInput): CommandRecord;
  approveCommand(input: ApprovalInput): CommandRecord;
  markCommandRunning(commandId: string): CommandRecord;
  completeCommand(commandId: string, status: 'succeeded' | 'failed', result: unknown): CommandRecord;
  listCommands(limit?: number): CommandRecord[];
}

const MIGRATIONS: readonly { id: number; sql: string }[] = [
  {
    id: 1,
    sql: `
      CREATE TABLE IF NOT EXISTS schema_migrations (id INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        kind TEXT NOT NULL,
        actor TEXT NOT NULL,
        subject TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        previous_hash TEXT NOT NULL,
        event_hash TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS commands (
        id TEXT PRIMARY KEY,
        requested_by TEXT NOT NULL,
        principal_role TEXT NOT NULL,
        action TEXT NOT NULL,
        target TEXT NOT NULL,
        risk TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        status TEXT NOT NULL,
        policy_decision TEXT NOT NULL,
        policy_reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command_id TEXT NOT NULL,
        approved_by TEXT NOT NULL,
        reason TEXT NOT NULL,
        approval_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(command_id) REFERENCES commands(id)
      );
    `,
  },
];

function nowIso(): string { return new Date().toISOString(); }
function hash(value: string): string { return createHash('sha256').update(value, 'utf8').digest('hex'); }
function canonical(payload: unknown): string { return JSON.stringify(payload ?? {}, Object.keys(payload as Record<string, unknown> | {}).sort()); }
function commandId(seed: string): string { return `cmd_${hash(seed).slice(0, 16)}`; }

const VALID_ACTIONS = new Set(['read', 'execute', 'modify', 'delete', 'deploy', 'credential_access']);
const VALID_RISKS = new Set(['R0', 'R1', 'R2', 'R3', 'R4']);

function assertCommandInput(input: CommandInput): void {
  if (!VALID_ACTIONS.has(input.action)) throw new Error(`invalid action: ${input.action}`);
  if (!VALID_RISKS.has(input.risk)) throw new Error(`invalid risk: ${input.risk}`);
  if (!input.target.trim()) throw new Error('target is required');
  if (!input.requestedBy.trim()) throw new Error('requestedBy is required');
}

function mapCommand(row: Record<string, unknown>): CommandRecord {
  return {
    id: String(row.id),
    requestedBy: String(row.requested_by),
    principalRole: row.principal_role as CommandInput['principalRole'],
    action: row.action as CommandAction,
    target: String(row.target),
    risk: row.risk as RiskLevel,
    payload: JSON.parse(String(row.payload_json)),
    status: row.status as CommandStatus,
    policyDecision: String(row.policy_decision),
    policyReason: String(row.policy_reason),
    createdAt: String(row.created_at),
    updatedAt: String(row.updated_at),
  };
}

function mapAudit(row: Record<string, unknown>): AuditEvent {
  return {
    id: Number(row.id),
    createdAt: String(row.created_at),
    kind: String(row.kind),
    actor: String(row.actor),
    subject: String(row.subject),
    payloadJson: String(row.payload_json),
    previousHash: String(row.previous_hash),
    eventHash: String(row.event_hash),
  };
}

export function openCockpitStore(dbPath: string): CockpitStore {
  const db = new Database(dbPath);
  db.pragma('journal_mode = WAL');
  db.pragma('busy_timeout = 5000');
  db.exec('CREATE TABLE IF NOT EXISTS schema_migrations (id INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)');
  for (const migration of MIGRATIONS) {
    const exists = db.prepare('SELECT 1 FROM schema_migrations WHERE id = ?').get(migration.id);
    if (!exists) {
      const apply = db.transaction(() => {
        db.exec(migration.sql);
        db.prepare('INSERT INTO schema_migrations (id, applied_at) VALUES (?, ?)').run(migration.id, nowIso());
      });
      apply();
    }
  }

  function appendAuditEvent(kind: string, actor: string, subject: string, payload: unknown): AuditEvent {
    const createdAt = nowIso();
    const payloadJson = canonical(payload);
    const latest = db.prepare('SELECT event_hash FROM audit_events ORDER BY id DESC LIMIT 1').get() as { event_hash?: string } | undefined;
    const previousHash = latest?.event_hash ?? 'GENESIS';
    const eventHash = hash(`${createdAt}|${kind}|${actor}|${subject}|${payloadJson}|${previousHash}`);
    const info = db.prepare(`INSERT INTO audit_events (created_at, kind, actor, subject, payload_json, previous_hash, event_hash) VALUES (?, ?, ?, ?, ?, ?, ?)`).run(createdAt, kind, actor, subject, payloadJson, previousHash, eventHash);
    return mapAudit(db.prepare('SELECT * FROM audit_events WHERE id = ?').get(info.lastInsertRowid) as Record<string, unknown>);
  }

  function listAuditEvents(limit = 100): AuditEvent[] {
    const bounded = Math.max(1, Math.min(500, limit));
    return (db.prepare(`SELECT * FROM audit_events ORDER BY id DESC LIMIT ${bounded}`).all() as Record<string, unknown>[]).map(mapAudit);
  }

  function verifyAuditChain(): boolean {
    const events = db.prepare('SELECT * FROM audit_events ORDER BY id ASC').all() as Record<string, unknown>[];
    let previousHash = 'GENESIS';
    for (const row of events) {
      const expected = hash(`${row.created_at}|${row.kind}|${row.actor}|${row.subject}|${row.payload_json}|${previousHash}`);
      if (row.previous_hash !== previousHash || row.event_hash !== expected) return false;
      previousHash = String(row.event_hash);
    }
    return true;
  }

  function submitCommand(input: CommandInput): CommandRecord {
    assertCommandInput(input);
    const createdAt = nowIso();
    const principalRole = input.principalRole ?? (input.requestedBy === 'brenda' ? 'owner' : 'operator');
    const payloadJson = canonical(input.payload);
    const id = commandId(`${createdAt}|${input.requestedBy}|${input.action}|${input.target}|${input.risk}|${payloadJson}`);
    const policy = evaluatePolicy({
      principal: { id: input.requestedBy, role: principalRole },
      action: input.action,
      target: input.target,
      risk: input.risk,
      approvals: [],
    });
    const status: CommandStatus = policy.decision === 'deny' ? 'denied' : policy.decision === 'require_approval' ? 'pending_approval' : 'queued';
    const tx = db.transaction(() => {
      db.prepare(`INSERT INTO commands (id, requested_by, principal_role, action, target, risk, payload_json, status, policy_decision, policy_reason, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(id, input.requestedBy, principalRole, input.action, input.target, input.risk, payloadJson, status, policy.decision, policy.reason, createdAt, createdAt);
      appendAuditEvent('command.submitted', input.requestedBy, id, { action: input.action, target: input.target, risk: input.risk, status, policy });
    });
    tx();
    return mapCommand(db.prepare('SELECT * FROM commands WHERE id = ?').get(id) as Record<string, unknown>);
  }

  function approveCommand(input: ApprovalInput): CommandRecord {
    const existing = mapCommand(db.prepare('SELECT * FROM commands WHERE id = ?').get(input.commandId) as Record<string, unknown>);
    if (existing.status !== 'pending_approval') throw new Error(`command ${input.commandId} is not pending approval`);
    const createdAt = nowIso();
    const approvalHash = hash(`${input.commandId}|${input.approvedBy}|${input.reason}|${createdAt}`);
    const tx = db.transaction(() => {
      db.prepare('INSERT INTO approvals (command_id, approved_by, reason, approval_hash, created_at) VALUES (?, ?, ?, ?, ?)').run(input.commandId, input.approvedBy, input.reason, approvalHash, createdAt);
      db.prepare('UPDATE commands SET status = ?, updated_at = ?, policy_decision = ?, policy_reason = ? WHERE id = ?').run('queued', createdAt, 'allow', 'owner approval receipt recorded', input.commandId);
      appendAuditEvent('command.approved', input.approvedBy, input.commandId, { reason: input.reason, approvalHash });
    });
    tx();
    return mapCommand(db.prepare('SELECT * FROM commands WHERE id = ?').get(input.commandId) as Record<string, unknown>);
  }

  function listCommands(limit = 100): CommandRecord[] {
    const bounded = Math.max(1, Math.min(500, limit));
    return (db.prepare(`SELECT * FROM commands ORDER BY created_at DESC LIMIT ${bounded}`).all() as Record<string, unknown>[]).map(mapCommand);
  }

  function markCommandRunning(commandId: string): CommandRecord {
    const existing = mapCommand(db.prepare('SELECT * FROM commands WHERE id = ?').get(commandId) as Record<string, unknown>);
    if (existing.status !== 'queued') throw new Error(`command ${commandId} is not queued`);
    const updatedAt = nowIso();
    const tx = db.transaction(() => {
      db.prepare('UPDATE commands SET status = ?, updated_at = ? WHERE id = ?').run('running', updatedAt, commandId);
      appendAuditEvent('command.running', 'executor', commandId, { previousStatus: existing.status });
    });
    tx();
    return mapCommand(db.prepare('SELECT * FROM commands WHERE id = ?').get(commandId) as Record<string, unknown>);
  }

  function completeCommand(commandId: string, status: 'succeeded' | 'failed', result: unknown): CommandRecord {
    const existing = mapCommand(db.prepare('SELECT * FROM commands WHERE id = ?').get(commandId) as Record<string, unknown>);
    if (existing.status !== 'running') throw new Error(`command ${commandId} is not running`);
    const updatedAt = nowIso();
    const tx = db.transaction(() => {
      db.prepare('UPDATE commands SET status = ?, updated_at = ? WHERE id = ?').run(status, updatedAt, commandId);
      appendAuditEvent(`command.${status}`, 'executor', commandId, result);
    });
    tx();
    return mapCommand(db.prepare('SELECT * FROM commands WHERE id = ?').get(commandId) as Record<string, unknown>);
  }

  return { dbPath, close: () => db.close(), appendAuditEvent, listAuditEvents, verifyAuditChain, submitCommand, approveCommand, markCommandRunning, completeCommand, listCommands };
}
