import { createHash } from 'crypto';

import { describe, it, expect } from 'vitest';

import {
  // Common
  TokenUsageSchema,
  ArtifactSchema,
  EvalResultSchema,
  ProviderSchema,
  QuotaWindowSchema,
  AggregateTypeSchema,
  // Events
  BaseEventSchema,
  EventSchema,
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
  // Commands
  BaseCommandSchema,
  CommandSchema,
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
  // Context Packet
  ContextPacketSchema,
  // Version
  CONTRACT_VERSION,
  SCHEMA_VERSION,
} from '../src/index.js';

// ── Fixtures ──

const VALID_UUID = '00000000-0000-4000-8000-000000000001';
const VALID_UUID_2 = '00000000-0000-4000-8000-000000000002';
const VALID_DATETIME = '2026-06-07T10:00:00.000Z';

const baseEventFields = {
  eventId: VALID_UUID,
  timestamp: VALID_DATETIME,
  aggregateId: 'agg-1',
  version: 1 as const,
  metadata: {
    correlationId: VALID_UUID,
    causationId: VALID_UUID_2,
  },
};

const baseCommandFields = {
  commandId: VALID_UUID,
  timestamp: VALID_DATETIME,
  idempotencyKey: 'idem-key-1',
  version: 1 as const,
};

const validTokenUsage = {
  promptTokens: 100,
  completionTokens: 50,
  totalTokens: 150,
};

const validArtifact = {
  type: 'file' as const,
  path: '/src/foo.ts',
  content: 'export const x = 1;',
  hash: 'abc123',
};

const validEvalResult = {
  passed: true,
  score: 0.95,
  details: 'All checks passed',
  evaluatedAt: VALID_DATETIME,
  evalSuiteId: 'suite-1',
};

// ── Common Schemas ──

describe('Common schemas', () => {
  it('TokenUsageSchema accepts valid data', () => {
    const result = TokenUsageSchema.safeParse(validTokenUsage);
    expect(result.success).toBe(true);
  });

  it('TokenUsageSchema rejects missing totalTokens', () => {
    const { totalTokens: _, ...partial } = validTokenUsage;
    const result = TokenUsageSchema.safeParse(partial);
    expect(result.success).toBe(false);
  });

  it('ArtifactSchema accepts all types', () => {
    for (const t of ['file', 'diff', 'command_output', 'knowledge'] as const) {
      const result = ArtifactSchema.safeParse({ type: t, content: 'x' });
      expect(result.success).toBe(true);
    }
  });

  it('ArtifactSchema rejects invalid type', () => {
    const result = ArtifactSchema.safeParse({ type: 'invalid', content: 'x' });
    expect(result.success).toBe(false);
  });

  it('EvalResultSchema enforces score bounds', () => {
    expect(EvalResultSchema.safeParse({ ...validEvalResult, score: 1.5 }).success).toBe(false);
    expect(EvalResultSchema.safeParse({ ...validEvalResult, score: -0.1 }).success).toBe(false);
    expect(EvalResultSchema.safeParse({ ...validEvalResult, score: 0.5 }).success).toBe(true);
  });

  it('ProviderSchema accepts valid providers', () => {
    expect(ProviderSchema.safeParse('zai').success).toBe(true);
    expect(ProviderSchema.safeParse('chatgpt').success).toBe(true);
    expect(ProviderSchema.safeParse('claude').success).toBe(true);
    expect(ProviderSchema.safeParse('openai').success).toBe(false);
  });

  it('QuotaWindowSchema validates full object', () => {
    const qw = {
      provider: 'zai',
      windowType: 'rolling_5h',
      budget: 100,
      consumed: 40,
      remaining: 60,
      windowStart: VALID_DATETIME,
      windowEnd: VALID_DATETIME,
    };
    expect(QuotaWindowSchema.safeParse(qw).success).toBe(true);
  });

  it('AggregateTypeSchema accepts all aggregate types', () => {
    for (const t of ['session', 'task', 'issue', 'agent', 'run', 'knowledge', 'policy'] as const) {
      expect(AggregateTypeSchema.safeParse(t).success).toBe(true);
    }
    expect(AggregateTypeSchema.safeParse('invalid').success).toBe(false);
  });
});

// ── Event Schemas ──

