import { describe, expect, it } from 'vitest';

describe('adapter registry', () => {
  it('contains the expected production adapters', async () => {
    const mod = await import('..' + '/src/index.js');
    expect(mod.adapters.map((adapter) => adapter.id)).toEqual(['hermes', 'claude-code', 'codex', 'paperclip']);
  });
  it('matches capabilities deterministically', async () => {
    const mod = await import('..' + '/src/index.js');
    expect(mod.findAdaptersForCapability('code_editing').map((adapter) => adapter.id)).toEqual(['claude-code', 'codex']);
  });
  it('throws for unknown ids', async () => {
    const mod = await import('..' + '/src/index.js');
    expect(() => mod.getAdapter('missing')).toThrow('Unknown adapter');
  });
});
