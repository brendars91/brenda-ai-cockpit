import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { existsSync, mkdtempSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { backupCockpitDb, restoreTestCockpitDb } from './backup.js';
import { openCockpitStore, type CockpitStore } from './storage.js';

let fixtureDir = '';
let store: CockpitStore;
let dbPath = '';

beforeEach(() => {
  fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-backup-'));
  dbPath = join(fixtureDir, 'cockpit.db');
  store = openCockpitStore(dbPath);
});

afterEach(() => {
  store.close();
  rmSync(fixtureDir, { recursive: true, force: true });
});

describe('cockpit backup and restore drill', () => {
  it('creates a physical SQLite backup with manifest and validates restore', async () => {
    const command = store.submitCommand({ requestedBy: 'brenda', action: 'execute', target: 'run_verify', risk: 'R2', payload: { source: 'backup-test' } });
    store.markCommandRunning(command.id);
    store.completeCommand(command.id, 'succeeded', { ok: true });

    const backupDir = join(fixtureDir, 'backups');
    const backup = await backupCockpitDb(dbPath, backupDir, 'fixture');
    expect(existsSync(backup.backupPath)).toBe(true);
    expect(existsSync(backup.manifestPath)).toBe(true);
    expect(backup.bytes).toBeGreaterThan(0);
    expect(readFileSync(backup.manifestPath, 'utf8')).toContain(backup.sha256);

    const restore = restoreTestCockpitDb(backup.backupPath);
    expect(restore).toMatchObject({ ok: true, auditChainOk: true, commandCount: 1 });
    expect(restore.auditEventCount).toBeGreaterThanOrEqual(3);
    expect(restore.migrationCount).toBe(1);
  });

  it('fails restore-test for missing backups', () => {
    expect(() => restoreTestCockpitDb(join(fixtureDir, 'missing.db'))).toThrow(/does not exist/);
  });
});
