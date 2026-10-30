"""Calendar-day exposure and one private deterministic trial per ovulation.

Single-exposed-day clinical-pregnancy benchmarks for O-5..O are .04, .13,
.08, .29, .27, .08 (Li et al. 2015; verified source in RESEARCH.md).
For multiple exposed days, MAX is an explicit most-fertile-exposure
approximation, NOT a proven bound or a fitted joint probability model.
Uniform 24..35-day cycles and their initial phase are illustrative priors.
Calendar bins are coarse: this is NOT a strict 120-hour sperm model.
"""
import random
from typing import Any, Dict, Iterable, List, Mapping, Optional

DAY_PROBABILITIES = {5:.04, 4:.13, 3:.08, 2:.29, 1:.27, 0:.08}
MIN_CYCLE = 24
MAX_CYCLE = 35
MAX_FATHERS_PER_DAY = 4


def migrate_person(p: Dict[str, Any]) -> None:
    """No cycle phase or exposure history is inferred, and no RNG is used."""
    p.setdefault('reproduction', None)
    state = p['reproduction']
    if state is not None:
        state.setdefault('next_ovulation', None)
        state.setdefault('cycle_index', 0)
        state.setdefault('last_evaluated', None)
        state.setdefault('exposures', [])


def _state(p: Dict[str, Any]) -> Dict[str, Any]:
    migrate_person(p)
    if p['reproduction'] is None:
        p['reproduction'] = {'next_ovulation':None, 'cycle_index':0,
                             'last_evaluated':None, 'exposures':[]}
    return p['reproduction']


def _rng(u: Mapping[str, Any], p: Mapping[str, Any], index: int, purpose: str) -> random.Random:
    """Private stream independent of actor order, global RNG and tick frequency."""
    seed = 'u69-reproduction-v1:{}:{}:{}:{}:{}'.format(u['seed'],u['iteration'],p['id'],index,purpose)
    return random.Random(seed)


def _prune(state: Dict[str, Any], day: int) -> None:
    state['exposures'] = [r for r in state['exposures'] if 0 <= day-r['day'] <= 5]


def record(u: Mapping[str, Any], frames: Iterable[Mapping[str, Any]]) -> int:
    """Ingest captured current-part mate facts; father's later status is irrelevant.

    The unit is a father/calendar-day record, not a part or social token.
    Distinct fathers are retained up to four/day. Same-part overflow is
    resolved canonically by father ID, an explicit bounded model convention.
    No current male pool, partner, action, competence or withdrawal is read.
    """
    day = u['day']
    tick = u.get('parts',day*4+u.get('part',0))
    dead = (u.get('_ctx') or {}).get('dead',[])
    live = {p['id']:p for p in u['people'] if p not in dead}
    for p in live.values():
        if p.get('reproduction') is not None:
            migrate_person(p)
            _prune(p['reproduction'],day)
    candidates = [f for f in frames if f and f.get('kind')=='mate' and f.get('part')==tick]
    candidates.sort(key=lambda f:(f.get('mother',-1),f.get('father',-1)))
    added = 0
    for frame in candidates:
        p = live.get(frame.get('mother'))
        if p is None or p.get('s')!='f' or p.get('due'):
            continue
        state = _state(p)
        father = frame['father']
        today = [r for r in state['exposures'] if r['day']==day]
        if any(r['father']==father for r in today) or len(today)>=MAX_FATHERS_PER_DAY:
            continue
        state['exposures'].append({'day':day,'father':father,'traits':list(frame['traits'])})
        state['exposures'].sort(key=lambda r:(r['day'],r['father']))
        added += 1
    return added


def chance(exposures: Iterable[Mapping[str, Any]], ovulation_day: int, modifier: float = 1.) -> float:
    """One cycle probability: maximum actual exposed-day benchmark, scaled once."""
    benchmark = max((DAY_PROBABILITIES.get(ovulation_day-r['day'],0.) for r in exposures),default=0.)
    factor = min(1.,max(0.,modifier))
    return benchmark*factor


def _schedule_next(u: Mapping[str, Any], p: Mapping[str, Any], state: Dict[str, Any], previous: int) -> None:
    state['cycle_index'] += 1
    state['next_ovulation'] = previous + _rng(u,p,state['cycle_index'],'cycle_length').randint(MIN_CYCLE,MAX_CYCLE)


def advance(u: Mapping[str, Any], p: Dict[str, Any], modifier: float = 1.) -> Optional[Dict[str, Any]]:
    """Process a live mother's cycle; only the ovulation day's NIGHT evaluates.

    Caller ingests that part's actual exposures first, then applies any returned
    pregnancy payload. Existing pregnancies clear the schedule/exposures without
    touching due, hereditary values, paternity or the prior cycle index.
    """
    migrate_person(p)
    age = u['day']-p.get('b',0)
    if p.get('s')!='f' or (not 16*360 <= age <= 45*360 and not p.get('due')):
        return None
    if not any(q is p for q in u['people']) or p in (u.get('_ctx') or {}).get('dead',[]):
        return None
    if p.get('due'):
        if p['reproduction'] is not None:
            p['reproduction']['next_ovulation'] = None
            p['reproduction']['exposures'] = []
        return None
    state = _state(p)
    day = u['day']
    _prune(state,day)
    if state['next_ovulation'] is None:
        phase_rng = _rng(u,p,state['cycle_index'],'initial_phase')
        length = phase_rng.randint(MIN_CYCLE,MAX_CYCLE)
        state['next_ovulation'] = day+phase_rng.randrange(length)
    # A deliberately skipped calendar cannot fabricate past pregnancy trials.
    while state['next_ovulation'] < day:
        _schedule_next(u,p,state,state['next_ovulation'])
    ovulation = state['next_ovulation']
    if u.get('part',0)!=3 or day!=ovulation or state['last_evaluated']==ovulation:
        return None
    state['last_evaluated'] = ovulation
    index = state['cycle_index']
    _schedule_next(u,p,state,ovulation)
    probability = chance(state['exposures'],ovulation,modifier)
    if probability<=0 or _rng(u,p,index,'conception').random()>=probability:
        return None
    benchmark = max(DAY_PROBABILITIES.get(ovulation-r['day'],0.) for r in state['exposures'])
    best = [r for r in state['exposures'] if DAY_PROBABILITIES.get(ovulation-r['day'],0.)==benchmark]
    father = _rng(u,p,index,'father').choice(best)
    return {'father':father['father'],'traits':list(father['traits']),
            'ovulation_day':ovulation,'chance':probability}
