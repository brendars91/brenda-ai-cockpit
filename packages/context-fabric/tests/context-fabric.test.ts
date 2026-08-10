import { describe, it, expect, beforeEach, afterEach } from 'vitest';

import { canonicalJson, sha256 } from '../src/hash.js';
import {
  closeDatabase,
  createDatabase,
  DuplicateEventError,
  emptyProjectedState,
  EventLog,
  IdempotencyStore,
  initializeDatabase,
  ProjectionEngine,
  reduceEvent,
  replayToSequence,
  verifyDeterministicReplay,
} from '../src/index.js';

import type { Event } from '@cockpit/contracts';
import type Database from 'better-sqlite3';

// ── Helpers ──

let db: Database.Database;
let eventLog: EventLog;

function freshDb(): void {
  db = createDatabase();
  initializeDatabase(db);
  eventLog = new EventLog(db);
}

function uuid(): string {
  return crypto.randomUUID();
}

function ts(): string {
  return new Date().toISOString();
}

const correlationId = uuid();

function makeSessionCreated(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'session.created',
    aggregateId,
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    adapter: 'claude',
    agentName: 'test-agent',
    model: 'claude-3',
    worktree: '/tmp/worktree',
  };
}

function makeSessionStarted(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'session.started',
    aggregateId,
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    taskId: uuid(),
  };
}

function makeSessionOutput(aggregateId: string, content: string): Event {
  return {
    eventId: uuid(),
    eventType: 'session.output',
    aggregateId,
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    content,
    stream: 'stdout',
  };
}

function makeSessionCompleted(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'session.completed',
    aggregateId,
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    exitCode: 0,
    duration: 120,
    tokenUsage: { promptTokens: 100, completionTokens: 50, totalTokens: 150 },
  };
}

function makeTaskCreated(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'task.created',
    aggregateId,
    aggregateType: 'task',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    title: 'Test task',
    description: 'A test task',
    priority: 'high',
  };
}

function makeTaskAssigned(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'task.assigned',
    aggregateId,
    aggregateType: 'task',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    agentId: uuid(),
    adapter: 'claude',
  };
}

function makeTaskCompleted(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'task.completed',
    aggregateId,
    aggregateType: 'task',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    result: 'done',
    artifacts: [],
  };
}

function makeAgentRegistered(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'agent.registered',
    aggregateId,
    aggregateType: 'agent',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    name: 'test-agent',
    adapter: 'claude',
    capabilities: ['code', 'review'],
    model: 'claude-3',
  };
}

function makeAgentHealthChecked(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'agent.health_checked',
    aggregateId,
    aggregateType: 'agent',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    status: 'healthy',
    latency: 42,
  };
}

function makeIssueCreated(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'issue.created',
    aggregateId,
    aggregateType: 'issue',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    issueId: 'ISS-1',
    title: 'Test issue',
    status: 'open',
    priority: 'high',
  };
}

function makeIssueStatusChanged(aggregateId: string, to: string): Event {
  return {
    eventId: uuid(),
    eventType: 'issue.status_changed',
    aggregateId,
    aggregateType: 'issue',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    from: 'open',
    to,
  };
}

function makeIssueCommentAdded(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'issue.comment_added',
    aggregateId,
    aggregateType: 'issue',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    author: 'user',
    body: 'Looks good',
  };
}

function makeKnowledgeCreated(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'knowledge.created',
    aggregateId,
    aggregateType: 'knowledge',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    path: '/docs/test.md',
    content: 'Hello world',
    level: 'ephemeral',
  };
}

function makeKnowledgePromoted(aggregateId: string): Event {
  return {
    eventId: uuid(),
    eventType: 'knowledge.promoted',
    aggregateId,
    aggregateType: 'knowledge',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    from: 'ephemeral',
    to: 'canon',
    evalResult: {
      passed: true,
      score: 0.95,
      details: 'All checks passed',
      evaluatedAt: ts(),
      evalSuiteId: uuid(),
    },
  };
}

function makeSystemFreezeActivated(): Event {
  return {
    eventId: uuid(),
    eventType: 'system.freeze_activated',
    aggregateId: 'system',
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    reason: 'Emergency maintenance',
    by: 'admin',
  };
}

function makeSystemFreezeDeactivated(): Event {
  return {
    eventId: uuid(),
    eventType: 'system.freeze_deactivated',
    aggregateId: 'system',
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    by: 'admin',
  };
}

function makeSystemQuotaWarning(): Event {
  return {
    eventId: uuid(),
    eventType: 'system.quota_warning',
    aggregateId: 'system',
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    provider: 'claude',
    remaining: 1000,
    windowEndsAt: '2025-12-31T00:00:00Z',
  };
}

