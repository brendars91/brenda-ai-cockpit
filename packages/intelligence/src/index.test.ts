import { describe, it, expect } from 'vitest';
import { computeOperationalScore, detectFindings, getExecutiveBrief, getTopRecommendations, getToolLoopRisk, getDataQualityReport } from './index';
import { summary } from '@cockpit/telemetry-reader';

describe('intelligence layer over real telemetry', () => {
  it('computes a bounded operational score with component scores', () => {
    const score = computeOperationalScore();
    expect(score.score).toBeGreaterThanOrEqual(0);
    expect(score.score).toBeLessThanOrEqual(100);
    expect(['A', 'B', 'C', 'D', 'F']).toContain(score.grade);
    for (const v of Object.values(score.components)) {
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThanOrEqual(100);
    }
  });

  it('detects real findings from current telemetry', () => {
    const findings = detectFindings();
    expect(findings.length).toBeGreaterThan(0);
    for (const f of findings) {
      expect(f.id).toBeTruthy();
      expect(f.evidence).toBeTruthy();
      expect(f.recommendation).toBeTruthy();
    }
  });

  it('executive brief includes headline metrics grounded in real summary', () => {
    const brief = getExecutiveBrief();
    expect(brief.title).toContain('Brenda AI Cockpit');
    expect(brief.headlineMetrics.join(' ')).toContain(String(summary.total_sessions));
    expect(brief.findings.length).toBeGreaterThan(0);
  });

  it('recommendations are sorted by severity and bounded', () => {
    const recs = getTopRecommendations();
    expect(recs.length).toBeLessThanOrEqual(5);
    expect(recs.length).toBeGreaterThan(0);
  });

  it('tool loop risk identifies the top tool from real usage', () => {
    const risk = getToolLoopRisk();
    expect(risk).not.toBeNull();
    expect(risk!.calls).toBeGreaterThan(0);
  });

  it('data quality report confirms privacy-preserving sanitized snapshots', () => {
    const report = getDataQualityReport();
    expect(report.hasSessionData).toBe(true);
    expect(report.hasCostData).toBe(true);
    expect(report.hasToolData).toBe(true);
    expect(report.hasCronData).toBe(true);
    expect(report.hasMemoryData).toBe(true);
    expect(report.sanitized).toBe(true);
    expect(report.exposesMessageContent).toBe(false);
  });
});
