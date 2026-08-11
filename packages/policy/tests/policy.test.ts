import { describe, expect, it } from 'vitest';

describe('evaluatePolicy', () => {
  it('allows reads for viewers', async () => {
    const mod = await import('..' + '/src/index.js');
    expect(mod.evaluatePolicy({ principal: { id: 'b', role: 'viewer' }, action: 'read', target: 'dashboard', risk: 'R0' }).decision).toBe('allow');
  });
  it('denies credential access fail-closed', async () => {
    const mod = await import('..' + '/src/index.js');
    expect(mod.evaluatePolicy({ principal: { id: 'b', role: 'owner' }, action: 'credential_access', target: 'token', risk: 'R4', approvals: ['b'] }).decision).toBe('deny');
  });
  it('requires approval for destructive operations', async () => {
    const mod = await import('..' + '/src/index.js');
    const decision = mod.evaluatePolicy({ principal: { id: 'op', role: 'operator' }, action: 'delete', target: 'workflow', risk: 'R3' });
    expect(decision).toMatchObject({ decision: 'require_approval', requiredApproval: 'owner' });
  });
  it('allows approved owner deployment', async () => {
    const mod = await import('..' + '/src/index.js');
    expect(mod.evaluatePolicy({ principal: { id: 'brenda', role: 'owner' }, action: 'deploy', target: 'prod', risk: 'R3', approvals: ['brenda'] }).decision).toBe('allow');
  });
});
