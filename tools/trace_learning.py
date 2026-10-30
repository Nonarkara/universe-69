"""Bounded LAGOON learning trace; wrappers observe and call original functions.

Captured demo witnesses/listeners are ATTEMPTS, not successful lesson delivery.
Acquisition transitions record actual successful grants. Public comparison omits
only summarize.wall, the wall-clock capture timestamp.

Writes a diagnostic report and verifies identical final JSON/public state against
an uninstrumented replay. Neither replay runs EDEN or uses wall-clock pacing.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import sys
import time
from collections import Counter
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sim'))
import engine
import minds
import needs
import skills

TARGETS = ('stone_tools', 'fishing')
PARENTS = {t: p for t, p, _, _ in skills.TECH_LADDER}
BLOCKED = (minds.A_SLEEP, minds.A_MATE, minds.A_BIRTH, minds.A_FIGHT)


def public_state(world):
    """Compare modeled public facts; exclude only wall-clock capture time."""
    state = engine.summarize(world)
    state.pop("wall")
    return state


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class Trace:
    def __init__(self, u):
        self.u = u
        self.counts = Counter()
        self.actions = {t: Counter() for t in TARGETS}
        self.transitions = []
        self.deaths = []
        self.max_holders = Counter()
        self.originals = []

    def count(self, tech, name, amount=1):
        self.counts[tech + ':' + name] += amount

    def transition(self, p, tech, source):
        self.transitions.append({'day': self.u['day'], 'part': self.u['part'],
                                 'iteration': self.u['iteration'], 'id': p['id'],
                                 'name': p['n'], 'tech': tech, 'source': source,
                                 'entry': dict(p['skills'][tech])})

    @contextmanager
    def installed(self):
        def wrap(module, name, factory):
            original = getattr(module, name)
            self.originals.append((module, name, original))
            setattr(module, name, factory(original))

        def acquisition(original):
            def observed(p, tech, *args, **kwargs):
                before = skills.level(p, tech)
                result = original(p, tech, *args, **kwargs)
                if result and skills.level(p, tech) != before:
                    self.transition(p, tech, original.__name__)
                    if tech in TARGETS:
                        self.count(tech, 'successful_' + p['skills'][tech]['basis'])
                return result
            return observed

        def work(original):
            def observed(u, p, tech, day, worked):
                if tech in TARGETS:
                    self.count(tech, 'work_calls')
                    if worked:
                        self.count(tech, 'real_work_calls')
                        if skills.can_teach(p, tech):
                            self.count(tech, 'teacher_work_calls')
                    before = len(u.get('_demos', []))
                result = original(u, p, tech, day, worked)
                if tech in TARGETS:
                    frames = u.get('_demos', [])[before:]
                    self.count(tech, 'demo_frames', len(frames))
                    self.count(tech, 'demo_witnesses', sum(len(ls) for _, ls in frames))
                return result
            return observed

        def frames(original):
            def observed(u, entries, *args, **kwargs):
                living = {p['id']: p for p in u['people'] if p not in (u.get('_ctx') or {}).get('dead', [])
                          and not p.get('w') and not p.get('ab')}
                terr = engine.terrain_of(u)
                for teacher, listeners in entries:
                    counted = set()
                    for listener in listeners:
                        request = listener.get('request')
                        requested = (teacher.get('topics') is None and request
                                     and request['teacher'] == teacher['id'])
                        topic = None
                        if requested:
                            topic = request['tech']
                            while topic in PARENTS and PARENTS[topic] and not skills.knows(listener, PARENTS[topic]):
                                topic = PARENTS[topic]
                        for tech in TARGETS:
                            if not skills.can_teach(teacher, tech):
                                continue
                            if teacher.get('topics') is not None and tech not in teacher['topics']:
                                continue
                            if requested and tech != topic:
                                continue
                            source = 'demo' if teacher.get('topics') is not None else 'requested' if requested else 'talk'
                            if (tech, source) not in counted:
                                self.count(tech, source + '_completed_frames')
                                counted.add((tech, source))
                            self.count(tech, source + '_listeners')
                            pid = listener['id']
                            if teacher['id'] not in living or pid not in living:
                                self.count(tech, source + '_dead_or_unavailable'); continue
                            if pid == teacher['id']:
                                continue
                            if living[pid].get('skill_day') == u['day']:
                                self.count(tech, source + '_daily_limit'); continue
                            if ((teacher['x']-listener['x'])**2 + (teacher['y']-listener['y'])**2 > needs.CONTACT_RADIUS**2
                                    or not needs.reachable_contact(terr, teacher, listener)):
                                self.count(tech, source + '_unreachable'); continue
                            if requested:
                                offer = teacher.get('offer')
                                if (not offer or offer.get('until_part', -1) < u.get('parts', 0)
                                        or offer['student'] != pid or offer['desired'] != request['tech']
                                        or offer['tech'] != tech or not skills.can_teach(teacher, request['tech'])):
                                    self.count(tech, source + '_invalid_offer'); continue
                            if skills.level(listener, tech) > 0:
                                self.count(tech, source + '_already_aware'); continue
                            parent = PARENTS[tech]
                            if parent and not skills.knows(listener, parent):
                                self.count(tech, source + '_missing_prerequisite'); continue
                            self.count(tech, source + '_eligible_unknown')
                return original(u, entries, *args, **kwargs)
            return observed

        wrap(skills, 'invent', acquisition)
        wrap(skills, 'expose', acquisition)
        wrap(needs, 'practice_work', work)
        wrap(needs, '_teach_frames', frames)
        try:
            yield
        finally:
            for module, name, original in reversed(self.originals):
                setattr(module, name, original)

    def sample(self):
        u = self.u
        for tech in TARGETS:
            holders = [p for p in u['people'] if skills.knows(p, tech)]
            self.max_holders[tech] = max(self.max_holders[tech], len(holders))
            for p in holders:
                self.count(tech, 'holder_parts')
                self.actions[tech][str(p.get('a'))] += 1
                if (p['x'], p['y']) == (p.get('tx'), p.get('ty')):
                    self.count(tech, 'holder_arrived_parts')
                for q in u['people']:
                    if (q is p or q.get('w') or q.get('ab') or engine.age_of(q, u['day']) < 3*360
                            or q.get('a') in BLOCKED):
                        continue
                    if ((q['x']-p['x'])**2+(q['y']-p['y'])**2 <= needs.CONTACT_RADIUS**2):
                        self.count(tech, 'nearby_awake_person_parts')
                        if needs.reachable_contact(engine.terrain_of(u), p, q):
                            self.count(tech, 'nearby_reachable_person_parts')
                            if not skills.knows(q, tech) and (not PARENTS[tech] or skills.knows(q, PARENTS[tech])):
                                self.count(tech, 'nearby_eligible_unknown_person_parts')


def run(initial, days, trace=None):
    world = copy.deepcopy(initial)
    u = world['lagoon']
    if trace:
        trace.u = u
    start = time.monotonic()
    events = []
    for step in range(days * engine.PARTS_PER_DAY):
        before = {p['id']: p for p in u['people']} if trace else {}
        prior_iter = u['iteration']
        # Exact tick_world RNG derivation, restricted to LAGOON.
        part = u.get('part', 0)
        rng = random.Random((u['seed'] << 20) ^ (u['day'] + 1) ^ u['iteration'] ^ (part * 7919))
        engine.tick_lagoon(u, rng, events)
        if trace:
            alive = {p['id'] for p in u['people']} if prior_iter == u['iteration'] else set()
            for pid, p in before.items():
                held = [t for t in TARGETS if skills.knows(p, t)]
                if pid not in alive and held:
                    trace.deaths.append({'day': u['day'], 'iteration': prior_iter, 'id': pid,
                                         'name': p['n'], 'skills': held, 'last_action': p.get('a')})
            trace.sample()
        if (step+1) % (360*4) == 0:
            print(('traced' if trace else 'plain'), 'year', (step+1)//(360*4), 'population', len(u['people']), flush=True)
    return world, events, time.monotonic()-start


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--years', type=int, default=30)
    parser.add_argument('--seed', type=int, default=69)
    parser.add_argument('--out', type=Path, default=Path('/Volumes/Data/agent-scratch/u69-apprenticeship'))
    args = parser.parse_args()
    if not 1 <= args.years <= 30:
        parser.error('--years must be between 1 and 30')
    args.out.mkdir(parents=True, exist_ok=True)
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (ROOT/'sim').glob('*.py')}
    initial = engine.genesis(args.seed)
    initial['clock']['epoch'] = 0  # identical shared baseline; tick_lagoon never reads it
    tracer = Trace(None)
    with tracer.installed():
        traced, traced_events, traced_time = run(initial, args.years*360, tracer)
    plain, plain_events, plain_time = run(initial, args.years*360)
    comparisons = {'raw_state_equal': traced == plain,
                   'raw_json_equal': digest(traced) == digest(plain),
                   'public_state_equal': public_state(traced) == public_state(plain),
                   'events_equal': traced_events == plain_events}
    report = {'engine': engine.ENGINE_VERSION, 'seed': args.seed, 'years': args.years,
              'scope': 'LAGOON only; exact tick_world RNG derivation; no EDEN ticks',
              'sources': sources, 'source_unchanged': all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in sources.items()),
              'comparison': comparisons, 'public_comparison_excludes': ['wall capture timestamp'],
              'raw_sha256': digest(plain),
              'seconds': {'traced': traced_time, 'plain': plain_time},
              'counter_semantics': {'channels': 'demo=observed work; requested=explicit requested verbal lesson; talk=incidental verbal contact',
                                    'demo_witnesses': 'Captured witness attempts, including rejected prerequisites/contact; not successful delivery',
                                    'demo_listeners': 'Same attempts when passed to actual teaching evaluation',
                                    'eligible_unknown': 'Diagnostic gate opportunity, not a guaranteed grant; offers may compete',
                                    'transitions': 'Actual successful skill grants through original invent/expose functions'},
              'counters': dict(sorted(tracer.counts.items())),
              'holder_actions': {t:dict(v) for t,v in tracer.actions.items()},
              'activity_codes': {str(getattr(minds,n)):n[2:].lower() for n in dir(minds) if n.startswith('A_')},
              'max_holders': dict(tracer.max_holders), 'transitions': tracer.transitions,
              'holder_deaths': tracer.deaths,
              'final': {'day': plain['lagoon']['day'], 'population': len(plain['lagoon']['people']),
                        'history': plain['lagoon']['tech']}}
    for name, value in [('report.json',report), ('traced-world.json',traced), ('plain-world.json',plain), ('events.json',plain_events)]:
        (args.out/name).write_text(json.dumps(value, indent=2))
    print(json.dumps(report, indent=2), flush=True)
    if not all(comparisons.values()) or not report['source_unchanged']:
        raise SystemExit('Trace comparison failed')


if __name__ == '__main__':
    main()
