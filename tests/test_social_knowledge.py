"""Knowledge travels through completed local contacts, retaining provenance."""
import copy
import os
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sim'))
import engine
import needs
from tests.scratch_space import scratch_root


class TestSocialKnowledge(unittest.TestCase):
    def setUp(self):
        self.land=[[0]*40 for _ in range(40)]
        terrain=patch.object(engine,'terrain_of',return_value=self.land)
        terrain.start();self.addCleanup(terrain.stop)
        self.a=engine.person(1,'A','f',-18*360,1,10,10)
        self.b=engine.person(2,'B','m',-18*360,1,10,11)
        self.c=engine.person(3,'C','m',-18*360,1,10,12)
        for p in (self.a,self.b,self.c):p.update(a=engine.A_TALK,hun=20.,ene=1.,sol=1.)
        self.site=dict(x=18,y=10,kind='plants',left=50.,max=50.)
        self.u=dict(kind='LAGOON',day=0,part=1,people=[self.a,self.b,self.c],sites=[self.site],tech=[],
                    settlements=[dict(x=10,y=10,water=20.,store=0.,mouths=3)])
        self.a.update(x=18,y=10)
        needs.observe_sites(self.u,self.a)
        self.a.update(x=10,y=10)
        self.u['day']=10

    def contacts(self,*people):
        for p in people:p.update(tx=p['x'],ty=p['y'])
        return [needs.capture_contact(self.u,p) for p in people]

    def test_actual_contact_teaches_a_destination_without_changing_real_stock(self):
        before=copy.deepcopy(self.site)
        self.assertIsNone(needs.nearest_site(self.u,self.b,'plants',26)[0])
        needs.exchange(self.u,self.contacts(self.a,self.b))
        record=self.b['experience']['sites'][0]
        self.assertEqual((record['origin'],record['via'],record['seen_day'],record['heard_day']),(1,1,0,10))
        self.assertEqual(record['path'],[1,2])
        self.assertEqual(record['visits'],0)
        self.assertIsNone(record['gained'])
        needs.assign(self.u,self.b,10,random.Random(5))
        self.assertEqual((self.b['tx'],self.b['ty']),(18,10))
        self.assertEqual(self.site,before)

    def test_no_distant_or_across_water_contact(self):
        self.b.update(x=10,y=20)
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.assertEqual(self.b['experience']['sites'],[])
        self.b.update(x=10,y=12)
        self.land[11][10]=2
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.assertEqual(self.b['experience']['sites'],[])

    def test_deceased_or_withdrawn_speakers_cannot_transmit(self):
        contacts=self.contacts(self.a,self.b)
        self.u['people'].remove(self.a)
        needs.exchange(self.u,contacts)
        self.assertEqual(self.b['experience']['sites'],[])
        self.u['people'].append(self.a);self.a['w']=True
        needs.exchange(self.u,contacts)
        self.assertEqual(self.b['experience']['sites'],[])

    def test_one_phase_cannot_broadcast_through_a_contact_chain(self):
        self.a.update(x=10,y=8);self.b.update(x=10,y=12);self.c.update(x=10,y=16)
        needs.exchange(self.u,self.contacts(self.a,self.b,self.c))
        self.assertEqual(len(self.b['experience']['sites']),1)
        self.assertEqual(self.c['experience']['sites'],[])
        self.u['part']=2
        needs.exchange(self.u,self.contacts(self.b,self.c))
        record=self.c['experience']['sites'][0]
        self.assertEqual(record['path'],[1,2,3])
        self.assertEqual((record['seen_day'],record['heard_day'],record['via']),(0,10,2))

    def test_repetition_does_not_rejuvenate_or_increment_experience(self):
        needs.exchange(self.u,self.contacts(self.a,self.b))
        before=copy.deepcopy(self.b['experience']['sites'])
        self.u['day']=11
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.assertEqual(self.b['experience']['sites'],before)
        self.site['left']=0.
        self.b.update(x=18,y=10);needs.observe_sites(self.u,self.b)
        record=self.b['experience']['sites'][0]
        self.assertEqual(record['origin'],2)
        self.assertIsNone(record['via'])
        self.assertEqual(record['left'],0.)

    def test_no_target_selection_or_newborn_teaching(self):
        self.a['a']=engine.A_WALK
        self.assertIsNone(needs.capture_contact(self.u,self.a))
        self.a['a']=engine.A_TALK;self.a['b']=self.u['day']-100
        self.assertIsNone(needs.capture_contact(self.u,self.a))

    def test_report_is_detached_and_legacy_metadata_round_trips(self):
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.a['experience']['sites'][0]['left']=0.
        self.assertEqual(self.b['experience']['sites'][0]['left'],50.)
        w=engine.genesis();engine.migrate(w)
        p=w['lagoon']['people'][0]
        p['experience']['sites']=[dict(self.b['experience']['sites'][0])]
        with tempfile.TemporaryDirectory(dir=scratch_root()) as d:
            path=os.path.join(d,'state.json');engine.save_state(w,path)
            self.assertEqual(engine.load_state(path)['lagoon']['people'][0]['experience'],p['experience'])


    def test_import_uses_frozen_historical_facts_and_does_not_reward_the_body(self):
        contacts=self.contacts(self.a,self.b)
        meters=[(p['hun'],p['ene'],p['sol']) for p in self.u['people']]
        self.site['left']=0.
        self.a['experience']['sites'][0]['left']=0.
        needs.exchange(self.u,contacts)
        self.assertEqual(self.b['experience']['sites'][0]['left'],50.)
        self.assertEqual([(p['hun'],p['ene'],p['sol']) for p in self.u['people']],meters)
        self.assertEqual(self.site['left'],0.)

    def test_relocation_after_a_conversation_does_not_change_contact_geometry(self):
        self.b.update(x=10,y=20)
        far=self.contacts(self.a,self.b)
        self.b.update(x=10,y=11)
        needs.exchange(self.u,far)
        self.assertEqual(self.b['experience']['sites'],[])
        near=self.contacts(self.a,self.b)
        self.b.update(x=10,y=20)
        needs.exchange(self.u,near)
        self.assertEqual(len(self.b['experience']['sites']),1)

    def test_expired_and_maximum_hop_reports_do_not_spread(self):
        note=self.a['experience']['sites'][0]
        note['seen_day']=-100
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.assertEqual(self.b['experience']['sites'],[])
        note['seen_day']=0;note['path']=[9,8,7,1]
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.assertEqual(self.b['experience']['sites'],[])

    def test_incoming_capacity_does_not_evict_fresher_personal_knowledge(self):
        self.b['experience']['sites']=[dict(x=25+i,y=25,kind='plants',left=5.,max=5.,
            seen_day=10,origin=2,via=None,heard_day=None,path=[2],visits=1,gained=1.)
            for i in range(needs.MEMORY_SITES)]
        before=copy.deepcopy(self.b['experience']['sites'])
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.assertEqual(self.b['experience']['sites'],before)

    def test_sleep_and_unfinished_social_targets_are_not_contacts(self):
        self.a['a']=engine.A_SLEEP
        self.assertIsNone(needs.capture_contact(self.u,self.a))
        self.a.update(a=engine.A_TALK,tx=14,ty=10)
        self.assertIsNone(needs.capture_contact(self.u,self.a))

    def test_diagonal_water_corners_cannot_form_a_contact(self):
        self.land[:]=[[2]*40 for _ in range(40)]
        self.land[10][10]=self.land[11][11]=0
        self.b.update(x=11,y=11)
        needs.exchange(self.u,self.contacts(self.a,self.b))
        self.assertEqual(self.b['experience']['sites'],[])

