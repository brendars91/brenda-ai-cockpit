import type { IncomingMessage, ServerResponse } from 'node:http';

export interface CorsConfig {
  readonly allowedOrigins: readonly string[];
}

export function applyCors(req: IncomingMessage, res: ServerResponse, cors: CorsConfig): boolean {
  const origin = req.headers.origin;
  res.setHeader('Vary', 'Origin');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (!origin) return true;
  if (cors.allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    return true;
  }

  res.writeHead(403, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'cors_origin_denied', origin }));
  return false;
}
