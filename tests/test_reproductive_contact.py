"""Actual exposed days, private cycle outcomes and enduring paternity."""
import copy
import json
import os
import random
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(__file__)),'sim'))
import engine
import encounters
import reproduction


class TestReproductiveContact(unittest.TestCase):
    def setUp(self):
        terrain=patch.object(engine,'terrain_of',return_value=[[0]*160 for _ in range(160)])
        terrain.start();self.addCleanup(terrain.stop)
        self.world=engine.genesis()
        self.u=self.world['lagoon']
        self.u.update(innocent=False,day=10,part=3,parts=43)
        self.father,self.mother=self.u['people'][:2]
        self.father.update(ef=.2,ag=.3,vg=.4)
        self.frame=self.capture()
        self.mother['reproduction']={'next_ovulation':10,'cycle_index':0,
                                     'last_evaluated':None,'exposures':[]}

    def capture(self):
        for person,x in ((self.father,20),(self.mother,21)):
            person.update(x=x,y=20,tx=x,ty=20,a=engine.A_REST,
                          hun=0.,thirst=0.,ene=1.,social=None)
        self.assertTrue(encounters.propose(self.u,self.father,self.mother,'mate',self.u['parts'],(20,20)))
        self.assertTrue(encounters.propose(self.u,self.mother,self.father,'mate',self.u['parts'],(21,20)))
        fact=encounters.capture(self.u,self.father,{p['id']:p for p in self.u['people']},
                                self.u['parts'],engine.terrain_of(self.u))
        self.assertIsNotNone(fact)
        return fact

    def conceive(self,frames=(),positive=True):
        # Force only a private outcome, never a probability of one or global trial.
        real_rng=reproduction._rng
        def private_rng(u,p,index,purpose):
            rng=real_rng(u,p,index,purpose)
            if purpose=='conception':rng.random=lambda:0. if positive else .99
            return rng
        rng=random.Random(3)
        with patch.object(reproduction,'_rng',side_effect=private_rng), \
             patch.object(rng,'random',return_value=.99) as clinical:
            engine.try_conceive(self.u,rng,[self.mother],contacts=frames)
        return clinical.call_count

    def test_remote_pair_without_capture_has_no_pregnancy(self):
        self.father['x']=100
        self.assertEqual(self.conceive(),0)
        self.assertEqual(self.mother['due'],0)

    def test_eden_has_no_ambient_male_pool(self):
        self.u['kind']='EDEN'
        self.assertEqual(self.conceive(),0)
        self.assertEqual(self.mother['due'],0)

    def test_actual_exposure_supplies_paternity_and_detached_traits(self):
        self.father['ef']=.99
        self.assertEqual(self.conceive([self.frame]),1)
        self.assertEqual(self.mother['due'],10+engine.GESTATION)
        self.assertEqual(self.mother['pregnancy_father'],self.father['id'])
        self.assertEqual(self.mother['fe'],[.2,.3,.4])
        self.frame['traits'][0]=.8
        self.assertEqual(self.mother['fe'],[.2,.3,.4])

    def test_stale_and_groom_facts_do_not_supply_exposure(self):
        for key,value in (('part',42),('kind','groom')):
            with self.subTest(key=key):
                self.assertEqual(self.conceive([dict(self.frame,**{key:value})]),0)
                self.assertEqual(self.mother['reproduction']['exposures'],[])

    def test_sleep_withdrawal_and_boarding_before_capture_supply_nothing(self):
        for changes in ({'a':engine.A_SLEEP},{'w':True},{'ab':1}):
            before=copy.deepcopy(self.father);self.father.update(changes)
            fact=encounters.capture(self.u,self.father,{p['id']:p for p in self.u['people']},
                                    self.u['parts'],engine.terrain_of(self.u))
            self.assertIsNone(fact)
            self.assertEqual(self.conceive(),0)
            self.father.clear();self.father.update(before)

    def test_valid_exposure_survives_fathers_later_death(self):
        engine.remove_dead(self.u,[self.father])
        self.assertEqual(self.conceive([self.frame]),1)
        self.assertEqual(self.mother['pregnancy_father'],self.father['id'])
        self.assertEqual(self.mother['fe'],[.2,.3,.4])

    def test_later_withdrawal_or_departure_cannot_erase_exposure(self):
        for field in ('w','ab'):
            self.mother.update(due=0,pregnancy_father=None)
            self.mother['reproduction']={'next_ovulation':10,'cycle_index':0,
                                         'last_evaluated':None,'exposures':[]}
            self.father[field]=True
            self.assertEqual(self.conceive([self.frame]),1)
            self.assertEqual(self.mother['pregnancy_father'],self.father['id'])
            self.father[field]=False

    def test_dead_mother_cannot_ingest_or_advance(self):
        engine.remove_dead(self.u,[self.mother]);before=copy.deepcopy(self.mother)
        self.assertEqual(self.conceive([self.frame]),0)
        self.assertEqual(self.mother,before)

    def test_daily_duplicates_and_failed_cycle_evaluation_cannot_reroll(self):
        self.assertEqual(self.conceive([self.frame,self.frame],positive=False),0)
        state=copy.deepcopy(self.mother['reproduction'])
        self.assertEqual(len(state['exposures']),1)
        self.assertEqual(state['last_evaluated'],10)
        self.assertEqual(self.conceive([self.frame],positive=True),0)
        self.assertEqual(self.mother['due'],0)
        self.assertEqual(self.mother['reproduction'],state)

    def test_repeated_parts_collapse_but_another_exposed_day_is_distinct(self):
        self.u.update(part=0,parts=40)
        self.conceive([self.capture()])
        self.u.update(part=1,parts=41)
        self.conceive([self.capture()])
        self.assertEqual(len(self.mother['reproduction']['exposures']),1)
        self.u.update(day=11,part=0,parts=44)
        self.conceive([self.capture()])
        self.assertEqual([e['day'] for e in self.mother['reproduction']['exposures']],[10,11])

    def test_bonds_require_surviving_contact_and_are_separate_from_exposure(self):
        self.mother['p']=self.father['p']=None
        self.assertEqual(engine.reproductive_contacts(self.u,[]),[])
        self.assertIsNone(self.mother['p'])
        engine.reproductive_contacts(self.u,[self.frame])
        self.assertEqual(self.mother['p'],self.father['id'])
        self.assertEqual(self.father['p'],self.mother['id'])

    def test_eden_exposure_does_not_assign_permanent_bonds(self):
        self.u['kind']='EDEN';self.mother['p']=self.father['p']=None
        self.assertEqual(self.conceive([self.frame]),1)
        self.assertIsNone(self.mother['p']);self.assertIsNone(self.father['p'])

    def test_birth_keeps_actual_dad_after_partner_change_and_death(self):
        self.conceive([self.frame]);actual=self.father['id']
        self.mother['p']=None;engine.remove_dead(self.u,[self.father])
        due=self.mother['due']
        self.u.update(day=due,part=1,parts=due*4+1,people=[self.mother])
        self.mother.update(hun=0.,thirst=0.,a=engine.A_REST,ad=20,
                           tx=self.mother['x'],ty=self.mother['y'])
        rng=random.Random(4)
        with patch.object(rng,'random',return_value=.99),patch.object(engine.animals,'tick',return_value=[]):
            engine.tick_lagoon(self.u,rng,[])
        children=[p for p in self.u['people'] if p.get('mom')==self.mother['id']]
        self.assertEqual(len(children),1)
        self.assertEqual(children[0]['dad'],actual)
        self.assertIsNone(self.mother['pregnancy_father'])

    def test_migration_reload_invent_no_old_exposures_or_paternity(self):
        self.mother.update(due=270,fe=[.1,.2,.3])
        for u in (self.world['eden'],self.u):
            for p in u['people']:
                for key in ('dad','pregnancy_father','social','reproduction'):p.pop(key,None)
        engine.migrate(self.world)
        self.assertIsNone(self.mother['pregnancy_father'])
        self.assertIsNone(self.mother['reproduction'])
        self.assertEqual(self.mother['fe'],[.1,.2,.3])
        text=json.dumps(self.world,sort_keys=True)
        restored=json.loads(text);engine.migrate(restored)
        self.assertEqual(json.dumps(restored,sort_keys=True),text)

    def test_reload_after_failed_evaluation_does_not_reopen_cycle(self):
        self.conceive([self.frame],positive=False)
        state=copy.deepcopy(self.mother['reproduction'])
        restored=json.loads(json.dumps(self.world));engine.migrate(restored)
        self.u=restored['lagoon'];self.father,self.mother=self.u['people'][:2]
        self.assertEqual(self.conceive([self.frame],positive=True),0)
        self.assertEqual(self.mother['reproduction'],state)
        self.assertEqual(self.mother['due'],0)

    def test_founders_without_exposure_have_independent_empty_fields(self):
        for p in self.u['people'][2:]:
            for field in ('social','dad','pregnancy_father','reproduction'):
                self.assertIsNone(p[field])

    def test_grooming_benefits_only_completed_live_pair_once_daily(self):
        self.mother['sol']=self.father['sol']=0.
        engine.complete_social(self.u,[])
        self.assertEqual(self.mother['sol'],0.)
        frame={'kind':'groom','part':43,'ids':[self.mother['id'],self.father['id']]}
        engine.complete_social(self.u,[frame,frame])
        self.assertAlmostEqual(self.mother['sol'],.3)
        self.assertAlmostEqual(self.father['sol'],.3)
        engine.complete_social(self.u,[frame])
        self.assertAlmostEqual(self.mother['sol'],.3)
        self.u['people'].remove(self.father)
        engine.complete_social(self.u,[frame])
        self.assertAlmostEqual(self.mother['sol'],.3)

    def test_intimacy_requires_actual_live_contact(self):
        self.mother['intimacy']=self.father['intimacy']=1.
        engine.complete_social(self.u,[])
        self.assertEqual(self.mother['intimacy'],1.)
        engine.complete_social(self.u,[self.frame])
        self.assertEqual(self.mother['intimacy'],0.)
        self.assertEqual(self.father['intimacy'],0.)
        self.mother['intimacy']=1.;self.u['people'].remove(self.father)
        engine.complete_social(self.u,[self.frame])
        self.assertEqual(self.mother['intimacy'],1.)
