#!/usr/bin/env python3
from __future__ import annotations

import argparse
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path('/home/ubuntu/brenda-ai-cockpit/apps/cockpit-ui/dist').resolve()


class StaticSpaHandler(BaseHTTPRequestHandler):
    server_version = 'brenda-ai-cockpit-ui/1.0'

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == '/healthz':
            self._send_bytes(200, b'{"ok":true,"service":"brenda-ai-cockpit-ui"}\n', 'application/json; charset=utf-8')
            return
        rel = unquote(parsed.path.lstrip('/'))
        candidate = (ROOT / rel).resolve() if rel else ROOT / 'index.html'
        if not str(candidate).startswith(str(ROOT)):
            self._send_bytes(403, b'forbidden\n', 'text/plain; charset=utf-8')
            return
        if candidate.is_dir():
            candidate = candidate / 'index.html'
        if not candidate.exists() or not candidate.is_file():
            candidate = ROOT / 'index.html'
        content_type = mimetypes.guess_type(candidate.name)[0] or 'application/octet-stream'
        self._send_bytes(200, candidate.read_bytes(), content_type)

    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store' if self.path == '/healthz' else 'public, max-age=300')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print('%s - %s' % (self.address_string(), format % args), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8788)
    args = parser.parse_args()
    if args.host in {'0.0.0.0', '::'}:
        raise SystemExit('refusing public bind for cockpit UI')
    if not (ROOT / 'index.html').exists():
        raise SystemExit(f'missing UI build: {ROOT / "index.html"}')
    server = ThreadingHTTPServer((args.host, args.port), StaticSpaHandler)
    print(f'cockpit-ui listening on http://{args.host}:{args.port}', flush=True)
    server.serve_forever()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
