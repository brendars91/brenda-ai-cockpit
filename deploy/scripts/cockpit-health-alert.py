#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import socket
import subprocess
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path('/home/ubuntu/brenda-ai-cockpit')
TOKEN_FILE = REPO / 'deploy/runtime/cockpit-token.txt'
HERMES_ENV = pathlib.Path('/home/ubuntu/.hermes') / ('.' + 'env')
DISCORD_API = 'https://discord.com/api/v10'


def run_ok(args: list[str]) -> bool:
    return subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def run_out(args: list[str]) -> str:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout


def load_env_file(path: pathlib.Path) -> dict[str, str]:
    values = dict(os.environ)
    if not path.exists():
        return values
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return values


def clean_discord_id(raw: str) -> str:
    if not raw:
        return ''
    return raw.split(',', 1)[0].strip().strip('[]').strip().strip('"').strip("'")


def discord_request(method: str, path: str, token: str, payload: dict) -> dict:
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DISCORD_API + path,
        data=body,
        method=method,
        headers={'Authorization': f'Bot {token}', 'Content-Type': 'application/json', 'User-Agent': 'brenda-ai-cockpit-alert/1.0'},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode('utf-8', errors='replace')
            return {'ok': 200 <= resp.status < 300, 'status': resp.status, 'data': json.loads(text) if text else {}}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode('utf-8', errors='replace')
        try:
            data = json.loads(text)
        except Exception:
            data = {'raw': text[:500]}
        return {'ok': False, 'status': exc.code, 'data': data}
    except Exception as exc:
        return {'ok': False, 'status': 0, 'data': {'error': f'{type(exc).__name__}: {exc}'}}


def send_discord_message(content: str) -> dict:
    env = load_env_file(HERMES_ENV)
    bot_token = env.get('DISCORD_BOT_TOKEN', '').strip()
    recipient_id = clean_discord_id(env.get('DISCORD_ALLOWED_USERS', ''))
    if not bot_token:
        return {'ok': False, 'error': 'DISCORD_BOT_TOKEN missing'}
    if not recipient_id:
        return {'ok': False, 'error': 'DISCORD_ALLOWED_USERS missing'}
    dm = discord_request('POST', '/users/@me/channels', bot_token, {'recipient_id': recipient_id})
    if not dm.get('ok'):
        return {'ok': False, 'step': 'create_dm_channel', 'discord_status': dm.get('status')}
    channel_id = dm.get('data', {}).get('id')
    if not channel_id:
        return {'ok': False, 'step': 'create_dm_channel', 'error': 'missing channel id'}
    sent = discord_request('POST', f'/channels/{channel_id}/messages', bot_token, {'content': content[:1900]})
    if not sent.get('ok'):
        return {'ok': False, 'step': 'send_message', 'discord_status': sent.get('status')}
    return {'ok': True, 'message_id': sent.get('data', {}).get('id'), 'delivered_to': 'DISCORD_ALLOWED_USERS[0]'}


def collect_alerts() -> list[str]:
    alerts: list[str] = []
    if not run_ok(['systemctl', 'is-active', '--quiet', 'brenda-ai-cockpit-api.service']):
        alerts.append('api service is not active')
    if not run_ok(['systemctl', 'is-enabled', '--quiet', 'brenda-ai-cockpit-api.service']):
        alerts.append('api service is not enabled')
    if not run_ok(['systemctl', 'is-active', '--quiet', 'brenda-ai-cockpit-ui.service']):
        alerts.append('ui service is not active')
    if not run_ok(['systemctl', 'is-enabled', '--quiet', 'brenda-ai-cockpit-ui.service']):
        alerts.append('ui service is not enabled')
    if not run_ok(['systemctl', 'is-active', '--quiet', 'brenda-ai-cockpit-health.timer']):
        alerts.append('health timer is not active')
    if not run_ok(['systemctl', 'is-enabled', '--quiet', 'brenda-ai-cockpit-health.timer']):
        alerts.append('health timer is not enabled')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex(('127.0.0.1', 8787)) != 0:
            alerts.append('api is not reachable on 127.0.0.1:8787')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex(('127.0.0.1', 8788)) != 0:
            alerts.append('ui is not reachable on 127.0.0.1:8788')
    serve = run_out(['tailscale', 'serve', 'status'])
    if 'https://gemini-arm-node-01.tail22d85a.ts.net:8787 (tailnet only)' not in serve:
        alerts.append('tailscale serve :8787 is missing or not tailnet-only')
    if 'https://gemini-arm-node-01.tail22d85a.ts.net:8788 (tailnet only)' not in serve:
        alerts.append('tailscale serve :8788 is missing or not tailnet-only')
    try:
        token = TOKEN_FILE.read_text(encoding='utf-8').strip()
        req = urllib.request.Request('http://127.0.0.1:8787/api/v1/audit', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as response:
            body = json.loads(response.read().decode('utf-8'))
        if body.get('chain_ok') is not True:
            alerts.append('audit chain is not OK')
    except Exception as exc:
        alerts.append(f'deep health failed: {type(exc).__name__}: {exc}')
    return alerts


def main() -> int:
    if '--test' in sys.argv:
        result = send_discord_message('✅ Brenda AI Cockpit alert channel test: Discord delivery works.')
        print(json.dumps({'test': True, **result}, ensure_ascii=False))
        return 0 if result.get('ok') else 1
    alerts = collect_alerts()
    if not alerts:
        return 0
    result = send_discord_message('🚨 Brenda AI Cockpit health alert\n' + '\n'.join(f'- {item}' for item in alerts))
    print(json.dumps({'alert_count': len(alerts), **result}, ensure_ascii=False))
    return 0 if result.get('ok') else 1


if __name__ == '__main__':
    raise SystemExit(main())
