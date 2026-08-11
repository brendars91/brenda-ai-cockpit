#!/usr/bin/env python3
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []
manifest = json.loads((root / 'source_manifest.json').read_text())
for item in manifest:
    path = root / item['path']
    if not path.exists(): errors.append(f"missing source import: {item['path']}")
    elif len([p for p in path.rglob('*') if p.is_file()]) < 1: errors.append(f"empty source import: {item['path']}")
required_docs = ['README.md', 'docs/PRODUCT_SPEC.md', 'docs/ARCHITECTURE.md', 'docs/MIGRATION_ROADMAP.md', 'governance/DELETION_CANDIDATES.md']
for required in required_docs:
    if not (root / required).exists(): errors.append(f"missing required doc: {required}")
required_workspaces = ['packages/contracts', 'packages/context-fabric', 'packages/capability-registry', 'packages/policy', 'packages/quota-governor', 'packages/telemetry', 'packages/telemetry-reader', 'packages/intelligence', 'packages/adapters', 'apps/cockpit-ui', 'apps/control-plane-api', 'apps/agent-runtime-console']
for workspace in required_workspaces:
    package_json = root / workspace / 'package.json'
    if not package_json.exists():
        errors.append(f"missing workspace package.json: {workspace}")
        continue
    data = json.loads(package_json.read_text())
    scripts = data.get('scripts', {})
    for script in ['build', 'test']:
        value = scripts.get(script)
        if not value: errors.append(f"workspace {workspace} missing script: {script}")
        elif 'no test specified' in value.lower() or value.strip().startswith('echo '): errors.append(f"workspace {workspace} has non-real script: {script}")
workflow = root / '.github/workflows/deterministic-gates.yml'
if not workflow.exists(): errors.append('missing deterministic-gates workflow')
else:
    text = workflow.read_text()
    for marker in ['npm ci', 'npm run verify', 'actions/setup-node']:
        if marker not in text: errors.append(f"deterministic-gates missing marker: {marker}")
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f"validate_repo: PASS ({len(manifest)} source imports, {len(required_workspaces)} workspaces)")
