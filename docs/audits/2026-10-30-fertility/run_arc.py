"""Read-only instrumentation around the shipped bounded lab, with no RNG draws."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time
ROOT = Path('/Volumes/Data/Projects/Universe69')
BASE = Path('/Volumes/Data/agent-scratch/u69-fertility')
SEED = int(sys.argv[1])
OUT = BASE / ('seed-' + str(SEED))
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT/'sim'))
import engine
import reproduction

def hashes():
    files = sorted((ROOT/'sim').glob('*.py'))+[ROOT/'tools/lab.py']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

before=hashes()
counts=Counter()
probability_sums=Counter()
original_record, original_advance, original_tick = reproduction.record, reproduction.advance, engine.tick_world
latest=[None]
known=set()
for key in ('EDEN','LAGOON'):
    for pid in range(1,17): known.add((key,1,pid))

def record(u,frames):
    added=original_record(u,frames)
    counts[(u['kind'],'father_day_records')]+=added
    return added

def advance(u,p,modifier=1.):
    prior=(p.get('reproduction') or {}).get('last_evaluated')
    payload=original_advance(u,p,modifier)
    state=p.get('reproduction') or {}
    if state.get('last_evaluated')!=prior and state.get('last_evaluated')==u['day']:
        q=reproduction.chance(state.get('exposures',[]),u['day'],modifier)
        counts[(u['kind'],'evaluated_cycles')]+=1
        counts[(u['kind'],'exposed_cycles')]+=q>0
        probability_sums[u['kind']]+=q
    if payload is not None:
        counts[(u['kind'],'clinical_allocations')]+=1
    return payload

def tick(world,events):
    result=original_tick(world,events)
    latest[0]=world
    for key in ('eden','lagoon'):
        u=world[key]
        for p in u['people']:
            identity=(u['kind'],u['iteration'],p['id'])
            if identity not in known:
                known.add(identity)
                if p['g']>1:
                    counts[(u['kind'],'newborn_records')]+=1
                    counts[(u['kind'],'newborn_records_with_father')]+=p.get('dad') is not None
    day=world['eden']['day']
    if world['eden'].get('part')==0 and day%360==0:
        (OUT/'progress.json').write_text(json.dumps({'day':day,'year':day//360,
            'elapsed':round(time.monotonic()-start,2),
            'worlds':{k:{'population':len(world[k]['people']),'generation':world[k]['gen_max'],
                'iteration':world[k]['iteration']} for k in ('eden','lagoon')}}))
    if world['eden'].get('part')==0 and day in (3600,9000):
        (OUT/('snapshot-'+str(day)+'.json')).write_text(json.dumps(engine.summarize(world)))
    return result

reproduction.record, reproduction.advance, engine.tick_world = record,advance,tick
sys.argv=[str(ROOT/'tools/lab.py'),'--days','36000','--seed',str(SEED),'--json',str(OUT/'arc.json')]
start=time.monotonic()
runpy.run_path(str(ROOT/'tools/lab.py'),run_name='__main__')
world=latest[0]
reproduction.record, reproduction.advance = original_record,original_advance
engine.save_state(world,str(OUT/'final-state.json'))
(OUT/'snapshot-final.json').write_text(json.dumps(engine.summarize(world)))
report={'engine':engine.ENGINE_VERSION,'python':sys.version,'seed':SEED,'days':36000,
        'seconds':round(time.monotonic()-start,3),'source_before':before,'source_after':hashes(),
        'sources_unchanged':before==hashes(),
        'counts':{f'{k[0]}:{k[1]}':v for k,v in sorted(counts.items())},
        'sum_cycle_probabilities':dict(probability_sums),'endpoint':{}}
for key in ('eden','lagoon'):
    u=world[key]
    report['endpoint'][key]={'population':len(u['people']),'iteration':u['iteration'],
        'max_generation':u['gen_max'],'peak':u['peak'],'extinct_day':u['extinct_day'],
        'living_known_fathers':sum(p.get('dad') is not None for p in u['people']),
        'pending_pregnancies':sum(bool(p.get('due')) for p in u['people']),
        'historical_discoveries':u.get('tech',[])}
(OUT/'provenance.json').write_text(json.dumps(report,indent=2)+'\n')