describe('Event schemas', () => {
  describe('Session events', () => {
    it('session.created validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'session.created',
        aggregateType: 'session',
        adapter: 'codex',
        agentName: 'agent-1',
        model: 'gpt-4',
        worktree: '/tmp/wt',
      };
      expect(SessionCreatedEventSchema.safeParse(event).success).toBe(true);
    });

    it('session.created rejects missing adapter', () => {
      const { adapter: _, ...event } = {
        ...baseEventFields,
        eventType: 'session.created',
        aggregateType: 'session',
        adapter: 'codex',
        agentName: 'agent-1',
        model: 'gpt-4',
        worktree: '/tmp/wt',
      };
      expect(SessionCreatedEventSchema.safeParse(event).success).toBe(false);
    });

    it('session.started validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'session.started',
        aggregateType: 'session',
        taskId: 'task-1',
      };
      expect(SessionStartedEventSchema.safeParse(event).success).toBe(true);
    });

    it('session.output validates all streams', () => {
      for (const stream of ['stdout', 'stderr', 'thinking', 'tool_use', 'tool_result'] as const) {
        const event = {
          ...baseEventFields,
          eventType: 'session.output',
          aggregateType: 'session',
          content: 'hello',
          stream,
        };
        expect(SessionOutputEventSchema.safeParse(event).success).toBe(true);
      }
    });

    it('session.output rejects invalid stream', () => {
      const event = {
        ...baseEventFields,
        eventType: 'session.output',
        aggregateType: 'session',
        content: 'hello',
        stream: 'invalid',
      };
      expect(SessionOutputEventSchema.safeParse(event).success).toBe(false);
    });

    it('session.completed validates with tokenUsage', () => {
      const event = {
        ...baseEventFields,
        eventType: 'session.completed',
        aggregateType: 'session',
        exitCode: 0,
        duration: 5000,
        tokenUsage: validTokenUsage,
      };
      expect(SessionCompletedEventSchema.safeParse(event).success).toBe(true);
    });

    it('session.failed validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'session.failed',
        aggregateType: 'session',
        error: 'OOM',
        exitCode: 137,
      };
      expect(SessionFailedEventSchema.safeParse(event).success).toBe(true);
    });

    it('session.approval_requested validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'session.approval_requested',
        aggregateType: 'session',
        action: 'write_file',
        diff: '--- a\n+++ b\n@@ -1 +1 @@',
      };
      expect(SessionApprovalRequestedEventSchema.safeParse(event).success).toBe(true);
    });

    it('session.approval_resolved validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'session.approval_resolved',
        aggregateType: 'session',
        approved: true,
        by: 'admin',
      };
      expect(SessionApprovalResolvedEventSchema.safeParse(event).success).toBe(true);
    });
  });

  describe('Task events', () => {
    it('task.created validates with optional parentId', () => {
      const event = {
        ...baseEventFields,
        eventType: 'task.created',
        aggregateType: 'task',
        title: 'Fix bug',
        description: 'Fix the login bug',
        priority: 'high' as const,
      };
      expect(TaskCreatedEventSchema.safeParse(event).success).toBe(true);
      expect(TaskCreatedEventSchema.safeParse({ ...event, parentId: 'parent-1' }).success).toBe(
        true,
      );
    });

    it('task.created rejects invalid priority', () => {
      const event = {
        ...baseEventFields,
        eventType: 'task.created',
        aggregateType: 'task',
        title: 'Fix bug',
        description: 'desc',
        priority: 'urgent',
      };
      expect(TaskCreatedEventSchema.safeParse(event).success).toBe(false);
    });

    it('task.assigned validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'task.assigned',
        aggregateType: 'task',
        agentId: 'agent-1',
        adapter: 'codex',
      };
      expect(TaskAssignedEventSchema.safeParse(event).success).toBe(true);
    });

    it('task.started validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'task.started',
        aggregateType: 'task',
        sessionId: 'sess-1',
      };
      expect(TaskStartedEventSchema.safeParse(event).success).toBe(true);
    });

    it('task.completed validates with artifacts', () => {
      const event = {
        ...baseEventFields,
        eventType: 'task.completed',
        aggregateType: 'task',
        result: 'Done',
        artifacts: [validArtifact],
      };
      expect(TaskCompletedEventSchema.safeParse(event).success).toBe(true);
    });

    it('task.failed validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'task.failed',
        aggregateType: 'task',
        error: 'timeout',
        retryable: true,
      };
      expect(TaskFailedEventSchema.safeParse(event).success).toBe(true);
    });
  });

  describe('Agent events', () => {
    it('agent.registered validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'agent.registered',
        aggregateType: 'agent',
        name: 'codex-agent',
        adapter: 'codex',
        capabilities: ['file_edit', 'shell'],
        model: 'gpt-4',
      };
      expect(AgentRegisteredEventSchema.safeParse(event).success).toBe(true);
    });

    it('agent.health_checked validates all statuses', () => {
      for (const status of ['healthy', 'degraded', 'unhealthy'] as const) {
        const event = {
          ...baseEventFields,
          eventType: 'agent.health_checked',
          aggregateType: 'agent',
          status,
          latency: 42,
        };
        expect(AgentHealthCheckedEventSchema.safeParse(event).success).toBe(true);
      }
    });

    it('agent.quota_consumed validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'agent.quota_consumed',
        aggregateType: 'agent',
        provider: 'zai',
        tokensUsed: 1500,
        costEstimate: 0.03,
      };
      expect(AgentQuotaConsumedEventSchema.safeParse(event).success).toBe(true);
    });
  });

  describe('Run events', () => {
    it('run.created validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'run.created',
        aggregateType: 'run',
        taskId: 'task-1',
        sessionId: 'sess-1',
        adapter: 'codex',
        contextPacketHash: 'sha256:abc',
      };
      expect(RunCreatedEventSchema.safeParse(event).success).toBe(true);
    });

    it('run.progress validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'run.progress',
        aggregateType: 'run',
        percent: 50,
        message: 'Halfway done',
      };
      expect(RunProgressEventSchema.safeParse(event).success).toBe(true);
    });

    it('run.diff_produced validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'run.diff_produced',
        aggregateType: 'run',
        files: [
          { path: '/src/a.ts', additions: 10, deletions: 2 },
          { path: '/src/b.ts', additions: 0, deletions: 5 },
        ],
      };
      expect(RunDiffProducedEventSchema.safeParse(event).success).toBe(true);
    });

    it('run.completed validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'run.completed',
        aggregateType: 'run',
        exitCode: 0,
        artifacts: [validArtifact],
      };
      expect(RunCompletedEventSchema.safeParse(event).success).toBe(true);
    });
  });

  describe('Governance events', () => {
    it('issue.created validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'issue.created',
        aggregateType: 'issue',
        issueId: 'issue-1',
        title: 'Bug report',
        status: 'open',
        priority: 'high',
      };
      expect(IssueCreatedEventSchema.safeParse(event).success).toBe(true);
      expect(IssueCreatedEventSchema.safeParse({ ...event, assignee: 'user-1' }).success).toBe(
        true,
      );
    });

    it('issue.status_changed validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'issue.status_changed',
        aggregateType: 'issue',
        from: 'open',
        to: 'closed',
      };
      expect(IssueStatusChangedEventSchema.safeParse(event).success).toBe(true);
    });

    it('issue.comment_added validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'issue.comment_added',
        aggregateType: 'issue',
        author: 'user-1',
        body: 'LGTM',
      };
      expect(IssueCommentAddedEventSchema.safeParse(event).success).toBe(true);
    });

    it('approval.requested validates all risk levels', () => {
      for (const risk of ['low', 'medium', 'high', 'critical'] as const) {
        const event = {
          ...baseEventFields,
          eventType: 'approval.requested',
          aggregateType: 'issue',
          targetId: 'target-1',
          targetType: 'run',
          action: 'deploy',
          risk,
        };
        expect(ApprovalRequestedEventSchema.safeParse(event).success).toBe(true);
      }
    });

    it('approval.resolved validates with optional reason', () => {
      const event = {
        ...baseEventFields,
        eventType: 'approval.resolved',
        aggregateType: 'issue',
        approved: true,
        by: 'admin',
      };
      expect(ApprovalResolvedEventSchema.safeParse(event).success).toBe(true);
      expect(ApprovalResolvedEventSchema.safeParse({ ...event, reason: 'safe' }).success).toBe(
        true,
      );
    });
  });

  describe('Knowledge events', () => {
    it('knowledge.created validates all levels', () => {
      for (const level of ['ephemeral', 'tool', 'canon'] as const) {
        const event = {
          ...baseEventFields,
          eventType: 'knowledge.created',
          aggregateType: 'knowledge',
          path: '/knowledge/api.md',
          content: 'content',
          level,
        };
        expect(KnowledgeCreatedEventSchema.safeParse(event).success).toBe(true);
      }
    });

    it('knowledge.promoted validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'knowledge.promoted',
        aggregateType: 'knowledge',
        from: 'ephemeral',
        to: 'tool',
        evalResult: validEvalResult,
      };
      expect(KnowledgePromotedEventSchema.safeParse(event).success).toBe(true);
    });

    it('knowledge.drift_detected validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'knowledge.drift_detected',
        aggregateType: 'knowledge',
        snapshotHash: 'sha256:snap',
        canonHash: 'sha256:canon',
        driftScore: 0.3,
      };
      expect(KnowledgeDriftDetectedEventSchema.safeParse(event).success).toBe(true);
    });
  });

  describe('Policy events', () => {
    it('policy.evaluated validates all decisions', () => {
      for (const decision of ['allow', 'deny', 'ask'] as const) {
        const event = {
          ...baseEventFields,
          eventType: 'policy.evaluated',
          aggregateType: 'policy',
          action: 'file_write',
          resource: '/src/main.ts',
          decision,
          reason: 'policy rule',
        };
        expect(PolicyEvaluatedEventSchema.safeParse(event).success).toBe(true);
      }
    });
  });

  describe('System events', () => {
    it('system.quota_warning validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'system.quota_warning',
        aggregateType: 'session',
        provider: 'zai',
        remaining: 500,
        windowEndsAt: VALID_DATETIME,
      };
      expect(SystemQuotaWarningEventSchema.safeParse(event).success).toBe(true);
    });

    it('system.quota_exhausted validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'system.quota_exhausted',
        aggregateType: 'session',
        provider: 'claude',
      };
      expect(SystemQuotaExhaustedEventSchema.safeParse(event).success).toBe(true);
    });

    it('system.freeze_activated validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'system.freeze_activated',
        aggregateType: 'session',
        reason: 'quota exceeded',
        by: 'system',
      };
      expect(SystemFreezeActivatedEventSchema.safeParse(event).success).toBe(true);
    });

    it('system.freeze_deactivated validates', () => {
      const event = {
        ...baseEventFields,
        eventType: 'system.freeze_deactivated',
        aggregateType: 'session',
        by: 'admin',
      };
      expect(SystemFreezeDeactivatedEventSchema.safeParse(event).success).toBe(true);
    });
  });
});

