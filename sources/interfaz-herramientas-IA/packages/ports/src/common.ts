/**
 * Shared port types used across all port interfaces.
 *
 * These types define the common vocabulary for the hexagonal architecture:
 * health checks, risk levels, approval decisions, adapter capabilities,
 * and async event streaming.
 */

// ── Health ──

export type PortHealthStatus = 'healthy' | 'degraded' | 'unhealthy';

export interface PortHealth {
  readonly adapterName: string;
  readonly status: PortHealthStatus;
  readonly latencyMs: number;
  readonly checkedAt: string;
  readonly message?: string;
  readonly details?: Readonly<Record<string, unknown>>;
}

// ── Streaming ──

export type AsyncEventStream<T> = AsyncIterable<T>;

// ── Idempotency ──

export type IdempotencyKey = string;

// ── Risk & Approval ──

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type ApprovalDecision = 'approved' | 'rejected' | 'pending';

// ── Adapter Metadata ──

export interface AdapterCapabilities {
  readonly adapterName: string;
  readonly portType: string;
  readonly capabilities: readonly string[];
  readonly riskLevel: RiskLevel;
  readonly quotaProvider?: 'zai' | 'chatgpt' | 'claude';
}
