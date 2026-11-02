"""Background camp routines cannot commandeer another explicit activity."""
import copy
import os
import random
import sys
import unittest
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(__file__)),'sim'))
import engine
import labor
import needs
import skills


class TestWatchAgency(unittest.TestCase):
    def setUp(self):
        self.u=engine.genesis(69)['lagoon']
        self.p,self.mother,self.guard=self.u['people'][:3]
        self.u.update(day=0,part=3,parts=3,people=[self.p,self.mother,self.guard])
        self.st=self.u['settlements'][0]
        for p in self.u['people']:
            p.update(x=self.st['x'],y=self.st['y'],tx=self.st['x'],ty=self.st['y'],
                     a=engine.A_REST,ad=8,hun=0.,thirst=0.,ene=1.,inj=0.,due=0,
                     social=None,learning=None,teaching=None)
        self.guard.update(a=engine.A_TALK,vg=1.)
        self.p['vg']=.1
        skills.invent(self.guard,'fire',0)

    def watch(self,part=3):
        engine.keep_watch(self.u,self.u['people'],0,[],part=part,rng=random.Random(0))

    def test_actual_prepared_labour_stays_at_its_own_position_and_target(self):
        self.mother.update(due=1,mc=False)
        self.assertTrue(labor.prepare(self.u,self.mother))
        before=copy.deepcopy(self.mother)
        self.watch()
        self.assertEqual(self.mother,before)
        self.assertEqual(self.st['watch'],self.guard['id'])

    def test_arrived_caregiver_is_not_selected_as_guard_or_retargeted(self):
        for part in (1,3):
            with self.subTest(part=part):
                self.setUp();self.p['a']=engine.A_TEND
                skills.invent(self.p,'fire',0)
                # Other guard is deliberately not eligible: no available guard
                # is preferable to stealing an arrived caregiver's body.
                self.guard['a']=engine.A_REST
                before=copy.deepcopy(self.p)
                self.watch(part)
                self.assertEqual(self.p,before)
                self.assertFalse(self.st['watch'])
        self.setUp();self.p['a']=engine.A_TEND;before=copy.deepcopy(self.p)
        self.watch()
        self.assertEqual(self.p,before)
        self.assertEqual(self.st['watch'],self.guard['id'])

    def test_explicit_bodily_social_work_goals_are_not_night_gathering_targets(self):
        acts=(engine.A_SLEEP,engine.A_REST,engine.A_EAT,engine.A_DRINK,
              engine.A_BIRTH,engine.A_TEND,engine.A_FIGHT,engine.A_RITE,
              engine.A_MATE,engine.A_GROOM,engine.A_WORK,engine.A_HUNT,
              engine.A_FORAGE,engine.A_FISH,engine.A_FARM,engine.A_BUILD,engine.A_SCOUT)
        for act in acts:
            with self.subTest(act=act):
                self.setUp();self.p.update(a=act,tx=self.p['x']+1,ty=self.p['y'])
                if act==engine.A_DRINK:self.p['thirst']=1.5
                before=copy.deepcopy(self.p)
                self.watch()
                self.assertEqual(self.p,before)
                self.assertEqual(self.st['watch'],self.guard['id'])

    def test_instruction_goal_survives_background_even_when_night_label_is_inactive(self):
        for key,goal in [('learning',{'teacher':2,'tech':'fire','x':1,'y':1,'started_part':0,'until_part':20}),
                         ('teaching',{'student':2,'tech':'fire','desired':'fire','until_part':20})]:
            with self.subTest(key=key):
                self.setUp();self.p.update(a=engine.A_TALK,tx=self.p['x']+1,ty=self.p['y'])
                self.p[key]=goal;skills.invent(self.p,'fire',0)
                self.assertIsNone(needs.instruction_state(self.u,self.p))
                self.guard['a']=engine.A_REST
                before=copy.deepcopy(self.p)
                self.watch()
                self.assertEqual(self.p,before)
                self.assertFalse(self.st['watch'])
                # A separate eligible guard must not cause gathering to
                # retarget the still-owned meeting either.
                self.guard['a']=engine.A_TALK
                self.watch()
                self.assertEqual(self.p,before)

    def test_eligible_awake_guard_and_uncommitted_camp_convergence_still_work(self):
        self.p['a']=engine.A_IDLE
        before=(self.p['tx'],self.p['ty'])
        self.watch()
        self.assertEqual(self.st['watch'],self.guard['id'])
        self.assertEqual(self.guard['a'],engine.A_WATCH)
        self.assertNotEqual((self.p['tx'],self.p['ty']),before)
        self.assertIn(self.p['a'],(engine.A_TALK,engine.A_SLEEP))
        fx,fy=self.st['x']+2,self.st['y']+1
        self.assertTrue(fx-2<=self.p['tx']<=fx+2 and fy-1<=self.p['ty']<=fy+2)

    def test_story_requires_actual_arrived_talk_and_lit_hearth(self):
        fx,fy=self.st['x']+2,self.st['y']+1
        self.p.update(x=fx+1,y=fy,tx=fx+1,ty=fy,a=engine.A_TALK)
        before=self.u.get('stories',0.)
        self.watch(part=1)
        self.assertEqual(self.u.get('stories',0.),before)
        self.st['fire_until']=100
        self.watch(part=1)
        self.assertGreater(self.u['stories'],before)

    def test_actual_independently_chosen_arrived_birth_helper_keeps_caring(self):
        self.mother.update(due=1,mc=False)
        labor.prepare(self.u,self.mother)
        self.st.update(store=500.,water=100.,mouths=3)
        skills.invent(self.p,'fire',0)
        needs.observe_sites(self.u,self.p)
        needs.assign(self.u,self.p,0,random.Random(0),needs.CONDITIONS['LAGOON'])
        self.assertEqual(self.p['a'],engine.A_TEND)
        self.assertTrue(engine.step_toward(self.p,engine.terrain_of(self.u),engine.LAGOON_WALK))
        self.assertTrue(needs.can_assist(self.u,self.p))
        before=copy.deepcopy(self.p)
        self.watch()
        self.assertEqual(self.p,before)
        self.assertEqual(self.st['watch'],self.guard['id'])
