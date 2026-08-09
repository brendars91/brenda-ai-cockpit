import { z } from 'zod';

import {
  TokenUsageSchema,
  ArtifactSchema,
  EvalResultSchema,
  AggregateTypeSchema,
} from './common.js';

// ── Base Event ──

export const BaseEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.string(),
  timestamp: z.string().datetime(),
  aggregateId: z.string(),
  aggregateType: AggregateTypeSchema,
  version: z.literal(1),
  metadata: z.object({
    correlationId: z.string().uuid(),
    causationId: z.string().uuid().optional(),
  }),
});

// ── Session Events ──

export const SessionCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('session.created'),
  aggregateType: z.literal('session'),
  adapter: z.string(),
  agentName: z.string(),
  model: z.string(),
  worktree: z.string(),
});

export const SessionStartedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('session.started'),
  aggregateType: z.literal('session'),
  taskId: z.string(),
});

export const SessionOutputEventSchema = BaseEventSchema.extend({
  eventType: z.literal('session.output'),
  aggregateType: z.literal('session'),
  content: z.string(),
  stream: z.enum(['stdout', 'stderr', 'thinking', 'tool_use', 'tool_result']),
});

export const SessionCompletedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('session.completed'),
  aggregateType: z.literal('session'),
  exitCode: z.number(),
  duration: z.number(),
  tokenUsage: TokenUsageSchema,
});

export const SessionFailedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('session.failed'),
  aggregateType: z.literal('session'),
  error: z.string(),
  exitCode: z.number(),
});

export const SessionApprovalRequestedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('session.approval_requested'),
  aggregateType: z.literal('session'),
  action: z.string(),
  diff: z.string(),
});

export const SessionApprovalResolvedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('session.approval_resolved'),
  aggregateType: z.literal('session'),
  approved: z.boolean(),
  by: z.string(),
});

// ── Task Events ──

export const TaskCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('task.created'),
  aggregateType: z.literal('task'),
  title: z.string(),
  description: z.string(),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  parentId: z.string().optional(),
});

export const TaskAssignedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('task.assigned'),
  aggregateType: z.literal('task'),
  agentId: z.string(),
  adapter: z.string(),
});

export const TaskStartedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('task.started'),
  aggregateType: z.literal('task'),
  sessionId: z.string(),
});

export const TaskCompletedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('task.completed'),
  aggregateType: z.literal('task'),
  result: z.string(),
  artifacts: z.array(ArtifactSchema),
});

export const TaskFailedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('task.failed'),
  aggregateType: z.literal('task'),
  error: z.string(),
  retryable: z.boolean(),
});

// ── Agent Events ──

export const AgentRegisteredEventSchema = BaseEventSchema.extend({
  eventType: z.literal('agent.registered'),
  aggregateType: z.literal('agent'),
  name: z.string(),
  adapter: z.string(),
  capabilities: z.array(z.string()),
  model: z.string(),
});

export const AgentHealthCheckedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('agent.health_checked'),
  aggregateType: z.literal('agent'),
  status: z.enum(['healthy', 'degraded', 'unhealthy']),
  latency: z.number(),
});

export const AgentQuotaConsumedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('agent.quota_consumed'),
  aggregateType: z.literal('agent'),
  provider: z.string(),
  tokensUsed: z.number(),
  costEstimate: z.number(),
});

// ── Run Events ──

export const RunCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('run.created'),
  aggregateType: z.literal('run'),
  taskId: z.string(),
  sessionId: z.string(),
  adapter: z.string(),
  contextPacketHash: z.string(),
});

export const RunProgressEventSchema = BaseEventSchema.extend({
  eventType: z.literal('run.progress'),
  aggregateType: z.literal('run'),
  percent: z.number(),
  message: z.string(),
});

export const RunDiffProducedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('run.diff_produced'),
  aggregateType: z.literal('run'),
  files: z.array(
    z.object({
      path: z.string(),
      additions: z.number(),
      deletions: z.number(),
    }),
  ),
});

export const RunCompletedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('run.completed'),
  aggregateType: z.literal('run'),
  exitCode: z.number(),
  artifacts: z.array(ArtifactSchema),
});

// ── Governance Events ──

export const IssueCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('issue.created'),
  aggregateType: z.literal('issue'),
  issueId: z.string(),
  title: z.string(),
  status: z.string(),
  priority: z.string(),
  assignee: z.string().optional(),
});

export const IssueStatusChangedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('issue.status_changed'),
  aggregateType: z.literal('issue'),
  from: z.string(),
  to: z.string(),
});

export const IssueCommentAddedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('issue.comment_added'),
  aggregateType: z.literal('issue'),
  author: z.string(),
  body: z.string(),
});

export const ApprovalRequestedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('approval.requested'),
  aggregateType: z.literal('issue'),
  targetId: z.string(),
  targetType: z.string(),
  action: z.string(),
  risk: z.enum(['low', 'medium', 'high', 'critical']),
});

export const ApprovalResolvedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('approval.resolved'),
  aggregateType: z.literal('issue'),
  approved: z.boolean(),
  by: z.string(),
  reason: z.string().optional(),
});

// ── Knowledge Events ──

export const KnowledgeCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('knowledge.created'),
  aggregateType: z.literal('knowledge'),
  path: z.string(),
  content: z.string(),
  level: z.enum(['ephemeral', 'tool', 'canon']),
});

export const KnowledgePromotedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('knowledge.promoted'),
  aggregateType: z.literal('knowledge'),
  from: z.enum(['ephemeral', 'tool']),
  to: z.enum(['tool', 'canon']),
  evalResult: EvalResultSchema,
});

export const KnowledgeDriftDetectedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('knowledge.drift_detected'),
  aggregateType: z.literal('knowledge'),
  snapshotHash: z.string(),
  canonHash: z.string(),
  driftScore: z.number(),
});

