import { describe, expect, it } from 'vitest';

describe('CapabilityRegistry', () => {
  it('registers, lists and matches capabilities', async () => {
    const mod = await import('..' + '/src/index.js');
    const registry = new mod.CapabilityRegistry();
    registry.register({ id: 'hermes.tools', adapterId: 'hermes', capability: 'tools', risk: 'R1', evidenceRequired: true });
    registry.register({ id: 'codex.code', adapterId: 'codex', capability: 'code_editing', risk: 'R2', evidenceRequired: true });
    expect(registry.list().map((record) => record.id)).toEqual(['codex.code', 'hermes.tools']);
    expect(registry.match('TOOLS')).toHaveLength(1);
  });
  it('rejects empty ids fail-closed', async () => {
    const mod = await import('..' + '/src/index.js');
    const registry = new mod.CapabilityRegistry();
    expect(() => registry.register({ id: ' ', adapterId: 'x', capability: 'x', risk: 'R0', evidenceRequired: false })).toThrow('capability id');
  });
});