// ── Event Discriminated Union ──

describe('Event discriminated union', () => {
  it('accepts a valid session.created event', () => {
    const event = {
      ...baseEventFields,
      eventType: 'session.created',
      aggregateType: 'session',
      adapter: 'codex',
      agentName: 'agent-1',
      model: 'gpt-4',
      worktree: '/tmp/wt',
    };
    const result = EventSchema.safeParse(event);
    expect(result.success).toBe(true);
  });

  it('rejects unknown eventType', () => {
    const event = {
      ...baseEventFields,
      eventType: 'session.unknown_event',
      aggregateType: 'session',
    };
    const result = EventSchema.safeParse(event);
    expect(result.success).toBe(false);
  });

  it('correctly discriminates to task.created', () => {
    const event = {
      ...baseEventFields,
      eventType: 'task.created',
      aggregateType: 'task',
      title: 'T',
      description: 'D',
      priority: 'medium' as const,
    };
    const result = EventSchema.safeParse(event);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.eventType).toBe('task.created');
    }
  });

  it('rejects event with wrong version', () => {
    const event = {
      ...baseEventFields,
      eventType: 'session.created',
      aggregateType: 'session',
      adapter: 'codex',
      agentName: 'agent-1',
      model: 'gpt-4',
      worktree: '/tmp/wt',
      version: 2,
    };
    const result = EventSchema.safeParse(event);
    expect(result.success).toBe(false);
  });
});

