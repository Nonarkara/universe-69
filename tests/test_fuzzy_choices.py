"""Actual voluntary choices share needs while keeping modest personal variation."""
import copy
import json
import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sim'))
import engine
import needs


class FuzzyChoices(unittest.TestCase):
    def body(self, pid, hunger=2., energy=.5):
        p = engine.person(pid, 'P', 'm', -25*360, 1, 10, 10)
        p.update(a=engine.A_IDLE, ad=0, hun=hunger, ene=energy,
                 sol=1., box=0, role=None, tx=10, ty=10)
        return p

    def world(self, p):
        return dict(kind='EDEN', day=0, part=1, parts=1, people=[p],
                    innocent=True, ennui=0., sites=[], settlements=[],
                    fseed=69, iteration=1)

    def test_same_body_can_resolve_a_close_choice_differently_and_repeat_it(self):
        # Only identity differs; both have the same feasible food and rest.
        choices = []
        for pid in (1, 2):
            p = self.body(pid)
            u = self.world(p)
            reloaded = json.loads(json.dumps(u))
            original = copy.deepcopy(u)
            choices.append(needs.assign(u, p, 0, random.Random(5)))
            self.assertEqual(choices[-1], needs.assign(
                reloaded, reloaded['people'][0], 0, random.Random(5)))
            self.assertEqual(u, reloaded)
            self.assertEqual(original['people'][0]['hun'], p['hun'])
        self.assertEqual(choices, [engine.A_SLEEP, engine.A_EAT])

    def test_extreme_hunger_wins_for_every_personal_profile(self):
        for pid in range(1, 65):
            p = self.body(pid, hunger=20., energy=.5)
            self.assertEqual(needs.assign(self.world(p), p, 0, random.Random(5)), engine.A_EAT)

    def test_extreme_fatigue_with_a_fed_body_wins_for_every_profile(self):
        for pid in range(1, 65):
            p = self.body(pid, hunger=0., energy=.05)
            self.assertEqual(needs.assign(self.world(p), p, 0, random.Random(5)), engine.A_SLEEP)

