import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { authenticateRequest, type AuthConfig, type AuthScope } from './auth.js';
import { loadRuntimeConfig } from './config.js';
import { applyCors, type CorsConfig } from './cors.js';
import { executeQueuedCommand, type AllowedAction } from './executor.js';
import { routeData, type ApiPaths } from './readers.js';
import { openCockpitStore, type CockpitStore } from './storage.js';
import { validateDelegateRequest } from './delegate.js';

export interface ApiServerOptions {
  readonly paths?: ApiPaths;
  readonly auth?: AuthConfig;
  readonly cors?: CorsConfig;
  readonly store?: CockpitStore;
  readonly executorCwd?: string;
  readonly executorCatalog?: readonly AllowedAction[];
  readonly maxBodyBytes?: number;
}

const defaultCors: CorsConfig = { allowedOrigins: [] };

function json(res: ServerResponse, status: number, body: unknown): void {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

function requireScope(req: IncomingMessage, res: ServerResponse, auth: AuthConfig | undefined, scope: AuthScope): ReturnType<typeof authenticateRequest> {
  const decision = authenticateRequest(req, auth, scope);
  if (decision.ok) return decision;
  json(res, decision.status, { error: decision.code, message: decision.message });
  return decision;
}

async function readRequestBody(req: IncomingMessage, maxBodyBytes: number): Promise<{ ok: true; body: string } | { ok: false }> {
  let body = '';
  for await (const chunk of req) {
    body += chunk;
    if (body.length > maxBodyBytes) return { ok: false };
  }
  return { ok: true, body };
}

function parseJsonObject(body: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(body || '{}');
    return parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed as Record<string, unknown> : null;
  } catch {
    return null;
  }
}

export function createApiServer(options: ApiServerOptions = {}) {
  const cors = options.cors ?? defaultCors;
  const maxBodyBytes = options.maxBodyBytes ?? 1024 * 1024;

  return createServer(async (req, res) => {
    const url = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`);
    if (!applyCors(req, res, cors)) return;
    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
    if (req.method !== 'GET' && req.method !== 'POST') { json(res, 405, { error: 'method_not_allowed' }); return; }

    try {
      if (req.method === 'GET') {
        if (url.pathname === '/api/health') {
          const data = routeData(url.pathname, options.paths);
          json(res, 200, data);
          return;
        }
        const authDecision = requireScope(req, res, options.auth, 'read');
        if (!authDecision.ok) return;
        if (url.pathname === '/api/v1/commands') {
          if (!options.store) { json(res, 503, { error: 'storage_not_configured' }); return; }
          json(res, 200, { commands: options.store.listCommands() });
          return;
        }
        if (url.pathname === '/api/v1/audit') {
          if (!options.store) { json(res, 503, { error: 'storage_not_configured' }); return; }
          json(res, 200, { audit: options.store.listAuditEvents(), chain_ok: options.store.verifyAuditChain() });
          return;
        }
        const data = routeData(url.pathname, options.paths);
        if (data === null) { json(res, 404, { error: 'not_found', path: url.pathname }); return; }
        json(res, 200, data);
        return;
      }

      if (url.pathname === '/api/v1/commands') {
        const commandAuth = requireScope(req, res, options.auth, 'command');
        if (!commandAuth.ok) return;
        if (!options.store) { json(res, 503, { error: 'storage_not_configured' }); return; }
        const readResult = await readRequestBody(req, maxBodyBytes);
        if (!readResult.ok) { json(res, 413, { error: 'payload_too_large' }); return; }
        const parsed = parseJsonObject(readResult.body);
        if (!parsed) { json(res, 400, { error: 'invalid_json' }); return; }
        try {
          const command = options.store.submitCommand({
            requestedBy: commandAuth.tokenId === 'admin' ? 'brenda' : commandAuth.tokenId,
            principalRole: commandAuth.tokenId === 'admin' ? 'owner' : 'operator',
            action: parsed.action as never,
            target: String(parsed.target ?? ''),
            risk: parsed.risk as never,
            payload: parsed.payload ?? {},
          });
          json(res, command.status === 'denied' ? 403 : 200, { command });
        } catch (error) {
          json(res, 400, { error: 'invalid_command', message: error instanceof Error ? error.message : String(error) });
        }
        return;
      }

      const executeMatch = url.pathname.match(/^\/api\/v1\/commands\/([^/]+)\/execute$/);
      if (executeMatch) {
        const adminAuth = requireScope(req, res, options.auth, 'admin');
        if (!adminAuth.ok) return;
        if (!options.store) { json(res, 503, { error: 'storage_not_configured' }); return; }
        try {
          const command = await executeQueuedCommand(options.store, executeMatch[1], options.executorCwd ?? process.cwd(), options.executorCatalog);
          json(res, command.status === 'succeeded' ? 200 : 409, { command });
        } catch (error) {
          json(res, 409, { error: 'execution_rejected', message: error instanceof Error ? error.message : String(error) });
        }
        return;
      }

      const approvalMatch = url.pathname.match(/^\/api\/v1\/commands\/([^/]+)\/approve$/);
      if (approvalMatch) {
        const adminAuth = requireScope(req, res, options.auth, 'admin');
        if (!adminAuth.ok) return;
        if (!options.store) { json(res, 503, { error: 'storage_not_configured' }); return; }
        const readResult = await readRequestBody(req, maxBodyBytes);
        if (!readResult.ok) { json(res, 413, { error: 'payload_too_large' }); return; }
        const parsed = parseJsonObject(readResult.body);
        if (!parsed) { json(res, 400, { error: 'invalid_json' }); return; }
        try {
          const command = options.store.approveCommand({ commandId: approvalMatch[1], approvedBy: 'brenda', reason: String(parsed.reason ?? 'approved by owner') });
          json(res, 200, { command });
        } catch (error) {
          json(res, 409, { error: 'approval_rejected', message: error instanceof Error ? error.message : String(error) });
        }
        return;
      }

      if (url.pathname !== '/api/v1/delegate') { json(res, 404, { error: 'not_found', path: url.pathname }); return; }
      const commandAuth = requireScope(req, res, options.auth, 'command');
      if (!commandAuth.ok) return;
      const readResult = await readRequestBody(req, maxBodyBytes);
      if (!readResult.ok) { json(res, 413, { error: 'payload_too_large' }); return; }
      const result = validateDelegateRequest(readResult.body);
      json(res, result.status === 'accepted' ? 200 : 400, result);
    } catch (error) {
      json(res, 500, { error: 'internal_error', message: error instanceof Error ? error.message : String(error) });
    }
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const rawSettings = process['env'] as Record<string, string | undefined>;
  const settings = { ...rawSettings, COCKPIT_PORT: process.argv[2] ?? rawSettings.COCKPIT_PORT };
  const config = loadRuntimeConfig(settings);
  const store = config.cockpitDbPath ? openCockpitStore(config.cockpitDbPath) : undefined;
  createApiServer({ auth: config.auth, cors: config.cors, store }).listen(config.port, config.host, () => {
    console.log(`control-plane-api listening on http://${config.host}:${config.port}`);
  });
}
