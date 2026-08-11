import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, statSync, mkdtempSync, copyFileSync, rmSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import Database from 'better-sqlite3';
import { openCockpitStore } from './storage.js';

export interface BackupResult {
  readonly backupPath: string;
  readonly manifestPath: string;
  readonly sha256: string;
  readonly bytes: number;
}

export interface RestoreTestResult {
  readonly ok: boolean;
  readonly backupPath: string;
  readonly auditChainOk: boolean;
  readonly commandCount: number;
  readonly auditEventCount: number;
  readonly migrationCount: number;
}

function sha256File(path: string): string {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function timestamp(): string {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

export async function backupCockpitDb(sourceDbPath: string, backupDir: string, label = timestamp()): Promise<BackupResult> {
  if (!existsSync(sourceDbPath)) throw new Error(`source db does not exist: ${sourceDbPath}`);
  mkdirSync(backupDir, { recursive: true });
  const safeLabel = label.replace(/[^a-zA-Z0-9_-]/g, '-');
  const backupPath = join(backupDir, `${basename(sourceDbPath, '.db')}-${safeLabel}.db`);
  const db = new Database(sourceDbPath, { readonly: true, fileMustExist: true });
  try {
    await db.backup(backupPath);
  } finally {
    db.close();
  }
  const sha256 = sha256File(backupPath);
  const bytes = statSync(backupPath).size;
  const manifestPath = `${backupPath}.manifest.json`;
  const manifest = { schema: 'brenda-ai-cockpit-backup-v1', source: sourceDbPath, backup: backupPath, sha256, bytes, created_at: new Date().toISOString() };
  mkdirSync(dirname(manifestPath), { recursive: true });
  await import('node:fs/promises').then((fs) => fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2)));
  return { backupPath, manifestPath, sha256, bytes };
}

export function restoreTestCockpitDb(backupPath: string): RestoreTestResult {
  if (!existsSync(backupPath)) throw new Error(`backup db does not exist: ${backupPath}`);
  const fixtureDir = mkdtempSync(join(tmpdir(), 'cockpit-restore-test-'));
  const restorePath = join(fixtureDir, 'restored-cockpit.db');
  copyFileSync(backupPath, restorePath);
  const store = openCockpitStore(restorePath);
  try {
    const migrationDb = new Database(restorePath, { readonly: true });
    let migrationCount = 0;
    try {
      migrationCount = Number((migrationDb.prepare('SELECT COUNT(*) AS count FROM schema_migrations').get() as { count: number }).count);
    } finally {
      migrationDb.close();
    }
    const auditChainOk = store.verifyAuditChain();
    const commandCount = store.listCommands(500).length;
    const auditEventCount = store.listAuditEvents(500).length;
    return { ok: migrationCount > 0 && auditChainOk, backupPath, auditChainOk, commandCount, auditEventCount, migrationCount };
  } finally {
    store.close();
    rmSync(fixtureDir, { recursive: true, force: true });
  }
}

async function main(): Promise<void> {
  const [, , command, dbPath, backupDirOrPath] = process.argv;
  if (command === 'backup') {
    if (!dbPath || !backupDirOrPath) throw new Error('usage: node dist/backup.js backup <cockpit.db> <backup-dir>');
    console.log(JSON.stringify(await backupCockpitDb(dbPath, backupDirOrPath), null, 2));
    return;
  }
  if (command === 'restore-test') {
    if (!dbPath) throw new Error('usage: node dist/backup.js restore-test <backup.db>');
    const result = restoreTestCockpitDb(dbPath);
    console.log(JSON.stringify(result, null, 2));
    if (!result.ok) process.exitCode = 1;
    return;
  }
  throw new Error('usage: node dist/backup.js <backup|restore-test> ...');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error instanceof Error ? error.message : String(error)); process.exitCode = 1; });
}
