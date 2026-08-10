import Database from 'better-sqlite3';

/**
 * Create a better-sqlite3 database connection.
 * Uses `:memory:` when path is omitted.
 */
export function createDatabase(path?: string): Database.Database {
  return new Database(path ?? ':memory:');
}

/** Initialize all tables and indexes for the event-sourced canon. */
export function initializeDatabase(db: Database.Database): void {
  db.exec(`
    PRAGMA journal_mode=WAL;
    PRAGMA foreign_keys=ON;

    -- Append-only event log
    CREATE TABLE IF NOT EXISTS events (
      sequence       INTEGER PRIMARY KEY AUTOINCREMENT,
      event_id       TEXT NOT NULL UNIQUE,
      event_type     TEXT NOT NULL,
      aggregate_id   TEXT NOT NULL,
      aggregate_type TEXT NOT NULL,
      version        INTEGER NOT NULL,
      timestamp      TEXT NOT NULL,
      metadata_json  TEXT NOT NULL,
      payload_json   TEXT NOT NULL,
      event_hash     TEXT NOT NULL,
      previous_hash  TEXT,
      created_at     TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_events_aggregate
      ON events (aggregate_type, aggregate_id, sequence);
    CREATE INDEX IF NOT EXISTS idx_events_type
      ON events (event_type, sequence);
    CREATE INDEX IF NOT EXISTS idx_events_timestamp
      ON events (timestamp);

    -- Idempotency dedup
    CREATE TABLE IF NOT EXISTS idempotency_keys (
      idempotency_key TEXT PRIMARY KEY,
      command_id      TEXT NOT NULL,
      result_json     TEXT NOT NULL,
      created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- Projection tables ────────────────────────────────────
    CREATE TABLE IF NOT EXISTS projection_sessions (
      id          TEXT PRIMARY KEY,
      data_json   TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS projection_tasks (
      id          TEXT PRIMARY KEY,
      data_json   TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS projection_agents (
      id          TEXT PRIMARY KEY,
      data_json   TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS projection_runs (
      id          TEXT PRIMARY KEY,
      data_json   TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS projection_issues (
      id          TEXT PRIMARY KEY,
      data_json   TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS projection_knowledge (
      id          TEXT PRIMARY KEY,
      data_json   TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS projection_system (
      key   TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
  `);
}

/** Close the database connection. */
export function closeDatabase(db: Database.Database): void {
  db.close();
}
