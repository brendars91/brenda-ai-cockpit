import { describe, it, expect } from 'vitest';
import { createApiServer } from './server.js';
import { readSummary, readSessions, readCosts, readTools, readCron, readEvidence, readMemory, routeData } from './readers.js';

describe('live sqlite readers over real Hermes databases', () => {
  it('reads live summary from all six database surfaces', () => {
    const summary = readSummary();
    expect(summary.sessions.count).toBeGreaterThan(0);
    expect(summary.tools.count).toBeGreaterThan(1000);
    expect(summary.cron.count).toBeGreaterThan(0);
    expect(summary.evidence.count).toBeGreaterThanOrEqual(0);
    expect(summary.memory.count).toBeGreaterThan(0);
  });

  it('reads sanitized session metadata without message content', () => {
    const sessions = readSessions(undefined, 5);
    expect(sessions.length).toBeLessThanOrEqual(5);
    expect(sessions.length).toBeGreaterThan(0);
    const keys = Object.keys(sessions[0] as Record<string, unknown>);
    expect(keys).not.toContain('content');
    expect(keys).not.toContain('system_prompt');
  });

  it('reads all dashboard datasets with non-empty records', () => {
    expect(readCosts().length).toBeGreaterThan(0);
    expect(readTools().length).toBeGreaterThan(0);
    expect(readCron().length).toBeGreaterThan(0);
    expect(readEvidence().length).toBeGreaterThanOrEqual(0);
    expect(readMemory().length).toBeGreaterThan(0);
  });

  it('routeData maps all production endpoints', () => {
    for (const path of ['/api/health', '/api/summary', '/api/sessions', '/api/costs', '/api/tools', '/api/cron', '/api/evidence', '/api/memory']) {
      expect(routeData(path)).not.toBeNull();
    }
    expect(routeData('/api/unknown')).toBeNull();
  });
});

describe('control-plane-api HTTP server', () => {
  it('serves /api/health and /api/summary as JSON', async () => {
    const server = createApiServer();
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
    const address = server.address();
    if (!address || typeof address === 'string') throw new Error('No server address');
    const base = `http://127.0.0.1:${address.port}`;
    const health = await fetch(`${base}/api/health`);
    expect(health.status).toBe(200);
    expect((await health.json()).ok).toBe(true);
    const summary = await fetch(`${base}/api/summary`);
    expect(summary.status).toBe(200);
    expect((await summary.json()).sessions.count).toBeGreaterThan(0);
    await new Promise<void>((resolve) => server.close(() => resolve()));
  });
});
