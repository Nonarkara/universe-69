"""Read-only instrumentation around the shipped bounded lab; no RNG or state edits."""
import collections
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time
ROOT = Path('/Volumes/Data/Projects/Universe69')
OUT = Path('/Volumes/Data/agent-scratch/u69-encounters')
sys.path.insert(0, str(ROOT / 'sim'))
import engine
import encounters

def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT/'sim').glob('*.py'))}

before = hashes()
original_capture = encounters.capture
original_tick = engine.tick_world
seen = set()
counts = collections.Counter()
latest = [None]

def capture(u, p, byid, part, terrain=None):
    frame = original_capture(u,p,byid,part,terrain)
    if frame:
        key = (u['kind'],u['iteration'],part,frame['kind'],tuple(frame['ids']))
        if key not in seen:
            seen.add(key)
            counts[(u['kind'],frame['kind'])] += 1
    return frame

def tick(world, events):
    result = original_tick(world,events)
    latest[0] = world
    return result

encounters.capture = capture
engine.tick_world = tick
sys.argv = [str(ROOT/'tools/lab.py'), '--days','36000','--seed','69','--json',str(OUT/'arc.json')]
start = time.monotonic()
runpy.run_path(str(ROOT/'tools/lab.py'), run_name='__main__')
world = latest[0]
encounters.capture = original_capture
# Save workbench fixtures solely under scratch, never the live data directory.
engine.save_state(world, str(OUT/'final-state.json'))
(OUT/'snapshot.json').write_text(json.dumps(engine.summarize(world)))
report = {'engine':engine.ENGINE_VERSION,'seed':69,'days':36000,
          'seconds':round(time.monotonic()-start,3), 'source_before':before,
          'source_after':hashes(),'sources_unchanged':before==hashes(),
          'contacts':{f'{k[0]}:{k[1]}':v for k,v in counts.items()},
          'endpoint':{}}
for key in ('eden','lagoon'):
    u=world[key]
    report['endpoint'][key] = {'population':len(u['people']),'iteration':u['iteration'],
        'known_fathers':sum(p.get('dad') is not None for p in u['people']),
        'pregnant':sum(bool(p.get('due')) for p in u['people']),
        'pregnancies_with_father':sum(p.get('due',0)>0 and p.get('pregnancy_father') is not None for p in u['people'])}
(OUT/'arc-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