class TestWorldContactIntegration(unittest.TestCase):
    def test_both_worlds_transmit_from_completed_social_actions(self):
        w=engine.genesis()
        for key in ('eden','lagoon'):
            u=w[key]
            needs.ensure_sites(u)
            a,b=u['people'][:2]
            home=a['x'],a['y']
            far=next(s for s in u['sites'] if (s['x']-home[0])**2+(s['y']-home[1])**2>144
                     and (key=='eden' or engine.same_land(engine.terrain_of(u),*home,s['x'],s['y'])))
            a.update(x=far['x'],y=far['y']);needs.observe_sites(u,a)
            for p in u['people']:
                p.update(a=engine.A_REST,ad=20,tx=p['x'],ty=p['y'])
            for p in (a,b):p.update(x=home[0],y=home[1],tx=home[0],ty=home[1],a=engine.A_TALK,ad=20)
            u.update(day=10,part=1,parts=41)
        engine.tick_world(w,[])
        for key in ('eden','lagoon'):
            a,b=w[key]['people'][:2]
            reports=[n for n in b['experience']['sites'] if n.get('via')==a['id']]
            self.assertTrue(reports,key)
            self.assertTrue(all(n['visits']==0 for n in reports))

    def test_hopper_observations_track_expanded_pen_positions(self):
        u=engine.genesis()['eden']
        needs.ensure_sites(u)
        u['size']=80
        needs.ensure_sites(u)
        self.assertEqual([(s['x'],s['y']) for s in u['sites']],list(engine.hoppers(u)))


class TestObserverHonesty(unittest.TestCase):
    def test_lab_memory_sampling_is_read_only(self):
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'tools/lab.py'
        spec=importlib.util.spec_from_file_location('u69_lab',path)
        lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
        w=engine.genesis();before=copy.deepcopy(w)
        sample=lab.sample(w['lagoon'],0)
        self.assertEqual(sample['knowledge']['reported_notes'],0)
        self.assertEqual(w,before)

    def test_postmortems_do_not_claim_proven_prevention_or_inevitability(self):
        w=engine.genesis()
        for key in ('eden','lagoon'):
            u=w[key];u['cod']={'starvation':10};events=[]
            engine.write_postmortem(u,events)
            text=' '.join(e[3] for e in events)
            self.assertNotIn('will not make this mistake',text)
            self.assertNotIn('Nothing within the walls',text)
            self.assertIn('hypothesis' if key=='lagoon' else 'does not establish',text)
