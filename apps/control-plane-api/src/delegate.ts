import { z } from 'zod';

export const DelegateOptionsSchema = z.object({
  max_children: z.number().min(1).max(20).default(1),
  max_spawn_depth: z.number().min(0).max(10).default(1),
  provider: z.string().optional(),
  model: z.string().optional(),
  prompt: z.string().min(10, 'Prompt must be at least 10 characters').optional(),
  task: z.string().min(5, 'Task must be at least 5 characters').optional(),
});

export type DelegateOptions = z.infer<typeof DelegateOptionsSchema>;

export interface DelegateResult {
  readonly status: 'accepted' | 'rejected';
  readonly reason?: string;
  readonly config?: DelegateOptions;
  readonly timestamp: string;
}

export function validateDelegateRequest(body: string): DelegateResult {
  try {
    const options = DelegateOptionsSchema.parse(JSON.parse(body));
    return {
      status: 'accepted',
      config: options,
      timestamp: new Date().toISOString(),
    };
  } catch (e) {
    return {
      status: 'rejected',
      reason: e instanceof Error ? e.message : 'Invalid request',
      timestamp: new Date().toISOString(),
    };
  }
}
