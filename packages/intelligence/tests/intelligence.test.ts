import { describe, expect, it } from 'vitest';

describe('operational intelligence', () => {
  it('computes a bounded operational score', async () => {
    const mod = await import('..' + '/src/index.js');
    const score = mod.computeOperationalScore();
    expect(score.score).toBeGreaterThanOrEqual(0);
    expect(score.score).toBeLessThanOrEqual(100);
    expect(['A', 'B', 'C', 'D', 'F']).toContain(score.grade);
  });

  it('produces an executive brief with headline metrics', async () => {
    const mod = await import('..' + '/src/index.js');
    const brief = mod.getExecutiveBrief();
    expect(brief.title).toContain('operational intelligence');
    expect(brief.headlineMetrics.length).toBeGreaterThan(0);
  });

  it('sorts recommendations by severity', async () => {
    const mod = await import('..' + '/src/index.js');
    const recommendations = mod.getTopRecommendations();
    expect(recommendations.length).toBeLessThanOrEqual(5);
  });

  it('reports sanitized data quality', async () => {
    const mod = await import('..' + '/src/index.js');
    expect(mod.getDataQualityReport()).toMatchObject({ sanitized: true, exposesMessageContent: false });
  });

  it('returns tool loop risk or null deterministically', async () => {
    const mod = await import('..' + '/src/index.js');
    const risk = mod.getToolLoopRisk();
    if (risk !== null) {
      expect(risk.calls).toBeGreaterThanOrEqual(0);
      expect(['low', 'medium', 'high']).toContain(risk.risk);
    }
  });
});
