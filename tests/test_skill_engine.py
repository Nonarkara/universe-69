"""Personal procedures and local public effects, without century forecasts."""
import copy
import os
import random
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(__file__)),'sim'))
import engine
import needs
import skills


def train(p, *targets):
    registry={name:parent for name,parent,_chance,_pop in skills.TECH_LADDER}
    def learn(name):
        if registry[name]:learn(registry[name])
        skills.invent(p,name,0)
    for target in targets:learn(target)


class TestSkillEngine(unittest.TestCase):
    def setUp(self):
        self.w=engine.genesis(69)
        self.u=self.w['lagoon']
        self.p=self.u['people'][0]
        self.st=self.u['settlements'][0]
        self.p.update(x=self.st['x'],y=self.st['y'],tx=self.st['x'],ty=self.st['y'],a=engine.A_TALK)

    def test_global_agriculture_does_not_shorten_nursing(self):
        self.u['tech']=['agriculture']
        engine.nurse(self.u,self.p,0)
        self.assertEqual(self.p['nurse_len'],3*360)
        self.st.update(farm_food=100.,mouths=16)
        engine.nurse(self.u,self.p,0)
        self.assertEqual(self.p['nurse_len'],2*360)

    def test_global_fire_does_not_create_watch_or_light(self):
        self.u['tech']=['fire']
        engine.keep_watch(self.u,self.u['people'],0,[],part=3,rng=random.Random(1))
        self.assertFalse(self.st.get('watch'))
        self.assertFalse(needs.fire_lit(self.u,self.st))

    def test_present_fire_learner_can_tend_watch_without_lighting_it_magically(self):
        skills.expose(self.p,'fire',0)
        engine.keep_watch(self.u,self.u['people'],0,[],part=3,rng=random.Random(1))
        self.assertEqual(self.st['watch'],self.p['id'])
        self.assertFalse(needs.fire_lit(self.u,self.st))

    def test_global_writing_and_granary_do_not_upgrade_local_organisation(self):
        self.u['tech']=['writing','granary']
        self.st['org']='tribe'
        self.u['people']=[dict(self.p,id=i+1) for i in range(300)]
        engine.organise(self.u,self.u['people'],random.Random(1),[])
        self.assertEqual(self.st['org'],'tribe')
        self.assertEqual(self.st['arb'],engine.ARBITER['tribe'])
        self.st['works']={'granary':needs.CRAFT_WORK['granary']}
        engine.organise(self.u,self.u['people'],random.Random(1),[])
        self.assertEqual(self.st['org'],'chiefdom')

    def test_global_lore_does_not_hold_a_rite(self):
        self.u['tech']=['lore']
        engine.hold_rites(self.u,self.u['people'],0.,random.Random(1),[])
        self.assertFalse(self.st.get('rites'))

    def test_living_local_storyteller_can_hold_a_physical_rite(self):
        train(self.p,'lore')
        self.p['a']=engine.A_TALK
        neighbor=self.u['people'][1]
        neighbor.update(x=self.p['x']+1,y=self.p['y'],a=engine.A_TALK)
        engine.hold_rites(self.u,self.u['people'],0.,random.Random(1),[])
        self.assertEqual(self.st.get('rites'),1)
        self.assertGreater(self.st.get('coh',0),0)

    def test_history_cannot_name_an_unqualified_inventor(self):
        self.u['tech']=['fire']
        self.u['people']=[self.p]
        with patch.object(engine,'TECH_LADDER',[('shelter','fire',1.,1)]):
            engine.discover_tech(self.u,random.Random(1),[],0.)
        self.assertFalse(skills.knows(self.p,'shelter'))

    def test_lost_historical_skill_can_be_rediscovered_personally(self):
        self.u['tech']=['fire']
        self.u['people']=[self.p]
        with patch.object(engine,'TECH_LADDER',[('fire',None,1.,1)]):
            engine.discover_tech(self.u,random.Random(1),[],0.)
        self.assertTrue(skills.qualified(self.p,'fire'))
        self.assertEqual(self.u['tech'],['fire'])

    def test_finished_boat_waits_for_a_present_qualified_operator(self):
        y=next(y for y in range(40,120) if engine.boatyard(self.u,y))
        x,_=engine.boatyard(self.u,y)
        boat={'x':x,'y':y,'work':engine.BOAT_WORK,'builders':[]}
        self.u['boat']=boat
        self.u['tech']=['seacraft']
        self.p.update(x=x,y=y)
        self.assertFalse(engine.launch(self.u,self.u['people'],boat,random.Random(1),[],0,0))
        self.assertNotIn('voyage',self.u)
        train(self.p,'seacraft')
        self.assertTrue(engine.launch(self.u,self.u['people'],boat,random.Random(1),[],0,0))
        self.assertEqual(self.u['voyage']['operator'],self.p['id'])
        self.assertTrue(self.p.get('ab'))

    def test_summary_uses_built_assets_not_discovery_history(self):
        self.u['tech']=[row[0] for row in skills.TECH_LADDER]
        snap=engine.summarize(self.w)['u']['lagoon']
        self.assertFalse(snap['camp_state'][0]['fire'])
        self.assertFalse(snap['camp_state'][0]['granary'])
        self.st['works']={'granary':needs.CRAFT_WORK['granary']}
        train(self.p,'granary','writing')
        self.p.update(a=engine.A_WORK,craft={'skill':'writing','x':self.p['x'],'y':self.p['y']},tx=self.p['x'],ty=self.p['y'])
        snap=engine.summarize(self.w)['u']['lagoon']
        self.assertTrue(snap['camp_state'][0]['granary'])
        self.assertEqual(snap['crafts'][str(self.p['id'])],'writing')

    def test_summary_rejects_stale_job_coordinates(self):
        train(self.p,'granary')
        self.p.update(a=engine.A_WORK,craft={'skill':'granary','x':1,'y':1})
        self.assertNotIn(str(self.p['id']),engine.summarize(self.w)['u']['lagoon']['crafts'])

    def test_elder_holder_prevents_false_lost_skill_rediscovery(self):
        self.p['b']=-70*360
        train(self.p,'fire')
        student=self.u['people'][1]
        student['a']=engine.A_TALK
        self.u['people']=[self.p,student]
        with patch.object(engine,'TECH_LADDER',[('fire',None,1.,1)]):
            engine.discover_tech(self.u,random.Random(1),[],0.)
        self.assertFalse(skills.knows(student,'fire'))

    def test_storm_destroys_the_same_fraction_of_stored_food_labels(self):
        self.u.update(day=360,part=0,parts=1440)
        self.st.update(store=100.,prepared=20.,farm_food=30.)
        for p in self.u['people']:
            p.update(a=engine.A_REST,ad=100,tx=p['x'],ty=p['y'])
        rng=random.Random(1)
        with patch.object(engine.animals,'tick',return_value=[]), patch.object(engine,'base_mortality',return_value=False), patch.object(engine,'lagoon_violence',return_value=False), patch.object(needs,'keep_stores'), patch.object(rng,'random',return_value=.01):
            engine.tick_lagoon(self.u,rng,[])
        self.assertEqual(self.st['store'],40.)
        self.assertEqual(self.st['prepared'],8.)
        self.assertEqual(self.st['farm_food'],12.)

    def test_remote_historical_builder_cannot_learn_completion(self):
        y=next(y for y in range(40,120) if engine.boatyard(self.u,y))
        x,_=engine.boatyard(self.u,y)
        train(self.p,'fishing','shelter')
        self.u['boat']={'x':x,'y':y,'work':engine.BOAT_WORK,'builders':[self.p['id']]}
        engine.finish_boat(self.u,self.u['people'],random.Random(1),[],0)
        self.assertFalse(skills.knows(self.p,'seacraft'))
        self.assertNotIn('voyage',self.u)
        self.assertFalse(self.u['boat'].get('completion_recorded',False))
        self.p.update(x=x,y=y,tx=x,ty=y,a=engine.A_BUILD)
        engine.finish_boat(self.u,self.u['people'],random.Random(1),[],0)
        self.assertTrue(skills.qualified(self.p,'seacraft'))
        self.assertEqual(self.u['voyage']['operator'],self.p['id'])

    def test_completed_finite_project_is_not_an_active_job(self):
        train(self.p,'granary')
        self.st['works']={'granary':needs.CRAFT_WORK['granary']}
        self.p.update(a=engine.A_WORK,craft={'skill':'granary','x':self.p['x'],'y':self.p['y']})
        self.assertEqual(engine.active_craft(self.u,self.p),'')

    def test_rite_cannot_include_a_listener_across_water(self):
        train(self.p,'lore')
        q=self.u['people'][1]
        self.u['people']=[self.p,q]
        self.st.update(x=2,y=4)
        self.p.update(x=2,y=4,a=engine.A_TALK)
        q.update(x=4,y=4,a=engine.A_TALK)
        terrain=[[0]*9 for _ in range(9)]
        for y in range(2,9):terrain[y][3]=2
        with patch.object(engine,'terrain_of',return_value=terrain):
            engine.hold_rites(self.u,self.u['people'],0.,random.Random(1),[])
        self.assertFalse(self.st.get('rites'))

    def test_watch_does_not_override_sleep_exhaustion_or_urgent_needs(self):
        train(self.p,'fire')
        self.u['people']=[self.p]
        self.st['fire_until']=100
        for changes in ({'a':engine.A_SLEEP}, {'a':engine.A_REST},
                        {'ene':.2}, {'hun':needs.HUNGRY}, {'thirst':1.}):
            self.p.update(a=engine.A_TALK,ene=1.,hun=0.,thirst=0.)
            self.p.update(changes)
            before=self.p['a']
            engine.keep_watch(self.u,[self.p],0,[],part=3,rng=random.Random(1))
            self.assertFalse(self.st['watch'],changes)
            self.assertEqual(self.p['a'],before,changes)

    def test_awake_guard_can_cover_a_sleeping_fire_expert(self):
        train(self.p,'fire')
        self.p['a']=engine.A_SLEEP
        q=self.u['people'][1]
        q.update(x=self.st['x'],y=self.st['y'],a=engine.A_TALK,ene=1.,hun=0.,thirst=0.)
        self.st['fire_until']=100
        engine.keep_watch(self.u,[self.p,q],0,[],part=3,rng=random.Random(1))
        self.assertEqual(self.st['watch'],q['id'])
        self.assertEqual(self.p['a'],engine.A_SLEEP)
