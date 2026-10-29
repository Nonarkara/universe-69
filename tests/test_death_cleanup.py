"""Every casualty route releases social claims and counts one death."""
import copy
import json
import os
import random
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sim'))
import engine
import skills


def rest(u):
    for p in u['people']:
        p['a'], p['ad'] = engine.A_REST, 100
        p['tx'], p['ty'] = p['x'], p['y']


def population(n):
    u = engine.genesis()['lagoon']
    founders = u['people'][:]
    u['people'] = [dict(copy.deepcopy(founders[i % len(founders)]), id=i+1,
                        p=i+2 if i % 2 == 0 else i, n=f'P{i+1}') for i in range(n)]
    rest(u)
    return u


class TestClaims(unittest.TestCase):
    def eden_pair(self):
        u = engine.genesis()['eden']
        u['people'] = u['people'][:2]
        u['box_occ'] = {'0': 1, '1': 1}
        u['roles'] = [{'who': 1}]
        u['people'][0]['box'], u['people'][0]['role'] = 0, 0
        u['people'][1]['box'] = 1
        u['day'] = 1
        rest(u)
        return u

    def assert_released(self, u):
        self.assertEqual([p['id'] for p in u['people']], [2])
        self.assertEqual(u['box_occ'], {'0': 0, '1': 1})
        self.assertEqual(u['roles'][0]['who'], 0)
        self.assertIsNone(u['people'][0]['p'])
        self.assertFalse(u['_ctx']['am'])

    def test_ordinary_eden_death_releases_claims_and_bond(self):
        u = self.eden_pair()
        with patch.object(engine, 'base_mortality', side_effect=[True, False]):
            engine.tick_eden(u, random.Random(1), [])
        self.assert_released(u)
        self.assertEqual(u['cod'], {'age': 1})

    def test_plague_releases_claims_and_cannot_leave_a_dead_father(self):
        u = self.eden_pair()
        u['part'], u['std_years'], u['innocent'] = 1, 1, False
        rng = random.Random(1)
        with patch.object(rng, 'random', side_effect=[0.0, 1.0]), patch.object(engine, 'try_conceive') as conceive:
            engine.tick_eden(u, rng, [])
        self.assert_released(u)
        conceive.assert_not_called()
        self.assertEqual(u['cod'], {'plague': 1})

    def test_repeated_cleanup_does_not_remove_a_survivors_shared_room_claim(self):
        u = self.eden_pair()
        p, survivor = u["people"]
        survivor["box"] = 0
        u["box_occ"] = {"0": 2}
        engine.remove_dead(u, [p, p])
        engine.remove_dead(u, [p])
        self.assertEqual(u["box_occ"], {"0": 1})
        self.assertEqual(u["people"], [survivor])
        self.assertIsNone(survivor["p"])

    def test_withdrawal_breaks_the_bond_reciprocally(self):
        u = self.eden_pair()
        engine.withdraw(u, u['people'][0], random.Random(1))
        self.assertTrue(all(p['p'] is None for p in u['people']))

    def test_migration_repairs_ghost_claims_and_broken_bonds_idempotently(self):
        w = engine.genesis()
        u = w['eden']
        u['people'] = u['people'][:3]
        u['people'][0]['box'] = 0
        u['people'][1]['box'] = 0
        u['box_occ'] = {'0': 99, '1': 12, '2': 0}
        u['roles'] = [{'who': 999}]
        u['people'][0]['role'] = 0
        u['people'][0]['p'] = 999
        # P2 -> P1 is now one-sided; P3 -> missing P4 is dangling.
        engine.migrate(w)
        self.assertEqual(u['box_occ'], {'0': 2, '1': 0, '2': 0})
        self.assertTrue(all(p['p'] is None for p in u['people']))
        self.assertEqual(u['roles'][0]['who'], 0)
        self.assertIsNone(u['people'][0]['role'])
        before = json.dumps(w, sort_keys=True)
        engine.migrate(w)
        self.assertEqual(before, json.dumps(w, sort_keys=True))

    def test_eden_father_pool_excludes_living_withdrawn_males(self):
        u = engine.genesis()['eden']
        u['part'], u['day'], u['innocent'] = 1, 1, False
        u['people'] = u['people'][:3]
        u['people'][2]['w'] = True
        rest(u)
        with patch.object(engine, 'try_conceive') as conceive:
            engine.tick_eden(u, random.Random(1), [])
        self.assertEqual([p['id'] for p in conceive.call_args.kwargs['males']], [1])


