import { z } from 'zod';

// ── Shared schemas used across events, commands, and context packets ──

export const TokenUsageSchema = z.object({
  promptTokens: z.number(),
  completionTokens: z.number(),
  totalTokens: z.number(),
});

export type TokenUsage = z.infer<typeof TokenUsageSchema>;

export const ArtifactSchema = z.object({
  type: z.enum(['file', 'diff', 'command_output', 'knowledge']),
  path: z.string().optional(),
  content: z.string(),
  hash: z.string().optional(),
});

export type Artifact = z.infer<typeof ArtifactSchema>;

export const EvalResultSchema = z.object({
  passed: z.boolean(),
  score: z.number().min(0).max(1),
  details: z.string(),
  evaluatedAt: z.string().datetime(),
  evalSuiteId: z.string(),
});

export type EvalResult = z.infer<typeof EvalResultSchema>;

export const ProviderSchema = z.enum(['zai', 'chatgpt', 'claude']);

export type Provider = z.infer<typeof ProviderSchema>;

export const QuotaWindowSchema = z.object({
  provider: ProviderSchema,
  windowType: z.enum(['rolling_5h', 'weekly']),
  budget: z.number(),
  consumed: z.number(),
  remaining: z.number(),
  windowStart: z.string().datetime(),
  windowEnd: z.string().datetime(),
  projectedExhaustion: z.string().datetime().optional(),
});

export type QuotaWindow = z.infer<typeof QuotaWindowSchema>;

export const AggregateTypeSchema = z.enum([
  'session',
  'task',
  'issue',
  'agent',
  'run',
  'knowledge',
  'policy',
]);

export type AggregateType = z.infer<typeof AggregateTypeSchema>;
