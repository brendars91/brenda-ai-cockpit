import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import Database from 'better-sqlite3';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { tokenRecordFromPlaintext, type AuthConfig } from './auth.js';
import { createApiServer } from './server.js';
import { readSummary, readSessions, readCosts, readTools, readCron, readEvidence, readMemory, routeData, type ApiPaths } from './readers.js';

const readToken = 'fake-read-token-0000000000000000';
const auth: AuthConfig = { tokens: [tokenRecordFromPlaintext('read', readToken, ['read'])] };

let fixtureDir = '';
let paths: ApiPaths;

function createFixtureDatabase(filePath: string, statements: readonly string[]): void {
  const db = new Database(filePath);
  try {
    for (const statement of statements) db.exec(statement);
  } finally {
    db.close();
  }
}

beforeAll(() => {
  fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-api-fixture-'));
  paths = {
    stateDb: join(fixtureDir, 'state.db'),
    cronDb: join(fixtureDir, 'cron.db'),
    evidenceDb: join(fixtureDir, 'evidence.db'),
    memoryDb: join(fixtureDir, 'memory.db'),
  };

  createFixtureDatabase(paths.stateDb, [
    `CREATE TABLE sessions (
      id TEXT PRIMARY KEY,
      source TEXT,
      model TEXT,
      started_at TEXT,
      ended_at TEXT,
      message_count INTEGER,
      tool_call_count INTEGER,
      input_tokens INTEGER,
      output_tokens INTEGER,
      reasoning_tokens INTEGER,
      billing_provider TEXT,
      estimated_cost_usd REAL,
      title TEXT,
      chat_type TEXT,
      profile_name TEXT
    );`,
    `INSERT INTO sessions VALUES ('s1','discord','gpt-test','2026-01-01T00:00:00Z',NULL,4,2,1000,250,0,'openai',0.02,'fixture session','dm','default');`,
    `CREATE TABLE messages (id INTEGER PRIMARY KEY, session_id TEXT, tool_name TEXT);`,
    `INSERT INTO messages (session_id, tool_name) VALUES ('s1','terminal'),('s1','read_file');`,
  ]);

  createFixtureDatabase(paths.cronDb, [
    `CREATE TABLE executions (id INTEGER PRIMARY KEY, status TEXT);`,
    `INSERT INTO executions (status) VALUES ('completed'),('failed');`,
  ]);

  createFixtureDatabase(paths.evidenceDb, [
    `CREATE TABLE verification_events (id INTEGER PRIMARY KEY, created_at TEXT, session_id TEXT, command TEXT, canonical_command TEXT, kind TEXT);`,
    `INSERT INTO verification_events VALUES (1,'2026-01-01T00:00:00Z','s1','npm run verify','npm run verify','test');`,
  ]);

  createFixtureDatabase(paths.memoryDb, [
    `CREATE TABLE facts (fact_id INTEGER PRIMARY KEY, content TEXT, category TEXT, trust_score REAL, tags TEXT);`,
    `INSERT INTO facts VALUES (1,'fixture fact','general',0.9,'fixture');`,
  ]);
});

afterAll(() => {
  if (fixtureDir) rmSync(fixtureDir, { recursive: true, force: true });
});

describe('sqlite readers over deterministic fixture databases', () => {
  it('reads summary from all database surfaces', () => {
    const summary = readSummary(paths);
    expect(summary.sessions.count).toBe(1);
    expect(summary.tools.count).toBe(2);
    expect(summary.cron.count).toBe(2);
    expect(summary.evidence.count).toBe(1);
    expect(summary.memory.count).toBe(1);
  });

  it('reads sanitized session metadata without message content', () => {
    const sessions = readSessions(paths, 5);
    expect(sessions).toHaveLength(1);
    const keys = Object.keys(sessions[0] as Record<string, unknown>);
    expect(keys).not.toContain('content');
    expect(keys).not.toContain('system_prompt');
  });

  it('reads all dashboard datasets with fixture records', () => {
    expect(readCosts(paths)).toHaveLength(1);
    expect(readTools(paths)).toHaveLength(2);
    expect(readCron(paths)).toHaveLength(2);
    expect(readEvidence(paths)).toHaveLength(1);
    expect(readMemory(paths)).toHaveLength(1);
  });

  it('routeData maps all production endpoints', () => {
    for (const path of ['/api/health', '/api/summary', '/api/sessions', '/api/costs', '/api/tools', '/api/cron', '/api/evidence', '/api/memory', '/api/v1/adapters', '/api/v1/capabilities', '/api/v1/agents/status']) {
      expect(routeData(path, paths)).not.toBeNull();
    }
    expect(routeData('/api/unknown', paths)).toBeNull();
  });
});

describe('control-plane-api HTTP server', () => {
  it('serves /api/health and /api/summary as JSON using injected fixture paths', async () => {
    const server = createApiServer({ paths, auth });
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
    const address = server.address();
    if (!address || typeof address === 'string') throw new Error('No server address');
    const base = `http://127.0.0.1:${address.port}`;
    const health = await fetch(`${base}/api/health`);
    expect(health.status).toBe(200);
    expect((await health.json()).ok).toBe(true);
    const summary = await fetch(`${base}/api/summary`, { headers: { Authorization: `Bearer ${readToken}` } });
    expect(summary.status).toBe(200);
    expect((await summary.json()).sessions.count).toBe(1);
    await new Promise<void>((resolve) => server.close(() => resolve()));
  });
});