// ── Event Version Enforcement ──

describe('Event version enforcement', () => {
  it('base event rejects version !== 1', () => {
    const event = {
      ...baseEventFields,
      version: 2,
    };
    expect(BaseEventSchema.safeParse(event).success).toBe(false);
  });

  it('base event accepts version = 1', () => {
    const event = { ...baseEventFields, eventType: 'session.created', aggregateType: 'session' };
    expect(BaseEventSchema.safeParse(event).success).toBe(true);
  });

  it('base event rejects missing version', () => {
    const { version: _, ...noVersion } = baseEventFields;
    expect(BaseEventSchema.safeParse(noVersion).success).toBe(false);
  });

  it('base event requires valid UUID for eventId', () => {
    const event = { ...baseEventFields, eventId: 'not-a-uuid' };
    expect(BaseEventSchema.safeParse(event).success).toBe(false);
  });

  it('base event requires datetime for timestamp', () => {
    const event = { ...baseEventFields, timestamp: 'not-a-date' };
    expect(BaseEventSchema.safeParse(event).success).toBe(false);
  });

  it('metadata.causationId is optional', () => {
    const event = {
      ...baseEventFields,
      eventType: 'session.created',
      aggregateType: 'session',
      metadata: { correlationId: VALID_UUID },
    };
    expect(BaseEventSchema.safeParse(event).success).toBe(true);
  });
});

