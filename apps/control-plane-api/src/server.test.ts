import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { tokenRecordFromPlaintext, type AuthConfig } from './auth.js';
import { assertSafeBindHost, loadRuntimeConfig } from './config.js';
import { createApiServer, type ApiServerOptions } from './server.js';
import { openCockpitStore } from './storage.js';

const readToken = 'fake-read-token-0000000000000000';
const commandToken = 'fake-command-token-0000000000000';
const adminToken = 'fake-admin-token-000000000000000';

const auth: AuthConfig = {
  tokens: [
    tokenRecordFromPlaintext('read', readToken, ['read']),
    tokenRecordFromPlaintext('command', commandToken, ['command']),
    tokenRecordFromPlaintext('admin', adminToken, ['admin']),
  ],
};

interface ResponseShape { status: number; json: unknown; headers: Headers }
interface RequestOptions { method?: string; path?: string; body?: unknown; token?: string; origin?: string; serverOptions?: ApiServerOptions }

function request(options: RequestOptions = {}): Promise<ResponseShape> {
  const server = createApiServer({ auth, cors: { allowedOrigins: ['https://cockpit.tailnet.test'] }, ...options.serverOptions });
  return new Promise((resolve, reject) => {
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (address === null || typeof address === 'string') return reject(new Error('invalid address'));
      const headers: Record<string, string> = {};
      if (options.body !== undefined) headers['Content-Type'] = 'application/json';
      if (options.token) headers.Authorization = `Bearer ${options.token}`;
      if (options.origin) headers.Origin = options.origin;
      fetch(`http://127.0.0.1:${address.port}${options.path ?? '/api/health'}`, {
        method: options.method ?? 'GET',
        headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
      }).then(async (res) => {
        const json = await res.json();
        server.close(() => resolve({ status: res.status, json, headers: res.headers }));
      }, (error) => {
        server.close(() => reject(error));
      });
    });
  });
}

describe('control plane api auth and network boundary', () => {
  it('keeps superficial health public', async () => {
    const response = await request();
    expect(response.status).toBe(200);
    expect(response.json).toMatchObject({ ok: true, service: 'brenda-ai-cockpit-control-plane' });
  });

  it('rejects useful readonly endpoints without bearer auth', async () => {
    const response = await request({ path: '/api/v1/capabilities' });
    expect(response.status).toBe(401);
    expect(response.json).toMatchObject({ error: 'missing_auth' });
  });

  it('rejects invalid tokens without leaking token material', async () => {
    const response = await request({ path: '/api/v1/capabilities', token: 'fake-wrong-token-000000000000000' });
    expect(response.status).toBe(401);
    expect(JSON.stringify(response.json)).not.toContain('fake-wrong-token');
    expect(response.json).toMatchObject({ error: 'invalid_token' });
  });

  it('allows read-scoped tokens on readonly endpoints', async () => {
    const capabilities = await request({ path: '/api/v1/capabilities', token: readToken });
    expect(capabilities.status).toBe(200);
    expect(JSON.stringify(capabilities.json)).toContain('hermes.tools');
    const agents = await request({ path: '/api/v1/agents/status', token: readToken });
    expect(agents.status).toBe(200);
    expect(JSON.stringify(agents.json)).toContain('paperclip');
  });

  it('rejects read-scoped tokens on command endpoints', async () => {
    const response = await request({ method: 'POST', path: '/api/v1/delegate', token: readToken, body: { task: 'inspect repo', max_children: 1 } });
    expect(response.status).toBe(403);
    expect(response.json).toMatchObject({ error: 'insufficient_scope' });
  });

  it('allows command-scoped tokens on command endpoints', async () => {
    const response = await request({ method: 'POST', path: '/api/v1/delegate', token: commandToken, body: { max_children: 2, max_spawn_depth: 1, task: 'inspect repo' } });
    expect(response.status).toBe(200);
    expect(response.json).toMatchObject({ status: 'accepted' });
  });

  it('fails closed when auth is not configured', async () => {
    const response = await request({ path: '/api/v1/capabilities', serverOptions: { auth: undefined } });
    expect(response.status).toBe(503);
    expect(response.json).toMatchObject({ error: 'auth_not_configured' });
  });

  it('permits configured CORS origins and rejects unknown browser origins', async () => {
    const allowed = await request({ path: '/api/v1/capabilities', token: readToken, origin: 'https://cockpit.tailnet.test' });
    expect(allowed.status).toBe(200);
    expect(allowed.headers.get('access-control-allow-origin')).toBe('https://cockpit.tailnet.test');

    const denied = await request({ path: '/api/v1/capabilities', token: readToken, origin: 'https://evil.example.test' });
    expect(denied.status).toBe(403);
    expect(denied.json).toMatchObject({ error: 'cors_origin_denied' });
  });

  it('rejects oversized command payloads before validation', async () => {
    const response = await request({
      method: 'POST',
      path: '/api/v1/delegate',
      token: commandToken,
      serverOptions: { maxBodyBytes: 32 },
      body: { task: 'inspect repo with a body that is intentionally too large for this test' },
    });
    expect(response.status).toBe(413);
    expect(response.json).toMatchObject({ error: 'payload_too_large' });
  });

  it('refuses public bind unless an explicit unsafe override is present', () => {
    expect(() => assertSafeBindHost('0.0.0.0')).toThrow(/public bind/i);
    expect(() => assertSafeBindHost('::')).toThrow(/public bind/i);
    expect(() => assertSafeBindHost('0.0.0.0', true)).not.toThrow();
    expect(loadRuntimeConfig({ COCKPIT_HOST: '127.0.0.1', COCKPIT_PORT: '8787' }).host).toBe('127.0.0.1');
  });
});