// ── Policy Events ──

export const PolicyEvaluatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('policy.evaluated'),
  aggregateType: z.literal('policy'),
  action: z.string(),
  resource: z.string(),
  decision: z.enum(['allow', 'deny', 'ask']),
  reason: z.string(),
});

// ── System Events ──

export const SystemQuotaWarningEventSchema = BaseEventSchema.extend({
  eventType: z.literal('system.quota_warning'),
  aggregateType: z.literal('session'),
  provider: z.string(),
  remaining: z.number(),
  windowEndsAt: z.string(),
});

export const SystemQuotaExhaustedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('system.quota_exhausted'),
  aggregateType: z.literal('session'),
  provider: z.string(),
});

export const SystemFreezeActivatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('system.freeze_activated'),
  aggregateType: z.literal('session'),
  reason: z.string(),
  by: z.string(),
});

export const SystemFreezeDeactivatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('system.freeze_deactivated'),
  aggregateType: z.literal('session'),
  by: z.string(),
});

// ── Discriminated Union ──

export const EventSchema = z.discriminatedUnion('eventType', [
  SessionCreatedEventSchema,
  SessionStartedEventSchema,
  SessionOutputEventSchema,
  SessionCompletedEventSchema,
  SessionFailedEventSchema,
  SessionApprovalRequestedEventSchema,
  SessionApprovalResolvedEventSchema,
  TaskCreatedEventSchema,
  TaskAssignedEventSchema,
  TaskStartedEventSchema,
  TaskCompletedEventSchema,
  TaskFailedEventSchema,
  AgentRegisteredEventSchema,
  AgentHealthCheckedEventSchema,
  AgentQuotaConsumedEventSchema,
  RunCreatedEventSchema,
  RunProgressEventSchema,
  RunDiffProducedEventSchema,
  RunCompletedEventSchema,
  IssueCreatedEventSchema,
  IssueStatusChangedEventSchema,
  IssueCommentAddedEventSchema,
  ApprovalRequestedEventSchema,
  ApprovalResolvedEventSchema,
  KnowledgeCreatedEventSchema,
  KnowledgePromotedEventSchema,
  KnowledgeDriftDetectedEventSchema,
  PolicyEvaluatedEventSchema,
  SystemQuotaWarningEventSchema,
  SystemQuotaExhaustedEventSchema,
  SystemFreezeActivatedEventSchema,
  SystemFreezeDeactivatedEventSchema,
]);

// ── Inferred Types ──

export type BaseEvent = z.infer<typeof BaseEventSchema>;
export type SessionCreatedEvent = z.infer<typeof SessionCreatedEventSchema>;
export type SessionStartedEvent = z.infer<typeof SessionStartedEventSchema>;
export type SessionOutputEvent = z.infer<typeof SessionOutputEventSchema>;
export type SessionCompletedEvent = z.infer<typeof SessionCompletedEventSchema>;
export type SessionFailedEvent = z.infer<typeof SessionFailedEventSchema>;
export type SessionApprovalRequestedEvent = z.infer<typeof SessionApprovalRequestedEventSchema>;
export type SessionApprovalResolvedEvent = z.infer<typeof SessionApprovalResolvedEventSchema>;
export type TaskCreatedEvent = z.infer<typeof TaskCreatedEventSchema>;
export type TaskAssignedEvent = z.infer<typeof TaskAssignedEventSchema>;
export type TaskStartedEvent = z.infer<typeof TaskStartedEventSchema>;
export type TaskCompletedEvent = z.infer<typeof TaskCompletedEventSchema>;
export type TaskFailedEvent = z.infer<typeof TaskFailedEventSchema>;
export type AgentRegisteredEvent = z.infer<typeof AgentRegisteredEventSchema>;
export type AgentHealthCheckedEvent = z.infer<typeof AgentHealthCheckedEventSchema>;
export type AgentQuotaConsumedEvent = z.infer<typeof AgentQuotaConsumedEventSchema>;
export type RunCreatedEvent = z.infer<typeof RunCreatedEventSchema>;
export type RunProgressEvent = z.infer<typeof RunProgressEventSchema>;
export type RunDiffProducedEvent = z.infer<typeof RunDiffProducedEventSchema>;
export type RunCompletedEvent = z.infer<typeof RunCompletedEventSchema>;
export type IssueCreatedEvent = z.infer<typeof IssueCreatedEventSchema>;
export type IssueStatusChangedEvent = z.infer<typeof IssueStatusChangedEventSchema>;
export type IssueCommentAddedEvent = z.infer<typeof IssueCommentAddedEventSchema>;
export type ApprovalRequestedEvent = z.infer<typeof ApprovalRequestedEventSchema>;
export type ApprovalResolvedEvent = z.infer<typeof ApprovalResolvedEventSchema>;
export type KnowledgeCreatedEvent = z.infer<typeof KnowledgeCreatedEventSchema>;
export type KnowledgePromotedEvent = z.infer<typeof KnowledgePromotedEventSchema>;
export type KnowledgeDriftDetectedEvent = z.infer<typeof KnowledgeDriftDetectedEventSchema>;
export type PolicyEvaluatedEvent = z.infer<typeof PolicyEvaluatedEventSchema>;
export type SystemQuotaWarningEvent = z.infer<typeof SystemQuotaWarningEventSchema>;
export type SystemQuotaExhaustedEvent = z.infer<typeof SystemQuotaExhaustedEventSchema>;
export type SystemFreezeActivatedEvent = z.infer<typeof SystemFreezeActivatedEventSchema>;
export type SystemFreezeDeactivatedEvent = z.infer<typeof SystemFreezeDeactivatedEventSchema>;
export type Event = z.infer<typeof EventSchema>;