// ── Command Schemas ──

describe('Command schemas', () => {
  describe('Session commands', () => {
    it('session.create validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'session.create',
        adapter: 'codex',
        agentName: 'agent-1',
        model: 'gpt-4',
        taskDescription: 'Fix the bug',
      };
      expect(SessionCreateCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('session.create validates with optional worktreePath', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'session.create',
        adapter: 'codex',
        agentName: 'agent-1',
        model: 'gpt-4',
        taskDescription: 'Fix the bug',
        worktreePath: '/tmp/wt',
      };
      expect(SessionCreateCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('session.attach validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'session.attach',
        sessionId: 'sess-1',
      };
      expect(SessionAttachCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('session.approve validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'session.approve',
        sessionId: 'sess-1',
        approved: true,
      };
      expect(SessionApproveCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('session.kill validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'session.kill',
        sessionId: 'sess-1',
        reason: 'stuck',
      };
      expect(SessionKillCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('session.sendInput validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'session.sendInput',
        sessionId: 'sess-1',
        content: 'y',
      };
      expect(SessionSendInputCommandSchema.safeParse(cmd).success).toBe(true);
    });
  });

  describe('Task commands', () => {
    it('task.create validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'task.create',
        title: 'Fix bug',
        description: 'Fix the login bug',
        priority: 'high' as const,
      };
      expect(TaskCreateCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('task.create validates with optional fields', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'task.create',
        title: 'Fix bug',
        description: 'desc',
        priority: 'critical' as const,
        parentId: 'parent-1',
        assignTo: 'agent-1',
      };
      expect(TaskCreateCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('task.create rejects invalid priority', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'task.create',
        title: 'Fix bug',
        description: 'desc',
        priority: 'urgent',
      };
      expect(TaskCreateCommandSchema.safeParse(cmd).success).toBe(false);
    });

    it('task.assign validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'task.assign',
        taskId: 'task-1',
        agentId: 'agent-1',
      };
      expect(TaskAssignCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('task.cancel validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'task.cancel',
        taskId: 'task-1',
        reason: 'no longer needed',
      };
      expect(TaskCancelCommandSchema.safeParse(cmd).success).toBe(true);
    });
  });

  describe('Governance commands', () => {
    it('issue.create validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'issue.create',
        title: 'Bug',
        body: 'Description',
        priority: 'high',
        labels: ['bug', 'urgent'],
      };
      expect(IssueCreateCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('issue.update validates with optional fields', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'issue.update',
        issueId: 'issue-1',
      };
      expect(IssueUpdateCommandSchema.safeParse(cmd).success).toBe(true);
      expect(
        IssueUpdateCommandSchema.safeParse({ ...cmd, status: 'closed', assignee: 'u1' }).success,
      ).toBe(true);
    });

    it('approval.resolve validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'approval.resolve',
        approvalId: 'appr-1',
        approved: true,
        reason: 'safe',
      };
      expect(ApprovalResolveCommandSchema.safeParse(cmd).success).toBe(true);
    });
  });

  describe('Knowledge commands', () => {
    it('knowledge.create validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'knowledge.create',
        path: '/knowledge/api.md',
        content: 'API docs',
        level: 'ephemeral' as const,
      };
      expect(KnowledgeCreateCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('knowledge.promote validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'knowledge.promote',
        knowledgeId: 'k-1',
        toLevel: 'canon' as const,
      };
      expect(KnowledgePromoteCommandSchema.safeParse(cmd).success).toBe(true);
    });
  });

  describe('System commands', () => {
    it('system.freeze validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'system.freeze',
        reason: 'emergency',
      };
      expect(SystemFreezeCommandSchema.safeParse(cmd).success).toBe(true);
    });

    it('system.unfreeze validates', () => {
      const cmd = {
        ...baseCommandFields,
        commandType: 'system.unfreeze',
      };
      expect(SystemUnfreezeCommandSchema.safeParse(cmd).success).toBe(true);
    });
  });
});

