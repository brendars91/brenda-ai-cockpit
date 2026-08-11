import { describe, expect, it } from 'vitest';

describe('agent runtime console', () => {
  it('lists runtime status for every adapter', async () => {
    const mod = await import('..' + '/src/index.js');
    const statuses = mod.listRuntimeAgents(new Date('2026-01-01T00:00:00Z'));
    expect(statuses.map((status) => status.agent_id)).toEqual(['hermes', 'claude-code', 'codex', 'paperclip']);
    expect(statuses.every((status) => status.last_heartbeat === '2026-01-01T00:00:00.000Z')).toBe(true);
  });

  it('uses policy fail-closed for dangerous runtime commands', async () => {
    const mod = await import('..' + '/src/index.js');
    const decision = mod.authorizeRuntimeCommand({ agent_id: 'hermes', action: 'deploy', target: 'production', risk: 'R3', requested_by: 'operator' });
    expect(decision.decision).toBe('require_approval');
  });
});
