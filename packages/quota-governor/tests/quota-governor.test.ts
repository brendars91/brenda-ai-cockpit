import { describe, expect, it } from 'vitest';

import { createDefaultQuotaPolicy, QuotaGovernor, type QuotaProviderName } from '../src/index.js';

const NOW = '2026-06-07T10:00:00.000Z';

function makeGovernor(): QuotaGovernor {
  return new QuotaGovernor({
    now: () => new Date(NOW),
    policy: createDefaultQuotaPolicy({
      zai: { rolling5hBudget: 1_000, weeklyBudget: 10_000, warningThreshold: 0.2 },
      chatgpt: { rolling5hBudget: 2_000, weeklyBudget: 20_000, warningThreshold: 0.2 },
      claude: { rolling5hBudget: 1_500, weeklyBudget: 15_000, warningThreshold: 0.2 },
    }),
  });
}

describe('@cockpit/quota-governor', () => {
  it('allows work when the provider has enough quota', () => {
    const governor = makeGovernor();

    const decision = governor.check({ provider: 'zai', estimatedTokens: 100, taskValue: 'normal' });

    expect(decision).toMatchObject({ provider: 'zai', decision: 'allow' });
    expect(governor.getWindow('zai', 'rolling_5h').remaining).toBe(1_000);
  });

  it('records consumption into rolling and weekly windows', () => {
    const governor = makeGovernor();

    governor.recordConsumption({ provider: 'zai', tokensUsed: 250, source: 'session-1' });

    expect(governor.getWindow('zai', 'rolling_5h').remaining).toBe(750);
    expect(governor.getWindow('zai', 'weekly').remaining).toBe(9_750);
    expect(governor.getUsageEvents()).toHaveLength(1);
  });

  it('defers low-value work when quota is near warning threshold', () => {
    const governor = makeGovernor();
    governor.recordConsumption({ provider: 'zai', tokensUsed: 850, source: 'session-1' });

    const decision = governor.check({ provider: 'zai', estimatedTokens: 100, taskValue: 'low' });

    expect(decision.decision).toBe('defer');
    expect(decision.reason).toContain('warning threshold');
    expect(decision.retryAfter).toBeDefined();
  });

  it('degrades normal work to an alternative provider when available', () => {
    const governor = makeGovernor();
    governor.recordConsumption({ provider: 'zai', tokensUsed: 850, source: 'session-1' });

    const decision = governor.check({
      provider: 'zai',
      estimatedTokens: 100,
      taskValue: 'normal',
      alternativeProviders: ['chatgpt', 'claude'],
    });

    expect(decision).toMatchObject({
      provider: 'zai',
      decision: 'degrade',
      alternativeProvider: 'chatgpt',
    });
  });

  it('denies work when the estimated tokens exceed remaining quota', () => {
    const governor = makeGovernor();
    governor.recordConsumption({ provider: 'zai', tokensUsed: 950, source: 'session-1' });

    const decision = governor.check({
      provider: 'zai',
      estimatedTokens: 100,
      taskValue: 'critical',
    });

    expect(decision.decision).toBe('deny');
    expect(decision.reason).toContain('insufficient quota');
  });

  it('activates freeze when forced over the provider budget', () => {
    const governor = makeGovernor();

    governor.recordConsumption({ provider: 'zai', tokensUsed: 1_001, source: 'session-1' });

    expect(governor.isFrozen()).toBe(true);
    expect(governor.getFreezeState()).toMatchObject({ frozen: true, provider: 'zai' });
    expect(
      governor.check({ provider: 'chatgpt', estimatedTokens: 1, taskValue: 'critical' }).decision,
    ).toBe('deny');
  });

  it('manual freeze blocks all providers until unfrozen', () => {
    const governor = makeGovernor();

    governor.freeze('operator emergency', 'brenda');

    expect(
      governor.check({ provider: 'claude', estimatedTokens: 1, taskValue: 'critical' }),
    ).toMatchObject({
      decision: 'deny',
      reason: 'global freeze active: operator emergency',
    });

    governor.unfreeze('brenda');
    expect(
      governor.check({ provider: 'claude', estimatedTokens: 1, taskValue: 'critical' }).decision,
    ).toBe('allow');
  });

  it('exposes quota windows for the cockpit dashboard', () => {
    const governor = makeGovernor();
    governor.recordConsumption({ provider: 'chatgpt', tokensUsed: 500, source: 'codex' });

    const windows = governor.getAllWindows();
    const providers = new Set<QuotaProviderName>(windows.map((window) => window.provider));

    expect(providers).toEqual(new Set(['zai', 'chatgpt', 'claude']));
    expect(
      windows.find((window) => window.provider === 'chatgpt' && window.windowType === 'rolling_5h'),
    ).toMatchObject({
      consumed: 500,
      remaining: 1_500,
    });
  });
});
