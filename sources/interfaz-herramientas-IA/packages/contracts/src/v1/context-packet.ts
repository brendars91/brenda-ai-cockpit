import { z } from 'zod';

/**
 * Context Packet — delivered by the orchestrator to each adapter before a run.
 * Content-addressed by hash.
 */
export const ContextPacketSchema = z.object({
  // Identity
  packetId: z.string().uuid(),
  version: z.literal(1),

  // Task context
  taskId: z.string(),
  taskTitle: z.string(),
  taskDescription: z.string(),
  parentObjectives: z.array(
    z.object({
      id: z.string(),
      title: z.string(),
      status: z.string(),
    }),
  ),

  // File context (content-addressed)
  fileSnapshots: z.array(
    z.object({
      path: z.string(),
      hash: z.string(),
      content: z.string(),
    }),
  ),

  // Permission context
  permissions: z.object({
    allowedTools: z.array(z.string()),
    deniedTools: z.array(z.string()),
    maxRiskLevel: z.enum(['low', 'medium', 'high', 'critical']),
    requireApproval: z.array(z.string()),
  }),

  // Knowledge context
  relevantKnowledge: z.array(
    z.object({
      path: z.string(),
      level: z.enum(['ephemeral', 'tool', 'canon']),
      relevanceScore: z.number().min(0).max(1),
    }),
  ),

  // MCP context
  enabledMcpServers: z.array(z.string()),

  // Output contract
  outputContract: z.object({
    expectedFiles: z.array(z.string()),
    validationCommand: z.string().optional(),
    testCommand: z.string().optional(),
  }),

  // Metadata
  createdAt: z.string().datetime(),
  hash: z.string(),
});

export type ContextPacket = z.infer<typeof ContextPacketSchema>;
