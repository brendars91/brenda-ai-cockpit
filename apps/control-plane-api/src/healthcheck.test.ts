import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import type { Server } from 'node:http';
import { tokenRecordFromPlaintext, type AuthConfig } from './auth.js';
import { runHealthcheck } from './healthcheck.js';
import { createApiServer } from './server.js';
import { openCockpitStore, type CockpitStore } from './storage.js';

let fixtureDir = '';
let store: CockpitStore;

beforeEach(() => {
  fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-health-'));
  store = openCockpitStore(join(fixtureDir, 'cockpit.db'));
  store.appendAuditEvent('health.fixture', 'test', 'fixture', { ok: true });
});

afterEach(() => {
  store.close();
  rmSync(fixtureDir, { recursive: true, force: true });
});

function listen(server: Server): Promise<string> {
  return new Promise((resolve, reject) => {
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (address === null || typeof address === 'string') return reject(new Error('invalid address'));
      resolve(`http://127.0.0.1:${address.port}`);
    });
  });
}

describe('control plane healthcheck', () => {
  it('performs a deep authenticated healthcheck including audit chain', async () => {
    const token = 'fake-health-token-00000000000000';
    const auth: AuthConfig = { tokens: [tokenRecordFromPlaintext('admin', token, ['admin'])] };
    const server = createApiServer({ store, auth, cors: { allowedOrigins: [] } });
    try {
      const baseUrl = await listen(server);
      await expect(runHealthcheck(baseUrl)).resolves.toMatchObject({ ok: true, healthOk: true });
      await expect(runHealthcheck(baseUrl, token)).resolves.toMatchObject({ ok: true, healthOk: true, auditOk: true });
      await expect(runHealthcheck(baseUrl, 'wrong-token')).resolves.toMatchObject({ ok: false, healthOk: true, auditOk: false });
    } finally {
      await new Promise<void>((resolve) => server.close(() => resolve()));
    }
  });
});
