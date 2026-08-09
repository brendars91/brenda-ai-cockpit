/**
 * ModelProviderPort — interface for invoking LLM model providers.
 *
 * Adapters implement this port to provide access to model providers
 * (ZAI, ChatGPT, Claude) with quota checks, invocation, streaming,
 * and model discovery.
 */

import type {
  AdapterCapabilities,
  AsyncEventStream,
  IdempotencyKey,
  PortHealth,
} from './common.js';
import type { TokenUsage } from '@cockpit/contracts';

// ── Provider ──

export type ModelProviderName = 'zai' | 'chatgpt' | 'claude';

// ── Messages ──

export interface ModelMessage {
  readonly role: 'system' | 'user' | 'assistant' | 'tool';
  readonly content: string;
  readonly name?: string;
}

// ── Invocation ──

export interface ModelInvocationRequest {
  readonly provider: ModelProviderName;
  readonly model: string;
  readonly messages: readonly ModelMessage[];
  readonly temperature?: number;
  readonly maxTokens?: number;
  readonly tools?: readonly unknown[];
  readonly idempotencyKey: IdempotencyKey;
}

export interface ModelInvocationResponse {
  readonly provider: ModelProviderName;
  readonly model: string;
  readonly content: string;
  readonly finishReason: 'stop' | 'length' | 'tool_calls' | 'content_filter' | 'error';
  readonly tokenUsage: TokenUsage;
  readonly raw?: unknown;
}

// ── Quota ──

export interface QuotaCheckRequest {
  readonly provider: ModelProviderName;
  readonly estimatedTokens: number;
}

export interface QuotaDecision {
  readonly provider: ModelProviderName;
  readonly decision: 'allow' | 'defer' | 'deny' | 'degrade';
  readonly reason: string;
  readonly retryAfter?: string;
  readonly alternativeProvider?: ModelProviderName;
}

// ── Port Interface ──

export interface ModelProviderPort {
  readonly providerName: ModelProviderName;
  readonly capabilities: AdapterCapabilities;

  healthCheck(): Promise<PortHealth>;
  checkQuota(request: QuotaCheckRequest): Promise<QuotaDecision>;
  invoke(request: ModelInvocationRequest): Promise<ModelInvocationResponse>;
  stream(request: ModelInvocationRequest): AsyncEventStream<ModelInvocationResponse>;
  listModels(): Promise<readonly string[]>;
}