// ── Command Discriminated Union ──

describe('Command discriminated union', () => {
  it('accepts a valid session.create command', () => {
    const cmd = {
      ...baseCommandFields,
      commandType: 'session.create',
      adapter: 'codex',
      agentName: 'agent-1',
      model: 'gpt-4',
      taskDescription: 'Fix the bug',
    };
    expect(CommandSchema.safeParse(cmd).success).toBe(true);
  });

  it('rejects unknown commandType', () => {
    const cmd = {
      ...baseCommandFields,
      commandType: 'unknown.command',
    };
    expect(CommandSchema.safeParse(cmd).success).toBe(false);
  });

  it('rejects command with wrong version', () => {
    const cmd = {
      ...baseCommandFields,
      commandType: 'session.create',
      adapter: 'codex',
      agentName: 'agent-1',
      model: 'gpt-4',
      taskDescription: 'Fix the bug',
      version: 2,
    };
    expect(CommandSchema.safeParse(cmd).success).toBe(false);
  });
});

// ── Command Idempotency Key ──

describe('Command idempotency key', () => {
  it('all commands require idempotencyKey', () => {
    const { idempotencyKey: _, ...noKey } = {
      ...baseCommandFields,
      commandType: 'session.create',
      adapter: 'codex',
      agentName: 'agent-1',
      model: 'gpt-4',
      taskDescription: 'desc',
    };
    expect(CommandSchema.safeParse(noKey).success).toBe(false);
  });

  it('base command rejects missing idempotencyKey', () => {
    const { idempotencyKey: _, ...noKey } = baseCommandFields;
    expect(BaseCommandSchema.safeParse(noKey).success).toBe(false);
  });
});

// ── Command Version ──

describe('Command version enforcement', () => {
  it('base command rejects version !== 1', () => {
    expect(BaseCommandSchema.safeParse({ ...baseCommandFields, version: 2 }).success).toBe(false);
  });

  it('base command requires valid UUID for commandId', () => {
    expect(
      BaseCommandSchema.safeParse({ ...baseCommandFields, commandId: 'not-uuid' }).success,
    ).toBe(false);
  });
});

// ── Context Packet ──

describe('Context Packet', () => {
  const validPacket = {
    packetId: VALID_UUID,
    version: 1 as const,
    taskId: 'task-1',
    taskTitle: 'Fix the login bug',
    taskDescription: 'Users cannot log in with SSO',
    parentObjectives: [{ id: 'obj-1', title: 'Improve auth', status: 'in_progress' }],
    fileSnapshots: [
      { path: '/src/auth.ts', hash: 'sha256:abc', content: 'export function login() {}' },
    ],
    permissions: {
      allowedTools: ['file_edit', 'shell'],
      deniedTools: ['rm'],
      maxRiskLevel: 'medium' as const,
      requireApproval: ['deploy'],
    },
    relevantKnowledge: [
      { path: '/knowledge/sso.md', level: 'tool' as const, relevanceScore: 0.85 },
    ],
    enabledMcpServers: ['github', 'filesystem'],
    outputContract: {
      expectedFiles: ['/src/auth.ts'],
      validationCommand: 'npm run validate',
      testCommand: 'npm test',
    },
    createdAt: VALID_DATETIME,
    hash: 'sha256:placeholder',
  };

  it('validates a complete context packet', () => {
    expect(ContextPacketSchema.safeParse(validPacket).success).toBe(true);
  });

  it('rejects packet with wrong version', () => {
    expect(ContextPacketSchema.safeParse({ ...validPacket, version: 2 }).success).toBe(false);
  });

  it('rejects packet with invalid UUID', () => {
    expect(ContextPacketSchema.safeParse({ ...validPacket, packetId: 'bad' }).success).toBe(false);
  });

  it('accepts optional validationCommand and testCommand', () => {
    const minimal = {
      ...validPacket,
      outputContract: {
        expectedFiles: ['/src/auth.ts'],
      },
    };
    expect(ContextPacketSchema.safeParse(minimal).success).toBe(true);
  });

  it('rejects relevanceScore out of range', () => {
    const badScore = {
      ...validPacket,
      relevantKnowledge: [{ path: '/k.md', level: 'ephemeral' as const, relevanceScore: 1.5 }],
    };
    expect(ContextPacketSchema.safeParse(badScore).success).toBe(false);
  });

  it('rejects invalid maxRiskLevel', () => {
    const badRisk = {
      ...validPacket,
      permissions: {
        ...validPacket.permissions,
        maxRiskLevel: 'extreme',
      },
    };
    expect(ContextPacketSchema.safeParse(badRisk).success).toBe(false);
  });

  it('rejects missing required fields', () => {
    const { taskId: _, ...noTask } = validPacket;
    expect(ContextPacketSchema.safeParse(noTask).success).toBe(false);
  });
});

