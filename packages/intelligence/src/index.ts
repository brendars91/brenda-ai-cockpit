import {
  summary,
  costBreakdown,
  toolStats,
  cronHealth,
  evidenceLedger,
  memoryFacts,
  sessions,
  getConcentrationRisk,
  getCronSuccessRate,
  getCostAnomalies,
  getAverageTrustScore,
  getToolCategories,
  getTotalTokens,
} from '@cockpit/telemetry-reader';

export type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical';

export interface Finding {
  readonly id: string;
  readonly severity: Severity;
  readonly title: string;
  readonly evidence: string;
  readonly recommendation: string;
}

export interface OperationalScore {
  readonly score: number;
  readonly grade: 'A' | 'B' | 'C' | 'D' | 'F';
  readonly components: {
    readonly cron: number;
    readonly evidence: number;
    readonly cost: number;
    readonly memory: number;
    readonly tooling: number;
  };
}

function grade(score: number): OperationalScore['grade'] {
  if (score >= 90) return 'A';
  if (score >= 75) return 'B';
  if (score >= 60) return 'C';
  if (score >= 45) return 'D';
  return 'F';
}

export function computeOperationalScore(): OperationalScore {
  const cronScore = getCronSuccessRate();
  const evidenceScore = Math.min(100, Math.round((evidenceLedger.length / Math.max(1, summary.total_sessions)) * 100));
  const concentration = getConcentrationRisk();
  const costScore = concentration ? Math.max(25, 100 - Math.max(0, concentration.percentage - 50)) : 60;
  const memoryScore = Math.round(getAverageTrustScore() * 100);
  const toolCats = getToolCategories();
  const coverage = Object.values(toolCats).reduce((a, b) => a + b, 0) / Math.max(1, summary.total_tool_calls);
  const toolingScore = Math.round(Math.min(1, coverage) * 100);
  const weighted = Math.round(cronScore * 0.25 + evidenceScore * 0.15 + costScore * 0.25 + memoryScore * 0.2 + toolingScore * 0.15);
  return { score: weighted, grade: grade(weighted), components: { cron: cronScore, evidence: evidenceScore, cost: costScore, memory: memoryScore, tooling: toolingScore } };
}

export function detectFindings(): readonly Finding[] {
  const findings: Finding[] = [];
  const cronRate = getCronSuccessRate();
  const failed = cronHealth.find((c) => c.status === 'failed')?.count ?? 0;
  if (cronRate < 95) {
    findings.push({
      id: 'cron-failure-rate',
      severity: cronRate < 80 ? 'high' : 'medium',
      title: 'Cron failure rate is above production target',
      evidence: `${failed}/${summary.total_cron_executions} executions failed; success rate ${cronRate}%`,
      recommendation: 'Cluster failed executions by job_id/status and add failure fingerprints to the cockpit next.',
    });
  }

  const risk = getConcentrationRisk();
  if (risk && risk.percentage > 65) {
    findings.push({
      id: 'model-concentration',
      severity: risk.percentage > 80 ? 'high' : 'medium',
      title: 'Token consumption is concentrated in one model',
      evidence: `${risk.model} accounts for ${risk.percentage}% of input tokens`,
      recommendation: 'Use routing policy to shift low-risk auxiliary work to cheaper models and track before/after deltas.',
    });
  }

  const anomalies = getCostAnomalies();
  if (anomalies.length > 0) {
    findings.push({
      id: 'cost-anomalies',
      severity: anomalies.length > 5 ? 'medium' : 'low',
      title: 'Cost anomalies detected',
      evidence: `${anomalies.length} sessions cost >2x the average tracked cost`,
      recommendation: 'Open Session Forensics and inspect the top cost sessions for repeated context inflation or tool loops.',
    });
  }

  const trust = getAverageTrustScore();
  if (trust < 0.65) {
    findings.push({
      id: 'memory-trust',
      severity: 'medium',
      title: 'Memory trust average is below ideal operating threshold',
      evidence: `Average memory trust score is ${trust}`,
      recommendation: 'Review low-trust facts, mark helpful/unhelpful, and prune stale operational facts.',
    });
  }

  const evidenceRatio = evidenceLedger.length / Math.max(1, summary.total_sessions);
  if (evidenceRatio < 0.1) {
    findings.push({
      id: 'evidence-coverage',
      severity: 'medium',
      title: 'Evidence coverage is thin relative to session volume',
      evidence: `${evidenceLedger.length} evidence events across ${summary.total_sessions} sampled sessions`,
      recommendation: 'Increase verification_evidence emission for build/test/deploy claims and wire it into the final delivery gate.',
    });
  }

  return findings;
}

export function getExecutiveBrief(): {
  readonly title: string;
  readonly score: OperationalScore;
  readonly findings: readonly Finding[];
  readonly headlineMetrics: readonly string[];
} {
  const totals = getTotalTokens();
  const score = computeOperationalScore();
  const findings = detectFindings();
  return {
    title: 'Brenda AI Cockpit operational intelligence brief',
    score,
    findings,
    headlineMetrics: [
      `${summary.total_sessions} sessions sampled`,
      `${Math.round(totals.input / 1_000_000)}M input tokens tracked`,
      `${summary.total_cron_executions} cron executions`,
      `${summary.total_tool_calls} tool calls`,
      `${memoryFacts.length} memory facts`,
    ],
  };
}

export function getTopRecommendations(): readonly Finding[] {
  const severityRank: Record<Severity, number> = { critical: 5, high: 4, medium: 3, low: 2, info: 1 };
  return [...detectFindings()].sort((a, b) => severityRank[b.severity] - severityRank[a.severity]).slice(0, 5);
}

export function getToolLoopRisk(): { tool: string; calls: number; risk: Severity } | null {
  const top = toolStats[0];
  if (!top) return null;
  const share = top.call_count / Math.max(1, summary.total_tool_calls);
  return { tool: top.tool_name, calls: top.call_count, risk: share > 0.5 ? 'high' : share > 0.3 ? 'medium' : 'low' };
}

export function getDataQualityReport() {
  return {
    hasSessionData: sessions.length > 0,
    hasCostData: costBreakdown.length > 0,
    hasToolData: toolStats.length > 0,
    hasCronData: cronHealth.length > 0,
    hasEvidenceData: evidenceLedger.length >= 0,
    hasMemoryData: memoryFacts.length > 0,
    sanitized: true,
    exposesMessageContent: false,
  };
}
