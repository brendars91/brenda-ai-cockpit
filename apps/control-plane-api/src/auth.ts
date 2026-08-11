import { createHash, timingSafeEqual } from 'node:crypto';
import type { IncomingMessage } from 'node:http';

export type AuthScope = 'read' | 'command' | 'admin';

export interface AuthTokenRecord {
  readonly id: string;
  readonly sha256: string;
  readonly scopes: readonly AuthScope[];
}

export interface AuthConfig {
  readonly tokens: readonly AuthTokenRecord[];
}

export type AuthDecision =
  | { readonly ok: true; readonly tokenId: string; readonly scopes: readonly AuthScope[] }
  | { readonly ok: false; readonly status: 401 | 403 | 503; readonly code: string; readonly message: string };

const scopeRank: Record<AuthScope, number> = { read: 0, command: 1, admin: 2 };

export function sha256Hex(value: string): string {
  return createHash('sha256').update(value, 'utf8').digest('hex');
}

function hasScope(scopes: readonly AuthScope[], required: AuthScope): boolean {
  return scopes.some((scope) => scopeRank[scope] >= scopeRank[required]);
}

function safeEqualHex(left: string, right: string): boolean {
  if (!/^[a-f0-9]{64}$/i.test(left) || !/^[a-f0-9]{64}$/i.test(right)) return false;
  const a = Buffer.from(left, 'hex');
  const b = Buffer.from(right, 'hex');
  return a.length === b.length && timingSafeEqual(a, b);
}

export function tokenRecordFromPlaintext(id: string, token: string, scopes: readonly AuthScope[]): AuthTokenRecord {
  if (token.trim().length < 16) throw new Error('cockpit token must be at least 16 characters');
  return { id, sha256: sha256Hex(token), scopes };
}

export function authenticateRequest(req: IncomingMessage, auth: AuthConfig | undefined, required: AuthScope): AuthDecision {
  if (!auth || auth.tokens.length === 0) {
    return { ok: false, status: 503, code: 'auth_not_configured', message: 'API authentication is not configured' };
  }

  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    return { ok: false, status: 401, code: 'missing_auth', message: 'Missing bearer token' };
  }

  const token = header.slice('Bearer '.length).trim();
  if (!token) return { ok: false, status: 401, code: 'missing_auth', message: 'Missing bearer token' };

  const presented = sha256Hex(token);
  const matched = auth.tokens.find((record) => safeEqualHex(presented, record.sha256));
  if (!matched) return { ok: false, status: 401, code: 'invalid_token', message: 'Invalid bearer token' };
  if (!hasScope(matched.scopes, required)) {
    return { ok: false, status: 403, code: 'insufficient_scope', message: `Required scope: ${required}` };
  }

  return { ok: true, tokenId: matched.id, scopes: matched.scopes };
}
