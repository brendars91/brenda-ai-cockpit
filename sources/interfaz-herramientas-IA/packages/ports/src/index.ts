/**
 * @cockpit/ports — Hexagonal architecture port interfaces.
 *
 * This package defines the port interfaces that the core/orchestrator
 * depends on. Adapters implement these ports. No implementation details
 * or adapter-specific imports belong here.
 */

// ── Common types shared across all ports ──
export type {
  PortHealthStatus,
  PortHealth,
  AsyncEventStream,
  IdempotencyKey,
  RiskLevel,
  ApprovalDecision,
  AdapterCapabilities,
} from './common.js';

// ── Agent Runtime Port ──
export type {
  CreateSessionRequest,
  AgentSession,
  AttachSessionRequest,
  SessionInput,
  ApprovalRequest,
  ApprovalResolution,
  KillSessionRequest,
  AgentRuntimePort,
} from './agent-runtime-port.js';

// ── Knowledge Port ──
export type {
  KnowledgeLevel,
  KnowledgePromotionTarget,
  KnowledgeEntry,
  CreateKnowledgeRequest,
  ReadKnowledgeRequest,
  SearchKnowledgeRequest,
  KnowledgeSearchResult,
  PromoteKnowledgeRequest,
  KnowledgePort,
} from './knowledge-port.js';

// ── Governance Port ──
export type {
  IssuePriority,
  IssueStatus,
  GovernanceIssue,
  CreateIssueRequest,
  UpdateIssueRequest,
  Approval,
  CreateApprovalRequest,
  ResolveGovernanceApprovalRequest,
  GovernancePort,
} from './governance-port.js';

// ── Model Provider Port ──
export type {
  ModelProviderName,
  ModelMessage,
  ModelInvocationRequest,
  ModelInvocationResponse,
  QuotaCheckRequest,
  QuotaDecision,
  ModelProviderPort,
} from './model-provider-port.js';
