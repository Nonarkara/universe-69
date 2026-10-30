"""Own social proposals and simultaneous completed mate/groom contact.

A proposal changes one person only. Callers score the recipient's own decision,
provide real terrain, and commit completed facts after removing casualties.
Frames are detached JSON facts captured at ONE instant before reassignment;
separate endpoint observations are never combined into imaginary contact.
"""
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import minds

ACTIONS = {'mate': minds.A_MATE, 'groom': minds.A_GROOM}
SIGHT = 6
CONTACT_SQUARED = 2  # adjacent, including a dry diagonal; no surveyed scale


def migrate_person(p: Dict[str, Any]) -> None:
    p.setdefault('social', None)


def close_family(p: Mapping[str, Any], q: Mapping[str, Any]) -> bool:
    """Only explicitly known parents/shared parents; no inferred genetics."""
    if p.get('id') in (q.get('mom'), q.get('dad')) or q.get('id') in (p.get('mom'), p.get('dad')):
        return True
    return any(p.get(key) is not None and p.get(key) == q.get(key) for key in ('mom', 'dad'))


def available(u: Mapping[str, Any], p: Mapping[str, Any], kind: str) -> bool:
    """Existing bodily limits; an offer cannot wake or commandeer a person."""
    if kind not in ACTIONS or p in (u.get('_ctx') or {}).get('dead', []):
        return False
    age = u.get('day', 0)-p.get('b', 0)
    if age < (16*360 if kind == 'mate' else 3*360):
        return False
    return (not p.get('w') and not p.get('ab') and p.get('c', True)
            and p.get('a') not in (minds.A_SLEEP, minds.A_BIRTH, minds.A_FIGHT, minds.A_TEND,
                                  minds.A_WITHDRAW, ACTIONS['groom' if kind == 'mate' else 'mate'])
            and p.get('hun', 0.) < 14. and p.get('thirst', 0.) < 1.
            and p.get('ene', 1.) >= .4 and p.get('inj', 0.) <= .45
            and not (p.get('due') and p['due'] <= u.get('day', 0)))


def _compatible(u: Mapping[str, Any], p: Mapping[str, Any], q: Mapping[str, Any], kind: str) -> bool:
    if p.get('id') == q.get('id') or not available(u, p, kind) or not available(u, q, kind):
        return False
    if kind == 'mate':
        if p.get('s') == q.get('s') or {p.get('s'), q.get('s')} != {'m', 'f'} or close_family(p, q):
            return False
        if u.get('kind') == 'LAGOON' and (p.get('p') not in (None, q['id']) or q.get('p') not in (None, p['id'])):
            return False
    return True


def _dry(u: Mapping[str, Any], p: Mapping[str, Any], q: Mapping[str, Any], terrain: Optional[Sequence]) -> bool:
    if u.get('kind') != 'LAGOON':
        return True
    if terrain is None:
        return False
    x,y = p['x'],p['y']
    dx,dy = q['x']-x,q['y']-y
    steps = max(abs(dx), abs(dy), 1)
    cells = [(round(x+dx*i/steps), round(y+dy*i/steps)) for i in range(steps+1)]
    if any(not (0 <= cy < len(terrain) and 0 <= cx < len(terrain[cy])) or terrain[cy][cx] == 2 for cx,cy in cells):
        return False
    return not any(ax != bx and ay != by and (terrain[ay][bx] == 2 or terrain[by][ax] == 2)
                   for (ax,ay),(bx,by) in zip(cells,cells[1:]))


def candidates(u: Mapping[str, Any], p: Mapping[str, Any], people: Iterable[Dict[str, Any]],
               kind: str, terrain: Optional[Sequence] = None) -> List[Dict[str, Any]]:
    """Actually visible available people; selection/desire remains the caller's."""
    return [q for q in people if _compatible(u,p,q,kind)
            and (q['x']-p['x'])**2+(q['y']-p['y'])**2 <= SIGHT*SIGHT and _dry(u,p,q,terrain)]


def offer(u: Mapping[str, Any], p: Mapping[str, Any], byid: Mapping[int, Dict[str, Any]],
          kind: str, terrain: Optional[Sequence] = None) -> Optional[Dict[str, Any]]:
    """A local incoming proposal is information, not acceptance."""
    for q in sorted(candidates(u,p,byid.values(),kind,terrain), key=lambda q:q['id']):
        goal = q.get('social')
        if goal and goal['kind'] == kind and goal['other'] == p['id'] and q.get('a') == ACTIONS[kind]:
            return q
    return None


