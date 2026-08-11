import { readFileSync } from 'node:fs';
import { tokenRecordFromPlaintext, type AuthConfig, type AuthScope } from './auth.js';
import type { CorsConfig } from './cors.js';

type Settings = Record<string, string | undefined>;

export interface RuntimeConfig {
  readonly host: string;
  readonly port: number;
  readonly auth?: AuthConfig;
  readonly cors: CorsConfig;
  readonly cockpitDbPath?: string;
}

export function assertSafeBindHost(host: string, allowPublicBind = false): void {
  if ((host === '0.0.0.0' || host === '::') && !allowPublicBind) {
    throw new Error('Refusing public bind without explicit unsafe override');
  }
}

function parseScopes(value: string | undefined): AuthScope[] {
  if (!value) return ['admin'];
  const scopes = value.split(',').map((item) => item.trim()).filter(Boolean);
  for (const scope of scopes) {
    if (scope !== 'read' && scope !== 'command' && scope !== 'admin') throw new Error(`Invalid cockpit auth scope: ${scope}`);
  }
  return scopes as AuthScope[];
}

function loadToken(settings: Settings): AuthConfig | undefined {
  const tokenFile = settings.COCKPIT_TOKEN_FILE;
  const tokenValue = settings.COCKPIT_TOKEN;
  const token = tokenFile ? readFileSync(tokenFile, 'utf8').trim() : tokenValue?.trim();
  if (!token) return undefined;
  return { tokens: [tokenRecordFromPlaintext('primary', token, parseScopes(settings.COCKPIT_TOKEN_SCOPES))] };
}

export function loadRuntimeConfig(settings: Settings): RuntimeConfig {
  const host = settings.COCKPIT_HOST ?? '127.0.0.1';
  const port = Number(settings.COCKPIT_PORT ?? '8787');
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Invalid COCKPIT_PORT');
  assertSafeBindHost(host, settings.COCKPIT_ALLOW_PUBLIC_BIND === 'I_UNDERSTAND');
  const allowedOrigins = (settings.COCKPIT_ALLOWED_ORIGINS ?? '')
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);
  return { host, port, auth: loadToken(settings), cors: { allowedOrigins }, cockpitDbPath: settings.COCKPIT_DB_PATH };
}
