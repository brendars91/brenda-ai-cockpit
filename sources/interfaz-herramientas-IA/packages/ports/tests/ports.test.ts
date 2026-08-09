/**
 * Tests for @cockpit/ports — verify port interfaces via mock implementations.
 *
 * Since ports are TypeScript interfaces (compile-time only), these tests:
 * 1. Define mock classes implementing each port
 * 2. Verify the mocks satisfy interfaces at compile time and runtime
 * 3. Verify idempotencyKey is required in request objects
 * 4. Verify async event streams work
 * 5. Verify capabilities shape
 */

import { describe, expect, it, vi } from 'vitest';

import type {
  AdapterCapabilities,
  AgentRuntimePort,
  AgentSession,
  Approval,
  ApprovalResolution,
  AttachSessionRequest,
  CreateApprovalRequest,
  CreateIssueRequest,
  CreateKnowledgeRequest,
  CreateSessionRequest,
  GovernanceIssue,
  GovernancePort,
  KillSessionRequest,
  KnowledgeEntry,
  KnowledgePort,
  KnowledgeSearchResult,
  ModelInvocationRequest,
  ModelInvocationResponse,
  ModelProviderPort,
  PortHealth,
  PromoteKnowledgeRequest,
  QuotaCheckRequest,
  QuotaDecision,
  ReadKnowledgeRequest,
  ResolveGovernanceApprovalRequest,
  SearchKnowledgeRequest,
  SessionInput,
  UpdateIssueRequest,
} from '../src/index.js';
import type { ContextPacket, Event } from '@cockpit/contracts';

// ── Fixtures ──

const now = new Date().toISOString();

const fakeCapabilities: AdapterCapabilities = {
  adapterName: 'mock-adapter',
  portType: 'agent-runtime',
  capabilities: ['create', 'stream', 'kill'],
  riskLevel: 'medium',
  quotaProvider: 'zai',
};

const fakeHealth: PortHealth = {
  adapterName: 'mock-adapter',
  status: 'healthy',
  latencyMs: 5,
  checkedAt: now,
};

function makeFakeContextPacket(): ContextPacket {
  return {
    packetId: '00000000-0000-0000-0000-000000000001',
    version: 1,
    taskId: 'task-1',
    taskTitle: 'Test task',
    taskDescription: 'A test task',
    parentObjectives: [],
    fileSnapshots: [],
    permissions: {
      allowedTools: ['read', 'write'],
      deniedTools: [],
      maxRiskLevel: 'medium',
      requireApproval: ['delete'],
    },
    relevantKnowledge: [],
    enabledMcpServers: [],
    outputContract: {
      expectedFiles: [],
    },
    createdAt: now,
    hash: 'abc123',
  };
}

