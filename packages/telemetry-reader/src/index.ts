// Telemetry Reader — query layer over Hermes real SQLite databases
// Zero mock data. All data comes from real snapshots generated from the live system.

// ── Types ──

export interface SessionRecord {
  readonly id: string;
  readonly source: string;
  readonly model: string;
  readonly started_at: string;
  readonly ended_at: string | null;
  readonly message_count: number;
  readonly tool_call_count: number;
  readonly input_tokens: number;
  readonly output_tokens: number;
  readonly reasoning_tokens: number;
  readonly billing_provider: string;
  readonly estimated_cost_usd: number | null;
  readonly title: string;
  readonly chat_type: string;
  readonly profile_name: string;
}

export interface CostBreakdown {
  readonly model: string;
  readonly billing_provider: string;
  readonly session_count: number;
  readonly total_input_tokens: number;
  readonly total_output_tokens: number;
  readonly total_reasoning_tokens: number;
  readonly total_cost: number;
  readonly avg_input_per_session: number;
  readonly avg_output_per_session: number;
}

export interface ToolUsageStat {
  readonly tool_name: string;
  readonly call_count: number;
  readonly sessions_used_in: number;
}

export interface CronHealthStat {
  readonly status: string;
  readonly count: number;
}

export interface EvidenceRecord {
  readonly id: number;
  readonly created_at: string;
  readonly session_id: string;
  readonly command: string;
  readonly canonical_command: string;
  readonly kind: string;
}

export interface MemoryFact {
  readonly fact_id: number;
  readonly content: string;
  readonly category: string;
  readonly trust_score: number;
  readonly tags: string;
}

export interface TelemetrySummary {
  readonly generated_at: string;
  readonly total_sessions: number;
  readonly total_cost_tracked: number;
  readonly total_tool_calls: number;
  readonly total_cron_executions: number;
  readonly total_evidence_events: number;
  readonly total_facts: number;
}

// ── Snapshot loaders ──

import sessionsData from './snapshots/sessions.json';
import costData from './snapshots/cost-intelligence.json';
import toolsData from './snapshots/tool-analytics.json';
import cronData from './snapshots/cron-health.json';
import evidenceData from './snapshots/evidence-ledger.json';
import memoryData from './snapshots/memory-observatory.json';
import summaryData from './snapshots/summary.json';

export const sessions: readonly SessionRecord[] = sessionsData as unknown as SessionRecord[];
export const costBreakdown: readonly CostBreakdown[] = costData as unknown as CostBreakdown[];
export const toolStats: readonly ToolUsageStat[] = toolsData as unknown as ToolUsageStat[];
export const cronHealth: readonly CronHealthStat[] = cronData as unknown as CronHealthStat[];
export const evidenceLedger: readonly EvidenceRecord[] = evidenceData as unknown as EvidenceRecord[];
export const memoryFacts: readonly MemoryFact[] = memoryData as unknown as MemoryFact[];
export const summary: TelemetrySummary = summaryData as unknown as TelemetrySummary;

// ── Analysis engines ──

/** Get the top N most expensive sessions by estimated cost. */
export function getTopSessions(limit = 10): readonly SessionRecord[] {
  return [...sessions]
    .sort((a, b) => (b.estimated_cost_usd ?? 0) - (a.estimated_cost_usd ?? 0))
    .slice(0, limit);
}

/** Sessions sorted by tool call count descending. */
export function getMostActiveSessions(limit = 10): readonly SessionRecord[] {
  return [...sessions]
    .sort((a, b) => b.tool_call_count - a.tool_call_count)
    .slice(0, limit);
}

/** Compute total tokens across all models. */
export function getTotalTokens(): { input: number; output: number; reasoning: number } {
  let input = 0, output = 0, reasoning = 0;
  for (const m of costBreakdown) {
    input += m.total_input_tokens;
    output += m.total_output_tokens;
    reasoning += m.total_reasoning_tokens;
  }
  return { input, output, reasoning };
}

/** Identify anomalies: sessions costing >2x the average. */
export function getCostAnomalies(): readonly SessionRecord[] {
  const costs = sessions.map(s => s.estimated_cost_usd ?? 0).filter(c => c > 0);
  if (costs.length === 0) return [];
  const avg = costs.reduce((a, b) => a + b, 0) / costs.length;
  return sessions.filter(s => (s.estimated_cost_usd ?? 0) > avg * 2);
}

/** Compute the percentage of token consumption by the top model. */
export function getConcentrationRisk(): { model: string; percentage: number } | null {
  if (costBreakdown.length === 0) return null;
  const top = costBreakdown[0];
  const total = getTotalTokens().input;
  if (top === undefined || total === 0) return null;
  return {
    model: top.model,
    percentage: Math.round((top.total_input_tokens / total) * 100),
  };
}

/** Cron success rate as a percentage (0-100). */
export function getCronSuccessRate(): number {
  let completed = 0, total = 0;
  for (const c of cronHealth) {
    total += c.count;
    if (c.status === 'completed') completed += c.count;
  }
  return total === 0 ? 0 : Math.round((completed / total) * 100);
}

/** Group tools by category for heatmap visualization. */
export function getToolCategories(): Record<string, number> {
  const categories: Record<string, number> = {};
  const catMap: Record<string, string> = {
    'terminal': 'execution',
    'read_file': 'reading',
    'search_files': 'reading',
    'write_file': 'writing',
    'patch': 'writing',
    'execute_code': 'execution',
    'web_search': 'external',
    'web_extract': 'external',
    'browser_navigate': 'external',
    'skill_view': 'meta',
    'skill_manage': 'meta',
    'todo': 'meta',
    'memory': 'meta',
    'delegate_task': 'delegation',
  };
  for (const t of toolStats) {
    const cat = catMap[t.tool_name] ?? 'other';
    categories[cat] = (categories[cat] ?? 0) + t.call_count;
  }
  return categories;
}

/** Average trust score across all memory facts. */
export function getAverageTrustScore(): number {
  if (memoryFacts.length === 0) return 0;
  const sum = memoryFacts.reduce((acc, f) => acc + f.trust_score, 0);
  return Math.round((sum / memoryFacts.length) * 100) / 100;
}

/** Get facts with trust score below threshold (potentially unreliable). */
export function getLowTrustFacts(threshold = 0.4): readonly MemoryFact[] {
  return memoryFacts.filter(f => f.trust_score < threshold);
}

/** Session intensity score: combines tokens + tool calls into a single metric. */
export function getSessionIntensity(session: SessionRecord): number {
  const tokenScore = (session.input_tokens + session.output_tokens) / 1_000_000;
  const toolScore = session.tool_call_count / 100;
  return Math.round((tokenScore + toolScore) * 100) / 100;
}

/** Model comparison matrix for the intelligence layer. */
export function getModelComparison(): {
  readonly model: string;
  readonly costPerSession: number;
  readonly tokensPerSession: number;
  readonly efficiencyScore: number;
}[] {
  return costBreakdown.map(m => {
    const costPerSession = m.session_count > 0 ? m.total_cost / m.session_count : 0;
    const tokensPerSession = m.session_count > 0 ? m.total_input_tokens / m.session_count : 0;
    const efficiencyScore = tokensPerSession > 0
      ? Math.round((m.total_output_tokens / tokensPerSession) * 1000) / 1000
      : 0;
    return {
      model: m.model,
      costPerSession: Math.round(costPerSession * 100) / 100,
      tokensPerSession: Math.round(tokensPerSession),
      efficiencyScore,
    };
  });
}