def propose(u: Mapping[str, Any], p: Dict[str, Any], q: Mapping[str, Any], kind: str,
            part: int, target: Tuple[int, int]) -> bool:
    """Write ONLY the actor's intention/action/target; caller assigns duration.

    Recipient candidates must already have passed local terrain visibility via
    candidates/offer. capture independently rechecks actual contact terrain.
    """
    if not _compatible(u,p,q,kind) or (q['x']-p['x'])**2+(q['y']-p['y'])**2 > SIGHT*SIGHT:
        return False
    incoming = q.get('social')
    own = p.get('social')
    if incoming and incoming['kind'] == kind and incoming['other'] == p['id'] and q.get('a') == ACTIONS[kind]:
        token = list(incoming['token'])
    elif own and own['kind'] == kind and own['other'] == q['id'] and p.get('a') == ACTIONS[kind]:
        token = list(own['token'])
    else:
        token = [part, min(p['id'],q['id']), max(p['id'],q['id'])]
    p['social'] = {'kind':kind,'other':q['id'],'token':token,'target':list(target)}
    p['a'] = ACTIONS[kind]
    p['tx'],p['ty'] = target
    return True


def state(u: Mapping[str, Any], p: Mapping[str, Any], byid: Mapping[int, Dict[str, Any]],
          terrain: Optional[Sequence] = None) -> Optional[Dict[str, Any]]:
    """Active own intent for observers; this is not proof of completion."""
    goal = p.get('social')
    if not goal or goal.get('kind') not in ACTIONS or p.get('a') != ACTIONS[goal['kind']]:
        return None
    q = byid.get(goal['other'])
    if q is None or not _compatible(u,p,q,goal['kind']):
        return None
    other = q.get('social')
    mutual = bool(other and other['kind']==goal['kind'] and other['other']==p['id'] and other['token']==goal['token']
                  and q.get('a')==ACTIONS[goal['kind']])
    return {'kind':goal['kind'],'other':q['id'],'mutual':mutual}


def capture(u: Mapping[str, Any], p: Mapping[str, Any], byid: Mapping[int, Dict[str, Any]],
            part: int, terrain: Optional[Sequence] = None) -> Optional[Dict[str, Any]]:
    """Capture BOTH currently completed participants, never merge stale frames."""
    if byid.get(p['id']) is not p:
        return None
    goal = p.get('social')
    if not goal or goal.get('kind') not in ACTIONS:
        return None
    kind = goal['kind']
    q = byid.get(goal['other'])
    if q is None or not _compatible(u,p,q,kind):
        return None
    other = q.get('social')
    if (not other or other['kind'] != kind or other['other'] != p['id']
            or other['token'] != goal['token'] or goal['token'][0] > part):
        return None
    for actor,intent in ((p,goal),(q,other)):
        if (actor.get('a') != ACTIONS[kind] or (actor['x'],actor['y']) != (actor.get('tx'),actor.get('ty'))
                or [actor['x'],actor['y']] != intent['target']):
            return None
    if (q['x']-p['x'])**2+(q['y']-p['y'])**2 > CONTACT_SQUARED or not _dry(u,p,q,terrain):
        return None
    mother = p if p.get('s') == 'f' else q
    father = q if p.get('s') == 'f' else p
    return {'kind':kind,'part':part,'ids':sorted((p['id'],q['id'])),
            'token':list(goal['token']),
            'mother':mother['id'] if kind=='mate' else None,
            'father':father['id'] if kind=='mate' else None,
            'traits':[father.get(k,.5) for k in ('ef','ag','vg')] if kind=='mate' else None,
            'paired':p.get('p')==q['id'] and q.get('p')==p['id']}


def deduplicate(frames: Iterable[Optional[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Canonical same-part pair facts; caller also limits conception per mother."""
    unique = {}
    for frame in frames:
        if frame is not None:
            key = frame['part'],frame['kind'],tuple(frame['ids'])
            if key not in unique:
                unique[key] = frame
    return list(unique.values())
