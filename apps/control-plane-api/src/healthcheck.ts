import { existsSync, readFileSync } from 'node:fs';

type Settings = Record<string, string | undefined>;

export interface HealthcheckResult {
  readonly ok: boolean;
  readonly healthOk: boolean;
  readonly auditOk?: boolean;
  readonly message: string;
}

export async function runHealthcheck(baseUrl: string, token?: string): Promise<HealthcheckResult> {
  const normalized = baseUrl.replace(/\/$/, '');
  try {
    const health = await fetch(`${normalized}/api/health`);
    if (!health.ok) return { ok: false, healthOk: false, message: `health returned ${health.status}` };
    if (!token) return { ok: true, healthOk: true, message: 'health ok' };
    const audit = await fetch(`${normalized}/api/v1/audit`, { headers: { Authorization: `Bearer ${token}` } });
    if (!audit.ok) return { ok: false, healthOk: true, auditOk: false, message: `audit returned ${audit.status}` };
    const body = await audit.json() as { chain_ok?: boolean };
    return { ok: body.chain_ok === true, healthOk: true, auditOk: body.chain_ok === true, message: body.chain_ok === true ? 'deep health ok' : 'audit chain broken' };
  } catch (error) {
    return { ok: false, healthOk: false, message: error instanceof Error ? error.message : String(error) };
  }
}

function readTokenFromRuntime(settings: Settings): string | undefined {
  const tokenFile = settings.COCKPIT_TOKEN_FILE;
  if (tokenFile && existsSync(tokenFile)) return readFileSync(tokenFile, 'utf8').trim();
  return settings.COCKPIT_TOKEN;
}

async function main(): Promise<void> {
  const settings = process['env'] as Settings;
  const baseUrl = process.argv[2] ?? `http://127.0.0.1:${settings.COCKPIT_PORT ?? '8787'}`;
  const result = await runHealthcheck(baseUrl, readTokenFromRuntime(settings));
  console.log(JSON.stringify(result));
  if (!result.ok) process.exitCode = 1;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error instanceof Error ? error.message : String(error)); process.exitCode = 1; });
}