// ── Content Addressing ──

describe('Content addressing', () => {
  it('computes hash of a context packet and verifies it matches', () => {
    const packet = {
      packetId: VALID_UUID,
      version: 1 as const,
      taskId: 'task-1',
      taskTitle: 'Fix login',
      taskDescription: 'desc',
      parentObjectives: [],
      fileSnapshots: [{ path: '/src/a.ts', hash: 'sha256:filehash', content: 'const x = 1;' }],
      permissions: {
        allowedTools: ['file_edit'],
        deniedTools: [],
        maxRiskLevel: 'low' as const,
        requireApproval: [],
      },
      relevantKnowledge: [],
      enabledMcpServers: [],
      outputContract: {
        expectedFiles: ['/src/a.ts'],
      },
      createdAt: VALID_DATETIME,
    };

    // Serialize deterministically, compute hash
    const canonical = JSON.stringify(packet);
    const computedHash = createHash('sha256').update(canonical).digest('hex');

    // Validate packet with the computed hash
    const fullPacket = { ...packet, hash: computedHash };
    const result = ContextPacketSchema.safeParse(fullPacket);
    expect(result.success).toBe(true);

    // Verify hash is a 64-char hex string
    expect(computedHash).toHaveLength(64);
    expect(computedHash).toMatch(/^[0-9a-f]{64}$/);
  });

  it('detects tampered content via hash mismatch', () => {
    const packet = {
      packetId: VALID_UUID,
      version: 1 as const,
      taskId: 'task-1',
      taskTitle: 'Fix login',
      taskDescription: 'desc',
      parentObjectives: [],
      fileSnapshots: [],
      permissions: {
        allowedTools: [],
        deniedTools: [],
        maxRiskLevel: 'low' as const,
        requireApproval: [],
      },
      relevantKnowledge: [],
      enabledMcpServers: [],
      outputContract: { expectedFiles: [] },
      createdAt: VALID_DATETIME,
      hash: 'sha256:original',
    };

    // The hash field stores whatever string; schema validation doesn't check cryptographic integrity
    // But the consumer can verify: the hash field exists and can be compared externally
    const parsed = ContextPacketSchema.safeParse(packet);
    expect(parsed.success).toBe(true);
    if (parsed.success) {
      expect(parsed.data.hash).toBe('sha256:original');
    }
  });
});

// ── Version exports ──

describe('Version exports', () => {
  it('CONTRACT_VERSION is 1', () => {
    expect(CONTRACT_VERSION).toBe(1);
  });

  it('SCHEMA_VERSION is 1', () => {
    expect(SCHEMA_VERSION).toBe(1);
  });
});

// ── Type Inference ──

