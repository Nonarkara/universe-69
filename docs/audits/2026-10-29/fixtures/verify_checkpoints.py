"""Read raw laboratory saves without migration, so repairs cannot mask defects."""
from collections import Counter
import json
from pathlib import Path

root = Path(__file__).parent
paths = sorted(root.glob('day-*/saved-world.json'))
assert paths, 'No checkpoints to verify'
for path in paths:
    world = json.loads(path.read_text())
    for key in ('eden', 'lagoon'):
        u = world[key]
        people = u['people']
        ids = {p['id']: p for p in people}
        assert len(ids) == len(people), (path, key, 'duplicate IDs')
        assert all(p.get('p') is None or ids.get(p['p'], {}).get('p') == p['id'] for p in people), (path, key, 'dangling/asymmetric bond')
        assert u['parts'] == u['day'] * 4 + u['part'], (path, key, 'clock')
        if key == 'eden':
            actual = Counter(str(p['box']) for p in people if p.get('box') is not None and p['box'] >= 0)
            occupancy = u.get('box_occ', {})
            assert all(actual[k] == v for k, v in occupancy.items()), (path, key, 'ghost room')
            assert all(occupancy.get(k, 0) == v for k, v in actual.items()), (path, key, 'missing room claim')
            assert all(not r['who'] or r['who'] in ids for r in u.get('roles', [])), (path, key, 'dead role holder')
            assert all(p.get('role') is None or u['roles'][p['role']]['who'] == p['id'] for p in people), (path, key, 'role pointer')
        else:
            assert abs(u['store'] - sum(st.get('store', 0) for st in u['settlements'])) < 1e-6, (path, key, 'store total')
        for old, new in zip(u['census'], u['census'][1:]):
            assert new[1] - old[1] == new[2] - new[3], (path, key, 'census stock-flow', old[:4], new[:4])
        print('PASS', path.parent.name, key, 'engine', u['engine'], 'population', len(people), 'census rows', len(u['census']))
    print('PASS identity, reciprocal bonds, clock, room claims, living role holders, store totals, all adjacent census stock-flow')
