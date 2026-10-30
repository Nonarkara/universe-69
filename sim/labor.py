"""Mother-only observable labour; delivery remains the engine's responsibility.

The one-day lead is an illustrative visibility interval, not a clinical
estimate. No helper is assigned and no new persistent labour field is needed.
"""
from minds import A_BIRTH


def prepare(u: dict, p: dict) -> bool:
    """Hold a due mother at her actual dry position, without moving anyone."""
    due = p.get('due', 0)
    day = u['day']
    if p.get('s') != 'f' or not due or p.get('mc') or not 0 <= due-day <= 1:
        return False

    from engine import days, terrain_of
    x, y = p['x'], p['y']
    if u['kind'] == 'LAGOON':
        terr = terrain_of(u)
        if not (0 <= y < len(terr) and 0 <= x < len(terr[y])) or terr[y][x] == 2:
            return False

    p['a'], p['ad'] = A_BIRTH, days(1)
    p['tx'], p['ty'] = x, y
    for goal in ('social', 'learning', 'teaching'):
        if goal in p:
            p[goal] = None
    p.pop('was', None)
    p.pop('slept', None)
    return True
