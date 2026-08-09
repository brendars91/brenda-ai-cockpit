/**
 * KnowledgePort — interface for managing the knowledge base.
 *
 * Adapters implement this port to provide CRUD operations on knowledge
 * entries, full-text search, and promotion through knowledge levels
 * (ephemeral → tool → canon).
 */

import type { AdapterCapabilities, IdempotencyKey, PortHealth } from './common.js';

// ── Knowledge Levels & Entries ──

export type KnowledgeLevel = 'ephemeral' | 'tool' | 'canon';

export interface KnowledgeEntry {
  readonly knowledgeId: string;
  readonly path: string;
  readonly level: KnowledgeLevel;
  readonly contentHash: string;
  readonly title?: string;
  readonly tags: readonly string[];
  readonly createdAt: string;
  readonly updatedAt: string;
}

// ── Requests ──

export interface CreateKnowledgeRequest {
  readonly path: string;
  readonly content: string;
  readonly level: KnowledgeLevel;
  readonly tags?: readonly string[];
  readonly idempotencyKey: IdempotencyKey;
}

export interface ReadKnowledgeRequest {
  readonly knowledgeId?: string;
  readonly path?: string;
}

export interface SearchKnowledgeRequest {
  readonly query: string;
  readonly levels?: readonly KnowledgeLevel[];
  readonly limit?: number;
}

export interface KnowledgeSearchResult {
  readonly entry: KnowledgeEntry;
  readonly relevanceScore: number;
  readonly excerpt: string;
}

/**
 * Target level for promotion. Only non-ephemeral levels are valid targets.
 * 'tool' and 'canon' are the concrete promotion destinations.
 */
export type KnowledgePromotionTarget = Exclude<KnowledgeLevel, 'ephemeral'>;

export interface PromoteKnowledgeRequest {
  readonly knowledgeId: string;
  readonly toLevel: KnowledgePromotionTarget;
  readonly evalSuiteId?: string;
  readonly approvedBy?: string;
  readonly idempotencyKey: IdempotencyKey;
}

// ── Port Interface ──

export interface KnowledgePort {
  readonly adapterName: string;
  readonly capabilities: AdapterCapabilities;

  healthCheck(): Promise<PortHealth>;
  createKnowledge(request: CreateKnowledgeRequest): Promise<KnowledgeEntry>;
  readKnowledge(
    request: ReadKnowledgeRequest,
  ): Promise<{ readonly entry: KnowledgeEntry; readonly content: string }>;
  searchKnowledge(request: SearchKnowledgeRequest): Promise<readonly KnowledgeSearchResult[]>;
  promoteKnowledge(request: PromoteKnowledgeRequest): Promise<KnowledgeEntry>;
  listKnowledge(level?: KnowledgeLevel): Promise<readonly KnowledgeEntry[]>;
}
