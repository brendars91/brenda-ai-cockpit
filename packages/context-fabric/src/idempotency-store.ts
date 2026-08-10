import type Database from 'better-sqlite3';

/**
 * Idempotency store backed by SQLite.
 * Ensures commands are executed exactly once.
 */
export class IdempotencyStore {
  private readonly db: Database.Database;

  public constructor(db: Database.Database) {
    this.db = db;
  }

  /** Record a result for an idempotency key. */
  public record<T>(idempotencyKey: string, commandId: string, result: T): T {
    this.db
      .prepare(
        `INSERT OR IGNORE INTO idempotency_keys
          (idempotency_key, command_id, result_json, created_at)
         VALUES (?, ?, ?, datetime('now'))`,
      )
      .run(idempotencyKey, commandId, JSON.stringify(result));
    return result;
  }

  /** Retrieve a previously recorded result, or null. */
  public get<T>(idempotencyKey: string): T | null {
    const row = this.db
      .prepare('SELECT result_json FROM idempotency_keys WHERE idempotency_key = ?')
      .get(idempotencyKey) as { result_json: string } | undefined;
    if (!row) return null;
    return JSON.parse(row.result_json) as T;
  }

  /** Check whether a key exists. */
  public has(idempotencyKey: string): boolean {
    const row = this.db
      .prepare('SELECT 1 as cnt FROM idempotency_keys WHERE idempotency_key = ?')
      .get(idempotencyKey) as { cnt: number } | undefined;
    return row !== undefined;
  }

  /**
   * Execute a function exactly once per idempotency key.
   * On subsequent calls with the same key, returns the cached result.
   */
  public executeOnce<T>(idempotencyKey: string, commandId: string, fn: () => T): T {
    const existing = this.get<T>(idempotencyKey);
    if (existing !== null) {
      return existing;
    }
    const result = fn();
    return this.record(idempotencyKey, commandId, result);
  }
}