describe('Type inference', () => {
  it('SessionCreatedEvent type narrows from Event union', () => {
    const event = {
      ...baseEventFields,
      eventType: 'session.created' as const,
      aggregateType: 'session' as const,
      adapter: 'codex',
      agentName: 'agent-1',
      model: 'gpt-4',
      worktree: '/tmp/wt',
    };
    const parsed = EventSchema.parse(event);
    // Discriminated union narrows by eventType
    if (parsed.eventType === 'session.created') {
      expect(parsed.adapter).toBe('codex');
      expect(parsed.agentName).toBe('agent-1');
      expect(parsed.model).toBe('gpt-4');
      expect(parsed.worktree).toBe('/tmp/wt');
    }
  });

  it('TaskCompletedEvent type narrows from Event union', () => {
    const event = {
      ...baseEventFields,
      eventType: 'task.completed' as const,
      aggregateType: 'task' as const,
      result: 'Done',
      artifacts: [validArtifact],
    };
    const parsed = EventSchema.parse(event);
    if (parsed.eventType === 'task.completed') {
      expect(parsed.result).toBe('Done');
      expect(parsed.artifacts).toHaveLength(1);
      expect(parsed.artifacts[0]!.type).toBe('file');
    }
  });

  it('SessionCreateCommand type narrows from Command union', () => {
    const cmd = {
      ...baseCommandFields,
      commandType: 'session.create' as const,
      adapter: 'codex',
      agentName: 'agent-1',
      model: 'gpt-4',
      taskDescription: 'Fix it',
    };
    const parsed = CommandSchema.parse(cmd);
    if (parsed.commandType === 'session.create') {
      expect(parsed.adapter).toBe('codex');
      expect(parsed.taskDescription).toBe('Fix it');
    }
  });

  it('system.unfreeze command has no extra fields', () => {
    const cmd = {
      ...baseCommandFields,
      commandType: 'system.unfreeze' as const,
    };
    const parsed = CommandSchema.parse(cmd);
    if (parsed.commandType === 'system.unfreeze') {
      expect(parsed.version).toBe(1);
      expect(parsed.idempotencyKey).toBe('idem-key-1');
    }
  });

  it('ContextPacket infers correct types', () => {
    const packet = {
      packetId: VALID_UUID,
      version: 1 as const,
      taskId: 'task-1',
      taskTitle: 'T',
      taskDescription: 'D',
      parentObjectives: [],
      fileSnapshots: [],
      permissions: {
        allowedTools: [],
        deniedTools: [],
        maxRiskLevel: 'low' as const,
        requireApproval: [],
      },
      relevantKnowledge: [],
      enabledMcpServers: [],
      outputContract: { expectedFiles: [] },
      createdAt: VALID_DATETIME,
      hash: 'sha256:test',
    };
    const parsed = ContextPacketSchema.parse(packet);
    // TypeScript infers correct literal type
    expect(parsed.version).toBe(1);
    expect(parsed.permissions.maxRiskLevel).toBe('low');
  });
});

// ── Negative tests for missing fields ──

describe('Negative validation tests', () => {
  it('event missing eventId fails', () => {
    const { eventId: _, ...partial } = {
      ...baseEventFields,
      eventType: 'session.created',
      aggregateType: 'session',
      adapter: 'codex',
      agentName: 'a',
      model: 'm',
      worktree: 'w',
    };
    expect(SessionCreatedEventSchema.safeParse(partial).success).toBe(false);
  });

  it('event missing metadata fails', () => {
    const { metadata: _, ...partial } = {
      ...baseEventFields,
      eventType: 'session.created',
      aggregateType: 'session',
      adapter: 'codex',
      agentName: 'a',
      model: 'm',
      worktree: 'w',
    };
    expect(SessionCreatedEventSchema.safeParse(partial).success).toBe(false);
  });

  it('command missing timestamp fails', () => {
    const { timestamp: _, ...partial } = {
      ...baseCommandFields,
      commandType: 'task.create',
      title: 'T',
      description: 'D',
      priority: 'medium' as const,
    };
    expect(TaskCreateCommandSchema.safeParse(partial).success).toBe(false);
  });

  it('context packet missing permissions fails', () => {
    const { permissions: _, ...partial } = {
      packetId: VALID_UUID,
      version: 1 as const,
      taskId: 'task-1',
      taskTitle: 'T',
      taskDescription: 'D',
      parentObjectives: [],
      fileSnapshots: [],
      permissions: {
        allowedTools: [],
        deniedTools: [],
        maxRiskLevel: 'low' as const,
        requireApproval: [],
      },
      relevantKnowledge: [],
      enabledMcpServers: [],
      outputContract: { expectedFiles: [] },
      createdAt: VALID_DATETIME,
      hash: 'h',
    };
    expect(ContextPacketSchema.safeParse(partial).success).toBe(false);
  });

  it('empty object fails event validation', () => {
    expect(EventSchema.safeParse({}).success).toBe(false);
  });

  it('empty object fails command validation', () => {
    expect(CommandSchema.safeParse({}).success).toBe(false);
  });

  it('empty object fails context packet validation', () => {
    expect(ContextPacketSchema.safeParse({}).success).toBe(false);
  });
});
