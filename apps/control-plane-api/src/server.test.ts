import { describe, expect, it } from 'vitest';
import { createApiServer } from './server.js';

function request(server: ReturnType<typeof createApiServer>, method: string, path: string, body?: unknown): Promise<{ status: number; json: unknown }> {
  return new Promise((resolve, reject) => {
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (address === null || typeof address === 'string') return reject(new Error('invalid address'));
      globalThis.fetch(`http://127.0.0.1:${address.port}${path}`, { method, headers: body === undefined ? undefined : { 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body) })
        .then(async (res) => { const json = await res.json(); server.close(() => resolve({ status: res.status, json })); }, reject);
    });
  });
}

describe('control plane api', () => {
  it('serves health', async () => {
    const response = await request(createApiServer(), 'GET', '/api/health');
    expect(response.status).toBe(200);
    expect(response.json).toMatchObject({ ok: true, service: 'brenda-ai-cockpit-control-plane' });
  });
  it('serves canonical capabilities and agent status', async () => {
    const capabilities = await request(createApiServer(), 'GET', '/api/v1/capabilities');
    expect(capabilities.status).toBe(200);
    expect(JSON.stringify(capabilities.json)).toContain('hermes.tools');
    const agents = await request(createApiServer(), 'GET', '/api/v1/agents/status');
    expect(agents.status).toBe(200);
    expect(JSON.stringify(agents.json)).toContain('paperclip');
  });

  it('validates delegation requests', async () => {
    const response = await request(createApiServer(), 'POST', '/api/v1/delegate', { max_children: 2, max_spawn_depth: 1, task: 'inspect repo' });
    expect(response.status).toBe(200);
    expect(response.json).toMatchObject({ status: 'accepted' });
  });
});
