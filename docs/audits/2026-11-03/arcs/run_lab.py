"""Observe standard bounded lab; no intervention, counters or RNG wrappers."""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time
ROOT = Path('/Volumes/Data/Projects/Universe69')
BASE = Path('/Volumes/Data/agent-scratch/u69-nov3-integration')
seed = int(sys.argv[1])
out = BASE / ('seed-' + str(seed))
out.mkdir(exist_ok=True)
def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'sim').glob('*.py')) + [ROOT / 'tools/lab.py']}
before = hashes()
sys.argv = [str(ROOT/'tools/lab.py'), '--seed', str(seed), '--days', '36000', '--json', str(out/'arc.json')]
start = time.monotonic()
runpy.run_path(str(ROOT/'tools/lab.py'), run_name='__main__')
report = dict(seed=seed, days=36000, seconds=round(time.monotonic()-start,3),
              python=sys.version, source_before=before, source_after=hashes(),
              sources_unchanged=before == hashes())
(out/'provenance.json').write_text(json.dumps(report, indent=2)+'\n')
assert report['sources_unchanged']
