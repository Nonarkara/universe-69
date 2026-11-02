"""One read-only progress observation of our own bounded lab; no RNG draws."""
import sys as _u69_sys
import os as _u69_os
import json as _u69_json
import random as _u69_random
_u69_before = _u69_random.getstate()
_u69_rows = []
for _u69_frame in _u69_sys._current_frames().values():
    while _u69_frame is not None:
        if _u69_frame.f_code.co_name == 'main' and _u69_frame.f_code.co_filename.endswith('/tools/lab.py'):
            _u69_world = _u69_frame.f_locals.get('world')
            if isinstance(_u69_world, dict) and 'eden' in _u69_world:
                _u69_rows.append({
                    'seed': _u69_world['seed'],
                    'worlds': {k: {'day': _u69_world[k]['day'],
                                    'part': _u69_world[k].get('part'),
                                    'population': len(_u69_world[k]['people']),
                                    'generation': _u69_world[k]['gen_max'],
                                    'iteration': _u69_world[k]['iteration']}
                               for k in ('eden', 'lagoon')}})
        _u69_frame = _u69_frame.f_back
assert _u69_random.getstate() == _u69_before
with open('/Volumes/Data/agent-scratch/u69-nov3-integration/progress-%s.json' % _u69_os.getpid(), 'w') as _u69_file:
    _u69_json.dump({'read_only': True, 'global_rng_unchanged': True, 'observations': _u69_rows}, _u69_file)