describe('control plane command persistence endpoints', () => {
  it('submits, approves, lists and audits commands through HTTP', async () => {
    const fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-command-http-'));
    const store = openCockpitStore(join(fixtureDir, 'cockpit.db'));
    try {
      const lowRisk = await request({
        method: 'POST',
        path: '/api/v1/commands',
        token: commandToken,
        serverOptions: { store },
        body: { action: 'execute', target: 'run_verify', risk: 'R2', payload: { repo: 'cockpit' } },
      });
      expect(lowRisk.status).toBe(200);
      expect(lowRisk.json).toMatchObject({ command: { status: 'queued' } });

      const highRisk = await request({
        method: 'POST',
        path: '/api/v1/commands',
        token: adminToken,
        serverOptions: { store },
        body: { action: 'deploy', target: 'cockpit-api', risk: 'R3', payload: { release: 'candidate' } },
      });
      expect(highRisk.status).toBe(200);
      const highRiskId = (highRisk.json as { command: { id: string } }).command.id;
      expect(highRisk.json).toMatchObject({ command: { status: 'pending_approval' } });

      const approved = await request({
        method: 'POST',
        path: `/api/v1/commands/${highRiskId}/approve`,
        token: adminToken,
        serverOptions: { store },
        body: { reason: 'owner approved deploy' },
      });
      expect(approved.status).toBe(200);
      expect(approved.json).toMatchObject({ command: { status: 'queued', policyDecision: 'allow' } });

      const listed = await request({ path: '/api/v1/commands', token: readToken, serverOptions: { store } });
      expect(listed.status).toBe(200);
      expect((listed.json as { commands: unknown[] }).commands).toHaveLength(2);

      const audit = await request({ path: '/api/v1/audit', token: readToken, serverOptions: { store } });
      expect(audit.status).toBe(200);
      expect(audit.json).toMatchObject({ chain_ok: true });
      expect(JSON.stringify(audit.json)).toContain('command.approved');

      const invalid = await request({
        method: 'POST',
        path: '/api/v1/commands',
        token: commandToken,
        serverOptions: { store },
        body: { action: 'shell', target: 'rm-all', risk: 'R9', payload: {} },
      });
      expect(invalid.status).toBe(400);
      expect(invalid.json).toMatchObject({ error: 'invalid_command' });
    } finally {
      store.close();
      rmSync(fixtureDir, { recursive: true, force: true });
    }
  });

  it('executes queued allowed actions through an admin-only endpoint', async () => {
    const fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-execute-http-'));
    const store = openCockpitStore(join(fixtureDir, 'cockpit.db'));
    try {
      const submitted = await request({
        method: 'POST',
        path: '/api/v1/commands',
        token: adminToken,
        serverOptions: { store },
        body: { action: 'execute', target: 'fixture_http_success', risk: 'R2', payload: {} },
      });
      expect(submitted.status).toBe(200);
      const commandId = (submitted.json as { command: { id: string } }).command.id;

      const fixtureCatalog = [{ id: 'fixture_http_success', command: process.execPath, args: ['-e', 'console.log("http-execute-ok")'], timeoutMs: 5_000, outputLimit: 1_000 }];
      const readTokenDenied = await request({ method: 'POST', path: `/api/v1/commands/${commandId}/execute`, token: readToken, serverOptions: { store, executorCatalog: fixtureCatalog }, body: {} });
      expect(readTokenDenied.status).toBe(403);

      const executed = await request({ method: 'POST', path: `/api/v1/commands/${commandId}/execute`, token: adminToken, serverOptions: { store, executorCatalog: fixtureCatalog }, body: {} });
      expect(executed.status).toBe(200);
      expect(executed.json).toMatchObject({ command: { status: 'succeeded' } });
      expect(JSON.stringify(store.listAuditEvents())).toContain('command.succeeded');
    } finally {
      store.close();
      rmSync(fixtureDir, { recursive: true, force: true });
    }
  });
});
