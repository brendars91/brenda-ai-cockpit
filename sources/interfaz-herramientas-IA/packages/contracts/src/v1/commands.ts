import { z } from 'zod';

// ── Base Command ──

export const BaseCommandSchema = z.object({
  commandId: z.string().uuid(),
  commandType: z.string(),
  timestamp: z.string().datetime(),
  idempotencyKey: z.string(),
  version: z.literal(1),
});

// ── Session Commands ──

export const SessionCreateCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('session.create'),
  adapter: z.string(),
  agentName: z.string(),
  model: z.string(),
  taskDescription: z.string(),
  worktreePath: z.string().optional(),
});

export const SessionAttachCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('session.attach'),
  sessionId: z.string(),
});

export const SessionApproveCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('session.approve'),
  sessionId: z.string(),
  approved: z.boolean(),
});

export const SessionKillCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('session.kill'),
  sessionId: z.string(),
  reason: z.string(),
});

export const SessionSendInputCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('session.sendInput'),
  sessionId: z.string(),
  content: z.string(),
});

// ── Task Commands ──

export const TaskCreateCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('task.create'),
  title: z.string(),
  description: z.string(),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  parentId: z.string().optional(),
  assignTo: z.string().optional(),
});

export const TaskAssignCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('task.assign'),
  taskId: z.string(),
  agentId: z.string(),
});

export const TaskCancelCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('task.cancel'),
  taskId: z.string(),
  reason: z.string(),
});

// ── Governance Commands ──

export const IssueCreateCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('issue.create'),
  title: z.string(),
  body: z.string(),
  priority: z.string(),
  assignee: z.string().optional(),
  labels: z.array(z.string()),
});

export const IssueUpdateCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('issue.update'),
  issueId: z.string(),
  status: z.string().optional(),
  assignee: z.string().optional(),
});

export const ApprovalResolveCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('approval.resolve'),
  approvalId: z.string(),
  approved: z.boolean(),
  reason: z.string().optional(),
});

// ── Knowledge Commands ──

export const KnowledgeCreateCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('knowledge.create'),
  path: z.string(),
  content: z.string(),
  level: z.enum(['ephemeral', 'tool', 'canon']),
});

export const KnowledgePromoteCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('knowledge.promote'),
  knowledgeId: z.string(),
  toLevel: z.enum(['tool', 'canon']),
});

// ── System Commands ──

export const SystemFreezeCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('system.freeze'),
  reason: z.string(),
});

export const SystemUnfreezeCommandSchema = BaseCommandSchema.extend({
  commandType: z.literal('system.unfreeze'),
});

// ── Discriminated Union ──

export const CommandSchema = z.discriminatedUnion('commandType', [
  SessionCreateCommandSchema,
  SessionAttachCommandSchema,
  SessionApproveCommandSchema,
  SessionKillCommandSchema,
  SessionSendInputCommandSchema,
  TaskCreateCommandSchema,
  TaskAssignCommandSchema,
  TaskCancelCommandSchema,
  IssueCreateCommandSchema,
  IssueUpdateCommandSchema,
  ApprovalResolveCommandSchema,
  KnowledgeCreateCommandSchema,
  KnowledgePromoteCommandSchema,
  SystemFreezeCommandSchema,
  SystemUnfreezeCommandSchema,
]);

// ── Inferred Types ──

export type BaseCommand = z.infer<typeof BaseCommandSchema>;
export type SessionCreateCommand = z.infer<typeof SessionCreateCommandSchema>;
export type SessionAttachCommand = z.infer<typeof SessionAttachCommandSchema>;
export type SessionApproveCommand = z.infer<typeof SessionApproveCommandSchema>;
export type SessionKillCommand = z.infer<typeof SessionKillCommandSchema>;
export type SessionSendInputCommand = z.infer<typeof SessionSendInputCommandSchema>;
export type TaskCreateCommand = z.infer<typeof TaskCreateCommandSchema>;
export type TaskAssignCommand = z.infer<typeof TaskAssignCommandSchema>;
export type TaskCancelCommand = z.infer<typeof TaskCancelCommandSchema>;
export type IssueCreateCommand = z.infer<typeof IssueCreateCommandSchema>;
export type IssueUpdateCommand = z.infer<typeof IssueUpdateCommandSchema>;
export type ApprovalResolveCommand = z.infer<typeof ApprovalResolveCommandSchema>;
export type KnowledgeCreateCommand = z.infer<typeof KnowledgeCreateCommandSchema>;
export type KnowledgePromoteCommand = z.infer<typeof KnowledgePromoteCommandSchema>;
export type SystemFreezeCommand = z.infer<typeof SystemFreezeCommandSchema>;
export type SystemUnfreezeCommand = z.infer<typeof SystemUnfreezeCommandSchema>;
export type Command = z.infer<typeof CommandSchema>;
