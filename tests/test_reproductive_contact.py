"""Pregnancy needs actual contact; paternity survives changes of social bond."""
import copy
import json
import os
import random
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sim'))
import engine


class TestReproductiveContact(unittest.TestCase):
    def setUp(self):
        self.world = engine.genesis()
        self.u = self.world['lagoon']
        self.u['innocent'] = False
        self.father, self.mother = self.u['people'][:2]
        self.frame = {'kind': 'mate', 'part': 0, 'mother': self.mother['id'],
                      'father': self.father['id'], 'traits': [.2, .3, .4]}

    def conceive(self, frames=()):
        # Force a successful trial and a surviving pregnancy. No rate calibration.
        rng = random.Random(3)
        with patch.object(rng, 'random', side_effect=[0., 1.]) as coin:
            engine.try_conceive(self.u, rng, [self.mother], 1., contacts=frames)
        return coin.call_count

    def test_remote_pair_has_no_trial(self):
        self.father['x'] = 100
        self.assertEqual(self.conceive(), 0)
        self.assertEqual(self.mother['due'], 0)

    def test_global_male_pool_without_contact_has_no_trial(self):
        self.u['kind'] = 'EDEN'
        rng = random.Random(3)
        with patch.object(rng, 'random') as coin:
            engine.try_conceive(self.u, rng, [self.mother], 1., require_pair=False,
                                males=[self.father])
        coin.assert_not_called()

    def test_actual_frame_supplies_paternity_and_frozen_traits(self):
        self.father['ef'] = .99
        self.assertEqual(self.conceive([self.frame]), 2)
        self.assertEqual(self.mother['due'], engine.GESTATION)
        self.assertEqual(self.mother['pregnancy_father'], self.father['id'])
        self.assertEqual(self.mother['fe'], [.2, .3, .4])
        self.frame['traits'][0] = .8
        self.assertEqual(self.mother['fe'], [.2, .3, .4])

    def test_stale_groom_and_dead_frames_do_not_draw(self):
        for field, value in [('part', -1), ('kind', 'groom'), ('father', 999)]:
            f = dict(self.frame, **{field: value})
            self.assertEqual(self.conceive([f]), 0)

    def test_withdrawal_and_departure_invalidate_resolution(self):
        for field in ('w', 'ab'):
            self.father[field] = True
            self.assertEqual(self.conceive([self.frame]), 0)
            self.father[field] = False

    def test_duplicate_frames_give_one_trial(self):
        self.assertEqual(self.conceive([self.frame, self.frame]), 2)

    def test_singles_bond_only_from_actual_contact(self):
        self.mother['p'] = self.father['p'] = None
        self.assertEqual(self.conceive(), 0)
        self.assertIsNone(self.mother['p'])
        self.conceive([self.frame])
        self.assertEqual(self.mother['p'], self.father['id'])
        self.assertEqual(self.father['p'], self.mother['id'])

    def test_eden_contact_does_not_assign_bonds(self):
        self.u['kind'] = 'EDEN'
        self.mother['p'] = self.father['p'] = None
        rng = random.Random(3)
        with patch.object(rng, 'random', side_effect=[0., 1.]):
            engine.try_conceive(self.u, rng, [self.mother], 1., require_pair=False,
                                contacts=[self.frame])
        self.assertIsNone(self.mother['p'])
        self.assertEqual(self.mother['pregnancy_father'], self.father['id'])

    def test_birth_keeps_actual_dad_after_partner_changes(self):
        self.conceive([self.frame])
        actual = self.father['id']
        self.mother['p'] = None
        self.u['day'], self.u['part'] = engine.GESTATION, 1
        self.u['parts'] = engine.GESTATION * 4 + 1
        self.u['people'] = [self.mother]
        self.mother['hun'], self.mother['thirst'] = 0., 0.
        self.mother['a'], self.mother['ad'] = engine.A_REST, 20
        self.mother['tx'], self.mother['ty'] = self.mother['x'], self.mother['y']
        rng = random.Random(4)
        with patch.object(rng, 'random', return_value=.99), \
             patch.object(engine.animals, 'tick', return_value=[]):
            engine.tick_lagoon(self.u, rng, [])
        children = [p for p in self.u['people'] if p.get('mom') == self.mother['id']]
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0]['dad'], actual)
        self.assertIsNone(self.mother['pregnancy_father'])

    def test_migration_does_not_invent_paternity_for_old_pregnancy(self):
        self.mother['due'], self.mother['fe'] = 270, [.1, .2, .3]
        for universe in (self.world['eden'], self.u):
            for p in universe['people']:
                for key in ('dad', 'pregnancy_father', 'social'):
                    p.pop(key, None)
        engine.migrate(self.world)
        self.assertIsNone(self.mother['pregnancy_father'])
        self.assertEqual(self.mother['fe'], [.1, .2, .3])
        serialized = json.dumps(self.world, sort_keys=True)
        restored = json.loads(serialized)
        engine.migrate(restored)
        self.assertEqual(json.dumps(restored, sort_keys=True), serialized)

    def test_newborn_and_founder_fields_are_independent(self):
        for p in self.u['people']:
            self.assertIsNone(p['social'])
            self.assertIsNone(p['dad'])
            self.assertIsNone(p['pregnancy_father'])

    def test_grooming_benefits_only_completed_live_pair_once_daily(self):
        self.mother['sol'] = self.father['sol'] = 0.
        engine.complete_social(self.u, [])
        self.assertEqual(self.mother['sol'], 0.)
        frame = {'kind':'groom', 'part':0, 'ids':[self.mother['id'],self.father['id']]}
        engine.complete_social(self.u, [frame, frame])
        self.assertAlmostEqual(self.mother['sol'], .3)
        self.assertAlmostEqual(self.father['sol'], .3)
        engine.complete_social(self.u, [frame])
        self.assertAlmostEqual(self.mother['sol'], .3)
        self.u['day'] += 1
        self.u['people'].remove(self.father)
        engine.complete_social(self.u, [frame])
        self.assertAlmostEqual(self.mother['sol'], .3)

    def test_intimacy_is_satisfied_only_by_actual_live_contact(self):
        self.mother['intimacy'] = self.father['intimacy'] = 1.
        engine.complete_social(self.u, [])
        self.assertEqual(self.mother['intimacy'], 1.)
        frame = dict(self.frame, ids=[self.mother['id'],self.father['id']])
        engine.complete_social(self.u, [frame])
        self.assertEqual(self.mother['intimacy'], 0.)
        self.assertEqual(self.father['intimacy'], 0.)
        self.mother['intimacy'] = 1.
        self.u['people'].remove(self.father)
        engine.complete_social(self.u, [frame])
        self.assertEqual(self.mother['intimacy'], 1.)
