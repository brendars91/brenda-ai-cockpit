/**
 * AgentRuntimePort — interface for managing agent sessions.
 *
 * Adapters implement this port to provide lifecycle management for
 * AI agent sessions: create, attach, stream events, send input,
 * resolve approvals, and kill sessions.
 */

import type {
  AdapterCapabilities,
  AsyncEventStream,
  IdempotencyKey,
  PortHealth,
  RiskLevel,
} from './common.js';
import type { ContextPacket, Event } from '@cockpit/contracts';

// ── Session Lifecycle ──

export interface CreateSessionRequest {
  readonly adapter: string;
  readonly agentName: string;
  readonly model: string;
  readonly taskDescription: string;
  readonly contextPacket: ContextPacket;
  readonly worktreePath?: string;
  readonly idempotencyKey: IdempotencyKey;
}

export interface AgentSession {
  readonly sessionId: string;
  readonly adapter: string;
  readonly agentName: string;
  readonly model: string;
  readonly status: 'created' | 'running' | 'blocked' | 'completed' | 'failed' | 'killed';
  readonly worktreePath?: string;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface AttachSessionRequest {
  readonly sessionId: string;
}

// ── Input & Approval ──

export interface SessionInput {
  readonly sessionId: string;
  readonly content: string;
  readonly idempotencyKey: IdempotencyKey;
}

export interface ApprovalRequest {
  readonly sessionId: string;
  readonly action: string;
  readonly diff?: string;
  readonly risk: RiskLevel;
}

export interface ApprovalResolution {
  readonly sessionId: string;
  readonly approved: boolean;
  readonly reason?: string;
  readonly by: string;
  readonly idempotencyKey: IdempotencyKey;
}

export interface KillSessionRequest {
  readonly sessionId: string;
  readonly reason: string;
  readonly idempotencyKey: IdempotencyKey;
}

// ── Port Interface ──

export interface AgentRuntimePort {
  readonly adapterName: string;
  readonly capabilities: AdapterCapabilities;

  healthCheck(): Promise<PortHealth>;
  createSession(request: CreateSessionRequest): Promise<AgentSession>;
  attachSession(request: AttachSessionRequest): Promise<AgentSession>;
  listSessions(): Promise<readonly AgentSession[]>;
  streamSessionEvents(sessionId: string): AsyncEventStream<Event>;
  sendInput(input: SessionInput): Promise<void>;
  resolveApproval(resolution: ApprovalResolution): Promise<void>;
  killSession(request: KillSessionRequest): Promise<void>;
}
