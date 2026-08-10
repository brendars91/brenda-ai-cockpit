import { hashProjectionState } from './hash.js';
import {
  emptyProjectedState,
  projectEvents,
  reduceEvent,
  selectCanonicalProjection,
} from './projections.js';

import type { EventLog, StoredEvent } from './event-log.js';
import type {
  ProjectedState,
  SessionProjection,
  TaskProjection,
  AgentProjection,
  RunProjection,
  IssueProjection,
  KnowledgeProjection,
} from './projections.js';
import type { Event } from '@cockpit/contracts';
import type Database from 'better-sqlite3';

/**
 * ProjectionEngine persists projected read-models to SQLite tables
 * and supports incremental application of events.
 */
export class ProjectionEngine {
  private readonly db: Database.Database;
  private readonly eventLog: EventLog;

  public constructor(db: Database.Database, eventLog: EventLog) {
    this.db = db;
    this.eventLog = eventLog;
  }

  /** Clear all projection tables, re-derive from the full event log, persist. */
  public rebuild(): ProjectedState {
    this.db.exec('DELETE FROM projection_sessions');
    this.db.exec('DELETE FROM projection_tasks');
    this.db.exec('DELETE FROM projection_agents');
    this.db.exec('DELETE FROM projection_runs');
    this.db.exec('DELETE FROM projection_issues');
    this.db.exec('DELETE FROM projection_knowledge');
    this.db.exec("DELETE FROM projection_system WHERE key = 'system'");

    const events = this.eventLog.getEvents();
    const state = projectEvents(events.map(this.storedToEvent));

    this.persistState(state);
    return state;
  }

  /** Apply a single stored event incrementally to the projection tables. */
  public applyStoredEvent(storedEvent: StoredEvent): void {
    const event = this.storedToEvent(storedEvent);
    const currentState = this.loadState();
    const newState = reduceEvent(currentState, event);
    this.persistState(newState);
  }

  /** Read the current projected state from the projection tables. */
  public getCurrentState(): ProjectedState {
    return this.loadState();
  }

  /** Hash the canonical projection for deterministic verification. */
  public getCurrentStateHash(): string {
    const state = this.getCurrentState();
    return hashProjectionState(selectCanonicalProjection(state));
  }

  // ── Private helpers ──

  private persistState(state: ProjectedState): void {
    this.persistProjectionTable('projection_sessions', state.sessions);
    this.persistProjectionTable('projection_tasks', state.tasks);
    this.persistProjectionTable('projection_agents', state.agents);
    this.persistProjectionTable('projection_runs', state.runs);
    this.persistProjectionTable('projection_issues', state.issues);
    this.persistProjectionTable('projection_knowledge', state.knowledge);

    this.db
      .prepare(`INSERT OR REPLACE INTO projection_system (key, value) VALUES ('system', ?)`)
      .run(JSON.stringify(state.system));
  }

  private persistProjectionTable(table: string, data: Record<string, unknown>): void {
    this.db.exec(`DELETE FROM ${table}`);
    const insert = this.db.prepare(`INSERT INTO ${table} (id, data_json) VALUES (?, ?)`);
    const transaction = this.db.transaction(() => {
      for (const [id, value] of Object.entries(data)) {
        insert.run(id, JSON.stringify(value));
      }
    });
    transaction();
  }

  private loadState(): ProjectedState {
    const sessions = this.loadProjectionTable<SessionProjection>('projection_sessions');
    const tasks = this.loadProjectionTable<TaskProjection>('projection_tasks');
    const agents = this.loadProjectionTable<AgentProjection>('projection_agents');
    const runs = this.loadProjectionTable<RunProjection>('projection_runs');
    const issues = this.loadProjectionTable<IssueProjection>('projection_issues');
    const knowledge = this.loadProjectionTable<KnowledgeProjection>('projection_knowledge');

    let system = emptyProjectedState().system;
    const systemRow = this.db
      .prepare("SELECT value FROM projection_system WHERE key = 'system'")
      .get() as { value: string } | undefined;
    if (systemRow) {
      system = JSON.parse(systemRow.value) as typeof system;
    }

    return { sessions, tasks, agents, runs, issues, knowledge, system };
  }

  private loadProjectionTable<T>(table: string): Record<string, T> {
    const rows = this.db.prepare(`SELECT id, data_json FROM ${table}`).all() as ReadonlyArray<{
      id: string;
      data_json: string;
    }>;
    const result: Record<string, T> = {};
    for (const row of rows) {
      result[row.id] = JSON.parse(row.data_json) as T;
    }
    return result;
  }

  private storedToEvent(stored: StoredEvent): Event {
    const base = {
      eventId: stored.eventId,
      eventType: stored.eventType,
      aggregateId: stored.aggregateId,
      aggregateType: stored.aggregateType,
      version: stored.version as 1,
      timestamp: stored.timestamp,
      metadata: stored.metadata,
    };
    return { ...base, ...stored.payload } as unknown as Event;
  }
}
