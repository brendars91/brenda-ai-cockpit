import { adapters } from '@cockpit/adapters';
import { CapabilityRegistry } from '@cockpit/capability-registry';
import { listRuntimeAgents } from '@cockpit/agent-runtime-console';
import Database from 'better-sqlite3';

export interface ApiPaths {
  readonly stateDb: string;
  readonly cronDb: string;
  readonly evidenceDb: string;
  readonly memoryDb: string;
}

export const defaultPaths: ApiPaths = {
  stateDb: '/home/ubuntu/.hermes/state.db',
  cronDb: '/home/ubuntu/.hermes/cron/executions.db',
  evidenceDb: '/home/ubuntu/.hermes/verification_evidence.db',
  memoryDb: '/home/ubuntu/.hermes/memory_store.db',
};

function read<T>(dbPath: string, sql: string): T[] {
  const db = new Database(dbPath, { readonly: true, fileMustExist: true });
  try {
    return db.prepare(sql).all() as T[];
  } finally {
    db.close();
  }
}

function first<T>(dbPath: string, sql: string): T {
  const db = new Database(dbPath, { readonly: true, fileMustExist: true });
  try {
    return db.prepare(sql).get() as T;
  } finally {
    db.close();
  }
}

export function readSummary(paths: ApiPaths = defaultPaths) {
  const sessions = first<{ count: number; input: number; output: number; cost: number }>(paths.stateDb, `
    SELECT COUNT(*) as count,
           COALESCE(SUM(input_tokens), 0) as input,
           COALESCE(SUM(output_tokens), 0) as output,
           COALESCE(SUM(estimated_cost_usd), 0) as cost
    FROM sessions
  `);
  const tools = first<{ count: number }>(paths.stateDb, `SELECT COUNT(*) as count FROM messages WHERE tool_name IS NOT NULL`);
  const cron = first<{ count: number }>(paths.cronDb, `SELECT COUNT(*) as count FROM executions`);
  const evidence = first<{ count: number }>(paths.evidenceDb, `SELECT COUNT(*) as count FROM verification_events`);
  const memory = first<{ count: number }>(paths.memoryDb, `SELECT COUNT(*) as count FROM facts`);
  return { generated_at: new Date().toISOString(), sessions, tools, cron, evidence, memory };
}

export function readSessions(paths: ApiPaths = defaultPaths, limit = 100) {
  const bounded = Math.max(1, Math.min(500, limit));
  return read(paths.stateDb, `
    SELECT id, source, model, started_at, ended_at, message_count, tool_call_count,
           input_tokens, output_tokens, reasoning_tokens, billing_provider,
           estimated_cost_usd, title, chat_type, profile_name
    FROM sessions ORDER BY started_at DESC LIMIT ${bounded}
  `);
}

export function readCosts(paths: ApiPaths = defaultPaths) {
  return read(paths.stateDb, `
    SELECT model, billing_provider,
           COUNT(*) as session_count,
           COALESCE(SUM(input_tokens), 0) as total_input_tokens,
           COALESCE(SUM(output_tokens), 0) as total_output_tokens,
           COALESCE(SUM(reasoning_tokens), 0) as total_reasoning_tokens,
           COALESCE(SUM(estimated_cost_usd), 0) as total_cost,
           COALESCE(AVG(input_tokens), 0) as avg_input_per_session,
           COALESCE(AVG(output_tokens), 0) as avg_output_per_session
    FROM sessions WHERE model IS NOT NULL
    GROUP BY model ORDER BY total_input_tokens DESC
  `);
}

export function readTools(paths: ApiPaths = defaultPaths) {
  return read(paths.stateDb, `
    SELECT tool_name, COUNT(*) as call_count, COUNT(DISTINCT session_id) as sessions_used_in
    FROM messages WHERE tool_name IS NOT NULL
    GROUP BY tool_name ORDER BY call_count DESC
  `);
}

export function readCron(paths: ApiPaths = defaultPaths) {
  return read(paths.cronDb, `SELECT status, COUNT(*) as count FROM executions GROUP BY status`);
}

export function readEvidence(paths: ApiPaths = defaultPaths) {
  return read(paths.evidenceDb, `
    SELECT id, created_at, session_id, command, canonical_command, kind
    FROM verification_events ORDER BY created_at DESC LIMIT 100
  `);
}

export function readMemory(paths: ApiPaths = defaultPaths) {
  return read(paths.memoryDb, `
    SELECT fact_id, content, category, trust_score, tags FROM facts ORDER BY fact_id LIMIT 100
  `);
}


function buildCapabilityRegistry() {
  const registry = new CapabilityRegistry();
  for (const adapter of adapters) {
    for (const capability of adapter.capabilities) {
      registry.register({
        id: `${adapter.id}.${capability}`,
        adapterId: adapter.id,
        capability,
        risk: capability === 'terminal' || capability === 'cron' ? 'R2' : 'R1',
        evidenceRequired: true,
      });
    }
  }
  return registry;
}

export function routeData(pathname: string, paths: ApiPaths = defaultPaths) {
  if (pathname === '/api/health') return { ok: true, service: 'brenda-ai-cockpit-control-plane', mode: 'live-sqlite', time: new Date().toISOString() };
  if (pathname === '/api/v1/adapters') return { adapters };
  if (pathname === '/api/v1/capabilities') return { capabilities: buildCapabilityRegistry().list() };
  if (pathname === '/api/v1/agents/status') return { agents: listRuntimeAgents() };
  if (pathname === '/api/summary') return readSummary(paths);
  if (pathname === '/api/sessions') return readSessions(paths);
  if (pathname === '/api/costs') return readCosts(paths);
  if (pathname === '/api/tools') return readTools(paths);
  if (pathname === '/api/cron') return readCron(paths);
  if (pathname === '/api/evidence') return readEvidence(paths);
  if (pathname === '/api/memory') return readMemory(paths);
  return null;
}
