"""Generate Linux amd64/Python 3.12 wheel hash lock from pip's actual resolution."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
report = json.loads((Path(__file__).parent / 'dependency-resolution.json').read_text(encoding='utf-8'))
lines = ['# Linux amd64, Python 3.12 wheel resolution; generated from dependency-resolution.json.']
for package in sorted(report['install'], key=lambda item: item['metadata']['name'].lower()):
    metadata = package['metadata']
    digest = package['download_info']['archive_info']['hashes']['sha256']
    lines.append(f"{metadata['name']}=={metadata['version']} --hash=sha256:{digest}")
(root / 'loadgen-requirements.lock').write_text('\n'.join(lines) + '\n')
print(f'LOCKED {len(report["install"])} packages')