function makeFakeSession(overrides?: Partial<AgentSession>): AgentSession {
  return {
    sessionId: 'sess-1',
    adapter: 'mock-adapter',
    agentName: 'test-agent',
    model: 'gpt-4',
    status: 'created',
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

// ── Mock Implementations ──

class MockAgentRuntimePort implements AgentRuntimePort {
  readonly adapterName = 'mock-adapter';
  readonly capabilities = fakeCapabilities;

  async healthCheck(): Promise<PortHealth> {
    return fakeHealth;
  }

  async createSession(request: CreateSessionRequest): Promise<AgentSession> {
    return makeFakeSession({
      adapter: request.adapter,
      agentName: request.agentName,
      model: request.model,
    });
  }

  async attachSession(request: AttachSessionRequest): Promise<AgentSession> {
    return makeFakeSession({ sessionId: request.sessionId });
  }

  async listSessions(): Promise<readonly AgentSession[]> {
    return [makeFakeSession()];
  }

  async *streamSessionEvents(_sessionId: string): AsyncGenerator<Event, void, unknown> {
    const baseEvent = {
      eventId: '00000000-0000-0000-0000-000000000002',
      timestamp: now,
      aggregateId: 'sess-1',
      aggregateType: 'session' as const,
      version: 1 as const,
      metadata: {
        correlationId: '00000000-0000-0000-0000-000000000003',
      },
    };

    yield {
      ...baseEvent,
      eventType: 'session.output',
      content: 'Hello',
      stream: 'stdout',
    } as Event;

    yield {
      ...baseEvent,
      eventId: '00000000-0000-0000-0000-000000000004',
      eventType: 'session.output',
      content: 'World',
      stream: 'stdout',
    } as Event;
  }

  async sendInput(_input: SessionInput): Promise<void> {
    // no-op
  }

  async resolveApproval(_resolution: ApprovalResolution): Promise<void> {
    // no-op
  }

  async killSession(_request: KillSessionRequest): Promise<void> {
    // no-op
  }
}

class MockKnowledgePort implements KnowledgePort {
  readonly adapterName = 'mock-knowledge';
  readonly capabilities: AdapterCapabilities = {
    ...fakeCapabilities,
    portType: 'knowledge',
  };

  async healthCheck(): Promise<PortHealth> {
    return { ...fakeHealth, adapterName: this.adapterName };
  }

  async createKnowledge(request: CreateKnowledgeRequest): Promise<KnowledgeEntry> {
    return {
      knowledgeId: 'k-1',
      path: request.path,
      level: request.level,
      contentHash: 'hash-1',
      tags: request.tags ?? [],
      createdAt: now,
      updatedAt: now,
    };
  }

  async readKnowledge(
    _request: ReadKnowledgeRequest,
  ): Promise<{ entry: KnowledgeEntry; content: string }> {
    return {
      entry: {
        knowledgeId: 'k-1',
        path: '/knowledge/test.md',
        level: 'tool',
        contentHash: 'hash-1',
        tags: [],
        createdAt: now,
        updatedAt: now,
      },
      content: '# Test Knowledge',
    };
  }

  async searchKnowledge(
    _request: SearchKnowledgeRequest,
  ): Promise<readonly KnowledgeSearchResult[]> {
    return [];
  }

  async promoteKnowledge(_request: PromoteKnowledgeRequest): Promise<KnowledgeEntry> {
    return {
      knowledgeId: 'k-1',
      path: '/knowledge/test.md',
      level: 'canon',
      contentHash: 'hash-2',
      tags: [],
      createdAt: now,
      updatedAt: now,
    };
  }

  async listKnowledge(): Promise<readonly KnowledgeEntry[]> {
    return [];
  }
}

class MockGovernancePort implements GovernancePort {
  readonly adapterName = 'mock-governance';
  readonly capabilities: AdapterCapabilities = {
    ...fakeCapabilities,
    portType: 'governance',
  };

  async healthCheck(): Promise<PortHealth> {
    return { ...fakeHealth, adapterName: this.adapterName };
  }

  async createIssue(request: CreateIssueRequest): Promise<GovernanceIssue> {
    return {
      issueId: 'issue-1',
      title: request.title,
      body: request.body,
      status: 'todo',
      priority: request.priority,
      labels: request.labels ?? [],
      createdAt: now,
      updatedAt: now,
    };
  }

  async updateIssue(request: UpdateIssueRequest): Promise<GovernanceIssue> {
    return {
      issueId: request.issueId,
      title: 'Updated',
      body: '',
      status: request.status ?? 'todo',
      priority: 'medium',
      labels: request.labels ?? [],
      createdAt: now,
      updatedAt: now,
    };
  }

  async getIssue(_issueId: string): Promise<GovernanceIssue> {
    return {
      issueId: 'issue-1',
      title: 'Test Issue',
      body: 'body',
      status: 'todo',
      priority: 'medium',
      labels: [],
      createdAt: now,
      updatedAt: now,
    };
  }

  async listIssues(): Promise<readonly GovernanceIssue[]> {
    return [];
  }

  async createApproval(request: CreateApprovalRequest): Promise<Approval> {
    return {
      approvalId: 'appr-1',
      targetId: request.targetId,
      targetType: request.targetType,
      action: request.action,
      risk: request.risk,
      decision: 'pending',
      requestedAt: now,
    };
  }

  async resolveApproval(_request: ResolveGovernanceApprovalRequest): Promise<Approval> {
    return {
      approvalId: 'appr-1',
      targetId: 't-1',
      targetType: 'session',
      action: 'approve',
      risk: 'low',
      decision: 'approved',
      requestedAt: now,
      resolvedAt: now,
      resolvedBy: 'admin',
    };
  }

  async listApprovals(): Promise<readonly Approval[]> {
    return [];
  }
}

class MockModelProviderPort implements ModelProviderPort {
  readonly providerName = 'zai' as const;
  readonly capabilities: AdapterCapabilities = {
    ...fakeCapabilities,
    portType: 'model-provider',
  };

  async healthCheck(): Promise<PortHealth> {
    return fakeHealth;
  }

  async checkQuota(request: QuotaCheckRequest): Promise<QuotaDecision> {
    return {
      provider: request.provider,
      decision: 'allow',
      reason: 'Within budget',
    };
  }

  async invoke(request: ModelInvocationRequest): Promise<ModelInvocationResponse> {
    return {
      provider: request.provider,
      model: request.model,
      content: 'Hello, world!',
      finishReason: 'stop',
      tokenUsage: {
        promptTokens: 10,
        completionTokens: 5,
        totalTokens: 15,
      },
    };
  }

  async *stream(
    request: ModelInvocationRequest,
  ): AsyncGenerator<ModelInvocationResponse, void, unknown> {
    yield {
      provider: request.provider,
      model: request.model,
      content: 'Chunk 1',
      finishReason: 'stop',
      tokenUsage: {
        promptTokens: 5,
        completionTokens: 2,
        totalTokens: 7,
      },
    };

    yield {
      provider: request.provider,
      model: request.model,
      content: 'Chunk 2',
      finishReason: 'stop',
      tokenUsage: {
        promptTokens: 5,
        completionTokens: 3,
        totalTokens: 8,
      },
    };
  }

  async listModels(): Promise<readonly string[]> {
    return ['gpt-4', 'gpt-3.5-turbo'];
  }
}

// ── Tests ──

describe('AgentRuntimePort', () => {
  it('implements the interface and returns health', async () => {
    const port: AgentRuntimePort = new MockAgentRuntimePort();
    const health = await port.healthCheck();
    expect(health.status).toBe('healthy');
    expect(health.adapterName).toBe('mock-adapter');
  });

  it('creates a session with idempotencyKey', async () => {
    const port = new MockAgentRuntimePort();
    const request: CreateSessionRequest = {
      adapter: 'mock-adapter',
      agentName: 'test-agent',
      model: 'gpt-4',
      taskDescription: 'Do something',
      contextPacket: makeFakeContextPacket(),
      idempotencyKey: 'idem-1',
    };
    const session = await port.createSession(request);
    expect(session.agentName).toBe('test-agent');
    expect(session.status).toBe('created');
  });

  it('attaches to an existing session', async () => {
    const port = new MockAgentRuntimePort();
    const session = await port.attachSession({ sessionId: 'sess-42' });
    expect(session.sessionId).toBe('sess-42');
  });

  it('lists sessions', async () => {
    const port = new MockAgentRuntimePort();
    const sessions = await port.listSessions();
    expect(sessions).toHaveLength(1);
  });

  it('streams session events as async iterable', async () => {
    const port = new MockAgentRuntimePort();
    const events: Event[] = [];
    for await (const event of port.streamSessionEvents('sess-1')) {
      events.push(event);
    }
    expect(events).toHaveLength(2);
    expect(events[0]!.eventType).toBe('session.output');
    expect(events[1]!.eventType).toBe('session.output');
  });

  it('sends input with idempotencyKey', async () => {
    const port = new MockAgentRuntimePort();
    const sendSpy = vi.spyOn(port, 'sendInput');
    await port.sendInput({
      sessionId: 'sess-1',
      content: 'hello',
      idempotencyKey: 'idem-input',
    });
    expect(sendSpy).toHaveBeenCalledWith({
      sessionId: 'sess-1',
      content: 'hello',
      idempotencyKey: 'idem-input',
    });
  });

  it('resolves approval with idempotencyKey', async () => {
    const port = new MockAgentRuntimePort();
    const spy = vi.spyOn(port, 'resolveApproval');
    await port.resolveApproval({
      sessionId: 'sess-1',
      approved: true,
      by: 'admin',
      idempotencyKey: 'idem-approve',
    });
    expect(spy).toHaveBeenCalled();
  });

  it('kills session with reason and idempotencyKey', async () => {
    const port = new MockAgentRuntimePort();
    const spy = vi.spyOn(port, 'killSession');
    await port.killSession({
      sessionId: 'sess-1',
      reason: 'timeout',
      idempotencyKey: 'idem-kill',
    });
    expect(spy).toHaveBeenCalled();
  });

  it('has correct capabilities shape', () => {
    const port = new MockAgentRuntimePort();
    expect(port.capabilities.adapterName).toBe('mock-adapter');
    expect(port.capabilities.portType).toBe('agent-runtime');
    expect(port.capabilities.riskLevel).toBe('medium');
    expect(port.capabilities.quotaProvider).toBe('zai');
    expect(Array.isArray(port.capabilities.capabilities)).toBe(true);
  });
});

describe('KnowledgePort', () => {
  it('creates knowledge with idempotencyKey', async () => {
    const port: KnowledgePort = new MockKnowledgePort();
    const request: CreateKnowledgeRequest = {
      path: '/knowledge/test.md',
      content: '# Test',
      level: 'ephemeral',
      idempotencyKey: 'idem-k-1',
    };
    const entry = await port.createKnowledge(request);
    expect(entry.path).toBe('/knowledge/test.md');
    expect(entry.level).toBe('ephemeral');
    expect(entry.knowledgeId).toBe('k-1');
  });

  it('reads knowledge by id', async () => {
    const port = new MockKnowledgePort();
    const result = await port.readKnowledge({ knowledgeId: 'k-1' });
    expect(result.entry.knowledgeId).toBe('k-1');
    expect(result.content).toBe('# Test Knowledge');
  });

  it('reads knowledge by path', async () => {
    const port = new MockKnowledgePort();
    const result = await port.readKnowledge({ path: '/knowledge/test.md' });
    expect(result.entry.path).toBe('/knowledge/test.md');
  });

  it('searches knowledge', async () => {
    const port = new MockKnowledgePort();
    const results = await port.searchKnowledge({ query: 'test' });
    expect(results).toHaveLength(0);
  });

  it('promotes knowledge with idempotencyKey', async () => {
    const port = new MockKnowledgePort();
    const request: PromoteKnowledgeRequest = {
      knowledgeId: 'k-1',
      toLevel: 'canon',
      idempotencyKey: 'idem-promote',
    };
    const entry = await port.promoteKnowledge(request);
    expect(entry.level).toBe('canon');
  });

  it('lists knowledge entries', async () => {
    const port = new MockKnowledgePort();
    const entries = await port.listKnowledge('ephemeral');
    expect(entries).toHaveLength(0);
  });

  it('has correct capabilities shape', () => {
    const port = new MockKnowledgePort();
    expect(port.capabilities.portType).toBe('knowledge');
    expect(port.adapterName).toBe('mock-knowledge');
  });
});

describe('GovernancePort', () => {
  it('creates an issue with idempotencyKey', async () => {
    const port: GovernancePort = new MockGovernancePort();
    const request: CreateIssueRequest = {
      title: 'Bug fix',
      body: 'Something broke',
      priority: 'high',
      idempotencyKey: 'idem-issue-1',
    };
    const issue = await port.createIssue(request);
    expect(issue.title).toBe('Bug fix');
    expect(issue.priority).toBe('high');
    expect(issue.status).toBe('todo');
  });

  it('updates an issue', async () => {
    const port = new MockGovernancePort();
    const request: UpdateIssueRequest = {
      issueId: 'issue-1',
      status: 'in_progress',
      idempotencyKey: 'idem-update-1',
    };
    const issue = await port.updateIssue(request);
    expect(issue.status).toBe('in_progress');
  });

  it('gets a single issue', async () => {
    const port = new MockGovernancePort();
    const issue = await port.getIssue('issue-1');
    expect(issue.issueId).toBe('issue-1');
  });

  it('lists issues', async () => {
    const port = new MockGovernancePort();
    const issues = await port.listIssues('todo');
    expect(issues).toHaveLength(0);
  });

  it('creates an approval with idempotencyKey', async () => {
    const port = new MockGovernancePort();
    const request: CreateApprovalRequest = {
      targetId: 'sess-1',
      targetType: 'session',
      action: 'delete',
      risk: 'high',
      idempotencyKey: 'idem-appr-1',
    };
    const approval = await port.createApproval(request);
    expect(approval.decision).toBe('pending');
    expect(approval.risk).toBe('high');
  });

  it('resolves an approval with idempotencyKey', async () => {
    const port = new MockGovernancePort();
    const request: ResolveGovernanceApprovalRequest = {
      approvalId: 'appr-1',
      approved: true,
      by: 'admin',
      idempotencyKey: 'idem-resolve-1',
    };
    const approval = await port.resolveApproval(request);
    expect(approval.decision).toBe('approved');
    expect(approval.resolvedBy).toBe('admin');
  });

  it('lists approvals', async () => {
    const port = new MockGovernancePort();
    const approvals = await port.listApprovals('approved');
    expect(approvals).toHaveLength(0);
  });
});

describe('ModelProviderPort', () => {
  it('checks quota and returns decision', async () => {
    const port: ModelProviderPort = new MockModelProviderPort();
    const request: QuotaCheckRequest = {
      provider: 'zai',
      estimatedTokens: 1000,
    };
    const decision = await port.checkQuota(request);
    expect(decision.decision).toBe('allow');
    expect(decision.provider).toBe('zai');
  });

  it('invokes a model with idempotencyKey', async () => {
    const port = new MockModelProviderPort();
    const request: ModelInvocationRequest = {
      provider: 'zai',
      model: 'gpt-4',
      messages: [{ role: 'user', content: 'Hello' }],
      idempotencyKey: 'idem-invoke-1',
    };
    const response = await port.invoke(request);
    expect(response.content).toBe('Hello, world!');
    expect(response.finishReason).toBe('stop');
    expect(response.tokenUsage.totalTokens).toBe(15);
  });

  it('streams model responses as async iterable', async () => {
    const port = new MockModelProviderPort();
    const request: ModelInvocationRequest = {
      provider: 'zai',
      model: 'gpt-4',
      messages: [{ role: 'user', content: 'Stream test' }],
      idempotencyKey: 'idem-stream-1',
    };
    const chunks: ModelInvocationResponse[] = [];
    for await (const chunk of port.stream(request)) {
      chunks.push(chunk);
    }
    expect(chunks).toHaveLength(2);
    expect(chunks[0]!.content).toBe('Chunk 1');
    expect(chunks[1]!.content).toBe('Chunk 2');
  });

  it('lists available models', async () => {
    const port = new MockModelProviderPort();
    const models = await port.listModels();
    expect(models).toContain('gpt-4');
    expect(models).toContain('gpt-3.5-turbo');
  });

  it('has correct capabilities shape', () => {
    const port = new MockModelProviderPort();
    expect(port.providerName).toBe('zai');
    expect(port.capabilities.portType).toBe('model-provider');
  });
});
