import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import Database from 'better-sqlite3';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { openCockpitStore, type CockpitStore } from './storage.js';

let fixtureDir = '';
let store: CockpitStore;

beforeEach(() => {
  fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-store-'));
  store = openCockpitStore(join(fixtureDir, 'cockpit.db'));
});

afterEach(() => {
  store.close();
  rmSync(fixtureDir, { recursive: true, force: true });
});

describe('cockpit persistent store', () => {
  it('creates schema migrations and enables WAL', () => {
    const db = new Database(store.dbPath, { readonly: true });
    try {
      const migration = db.prepare('SELECT id FROM schema_migrations WHERE id = 1').get() as { id: number };
      const journalMode = db.pragma('journal_mode', { simple: true });
      expect(migration.id).toBe(1);
      expect(String(journalMode).toLowerCase()).toBe('wal');
    } finally {
      db.close();
    }
  });

  it('appends audit events with a verifiable hash chain', () => {
    const first = store.appendAuditEvent('test.first', 'brenda', 'subject-a', { ok: true });
    const second = store.appendAuditEvent('test.second', 'brenda', 'subject-b', { ok: false });
    expect(first.previousHash).toBe('GENESIS');
    expect(second.previousHash).toBe(first.eventHash);
    expect(store.verifyAuditChain()).toBe(true);
    expect(store.listAuditEvents()).toHaveLength(2);
  });

  it('detects audit tampering', () => {
    store.appendAuditEvent('test.first', 'brenda', 'subject-a', { ok: true });
    const db = new Database(store.dbPath);
    try {
      db.prepare('UPDATE audit_events SET payload_json = ? WHERE id = 1').run('{"tampered":true}');
    } finally {
      db.close();
    }
    expect(store.verifyAuditChain()).toBe(false);
  });

  it('queues low-risk commands and audits submission', () => {
    const command = store.submitCommand({ requestedBy: 'brenda', action: 'execute', target: 'run_verify', risk: 'R2', payload: { repo: 'cockpit' } });
    expect(command.status).toBe('queued');
    expect(command.policyDecision).toBe('allow');
    expect(store.listCommands()).toHaveLength(1);
    expect(store.listAuditEvents()[0].kind).toBe('command.submitted');
  });

  it('keeps high-risk commands pending until owner approval', () => {
    const command = store.submitCommand({ requestedBy: 'brenda', action: 'deploy', target: 'cockpit-api', risk: 'R3', payload: { release: 'candidate' } });
    expect(command.status).toBe('pending_approval');
    const approved = store.approveCommand({ commandId: command.id, approvedBy: 'brenda', reason: 'personal production deploy' });
    expect(approved.status).toBe('queued');
    expect(approved.policyDecision).toBe('allow');
  });

  it('denies credential access fail-closed', () => {
    const command = store.submitCommand({ requestedBy: 'brenda', action: 'credential_access', target: 'local-token', risk: 'R4', payload: {} });
    expect(command.status).toBe('denied');
    expect(command.policyDecision).toBe('deny');
  });

  it('rejects unknown action and risk strings before policy evaluation', () => {
    expect(() => store.submitCommand({ requestedBy: 'brenda', action: 'shell' as never, target: 'bad', risk: 'R2', payload: {} })).toThrow(/invalid action/);
    expect(() => store.submitCommand({ requestedBy: 'brenda', action: 'execute', target: 'bad', risk: 'R9' as never, payload: {} })).toThrow(/invalid risk/);
  });
});
