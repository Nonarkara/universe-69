"""Observable labour changes the mother, never a helper or delivery date."""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sim'))
import minds
import engine
import labor


class TestLabor(unittest.TestCase):
    def mother(self, **updates):
        p = {'id': 1, 's': 'f', 'due': 101, 'x': 3, 'y': 4,
             'hx': 15, 'hy': 16, 'a': minds.A_TALK, 'ad': 2,
             'tx': 7, 'ty': 8, 'social': {'other': 2},
             'learning': {'teacher': 2}, 'teaching': {'student': 3},
             'was': [minds.A_FORAGE, 8, 8, 10], 'slept': 1}
        p.update(updates)
        return p

    def test_only_mother_changes_and_stays_at_actual_position(self):
        p = self.mother()
        helper = {'id': 2, 'a': minds.A_DRINK, 'thirst': 2, 'x': 8, 'y': 8,
                  'tx': 9, 'ty': 9, 'ad': 12, 'learning': {'teacher': 9}}
        u = {'kind': 'EDEN', 'day': 100, 'people': [p, helper]}
        old_helper = copy.deepcopy(helper)
        before = copy.deepcopy(p)
        self.assertTrue(labor.prepare(u, p))
        self.assertEqual(helper, old_helper)
        self.assertEqual((p['x'], p['y'], p['tx'], p['ty']), (3, 4, 3, 4))
        self.assertEqual(p['a'], minds.A_BIRTH)
        self.assertGreater(p['ad'], 0)
        self.assertEqual({k: p[k] for k in ('due', 'hx', 'hy')},
                         {k: before[k] for k in ('due', 'hx', 'hy')})
        for key in ('social', 'learning', 'teaching'):
            self.assertIsNone(p[key])
        self.assertNotIn('was', p)
        self.assertNotIn('slept', p)

    def test_no_pregnancy_far_due_past_due_or_miscarriage_are_unchanged(self):
        for updates in ({'due': 0}, {'due': 102}, {'due': 99},
                        {'due': 101, 'mc': True}, {'s': 'm'}):
            with self.subTest(updates=updates):
                p = self.mother(**updates)
                before = copy.deepcopy(p)
                self.assertFalse(labor.prepare({'kind': 'EDEN', 'day': 100}, p))
                self.assertEqual(p, before)

    def test_due_today_is_observable_without_delivering_or_clearing_due(self):
        p = self.mother(due=100)
        u = {'kind': 'EDEN', 'day': 100, 'people': [p], 'born': 0}
        self.assertTrue(labor.prepare(u, p))
        self.assertEqual(p['due'], 100)
        self.assertEqual(u['born'], 0)
        self.assertEqual(len(u['people']), 1)

    def test_repeated_preparation_adds_no_persistent_labor_state(self):
        p = self.mother()
        u = {'kind': 'EDEN', 'day': 100}
        labor.prepare(u, p)
        before = copy.deepcopy(p)
        self.assertTrue(labor.prepare(u, p))
        self.assertEqual(p, before)
        self.assertFalse(any(k.startswith('labor') for k in p))

    def test_lagoon_water_or_offmap_position_does_not_teleport(self):
        u = engine.genesis(seed=69)['lagoon']
        u['day'] = 100
        terr = engine.terrain_of(u)
        water = next((x, y) for y, row in enumerate(terr) for x, tile in enumerate(row) if tile == 2)
        for x, y in (water, (-1, 0), (len(terr[0]), 0)):
            p = self.mother(x=x, y=y)
            before = copy.deepcopy(p)
            self.assertFalse(labor.prepare(u, p))
            self.assertEqual(p, before)

    def test_lagoon_actual_dry_tile_is_preserved_even_far_from_home(self):
        u = engine.genesis(seed=69)['lagoon']
        u['day'] = 100
        terr = engine.terrain_of(u)
        x, y = next((x, y) for y, row in enumerate(terr) for x, tile in enumerate(row) if tile != 2)
        p = self.mother(x=x, y=y)
        self.assertTrue(labor.prepare(u, p))
        self.assertEqual((p['x'], p['y'], p['tx'], p['ty']), (x, y, x, y))
