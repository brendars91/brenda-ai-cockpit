#!/usr/bin/env python3
import json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'source_manifest.json').read_text())
errors=[]
for item in manifest:
    p=root/item['path']
    if not p.exists():
        errors.append(f"missing source import: {item['path']}")
for required in ['README.md','docs/PRODUCT_SPEC.md','docs/ARCHITECTURE.md','docs/MIGRATION_ROADMAP.md','governance/DELETION_CANDIDATES.md']:
    if not (root/required).exists():
        errors.append(f"missing required doc: {required}")
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'validate_repo: PASS ({len(manifest)} source imports)')