function makeSystemQuotaExhausted(): Event {
  return {
    eventId: uuid(),
    eventType: 'system.quota_exhausted',
    aggregateId: 'system',
    aggregateType: 'session',
    version: 1,
    timestamp: ts(),
    metadata: { correlationId },
    provider: 'claude',
  };
}

// ── Tests ──

describe('context-fabric', () => {
  beforeEach(() => {
    freshDb();
  });

  // 1. Database initialization
  it('creates tables and indexes on initialization', () => {
    const tables = db
      .prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
      .all() as { name: string }[];
    const tableNames = tables.map((t) => t.name);

    expect(tableNames).toContain('events');
    expect(tableNames).toContain('idempotency_keys');
    expect(tableNames).toContain('projection_sessions');
    expect(tableNames).toContain('projection_tasks');
    expect(tableNames).toContain('projection_agents');
    expect(tableNames).toContain('projection_runs');
    expect(tableNames).toContain('projection_issues');
    expect(tableNames).toContain('projection_knowledge');
    expect(tableNames).toContain('projection_system');

    const indexes = db
      .prepare(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name",
      )
      .all() as { name: string }[];
    const indexNames = indexes.map((i) => i.name);
    expect(indexNames).toContain('idx_events_aggregate');
    expect(indexNames).toContain('idx_events_type');
    expect(indexNames).toContain('idx_events_timestamp');
  });

  // 2. Append and retrieve
  it('appends a valid event and retrieves by sequence and eventId', () => {
    const event = makeSessionCreated(uuid());
    const stored = eventLog.append(event);

    expect(stored.sequence).toBe(1);
    expect(stored.eventId).toBe(event.eventId);
    expect(stored.eventType).toBe('session.created');
    expect(stored.eventHash).toBeTruthy();
    expect(stored.previousHash).toBeNull();

    const bySeq = eventLog.getBySequence(1);
    expect(bySeq).not.toBeNull();
    expect(bySeq!.eventId).toBe(event.eventId);

    const byId = eventLog.getByEventId(event.eventId);
    expect(byId).not.toBeNull();
    expect(byId!.sequence).toBe(1);
  });

  // 3. Duplicate event
  it('throws DuplicateEventError on duplicate event_id', () => {
    const event = makeSessionCreated(uuid());
    eventLog.append(event);

    // Try to append the same event again
    expect(() => eventLog.append(event)).toThrow(DuplicateEventError);
  });

  // 4. AppendMany transactional
  it('appendMany is transactional', () => {
    const id1 = uuid();
    const id2 = uuid();
    const e1 = makeSessionCreated(id1);
    const e2 = makeSessionCreated(id2);
    const stored = eventLog.appendMany([e1, e2]);

    expect(stored).toHaveLength(2);
    expect(stored[0]!.aggregateId).toBe(id1);
    expect(stored[1]!.aggregateId).toBe(id2);
    expect(stored[1]!.previousHash).toBe(stored[0]!.eventHash);

    // Both should be queryable
    expect(eventLog.getByEventId(e1.eventId)).not.toBeNull();
    expect(eventLog.getByEventId(e2.eventId)).not.toBeNull();
  });

  // 5. Hash chain verification
  it('verifies hash chain as true for normal log', () => {
    const events = [
      makeSessionCreated(uuid()),
      makeSessionStarted(uuid()),
      makeSessionCreated(uuid()),
    ];
    eventLog.appendMany(events);
    expect(eventLog.verifyHashChain()).toBe(true);
  });

  // 6. Hash chain detects tampering
  it('detects tampering via hash chain verification', () => {
    const event = makeSessionCreated(uuid());
    eventLog.append(event);

    // Tamper with payload_json
    db.prepare("UPDATE events SET payload_json = 'tampered' WHERE sequence = 1").run();
    expect(eventLog.verifyHashChain()).toBe(false);
  });

  // 7. IdempotencyStore
  it('executeOnce executes only once and returns stored result', () => {
    const store = new IdempotencyStore(db);
    let callCount = 0;

    const result1 = store.executeOnce('key-1', 'cmd-1', () => {
      callCount++;
      return { value: 42 };
    });
    expect(result1).toEqual({ value: 42 });
    expect(callCount).toBe(1);

    const result2 = store.executeOnce('key-1', 'cmd-1', () => {
      callCount++;
      return { value: 99 };
    });
    expect(result2).toEqual({ value: 42 });
    expect(callCount).toBe(1);

    expect(store.has('key-1')).toBe(true);
    expect(store.has('key-unknown')).toBe(false);
    expect(store.get<{ value: number }>('key-1')).toEqual({ value: 42 });
  });

  // 8. Projection reducer
  describe('projection reducer', () => {
    it('handles session.created -> projection session exists', () => {
      const id = uuid();
      const state = reduceEvent(emptyProjectedState(), makeSessionCreated(id));
      expect(state.sessions[id]).toBeDefined();
      expect(state.sessions[id]!.status).toBe('created');
    });

    it('handles session.started/completed updating status', () => {
      const id = uuid();
      let state = reduceEvent(emptyProjectedState(), makeSessionCreated(id));
      state = reduceEvent(state, makeSessionStarted(id));
      expect(state.sessions[id]!.status).toBe('started');

      state = reduceEvent(state, makeSessionCompleted(id));
      expect(state.sessions[id]!.status).toBe('completed');
    });

    it('handles session.output tracking outputCount and lastOutput', () => {
      const id = uuid();
      let state = reduceEvent(emptyProjectedState(), makeSessionCreated(id));
      state = reduceEvent(state, makeSessionOutput(id, 'hello'));
      state = reduceEvent(state, makeSessionOutput(id, 'world'));
      expect(state.sessions[id]!.outputCount).toBe(2);
      expect(state.sessions[id]!.lastOutput).toBe('world');
    });

    it('handles task.created/assigned/completed', () => {
      const id = uuid();
      let state = reduceEvent(emptyProjectedState(), makeTaskCreated(id));
      expect(state.tasks[id]).toBeDefined();
      expect(state.tasks[id]!.status).toBe('created');

      state = reduceEvent(state, makeTaskAssigned(id));
      expect(state.tasks[id]!.status).toBe('assigned');

      state = reduceEvent(state, makeTaskCompleted(id));
      expect(state.tasks[id]!.status).toBe('completed');
    });

    it('handles agent.registered/health_checked', () => {
      const id = uuid();
      let state = reduceEvent(emptyProjectedState(), makeAgentRegistered(id));
      expect(state.agents[id]).toBeDefined();
      expect(state.agents[id]!.status).toBe('registered');

      state = reduceEvent(state, makeAgentHealthChecked(id));
      expect(state.agents[id]!.status).toBe('healthy');
      expect(state.agents[id]!.latency).toBe(42);
    });

    it('handles issue.created/status_changed/comment_added', () => {
      const id = uuid();
      let state = reduceEvent(emptyProjectedState(), makeIssueCreated(id));
      expect(state.issues[id]).toBeDefined();
      expect(state.issues[id]!.status).toBe('open');
      expect(state.issues[id]!.commentCount).toBe(0);

      state = reduceEvent(state, makeIssueStatusChanged(id, 'in_progress'));
      expect(state.issues[id]!.status).toBe('in_progress');

      state = reduceEvent(state, makeIssueCommentAdded(id));
      expect(state.issues[id]!.commentCount).toBe(1);
    });

    it('handles knowledge.created/promoted', () => {
      const id = uuid();
      let state = reduceEvent(emptyProjectedState(), makeKnowledgeCreated(id));
      expect(state.knowledge[id]).toBeDefined();
      expect(state.knowledge[id]!.level).toBe('ephemeral');

      state = reduceEvent(state, makeKnowledgePromoted(id));
      expect(state.knowledge[id]!.level).toBe('canon');
    });

    it('handles system.freeze_activated/deactivated', () => {
      let state = reduceEvent(emptyProjectedState(), makeSystemFreezeActivated());
      expect(state.system.frozen).toBe(true);
      expect(state.system.freezeReason).toBe('Emergency maintenance');

      state = reduceEvent(state, makeSystemFreezeDeactivated());
      expect(state.system.frozen).toBe(false);
      expect(state.system.freezeReason).toBeUndefined();
    });

    it('handles system.quota_warning/exhausted', () => {
      let state = reduceEvent(emptyProjectedState(), makeSystemQuotaWarning());
      expect(state.system.quotaWarnings['claude']).toBeDefined();
      expect(state.system.quotaWarnings['claude']!.remaining).toBe(1000);

      state = reduceEvent(state, makeSystemQuotaExhausted());
      expect(state.system.quotaExhausted).toContain('claude');
    });
  });

  // 9. ProjectionEngine rebuild
  it('ProjectionEngine rebuild persists projections', () => {
    const sessionId = uuid();
    const taskId = uuid();

    eventLog.append(makeSessionCreated(sessionId));
    eventLog.append(makeTaskCreated(taskId));

    const engine = new ProjectionEngine(db, eventLog);
    const state = engine.rebuild();

    expect(state.sessions[sessionId]).toBeDefined();
    expect(state.tasks[taskId]).toBeDefined();

    // Can retrieve from DB too
    const loaded = engine.getCurrentState();
    expect(loaded.sessions[sessionId]).toBeDefined();
    expect(loaded.tasks[taskId]).toBeDefined();
  });

  // 10. Deterministic replay
  it('replay produces deterministic hash across two runs', () => {
    const sessionId = uuid();
    eventLog.append(makeSessionCreated(sessionId));
    eventLog.append(makeSessionOutput(sessionId, 'test output'));
    eventLog.append(makeSessionCompleted(sessionId));
    eventLog.append(makeTaskCreated(uuid()));
    eventLog.append(makeAgentRegistered(uuid()));

    const result = verifyDeterministicReplay(eventLog);
    expect(result.deterministic).toBe(true);
    expect(result.firstHash).toBe(result.secondHash);
    expect(result.firstHash.length).toBeGreaterThan(0);
  });

  // 11. replayToSequence time-travel
  it('replayToSequence gives intermediate state', () => {
    const s1 = uuid();
    const s2 = uuid();

    eventLog.append(makeSessionCreated(s1)); // seq 1
    eventLog.append(makeSessionCreated(s2)); // seq 2
    eventLog.append(makeSessionCompleted(s1)); // seq 3

    const atSeq1 = replayToSequence(eventLog, 1);
    expect(Object.keys(atSeq1.sessions)).toHaveLength(1);
    expect(atSeq1.sessions[s1]).toBeDefined();

    const atSeq2 = replayToSequence(eventLog, 2);
    expect(Object.keys(atSeq2.sessions)).toHaveLength(2);

    const atSeq3 = replayToSequence(eventLog, 3);
    expect(atSeq3.sessions[s1]!.status).toBe('completed');
  });

  // 12. Schema validation rejects invalid event
  it('rejects invalid events', () => {
    const badEvent = {
      eventId: 'not-a-uuid',
      eventType: 'session.created',
      aggregateId: uuid(),
      aggregateType: 'session',
      version: 1,
      timestamp: 'not-a-date',
      metadata: { correlationId: uuid() },
      adapter: 'test',
      agentName: 'test',
      model: 'test',
      worktree: '/tmp',
    } as unknown as Event;

    expect(() => eventLog.append(badEvent)).toThrow();
  });

  // 13. Stored event includes sequence, eventHash, previousHash
  it('stored event includes sequence, eventHash, previousHash', () => {
    const event = makeSessionCreated(uuid());
    const stored = eventLog.append(event);

    expect(stored.sequence).toBeTypeOf('number');
    expect(stored.eventHash).toMatch(/^[a-f0-9]{64}$/);
    expect(stored.previousHash).toBeNull();

    const event2 = makeSessionCreated(uuid());
    const stored2 = eventLog.append(event2);
    expect(stored2.previousHash).toBe(stored.eventHash);
  });

  // Additional: canonical JSON determinism
  it('canonicalJson produces deterministic output', () => {
    const obj1 = { b: 2, a: 1 };
    const obj2 = { a: 1, b: 2 };
    expect(canonicalJson(obj1)).toBe(canonicalJson(obj2));
  });

  // Additional: sha256
  it('sha256 produces consistent hash', () => {
    const hash1 = sha256('hello');
    const hash2 = sha256('hello');
    expect(hash1).toBe(hash2);
    expect(hash1).toMatch(/^[a-f0-9]{64}$/);
  });

  // Additional: getEvents with filters
  it('getEvents supports filtering', () => {
    const s1 = uuid();
    const s2 = uuid();
    eventLog.append(makeSessionCreated(s1));
    eventLog.append(makeTaskCreated(uuid()));
    eventLog.append(makeSessionCreated(s2));

    const all = eventLog.getEvents();
    expect(all).toHaveLength(3);

    const sessions = eventLog.getEvents({ aggregateType: 'session' });
    expect(sessions).toHaveLength(2);

    const limited = eventLog.getEvents({ limit: 1 });
    expect(limited).toHaveLength(1);

    const afterFirst = eventLog.getEvents({ afterSequence: 1 });
    expect(afterFirst).toHaveLength(2);
  });

  // Additional: getLatestSequence/getLatestHash
  it('tracks latest sequence and hash', () => {
    expect(eventLog.getLatestSequence()).toBe(0);
    expect(eventLog.getLatestHash()).toBeNull();

    eventLog.append(makeSessionCreated(uuid()));
    expect(eventLog.getLatestSequence()).toBe(1);
    expect(eventLog.getLatestHash()).not.toBeNull();
  });

  // Additional: ProjectionEngine getCurrentStateHash
  it('ProjectionEngine getCurrentStateHash returns consistent hash', () => {
    eventLog.append(makeSessionCreated(uuid()));
    const engine = new ProjectionEngine(db, eventLog);
    engine.rebuild();

    const hash1 = engine.getCurrentStateHash();
    const hash2 = engine.getCurrentStateHash();
    expect(hash1).toBe(hash2);
  });

  // Close db after each
  afterEach(() => {
    closeDatabase(db);
  });
});
