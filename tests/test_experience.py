"""Personal knowledge is earned locally, not read from distant world stock."""
import copy
import json
import os
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sim'))
import engine
import needs
from tests.scratch_space import scratch_root


class TestExperience(unittest.TestCase):
    def setUp(self):
        self.land = [[0]*32 for _ in range(32)]
        self.terrain = patch.object(engine, 'terrain_of', return_value=self.land)
        self.terrain.start()
        self.addCleanup(self.terrain.stop)
        self.p = engine.person(1, 'A', 'f', -18*360, 1, 10, 10)
        self.p.update(hun=20., ene=1., sol=1.)
        self.u = dict(kind='LAGOON', day=0, part=1, people=[self.p], tech=[],
                      settlements=[dict(x=10,y=10,store=0.,water=20.,mouths=1)],
                      sites=[dict(x=18,y=10,kind='plants',left=50.,max=50.),
                             dict(x=10,y=18,kind='plants',left=50.,max=50.)])

    def visit(self, p, site):
        p['x'],p['y'] = site['x'],site['y']
        needs.observe_sites(self.u,p)
        p['x'],p['y'] = 10,10

    def test_unseen_stock_is_not_a_known_destination(self):
        self.assertIsNone(needs.nearest_site(self.u,self.p,'plants',26)[0])
        self.assertEqual(self.p['experience']['sites'],[])

    def test_different_experience_changes_the_same_needs_decision(self):
        q=copy.deepcopy(self.p)
        self.visit(self.p,self.u['sites'][0]);self.visit(q,self.u['sites'][1])
        for p in (self.p,q):
            self.assertEqual(needs.assign(self.u,p,0,random.Random(5)),engine.A_FORAGE)
        self.assertEqual((self.p['tx'],self.p['ty']),(18,10))
        self.assertEqual((q['tx'],q['ty']),(10,18))

    def test_remote_depletion_does_not_update_belief_or_decision(self):
        self.visit(self.p,self.u['sites'][0])
        before=copy.deepcopy(self.p)
        needs.assign(self.u,self.p,0,random.Random(5))
        target=self.p['tx'],self.p['ty']
        self.u['sites'][0]['left']=0.
        q=copy.deepcopy(before)
        needs.assign(self.u,q,0,random.Random(5))
        self.assertEqual(target,(q['tx'],q['ty']))
        self.assertEqual(q['experience']['sites'][0]['left'],50.)

    def test_arrival_learns_empty_and_actual_meal_even_without_carry(self):
        s=self.u['sites'][0]
        self.p.update(x=s['x'],y=s['y'],a=engine.A_FORAGE)
        s['left']=4.
        self.assertEqual(needs.fulfil(self.u,self.p,0,random.Random(1),engine.A_FORAGE),0)
        entry=self.p['experience']['sites'][0]
        self.assertEqual(entry['gained'],4.)
        self.assertEqual(entry['visits'],1)
        self.assertEqual(entry['left'],0.)
        needs.fulfil(self.u,self.p,0,random.Random(1),engine.A_FORAGE)
        self.assertEqual(self.p['experience']['sites'][0]['gained'],0.)

    def test_memory_is_bounded_and_new_people_do_not_inherit_it(self):
        for i in range(needs.MEMORY_SITES+8):
            self.u['sites']=[dict(x=i%30+1,y=i//30+1,kind='plants',left=5.,max=10.)]
            self.visit(self.p,self.u['sites'][0])
        self.assertLessEqual(len(self.p['experience']['sites']),needs.MEMORY_SITES)
        json.dumps(self.p)
        baby=engine.person(2,'B','m',0,2,10,10)
        self.assertEqual(baby['experience']['sites'],[])
        self.assertIsNot(baby['experience'],self.p['experience'])

    def test_empty_memory_explores_local_dry_ground_without_site_knowledge(self):
        self.u['sites']=[]
        needs.assign(self.u,self.p,0,random.Random(5))
        self.assertEqual(self.p['a'],engine.A_WALK)
        distance=((self.p['tx']-10)**2+(self.p['ty']-10)**2)**.5
        self.assertGreater(distance,0)
        self.assertLessEqual(distance,needs.SIGHT)
        self.assertEqual(self.p['experience']['sites'],[])

    def test_legacy_defaults_are_independent_and_json_persistent(self):
        self.terrain.stop()
        w=engine.genesis()
        for u in (w['eden'],w['lagoon']):
            for p in u['people']:p.pop('experience',None)
        engine.migrate(w)
        a,b=w['lagoon']['people'][:2]
        a['experience']['sites'].append({'x':1,'y':2,'kind':'plants','left':1,'max':2,'seen_day':0})
        self.assertEqual(b['experience']['sites'],[])
        engine.migrate(w)  # normalize new provenance defaults before exact round-trip
        self.assertEqual(a['experience']['sites'][0]['origin'],a['id'])
        with tempfile.TemporaryDirectory(dir=scratch_root()) as d:
            path=os.path.join(d,'fixture.json');engine.save_state(w,path)
            self.assertEqual(engine.load_state(path)['lagoon']['people'][0]['experience'],a['experience'])
        self.terrain.start()

    def test_actual_empty_and_productive_attempts_change_the_next_choice(self):
        q=copy.deepcopy(self.p)
        for person, stocks in ((self.p,(0.,50.)),(q,(50.,0.))):
            for site,stock in zip(self.u['sites'],stocks):
                site['left']=stock
                person.update(x=site['x'],y=site['y'],a=engine.A_FORAGE)
                needs.fulfil(self.u,person,0,random.Random(1),engine.A_FORAGE)
            person.update(x=10,y=10,hun=20.,ene=1.,sol=1.,carry=0.)
        for site in self.u['sites']:site['left']=50.
        for person in (self.p,q):needs.assign(self.u,person,0,random.Random(5))
        self.assertEqual((self.p['tx'],self.p['ty']),(10,18))
        self.assertEqual((q['tx'],q['ty']),(18,10))

    def test_empty_remote_memory_can_be_rechecked_without_observing_regrowth(self):
        self.u['sites'][0]['left']=0.
        self.visit(self.p,self.u['sites'][0])
        self.assertIsNone(needs.nearest_site(self.u,self.p,'plants',26)[0])
        self.u['day']=8
        belief,_=needs.nearest_site(self.u,self.p,'plants',26)
        self.assertGreater(belief['left'],0.)
        self.assertEqual(self.p['experience']['sites'][0]['left'],0.)
        self.assertEqual(self.u['sites'][0]['left'],0.)

    def test_away_camp_stock_changes_do_not_telepathically_update_the_worker(self):
        needs.observe_sites(self.u,self.p)
        self.p.update(x=28,y=10)
        self.u['settlements'][0]['water']=0.
        self.assertEqual(needs.water_target(self.u,self.p),(10,10))
        self.assertEqual(self.p['experience']['camp']['water'],20.)

    def test_water_outcome_does_not_credit_drinking_a_previously_carried_load(self):
        s=dict(x=10,y=10,kind='water',left=20.,max=20.)
        self.u['sites']=[s]
        self.p.update(a=engine.A_DRINK,thirst=1.,carry_water=12.)
        needs.fulfil(self.u,self.p,0,random.Random(1),engine.A_DRINK)
        self.assertEqual(self.p['thirst'],0.)
        self.assertEqual(self.p['experience']['sites'][0]['gained'],1.)
        self.assertEqual(s['left'],19.)

    def test_empty_farm_is_still_a_work_target_and_tending_is_not_a_harvest(self):
        s=dict(x=10,y=10,kind='farm',left=0.,max=20.)
        self.u['sites']=[s]
        import skills
        for tech in ('fire','preservation','agriculture'):
            skills.invent(self.p,tech,0)
        self.p.update(a=engine.A_FARM)
        self.assertIsNotNone(needs._field_to_work(self.u,self.p,26))
        needs.fulfil(self.u,self.p,0,random.Random(1),engine.A_FARM)
        self.assertEqual(s['worked'],0)
        self.assertEqual(self.p['experience']['sites'][0]['gained'],0.)

    def test_urgent_scout_continues_a_trip_instead_of_retargeting_midway(self):
        self.u['sites']=[]
        self.u['settlements'][0]['water']=0.
        self.p.update(thirst=2.)
        target=needs.water_target(self.u,self.p)
        self.p.update(a=engine.A_DRINK,tx=target[0],ty=target[1])
        self.p['x']+=1
        self.assertEqual(needs.water_target(self.u,self.p),target)

    def test_unseen_party_target_cannot_override_a_persons_known_resource(self):
        self.visit(self.p,self.u['sites'][0])
        self.u['settlements'][0]['party']=dict(d=0,a=engine.A_FORAGE,x=10,y=18,n=1)
        needs.assign(self.u,self.p,0,random.Random(5))
        self.assertEqual((self.p['tx'],self.p['ty']),(18,10))

    def test_reseed_drops_personal_experience_but_keeps_the_existing_lesson_rule(self):
        self.terrain.stop()
        w=engine.genesis()
        for key,tick in (('eden',engine.tick_eden),('lagoon',engine.tick_lagoon)):
            u=w[key]
            u['people'][0]['experience']['sites'].append({'x':1,'y':1,'kind':'plants'})
            u['people']=[]
            u['cod']={'starvation':20}
            tick(u,random.Random(1),[])
            u['extinct_day']=u['day']-(engine.RESEED_YEARS*360+1)
            tick(u,random.Random(2),[])
            self.assertEqual(u['iteration'],2)
            self.assertTrue(all(p['experience']['sites']==[] for p in u['people']))
            self.assertEqual(u['lessons'],[] if key=='eden' else ['preserve'])
        self.terrain.start()

    def test_save_reload_preserves_the_next_decisions_and_world_trajectory(self):
        self.terrain.stop()
        w=engine.genesis()
        for _ in range(32):engine.tick_world(w,[])
        engine.migrate(w)  # normalize existing migration-only defaults on both branches
        with tempfile.TemporaryDirectory(dir=scratch_root()) as d:
            path=os.path.join(d,'fixture.json');engine.save_state(w,path)
            restored=engine.load_state(path)
        for _ in range(80):
            engine.tick_world(w,[]);engine.tick_world(restored,[])
        for key in ('eden','lagoon'):
            clean=lambda u:{k:v for k,v in u.items() if not k.startswith('_')}
            self.assertEqual(clean(w[key]),clean(restored[key]))
        self.terrain.start()

    def test_perception_updates_during_a_long_stint_not_only_when_choosing(self):
        self.p.update(x=17,y=10,a=engine.A_FORAGE,ad=40)
        needs.meters(self.u,self.p,0,random.Random(1),needs.CONDITIONS['LAGOON'])
        self.assertTrue(any(m['x']==18 for m in self.p['experience']['sites']))
        self.assertEqual(self.p['ad'],40)

class TestMaturation(unittest.TestCase):
    def test_decision_adapter_converts_years_to_the_minds_day_units(self):
        p=engine.person(1,'A','m',-22*360,1,10,10)
        p['ef']=.8
        self.assertAlmostEqual(needs._self_control(p,22),engine.minds.self_control(p,22*360))
        self.assertAlmostEqual(needs._self_control(p,16),engine.minds.self_control(p,16*360))

    def test_maturation_changes_fight_selection_under_the_same_crowding(self):
        p=engine.person(1,'A','m',-22*360,1,10,10)
        p.update(ef=.8,ag=.2,ene=1.,sol=1.,hun=0.,pu=.6,box=None,role=None)
        neighbors=[engine.person(i+2,'B','f',-22*360,1,10,10) for i in range(24)]
        u=dict(kind='EDEN',day=0,part=1,people=[p]+neighbors,sites=[],innocent=True)
        self.assertEqual(needs.assign(u,p,0,random.Random(5)),engine.A_WALK)
        p['b']=-16*360
        self.assertEqual(needs.assign(u,p,0,random.Random(5)),engine.A_FIGHT)

class TestPhysicalNursing(unittest.TestCase):
    def setUp(self):
        self.mother=engine.person(1,'M','f',-22*360,1,2,4)
        self.baby=engine.person(2,'B','m',-180,2,2,4)
        self.baby.update(mom=1,hun=8.,thirst=1.)
        self.u=dict(kind='LAGOON',day=0,people=[self.mother,self.baby],sites=[],settlements=[])
        terrain=patch.object(engine,'terrain_of',return_value=[[0]*20 for _ in range(20)])
        terrain.start()
        self.addCleanup(terrain.stop)

    def test_food_cannot_arrive_from_a_distant_mother(self):
        self.baby['x']=12
        self.assertEqual(needs.eat(self.u,self.baby),0.)
        self.assertEqual(self.mother['hun'],0.)

    def test_nearby_nursing_pays_the_mother_and_does_not_invent_a_site_visit(self):
        self.assertGreater(needs.eat(self.u,self.baby),0.)
        self.assertGreater(needs.drink(self.u,self.baby),0.)
        self.assertGreater(self.mother['hun'],0.)
        self.assertGreater(self.mother['thirst'],0.)
        self.assertEqual(self.baby['experience']['sites'],[])

    def test_milk_food_and_water_cannot_bridge_a_strait(self):
        land=[[2]*8 for _ in range(8)]
        land[4][2]=land[4][4]=0
        self.baby['x']=4
        with patch.object(engine,'terrain_of',return_value=land):
            self.assertEqual(needs.eat(self.u,self.baby),0.)
            self.assertEqual(needs.drink(self.u,self.baby),0.)
