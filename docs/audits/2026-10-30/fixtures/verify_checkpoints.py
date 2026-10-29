"""Inspect raw JSON without migration so repairs cannot hide invalid state."""
import json
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'sim'))
import engine
BASE = Path(__file__).resolve().parent
for day in (3000,36000):
    path = BASE/('day-%d'%day)/'saved-world.json'
    if not path.exists():
        continue
    w = json.loads(path.read_text())
    assert w['clock']['seconds'] == engine.SEC_PER_PART
    for name in ('eden','lagoon'):
        u = w[name]
        ids = {p['id'] for p in u['people']}
        byid = {p['id']:p for p in u['people']}
        assert len(ids) == len(u['people'])
        assert u['parts'] == u['day']*4+u['part']
        assert u['engine'] == '2026.10.30.1'
        for p in u['people']:
            assert p.get('p') is None or (p['p'] in ids and byid[p['p']]['p']==p['id'])
            assert p.get('carry_water',0) >= 0
            assert p.get('thirst',0) >= 0
        for a,b in zip(u['census'],u['census'][1:]):
            assert b[1]-a[1] == b[2]-b[3], (name,a,b)
        if name == 'eden':
            actual = {}
            for p in u['people']:
                box = p.get('box')
                if box is not None and box>=0:
                    actual[str(box)] = actual.get(str(box),0)+1
            assert all(v == actual.get(k,0) for k,v in u.get('box_occ',{}).items())
            assert all(u['box_occ'].get(k,0)==v for k,v in actual.items())
            for i,r in enumerate(u.get('roles',[])):
                assert not r['who'] or (r['who'] in ids and byid[r['who']].get('role')==i)
        else:
            terr = engine.terrain_of(u)
            assert math.isclose(u['store'],sum(st.get('store',0) for st in u['settlements']),abs_tol=1e-8)
            assert all(st.get('water',0)>=0 for st in u['settlements'])
            sites = [(s['x'],s['y'],s['kind']) for s in u['sites']]
            assert len(sites) == len(set(sites))
            for s in u['sites']:
                x,y = s['x'],s['y']
                assert 0 <= s['left'] <= s['max']
                assert terr[y][x] != 2
                if s['kind']=='fish':
                    assert any(terr[y+dy][x+dx]==2 for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
            assert any(s['kind']=='water' for s in u['sites'])
            assert len({a['i'] for a in u['animals']}) == len(u['animals'])
            for p in u['people']:
                if not p.get('ab'):
                    assert terr[p['y']][p['x']] != 2, p
            snap = json.loads((path.parent/'state.json').read_text())
            assert snap['u'][name]['climate'] == 'tropical'
            assert snap['u'][name]['season'] in ('monsoon','dry season')
            assert 'water' in snap['u'][name] and 'thirst' in snap['u'][name]
            assert all(row['y']==row['d']//360 for row in snap.get('events',[]))
        print('PASS raw day',day,name,'pop',len(u['people']),'census_rows',len(u['census']),flush=True)
print('PASS identity/bonds/clock/version/claims/roles/resourcebounds/shore/census stock-flow')
