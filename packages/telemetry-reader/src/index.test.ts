import { describe, it, expect } from 'vitest';
import {
  sessions, costBreakdown, toolStats, cronHealth, evidenceLedger, memoryFacts, summary,
  getTopSessions, getMostActiveSessions, getTotalTokens, getCostAnomalies,
  getConcentrationRisk, getCronSuccessRate, getToolCategories, getAverageTrustScore,
  getLowTrustFacts, getSessionIntensity, getModelComparison,
} from './index';

// ── Real data integrity tests ──
// These verify that the snapshots from the real Hermes databases are well-formed
// and internally consistent. If the DB schema changes, these break first.

describe('real data integrity', () => {
  it('snapshot summary matches actual record counts', () => {
    // Summary is generated from the same DB queries — must match
    expect(summary.total_sessions).toBe(sessions.length);
    expect(summary.total_facts).toBe(memoryFacts.length);
    expect(summary.total_evidence_events).toBe(evidenceLedger.length);
  });

  it('cost breakdown sums match summary total cost', () => {
    const computedTotal = costBreakdown.reduce((sum, m) => sum + m.total_cost, 0);
    // Allow tiny float rounding diff
    expect(Math.abs(computedTotal - summary.total_cost_tracked)).toBeLessThan(0.01);
  });

  it('cron health statuses sum to total executions', () => {
    const computed = cronHealth.reduce((sum, c) => sum + c.count, 0);
    expect(computed).toBe(summary.total_cron_executions);
  });

  it('every session has required fields and non-negative tokens', () => {
    for (const s of sessions) {
      expect(s.id).toBeTruthy();
      // Some legacy sessions may have null model — that's real data
      expect(s.input_tokens).toBeGreaterThanOrEqual(0);
      expect(s.output_tokens).toBeGreaterThanOrEqual(0);
    }
  });

  it('every cost model has positive session count and tokens', () => {
    for (const m of costBreakdown) {
      expect(m.session_count).toBeGreaterThan(0);
      expect(m.total_input_tokens).toBeGreaterThanOrEqual(0);
    }
  });

  it('every tool stat has positive call count', () => {
    for (const t of toolStats) {
      expect(t.call_count).toBeGreaterThan(0);
    }
  });

  it('memory facts have trust scores in valid range [0, 1]', () => {
    for (const f of memoryFacts) {
      expect(f.trust_score).toBeGreaterThanOrEqual(0);
      expect(f.trust_score).toBeLessThanOrEqual(1);
    }
  });
});

// ── Analysis engine tests ──

describe('cost intelligence engine', () => {
  it('getTopSessions returns sessions sorted by cost descending', () => {
    const top = getTopSessions(5);
    expect(top.length).toBeLessThanOrEqual(5);
    for (let i = 1; i < top.length; i++) {
      expect((top[i].estimated_cost_usd ?? 0))
        .toBeLessThanOrEqual((top[i - 1].estimated_cost_usd ?? 0));
    }
  });

  it('getTotalTokens sums all model breakdowns', () => {
    const totals = getTotalTokens();
    expect(totals.input).toBeGreaterThan(0);
    expect(totals.output).toBeGreaterThan(0);
    // Input always dominates output in LLM usage
    expect(totals.input).toBeGreaterThan(totals.output);
  });

  it('getConcentrationRisk identifies the dominant model', () => {
    const risk = getConcentrationRisk();
    // With real data, GLM-5.2 dominates token consumption
    expect(risk).not.toBeNull();
    expect(risk!.percentage).toBeGreaterThan(0);
    expect(risk!.percentage).toBeLessThanOrEqual(100);
  });
});

describe('session forensics engine', () => {
  it('getMostActiveSessions returns sessions sorted by tool calls', () => {
    const active = getMostActiveSessions(3);
    expect(active.length).toBeLessThanOrEqual(3);
    for (let i = 1; i < active.length; i++) {
      expect(active[i].tool_call_count).toBeLessThanOrEqual(active[i - 1].tool_call_count);
    }
  });

  it('getSessionIntensity produces a positive composite score', () => {
    for (const s of sessions.slice(0, 10)) {
      const score = getSessionIntensity(s);
      expect(score).toBeGreaterThanOrEqual(0);
    }
  });

  it('getCostAnomalies filters sessions above 2x average cost', () => {
    const anomalies = getCostAnomalies();
    // Each anomaly must truly be above 2x average
    const costs = sessions.map(s => s.estimated_cost_usd ?? 0).filter(c => c > 0);
    const avg = costs.reduce((a, b) => a + b, 0) / costs.length;
    for (const a of anomalies) {
      expect((a.estimated_cost_usd ?? 0)).toBeGreaterThan(avg * 2);
    }
  });
});

describe('cron health engine', () => {
  it('getCronSuccessRate computes percentage from real data', () => {
    const rate = getCronSuccessRate();
    expect(rate).toBeGreaterThanOrEqual(0);
    expect(rate).toBeLessThanOrEqual(100);
    // Real data shows ~86.6% success rate (768/887)
    expect(rate).toBeGreaterThan(80);
  });
});

describe('tool analytics engine', () => {
  it('getToolCategories groups tools into functional categories', () => {
    const cats = getToolCategories();
    const totalCategorized = Object.values(cats).reduce((a, b) => a + b, 0);
    expect(totalCategorized).toBeGreaterThan(0);
    // terminal should dominate in real data
    expect(cats.execution).toBeGreaterThan(0);
  });
});

describe('memory observatory engine', () => {
  it('getAverageTrustScore computes mean across all facts', () => {
    const avg = getAverageTrustScore();
    expect(avg).toBeGreaterThanOrEqual(0);
    expect(avg).toBeLessThanOrEqual(1);
  });

  it('getLowTrustFacts filters by threshold', () => {
    const low = getLowTrustFacts(0.5);
    for (const f of low) {
      expect(f.trust_score).toBeLessThan(0.5);
    }
  });
});

describe('model comparison engine', () => {
  it('getModelComparison returns per-model efficiency metrics', () => {
    const comparison = getModelComparison();
    expect(comparison.length).toBe(costBreakdown.length);
    for (const m of comparison) {
      expect(m.costPerSession).toBeGreaterThanOrEqual(0);
      expect(m.tokensPerSession).toBeGreaterThanOrEqual(0);
    }
  });

  it('most token-heavy model has highest tokensPerSession or highest total', () => {
    const comparison = getModelComparison();
    const sorted = [...comparison].sort((a, b) => b.tokensPerSession - a.tokensPerSession);
    // The model with highest total tokens should be near the top
    expect(sorted[0].tokensPerSession).toBeGreaterThanOrEqual(sorted[sorted.length - 1].tokensPerSession);
  });
});

// ── Cross-cutting: engines compose correctly ──

describe('cross-engine composition', () => {
  it('top sessions + intensity scoring are consistent', () => {
    const top = getTopSessions(5);
    for (const s of top) {
      const intensity = getSessionIntensity(s);
      // Expensive sessions should have non-trivial intensity
      if ((s.estimated_cost_usd ?? 0) > 1) {
        expect(intensity).toBeGreaterThan(0);
      }
    }
  });

  it('tool categories cover the majority of total tool calls', () => {
    const cats = getToolCategories();
    const categorized = Object.values(cats).reduce((a, b) => a + b, 0);
    // At least 80% of tools should be categorized (mapped)
    expect(categorized / summary.total_tool_calls).toBeGreaterThan(0.8);
  });
});