class TestMassDeaths(unittest.TestCase):
    def test_epidemic_releases_bonds_and_discovery_uses_survivors(self):
        for min_pop in (35, 1):
            u = population(40)
            u['day'], u['part'], u['tech'] = 360, 0, ['domestication']
            for p in u['people']:
                p['ef'] = 1 if p['id'] % 2 else 0.1
            rng = random.Random(7)
            forced = [False]
            # Trigger the epidemic coin from actual local livestock exposure,
            # rather than the removed world-history capability check.
            class ExposedCamp(dict):
                def get(self, key, default=None):
                    if key == 'domestic': forced[0] = True
                    return super().get(key,default)
            u['settlements'][0]=ExposedCamp(u['settlements'][0],domestic=1)
            for person in u['people']:
                for tech in ('fire','shelter','lore'):
                    skills.invent(person,tech,0)
            def coin():
                if forced[0]:
                    forced[0] = False
                    return 0.0
                return 0.99
            def sample(values, n):
                return ([p for p in values if p['id'] % 2] if n > 5 else values)[:n]
            events = []
            with patch.object(rng, 'random', side_effect=coin), patch.object(rng, 'sample', side_effect=sample), patch.object(engine, 'base_mortality', return_value=False), patch.object(engine.animals, 'tick', return_value=[]), patch.object(engine, 'lagoon_violence', return_value=False), patch.object(engine, 'TECH_LADDER', [('writing', None, 1e6, min_pop)]):
                engine.tick_lagoon(u, rng, events)
            self.assertEqual(len(u['people']), 27)
            self.assertEqual(u['cod'].get('epidemic'), 13)
            self.assertTrue(all(p['p'] is None for p in u['people'] if p['id'] <= 26 and p['id'] % 2 == 0))
            self.assertEqual('writing' in u['tech'], min_pop == 1)
            if min_pop == 1:
                self.assertTrue(any(engine.TECH_LABEL['writing'] in msg and 'P2 discovers' in msg for _, _, _, msg in events))

    def test_feud_losses_release_living_partners(self):
        u = population(100)
        u['day'], u['part'] = 360, 0
        rng = random.Random(7)
        def sample(values, n):
            return sorted((p for p in values if p['id'] % 2), key=lambda p: p['id'])[:n]
        with patch.object(engine, 'terrain_of', return_value=[[0] * 160 for _ in range(160)]), patch.object(rng, 'random', return_value=0.99), patch.object(rng, 'sample', side_effect=sample), patch.object(engine, 'base_mortality', return_value=False), patch.object(engine.animals, 'tick', return_value=[]), patch.object(engine, 'lagoon_violence', return_value=False), patch.object(engine, 'TECH_LADDER', []):
            engine.tick_lagoon(u, rng, [])
        self.assertEqual(u['cod'].get('feud'), 2)
        self.assertEqual(len(u['people']), 98)
        self.assertTrue(all(p['p'] is None for p in u['people'] if p['id'] in (2, 4)))


class TestStagedDeathsAndBirths(unittest.TestCase):
    def test_revenge_does_not_kill_an_already_staged_casualty(self):
        u = population(2)
        p, target = u['people']
        p['gd'], p['gk'] = 1, target['id']
        dead = [target]
        rng = random.Random(1)
        with patch.object(rng, 'random', return_value=0):
            result = engine.lagoon_violence(u, p, engine.age_of(p, u['day']), u['people'], {q['id']: q for q in u['people']}, {}, dead, rng, [])
        self.assertFalse(result)
        self.assertEqual(dead, [target])
        self.assertEqual(u['cod'], {})
        self.assertEqual(p['gd'], 0)

    def test_exile_breaks_bonds_on_both_sides(self):
        u = population(4)
        u['settlements'][0]['arb'] = 1
        u['settlements'].append(dict(x=100, y=100, r=5, n='Other'))
        p, partner, victim, _ = u['people']
        rng = random.Random(1)
        dead = []
        with patch.object(rng, 'random', return_value=0), patch.object(rng, 'sample', return_value=[victim]):
            engine.lagoon_violence(u, p, engine.age_of(p, 0), u['people'], {q['id']: q for q in u['people']}, {}, dead, rng, [])
        self.assertEqual(p['st'], 1)
        self.assertIsNone(p['p'])
        self.assertIsNone(partner['p'])
        self.assertEqual(dead, [victim])

    def test_immediate_infant_loss_balances_births_and_deaths(self):
        u = engine.genesis()['eden']
        u['people'] = u['people'][:2]
        u['day'], u['part'] = 1, 1
        u['people'][1]['due'] = 1
        rest(u)
        with patch.object(engine, 'rearing', return_value=(1.0, 1.0)):
            engine.tick_eden(u, random.Random(1), [])
        self.assertEqual(u['births_y'], 1)
        self.assertEqual(u['deaths_y'], 1)
        self.assertEqual(u['births_y'] - u['deaths_y'], len(u['people']) - 2)

    def test_lagoon_infant_loss_balances_births_and_deaths(self):
        u = population(2)
        u['day'], u['part'] = 1, 1
        u['people'][1]['due'] = 1
        rng = random.Random(1)
        with patch.object(engine.animals, 'tick', return_value=[]), patch.object(engine, 'lagoon_violence', return_value=False), patch.object(rng, 'random', side_effect=[0.5, 0.5, 0.5, 0.0]):
            engine.tick_lagoon(u, rng, [])
        self.assertEqual(u['births_y'], 1)
        self.assertEqual(u['deaths_y'], 1)
        self.assertEqual(u['births_y'] - u['deaths_y'], len(u['people']) - 2)
