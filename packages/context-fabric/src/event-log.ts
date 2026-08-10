import { EventSchema } from '@cockpit/contracts';

import { DuplicateEventError } from './errors.js';
import { hashEvent } from './hash.js';

import type { Event } from '@cockpit/contracts';
import type Database from 'better-sqlite3';

/** A fully persisted event with storage metadata. */
export interface StoredEvent {
  readonly eventId: string;
  readonly eventType: string;
  readonly aggregateId: string;
  readonly aggregateType: string;
  readonly version: number;
  readonly timestamp: string;
  readonly metadata: {
    correlationId: string;
    causationId?: string;
  };
  readonly payload: Record<string, unknown>;
  readonly sequence: number;
  readonly eventHash: string;
  readonly previousHash: string | null;
}

interface EventRow {
  sequence: number;
  event_id: string;
  event_type: string;
  aggregate_id: string;
  aggregate_type: string;
  version: number;
  timestamp: string;
  metadata_json: string;
  payload_json: string;
  event_hash: string;
  previous_hash: string | null;
}

function rowToStoredEvent(row: EventRow): StoredEvent {
  const metadata = JSON.parse(row.metadata_json) as {
    correlationId: string;
    causationId?: string;
  };
  const payload = JSON.parse(row.payload_json) as Record<string, unknown>;
  return {
    eventId: row.event_id,
    eventType: row.event_type,
    aggregateId: row.aggregate_id,
    aggregateType: row.aggregate_type,
    version: row.version,
    timestamp: row.timestamp,
    metadata,
    payload,
    sequence: row.sequence,
    eventHash: row.event_hash,
    previousHash: row.previous_hash,
  };
}

function extractPayload(event: Event): Record<string, unknown> {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { eventId, eventType, timestamp, aggregateId, aggregateType, version, metadata, ...rest } =
    event;
  return rest as Record<string, unknown>;
}

export class EventLog {
  private readonly db: Database.Database;

  public constructor(db: Database.Database) {
    this.db = db;
  }

  /** Append a single validated event. Returns the stored event with sequence and hashes. */
  public append(event: Event): StoredEvent {
    const parsed = EventSchema.safeParse(event);
    if (!parsed.success) {
      throw new DuplicateEventError(
        `Invalid event: ${parsed.error.issues.map((i) => i.message).join(', ')}`,
      );
    }

    const latest = this.getLatestRow();
    const previousHash: string | null = latest?.event_hash ?? null;
    const eventHash = hashEvent(event, previousHash);
    const metadataJson = JSON.stringify(event.metadata);
    const payloadJson = JSON.stringify(extractPayload(event));

    const insert = this.db.prepare(`
      INSERT INTO events
        (event_id, event_type, aggregate_id, aggregate_type, version,
         timestamp, metadata_json, payload_json, event_hash, previous_hash)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    try {
      const info = insert.run(
        event.eventId,
        event.eventType,
        event.aggregateId,
        event.aggregateType,
        event.version,
        event.timestamp,
        metadataJson,
        payloadJson,
        eventHash,
        previousHash,
      );
      return {
        eventId: event.eventId,
        eventType: event.eventType,
        aggregateId: event.aggregateId,
        aggregateType: event.aggregateType,
        version: event.version,
        timestamp: event.timestamp,
        metadata: event.metadata,
        payload: extractPayload(event),
        sequence: info.lastInsertRowid as number,
        eventHash,
        previousHash,
      };
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      if (message.includes('UNIQUE constraint failed: events.event_id')) {
        throw new DuplicateEventError(event.eventId);
      }
      throw err;
    }
  }

  /** Append multiple events inside a single transaction. */
  public appendMany(events: readonly Event[]): readonly StoredEvent[] {
    const transaction = this.db.transaction((): StoredEvent[] => {
      const results: StoredEvent[] = [];
      for (const event of events) {
        results.push(this.append(event));
      }
      return results;
    });
    return transaction();
  }

  public getBySequence(sequence: number): StoredEvent | null {
    const row = this.db.prepare('SELECT * FROM events WHERE sequence = ?').get(sequence) as
      | EventRow
      | undefined;
    return row ? rowToStoredEvent(row) : null;
  }

  public getByEventId(eventId: string): StoredEvent | null {
    const row = this.db.prepare('SELECT * FROM events WHERE event_id = ?').get(eventId) as
      | EventRow
      | undefined;
    return row ? rowToStoredEvent(row) : null;
  }

  public getEvents(options?: {
    afterSequence?: number;
    limit?: number;
    aggregateId?: string;
    aggregateType?: string;
    eventType?: string;
  }): readonly StoredEvent[] {
    const conditions: string[] = [];
    const params: unknown[] = [];

    if (options?.afterSequence !== undefined) {
      conditions.push('sequence > ?');
      params.push(options.afterSequence);
    }
    if (options?.aggregateId !== undefined) {
      conditions.push('aggregate_id = ?');
      params.push(options.aggregateId);
    }
    if (options?.aggregateType !== undefined) {
      conditions.push('aggregate_type = ?');
      params.push(options.aggregateType);
    }
    if (options?.eventType !== undefined) {
      conditions.push('event_type = ?');
      params.push(options.eventType);
    }

    const where = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
    const limit = options?.limit !== undefined ? `LIMIT ${options.limit}` : '';

    const sql = `SELECT * FROM events ${where} ORDER BY sequence ASC ${limit}`;
    const rows = this.db.prepare(sql).all(...params) as EventRow[];
    return rows.map(rowToStoredEvent);
  }

  public getLatestSequence(): number {
    const row = this.db.prepare('SELECT MAX(sequence) as seq FROM events').get() as
      | { seq: number | null }
      | undefined;
    return row?.seq ?? 0;
  }

  public getLatestHash(): string | null {
    const row = this.getLatestRow();
    return row?.event_hash ?? null;
  }

  /** Verify the entire hash chain from first to latest event. */
  public verifyHashChain(): boolean {
    const rows = this.db.prepare('SELECT * FROM events ORDER BY sequence ASC').all() as EventRow[];

    if (rows.length === 0) return true;

    let previousHash: string | null = null;
    for (const row of rows) {
      let event: Event;
      try {
        event = this.reconstructEvent(row);
      } catch {
        return false;
      }
      const expected = hashEvent(event, previousHash);
      if (row.event_hash !== expected) return false;
      previousHash = row.event_hash;
    }
    return true;
  }

  private getLatestRow(): EventRow | null {
    const row = this.db.prepare('SELECT * FROM events ORDER BY sequence DESC LIMIT 1').get() as
      | EventRow
      | undefined;
    return row ?? null;
  }

  private reconstructEvent(row: EventRow): Event {
    const metadata = JSON.parse(row.metadata_json) as {
      correlationId: string;
      causationId?: string;
    };
    const payload = JSON.parse(row.payload_json) as Record<string, unknown>;

    const base = {
      eventId: row.event_id,
      eventType: row.event_type,
      aggregateId: row.aggregate_id,
      aggregateType: row.aggregate_type,
      version: row.version as 1,
      timestamp: row.timestamp,
      metadata,
    };

    return { ...base, ...payload } as unknown as Event;
  }
}
