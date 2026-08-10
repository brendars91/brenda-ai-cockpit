import Database from 'better-sqlite3';
import crypto from 'node:crypto';
import path from 'node:path';

interface EvidenceRecord {
  id: string;
  created_at: string;
  session_id: string;
  command: string | null;
  canonical_command: string | null;
  kind: string;
  diff_hash: string | null;
}

const DEFAULT_DB = '/home/ubuntu/.hermes/verification_evidence.db';

function tableExists(db: Database.Database, tableName: string): boolean {
  const res = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").get(tableName);
  return !!res;
}

function getTableName(db: Database.Database): string {
  const candidates = ['verification_events', 'evidence', 'verification_log', 'events'];
  for (const c of candidates) {
    if (tableExists(db, c)) return c;
  }
  throw new Error('No verification evidence table found in database');
}

export function readEvidence(
  dbPath: string = DEFAULT_DB,
  limit = 100,
): EvidenceRecord[] {
  const db = new Database(dbPath, { readonly: true, fileMustExist: true });
  try {
    const table = getTableName(db);
    const rows = db
      .prepare(`SELECT * FROM ${table} ORDER BY created_at DESC LIMIT ?`)
      .all(limit) as EvidenceRecord[];
    return rows;
  } finally {
    db.close();
  }
}

export function auditSkillExecution(
  dbPath: string = DEFAULT_DB,
  sessionId: string,
  skillName: string,
  diffContent: string,
): { id: string; diff_hash: string } {
  const db = new Database(dbPath, { readonly: false });
  try {
    const table = getTableName(db);
    const tx = db.transaction(() => {
      const stmt = db.prepare(`
        CREATE TABLE IF NOT EXISTS ${table}_audit (
          id TEXT PRIMARY KEY,
          created_at TEXT NOT NULL,
          session_id TEXT NOT NULL,
          skill_name TEXT NOT NULL,
          command TEXT,
          canonical_command TEXT,
          kind TEXT,
          diff_hash TEXT
        )
      `);
      stmt.run();

      const diffHash = crypto.createHash('sha256').update(diffContent).digest('hex').slice(0, 16);
      const id = `${sessionId}:${skillName}:${diffHash}`;
      const now = new Date().toISOString();

      db.prepare(`
        INSERT OR REPLACE INTO ${table}_audit
          (id, created_at, session_id, skill_name, canonical_command, kind, diff_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(id, now, sessionId, skillName, skillName, 'skill-execution-completed', diffHash);

      return { id, diff_hash: diffHash };
    });
    return tx();
  } finally {
    db.close();
  }
}
