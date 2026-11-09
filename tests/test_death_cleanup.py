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
import encounters
import reproduction


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

    def test_plague_releases_claims_and_creates_no_unexposed_pregnancy(self):
        u = self.eden_pair()
        u['part'], u['std_years'], u['innocent'] = 1, 1, False
        rng = random.Random(1)
        with patch.object(engine, 'omen'), patch.object(rng, 'random', side_effect=[0.0, 1.0]):
            engine.tick_eden(u, rng, [])
        self.assert_released(u)
        self.assertEqual(u['cod'], {'plague': 1})
        self.assertEqual(u['people'][0]['due'],0)
        self.assertIsNone(u['people'][0]['pregnancy_father'])

    def test_a_prior_real_exposure_can_lead_to_pregnancy_after_fathers_plague_death(self):
        u=self.eden_pair()
        father,mother=u['people']
        u.update(day=0,part=3,parts=3,innocent=False)
        for p,x in ((father,20),(mother,21)):
            p.update(x=x,y=20,tx=x,ty=20,a=engine.A_REST,hun=0.,thirst=0.,ene=1.)
        encounters.propose(u,father,mother,'mate',3,(20,20))
        encounters.propose(u,mother,father,'mate',3,(21,20))
        fact=encounters.capture(u,father,{p['id']:p for p in u['people']},3)
        self.assertIsNotNone(fact)
        self.assertEqual(reproduction.record(u,[fact]),1)
        mother['reproduction']['next_ovulation']=1
        u.update(day=1,part=3,parts=7,std_years=1)
        rest(u)
        real_rng=reproduction._rng
        def private_rng(world,p,index,purpose):
            result=real_rng(world,p,index,purpose)
            if purpose=='conception':result.random=lambda:0.
            return result
        rng=random.Random(1)
        with patch.object(reproduction,'_rng',side_effect=private_rng), \
             patch.object(engine, 'omen'), \
             patch.object(rng,'random',side_effect=[0.,1.,.99]):
            engine.tick_eden(u,rng,[])
        self.assert_released(u)
        self.assertEqual(u['cod'],{'plague':1})
        self.assertEqual(mother['due'],1+engine.GESTATION)
        self.assertEqual(mother['pregnancy_father'],father['id'])

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

    def test_withdrawn_or_available_males_cannot_create_ambient_exposure(self):
        u = engine.genesis()['eden']
        u['part'], u['day'], u['innocent'] = 1, 1, False
        u['people'] = u['people'][:3]
        u['people'][2]['w'] = True
        rest(u)
        engine.tick_eden(u, random.Random(1), [])
        self.assertTrue(u['people'][2]['w'])
        self.assertEqual(u['people'][1]['due'],0)
        self.assertIsNone(u['people'][1]['pregnancy_father'])
        self.assertEqual(u['people'][1]['reproduction']['exposures'],[])


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

    def test_quarrel_trigger_scales_with_camp_hunger(self):
        # DESIGN.md: "too many young unmated men" already scaled aggression
        # by pairing status; it did not scale with whether anyone was fed.
        # A fixed roll of 0.001 sits between a fed camp's threshold (4.8e-4)
        # and a starving one's (1.44e-3), so only the hungry camp kills.
        u = population(4)
        p = u['people'][0]
        p['p'] = None
        with patch.object(engine.minds, 'aggression', return_value=1.0), \
             patch.object(engine.minds, 'self_control', return_value=0.0):
            rng = random.Random(1)
            with patch.object(rng, 'random', return_value=0.001):
                fed = engine.lagoon_violence(
                    u, p, engine.age_of(p, 0), u['people'],
                    {q['id']: q for q in u['people']}, {}, [], rng, [],
                    shortfall=0.0)
            self.assertFalse(fed)
            self.assertEqual(u['cod'], {})
            dead = []
            rng2 = random.Random(1)
            with patch.object(rng2, 'random', side_effect=[0.001, 0.0, 0.9, 0.9]), \
                 patch.object(rng2, 'sample', return_value=u['people'][1:]):
                engine.lagoon_violence(
                    u, p, engine.age_of(p, 0), u['people'],
                    {q['id']: q for q in u['people']}, {}, dead, rng2, [],
                    shortfall=1.0)
            self.assertEqual(len(dead), 1)
            self.assertEqual(u['cod'].get('violence'), 1)

    def test_quarrel_targets_a_rival_with_a_partner_over_a_random_neighbour(self):
        # An unpaired aggressor's quarrel used to fall on the first name in
        # an unweighted sample. It now prefers the candidate who has what
        # the aggressor does not: a partner (BOOKS.md "too many young
        # unmated men" read as status/mate rivalry, not anonymous murder).
        u = population(6)
        p, _, paired_rival, _, lone_bystander, _ = u['people']
        p['p'] = None
        lone_bystander['p'] = None
        rng = random.Random(1)
        dead = []
        # trigger roll (~0) fires regardless of shortfall; the weighted pick
        # (0.5 of a total weight of 4 = 1.0+3.0) lands past the unpaired
        # bystander's share (1.0) and into the paired rival's (3.0) — the
        # opposite of picking near[0], which would have been the bystander.
        with patch.object(engine.minds, 'aggression', return_value=1.0), \
             patch.object(engine.minds, 'self_control', return_value=0.0), \
             patch.object(rng, 'random', side_effect=[0.0, 0.5, 0.9, 0.9]), \
             patch.object(rng, 'sample', return_value=[lone_bystander, paired_rival]):
            engine.lagoon_violence(
                u, p, engine.age_of(p, 0), u['people'],
                {q['id']: q for q in u['people']}, {}, dead, rng, [],
                shortfall=0.0)
        self.assertEqual(dead, [paired_rival])

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
        with patch.object(engine.animals, 'tick', return_value=[]), patch.object(engine, 'lagoon_violence', return_value=False), patch.object(engine, 'omen'), patch.object(rng, 'random', side_effect=[0.5, 0.5, 0.5, 0.0]):
            engine.tick_lagoon(u, rng, [])
        self.assertEqual(u['births_y'], 1)
        self.assertEqual(u['deaths_y'], 1)
        self.assertEqual(u['births_y'] - u['deaths_y'], len(u['people']) - 2)
