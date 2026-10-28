import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sim'));sys.path.insert(0,str(ROOT/'tools'))
import engine, research, lab
assert engine.ENGINE_VERSION == '2026.10.29.1', 'Use the audited engine to reproduce its figures'
out=Path(sys.argv[1] if len(sys.argv)>1 else '/Volumes/Data/agent-scratch/u69-audit-reproduce').expanduser().resolve()
out.mkdir(parents=True, exist_ok=True)
original=engine.tick_world
captured=set()
def observe(world,events):
    original(world,events)
    day=world['eden']['day']
    if day in (3000,36000,60000) and day not in captured and world['eden']['part']==0:
        captured.add(day)
        folder=out/f'day-{day}';folder.mkdir(exist_ok=True)
        terrain={'eden_size':engine.EDEN_SIZE,'lagoon_size':engine.LAGOON_SIZE,'lagoon_iter':world['lagoon']['iteration'],'terrain':engine.terrain_of(world['lagoon'])}
        state=engine.summarize(world)
        records=[{'d':d,'y':d//engine.DAYS_PER_YEAR,'u':u,'t':t,'msg':msg} for d,u,t,msg in events]
        state.update(events=records[-500:],research=research.report(world),world=terrain,status={'catching_up':False,'behind_days':0,'fixture':True})
        (folder/'state.json').write_text(json.dumps(state,separators=(',',':')))
        (folder/'world.json').write_text(json.dumps(terrain,separators=(',',':')))
        (folder/'events.ndjson').write_text(''.join(json.dumps(e)+'\n' for e in records))
        engine.save_state(world,str(folder/'saved-world.json'))
        print('[fixture]',day,'pop',len(world['eden']['people']),len(world['lagoon']['people']),flush=True)
engine.tick_world=observe
sys.argv=['lab.py','--days','60000','--seed','69','--every','1800','--json',str(out/'arc-60000.json'),'--quiet']
lab.main()
