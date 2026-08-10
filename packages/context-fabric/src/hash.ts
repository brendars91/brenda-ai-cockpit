import { createHash } from 'node:crypto';

import type { Event } from '@cockpit/contracts';

/** Deterministic JSON stringify with sorted object keys recursively. */
export function canonicalJson(value: unknown): string {
  if (value === null || value === undefined || typeof value !== 'object') {
    if (typeof value === 'bigint') {
      return value.toString();
    }
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    const items: string[] = value.map((item: unknown) => canonicalJson(item));
    return `[${items.join(',')}]`;
  }

  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  const pairs: string[] = keys.map((key: string) => `"${key}":${canonicalJson(obj[key])}`);
  return `{${pairs.join(',')}}`;
}

/** SHA-256 hex digest. */
export function sha256(input: string): string {
  return createHash('sha256').update(input).digest('hex');
}

/** Hash an event combined with the previous hash for chain integrity. */
export function hashEvent(event: Event, previousHash: string | null): string {
  const payload = canonicalJson({
    event,
    previousHash,
  });
  return sha256(payload);
}

/** Deterministic hash of a projected state snapshot. */
export function hashProjectionState(state: unknown): string {
  return sha256(canonicalJson(state));
}
