import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { executeQueuedCommand, runAllowedAction, type AllowedAction } from './executor.js';
import { openCockpitStore, type CockpitStore } from './storage.js';

let fixtureDir = '';
let store: CockpitStore;

beforeEach(() => {
  fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-executor-'));
  store = openCockpitStore(join(fixtureDir, 'cockpit.db'));
});

afterEach(() => {
  store.close();
  rmSync(fixtureDir, { recursive: true, force: true });
});

describe('allowed action executor', () => {
  it('executes only catalogued actions and records success', async () => {
    const catalog: AllowedAction[] = [{ id: 'fixture_success', command: process.execPath, args: ['-e', 'console.log("fixture-ok")'], timeoutMs: 5_000, outputLimit: 1_000 }];
    const command = store.submitCommand({ requestedBy: 'brenda', action: 'execute', target: 'fixture_success', risk: 'R2', payload: {} });
    const result = await executeQueuedCommand(store, command.id, fixtureDir, catalog);
    expect(result.status).toBe('succeeded');
    expect(JSON.stringify(store.listAuditEvents())).toContain('fixture-ok');
  });

  it('fails closed for uncatalogued actions', async () => {
    const command = store.submitCommand({ requestedBy: 'brenda', action: 'execute', target: 'not_in_catalog', risk: 'R2', payload: {} });
    const result = await executeQueuedCommand(store, command.id, fixtureDir, []);
    expect(result.status).toBe('failed');
    expect(JSON.stringify(store.listAuditEvents())).toContain('action_not_allowed');
  });

  it('marks timed out actions as failed', async () => {
    const catalog: AllowedAction[] = [{ id: 'fixture_timeout', command: process.execPath, args: ['-e', 'setTimeout(() => console.log("late"), 2000)'], timeoutMs: 50, outputLimit: 1_000 }];
    const command = store.submitCommand({ requestedBy: 'brenda', action: 'execute', target: 'fixture_timeout', risk: 'R2', payload: {} });
    const result = await executeQueuedCommand(store, command.id, fixtureDir, catalog);
    expect(result.status).toBe('failed');
    expect(JSON.stringify(store.listAuditEvents())).toContain('timedOut');
  });

  it('truncates output from child processes', async () => {
    const action: AllowedAction = { id: 'fixture_output_cap', command: process.execPath, args: ['-e', 'console.log("x".repeat(200))'], timeoutMs: 5_000, outputLimit: 20 };
    const result = await runAllowedAction(action, fixtureDir);
    expect(result.stdout.length).toBeLessThan(80);
    expect(result.stdout).toContain('truncated');
  });
});
