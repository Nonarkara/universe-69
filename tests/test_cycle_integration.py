"""Whole-engine lifecycle boundaries for the private reproductive clock."""
import os
import random
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sim'))
import engine


class TestCycleIntegration(unittest.TestCase):
    def test_inactive_older_female_history_expires_without_any_new_mating(self):
        for kind, tick in [('eden', engine.tick_eden), ('lagoon', engine.tick_lagoon)]:
            with self.subTest(kind=kind):
                u = engine.genesis()[kind]
                u.update(day=100, part=1, parts=401)
                mother = next(p for p in u['people'] if p['s'] == 'f')
                mother['b'] = 100 - 46 * 360
                mother['reproduction'] = {'next_ovulation':None, 'cycle_index':7,
                    'last_evaluated':10, 'exposures':[{'day':0,'father':1,'traits':[.1,.2,.3]}]}
                for p in u['people']:
                    p.update(a=engine.A_REST, ad=100, tx=p['x'], ty=p['y'])
                rng = random.Random(10)
                with patch.object(rng,'random',return_value=.99):
                    tick(u,rng,[])
                self.assertEqual(mother['reproduction']['exposures'], [])
                self.assertIsNone(mother['reproduction']['next_ovulation'])
                self.assertEqual(mother['reproduction']['cycle_index'],7)
                self.assertEqual(mother['due'],0)

    def test_cycle_phase_exists_before_reproductive_discovery(self):
        for kind, tick in [('eden',engine.tick_eden),('lagoon',engine.tick_lagoon)]:
            with self.subTest(kind=kind):
                u=engine.genesis()[kind]
                self.assertTrue(u['innocent'])
                tick(u,random.Random(10),[])
                for p in u['people']:
                    if p['s']=='f':
                        self.assertIsNotNone(p['reproduction']['next_ovulation'])
                        self.assertEqual(p['reproduction']['exposures'],[])
                        self.assertEqual(p['due'],0)
