#!/usr/bin/env python3
import re, sys
from pathlib import Path
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

# Parse max-size argument
max_size = 10_000  # 10KB default for sensitive files
for arg in sys.argv[2:]:
    if arg.startswith('--max-size='):
        try:
            max_size = int(arg.split('=')[1])
        except ValueError:
            pass

patterns = {
    'github_token': re.compile(r'gh[opsu]_[A-Za-z0-9_]{20,}'),
    'neptune_token': re.compile(r'sk-[a-z]{2}[A-Z]{2}-[0-9a-f]{16}-[0-9]{4}-[a-f0-9]{12}-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'),
    'provider_key': re.compile(r'sk-[A-Za-z0-9_-]{30,}'),
    'google_key': re.compile(r'AIza[0-9A-Za-z_-]{20,}'),
    'private_key': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
}
allow = ('<REDACTED', 'example', 'EXAMPLE', 'placeholder', 'dummy', 'xxxx', 'fake')
findings = []
excluded_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build', '.next', 'coverage', 'test-results', 'playwright-report'}

for p in root.rglob('*'):
    if not p.is_file() or excluded_dirs.intersection(p.parts):
        continue
    try:
        if p.stat().st_size > max_size:
            continue
        text = p.read_text(errors='replace')
    except Exception:
        continue
    for name, pat in patterns.items():
        for m in pat.finditer(text):
            ctx = text[max(0, m.start()-80):m.end()+80]
            if any(a in ctx for a in allow):
                continue
            findings.append(f'{p.relative_to(root)}:{text.count(chr(10), 0, m.start())+1}:{name}')

if findings:
    print('Potential secret-like values found:')
    print('\n'.join(findings[:200]))
    sys.exit(1)
print('secret_scan: PASS')