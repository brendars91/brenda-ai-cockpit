import { describe, it, expect } from 'vitest';
import { randomUUID } from 'node:crypto';
import { createDatabase, initializeDatabase, EventLog, verifyDeterministicReplay, replayFromEventLog } from '@cockpit/context-fabric';
import { sessions, toolStats, summary, type SessionRecord } from './index';
import type { Event } from '@cockpit/contracts';

function makeBase(eventType: string, aggregateId: string, aggregateType: 'session' | 'task') {
  return {
    eventId: randomUUID(),
    eventType,
    aggregateId,
    aggregateType,
    version: 1,
    timestamp: '2026-08-10T08:00:00.000Z',
    metadata: { correlationId: randomUUID() },
  } as const;
}

function makeSessionCreatedEvent(session: SessionRecord): Event {
  return {
    ...makeBase('session.created', session.id, 'session'),
    adapter: session.source ?? 'unknown',
    agentName: session.profile_name ?? 'default',
    model: session.model ?? 'unknown',
    worktree: 'telemetry-snapshot',
  } as unknown as Event;
}

function makeTaskCompletedEvent(toolName: string, calls: number): Event {
  return {
    ...makeBase('task.completed', `tool-${toolName}`, 'task'),
    result: `${toolName} called ${calls} times in real Hermes telemetry`,
    artifacts: [],
  } as unknown as Event;
}

describe('phase 0 + phase 1 integration: real telemetry -> event-sourced ledger', () => {
  it('imports real telemetry snapshot into context-fabric with hash-chain verification', () => {
    expect(summary.total_sessions).toBeGreaterThan(0);
    expect(toolStats.length).toBeGreaterThan(0);

    const db = createDatabase(':memory:');
    initializeDatabase(db);
    const log = new EventLog(db);

    const events: Event[] = [
      ...sessions.slice(0, 5).map((s) => makeSessionCreatedEvent(s)),
      ...toolStats.slice(0, 5).map((t) => makeTaskCompletedEvent(t.tool_name, t.call_count)),
    ];

    const stored = log.appendMany(events);
    expect(stored.length).toBe(10);
    expect(log.getLatestSequence()).toBe(10);
    expect(log.verifyHashChain()).toBe(true);

    // Tamper detection: mutate one stored payload in DB and verify chain fails.
    db.prepare('UPDATE events SET payload_json = ? WHERE sequence = 1').run(JSON.stringify({ model: 'tampered' }));
    expect(log.verifyHashChain()).toBe(false);

    db.close();
  });

  it('supports deterministic replay over telemetry-derived event stream', () => {
    const db = createDatabase(':memory:');
    initializeDatabase(db);
    const log = new EventLog(db);

    const events: Event[] = [
      ...sessions.slice(0, 3).map((s) => makeSessionCreatedEvent(s)),
      ...toolStats.slice(0, 3).map((t) => makeTaskCompletedEvent(t.tool_name, t.call_count)),
    ];
    log.appendMany(events);

    const replay = replayFromEventLog(log);
    expect(Object.keys(replay.sessions).length).toBe(3);
    expect(Object.keys(replay.tasks).length).toBe(0); // task.completed without prior task.created does not create task projection
    const deterministic = verifyDeterministicReplay(log);
    expect(deterministic.deterministic).toBe(true);
    expect(deterministic.firstHash).toBe(deterministic.secondHash);

    db.close();
  });
});
