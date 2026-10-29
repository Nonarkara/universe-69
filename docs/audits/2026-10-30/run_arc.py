"""Observe the standard lab harness without changing its trajectory or RNG."""
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1] if len(sys.argv)>1 else '/Volumes/Data/agent-scratch/u69-oct30-reproduce').expanduser().resolve()
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools'))
import lab
import engine
import research

print("[python]",sys.version,flush=True)
assert engine.ENGINE_VERSION == "2026.10.30.1", "Check out the audited engine to reproduce its figures"
original = engine.tick_world
last = -1
started = time.monotonic()

def observe(world,events):
    global last
    original(world,events)
    day = world['eden']['day']
    if world['eden']['part'] != 0 or day == last:
        return
    last = day
    if day % 1800 == 0:
        print('[checkpoint]', day, 'eden',len(world['eden']['people']),
              'lagoon',len(world['lagoon']['people']),
              'elapsed',round(time.monotonic()-started,1),flush=True)
    if day not in (3000,36000):
        return
    folder = OUT/('day-%d'%day)
    folder.mkdir(exist_ok=True)
    engine.save_state(world,str(folder/'saved-world.json'))
    terrain = {'eden_size':engine.EDEN_SIZE,'lagoon_size':engine.LAGOON_SIZE,
               'lagoon_iter':world['lagoon']['iteration'],
               'terrain':engine.terrain_of(world['lagoon'])}
    rows = [dict(d=d,y=d//engine.DAYS_PER_YEAR,u=u,t=t,msg=msg) for d,u,t,msg in events]
    snap = engine.summarize(world)
    snap.update(world=terrain,events=rows[-500:],research=research.report(world),
                status={'catching_up':False,'behind_days':0})
    (folder/'state.json').write_text(json.dumps(snap,separators=(',',':')))
    (folder/'world.json').write_text(json.dumps(terrain,separators=(',',':')))
    (folder/'events.ndjson').write_text('\n'.join(json.dumps(row) for row in rows))
    print('[fixture]',str(folder),flush=True)

engine.tick_world = observe
sys.argv = ['lab.py','--days','36000','--seed','69','--every','1800','--quiet',
            '--json',str(OUT/'arc-36000.json')]
lab.main()
print('[runtime]',round(time.monotonic()-started,3),'seconds; peak_rss_bytes',
      resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,flush=True)
