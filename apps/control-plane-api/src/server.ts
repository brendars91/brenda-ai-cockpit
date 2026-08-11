import { createServer } from 'node:http';
import { routeData, type ApiPaths } from './readers.js';
import { validateDelegateRequest } from './delegate.js';

export function createApiServer(paths?: ApiPaths) {
  return createServer(async (req, res) => {
    const url = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
    if (req.method !== 'GET' && req.method !== 'POST') { res.writeHead(405, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ error: 'method_not_allowed' })); return; }
    try {
      if (req.method === 'GET') {
        const data = routeData(url.pathname, paths);
        if (data === null) { res.writeHead(404, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ error: 'not_found', path: url.pathname })); return; }
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(data)); return;
      }
      if (url.pathname !== '/api/v1/delegate') { res.writeHead(404, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ error: 'not_found', path: url.pathname })); return; }
      let body = '';
      for await (const chunk of req) { body += chunk.toString(); if (body.length > 1024 * 1024) { res.writeHead(413, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ error: 'payload_too_large' })); return; } }
      const result = validateDelegateRequest(body);
      res.writeHead(result.status === 'accepted' ? 200 : 400, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(result));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ error: 'internal_error', message: error instanceof Error ? error.message : String(error) }));
    }
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.argv[2] ?? 8787);
  createApiServer().listen(port, '127.0.0.1', () => { console.log(`control-plane-api listening on http://127.0.0.1:${port}`); });
}
