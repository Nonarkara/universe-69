"""A social invitation changes its author, never the recipient's own choice."""
import copy
import random
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sim'))
import engine
import encounters
import needs


class TestSocialChoices(unittest.TestCase):
    def setUp(self):
        self.land = [[0]*40 for _ in range(40)]
        terrain = patch.object(engine,'terrain_of',return_value=self.land)
        terrain.start()
        self.addCleanup(terrain.stop)
        self.p = engine.person(1,'A','m',-18*360,1,10,10)
        self.q = engine.person(2,'B','f',-18*360,1,12,10)
        for person in (self.p,self.q):
            person.update(a=engine.A_REST,ad=8,tx=person['x'],ty=person['y'],
                          hun=0.,thirst=0.,ene=1.,sol=1.,box=0,role=None)
        self.u = dict(kind='EDEN',day=0,part=1,parts=1,people=[self.p,self.q],
                      innocent=False,ennui=0.,sites=[],settlements=[])

    def choose(self,p):
        return needs.assign(self.u,p,self.u['day'],random.Random(5))

    def test_author_proposes_without_reassigning_the_recipient(self):
        recipient = copy.deepcopy(self.q)
        self.assertEqual(self.choose(self.p),engine.A_MATE)
        self.assertEqual(self.p['social']['other'],self.q['id'])
        self.assertEqual(self.q,recipient)
        self.assertIsNone(encounters.capture(self.u,self.p,{1:self.p,2:self.q},1))

    def test_recipient_independently_selects_a_reciprocal_meeting(self):
        self.choose(self.p)
        author = copy.deepcopy(self.p)
        self.assertEqual(self.choose(self.q),engine.A_MATE)
        self.assertEqual(self.p,author)
        self.assertEqual(self.p['social']['token'],self.q['social']['token'])
        for person in (self.p,self.q):
            while not engine.step_toward(person):
                pass
        frame = encounters.capture(self.u,self.p,{1:self.p,2:self.q},1)
        self.assertIsNotNone(frame)
        self.assertEqual(frame['ids'],[1,2])

    def test_hunger_can_refuse_a_visible_offer(self):
        self.choose(self.p)
        self.q['hun'] = 20.
        author = copy.deepcopy(self.p)
        self.assertEqual(self.choose(self.q),engine.A_EAT)
        self.assertIsNone(self.q.get('social'))
        self.assertEqual(self.p,author)

    def test_work_can_win_after_recipient_reopens_its_own_score(self):
        self.choose(self.p)
        self.q['role'] = 0
        author = copy.deepcopy(self.p)
        needs.update_social(self.u,self.q)
        self.assertEqual(self.q['a'],engine.A_REST)
        self.assertEqual(self.q['ad'],0)
        self.assertEqual(self.choose(self.q),engine.A_WORK)
        self.assertEqual(self.p,author)

    def test_a_post_holder_can_reopen_work_and_choose_its_own_high_need(self):
        self.choose(self.p)
        self.q.update(a=engine.A_WORK,role=0,ad=20,intimacy=1.)
        author = copy.deepcopy(self.p)
        needs.update_social(self.u,self.q)
        self.assertEqual(self.q['a'],engine.A_WORK)
        self.assertEqual(self.q['ad'],0)
        self.assertEqual(self.choose(self.q),engine.A_MATE)
        self.assertEqual(self.p,author)
        self.assertEqual(self.q['intimacy'],1.)

    def test_offer_cannot_wake_or_retarget_a_sleeping_recipient(self):
        self.choose(self.p)
        self.q.update(a=engine.A_SLEEP,ad=8,tx=15,ty=10)
        before = copy.deepcopy(self.q)
        needs.update_social(self.u,self.q)
        self.assertEqual(self.q,before)

    def test_thirst_injury_withdrawal_and_childhood_block_mating(self):
        for changes in ({'thirst':2.},{'inj':.8},{'w':True},{'b':-10*360},{'ab':1}):
            with self.subTest(changes=changes):
                before = copy.deepcopy(self.q)
                self.q.update(changes)
                self.choose(self.p)
                self.assertNotEqual(self.p['a'],engine.A_MATE)
                self.q.clear()
                self.q.update(before)

    def test_unpaired_lagoon_people_can_choose_without_an_assigned_bond(self):
        self.u.update(kind='LAGOON',resource_version=2)
        self.u['settlements'] = [dict(x=10,y=10,r=5,store=500.,water=100.,mouths=2)]
        self.assertEqual(self.choose(self.p),engine.A_MATE)
        self.assertIsNone(self.p['p'])
        self.assertIsNone(self.q['p'])
        self.assertEqual(self.choose(self.q),engine.A_MATE)
        self.assertEqual(self.p['social']['token'],self.q['social']['token'])

    def test_local_offer_cannot_cross_a_water_corner(self):
        self.u.update(kind='LAGOON',resource_version=2)
        self.u['settlements'] = [dict(x=10,y=10,r=5,store=500.,water=100.,mouths=2)]
        self.q.update(x=11,y=11,tx=11,ty=11)
        self.land[10][11] = self.land[11][10] = 2
        self.assertNotEqual(self.choose(self.p),engine.A_MATE)
        self.assertIsNone(self.p.get('social'))

    def test_non_social_choice_clears_only_ones_own_stale_offer(self):
        self.choose(self.p)
        author = copy.deepcopy(self.p)
        self.q['hun'] = 20.
        self.choose(self.q)
        self.assertIsNone(self.q.get('social'))
        self.assertEqual(self.p,author)
        needs.update_social(self.u,self.p)
        self.assertIsNone(self.p['social'])

    def test_one_way_grooming_label_grants_no_bilateral_reward(self):
        self.p['sol'] = self.q['sol'] = .2
        before = [p['sol'] for p in self.u['people']]
        needs.fulfil(self.u,self.p,0,random.Random(1),engine.A_GROOM)
        self.assertEqual([p['sol'] for p in self.u['people']],before)
        self.p.update(a=engine.A_GROOM,tx=self.p['x'],ty=self.p['y'])
        self.assertIsNone(needs.capture_contact(self.u,self.p))

    def test_only_actual_mutual_grooming_can_transmit_contact_knowledge(self):
        encounters.propose(self.u,self.p,self.q,'groom',1,(11,10))
        encounters.propose(self.u,self.q,self.p,'groom',1,(12,10))
        self.assertIsNone(needs.capture_contact(self.u,self.p))
        self.p['x'] = 11
        self.assertIsNotNone(needs.capture_contact(self.u,self.p))

    def test_visible_labor_can_be_chosen_without_commanding_the_mother(self):
        self.u.update(kind='LAGOON',resource_version=2,innocent=True)
        self.u['settlements'] = [dict(x=10,y=10,r=5,store=500.,water=100.,mouths=2)]
        self.q.update(a=engine.A_BIRTH,due=1)
        before = copy.deepcopy(self.q)
        self.assertEqual(self.choose(self.p),engine.A_TEND)
        self.assertEqual((self.p['tx'],self.p['ty']),(self.q['x'],self.q['y']))
        self.assertEqual(self.q,before)
        self.p['hun'] = 20.
        self.assertNotEqual(self.choose(self.p),engine.A_TEND)

    def test_helper_must_be_arrived_awake_and_not_urgently_exhausted(self):
        from tests.test_procedural_world import grant
        self.u.update(kind='LAGOON')
        self.u['settlements'] = [dict(x=10,y=10,r=5,store=500.,water=100.,mouths=2)]
        grant(self.p,'healing')
        self.p.update(a=engine.A_TEND,tx=10,ty=10)
        self.q.update(x=11,y=10,inj=.4)
        self.assertTrue(needs.healing_near(self.u,self.q))
        for changes in ({'a':engine.A_SLEEP},{'ene':.2},{'thirst':2.},{'tx':15}):
            before=copy.deepcopy(self.p)
            self.p.update(changes)
            self.assertFalse(needs.healing_near(self.u,self.q))
            self.p.clear();self.p.update(before)


class TestPersonalIntimacy(unittest.TestCase):
    def test_adult_daily_units_are_shared_by_both_worlds(self):
        for kind in ('EDEN','LAGOON'):
            p=engine.person(1,'A','m',-18*360,1,10,10)
            u=dict(kind=kind,day=0,part=1,people=[p],sites=[],settlements=[])
            with patch.object(engine,'terrain_of',return_value=[[0]*40 for _ in range(40)]):
                for _ in range(engine.PARTS_PER_DAY):
                    needs.meters(u,p,0,random.Random(1),needs.CONDITIONS[kind])
            self.assertAlmostEqual(p['intimacy'],1./7.)

    def test_children_have_no_adult_intimacy_need_and_the_meter_is_capped(self):
        child=engine.person(1,'C','f',-10*360,1,10,10)
        adult=engine.person(2,'A','m',-18*360,1,10,10)
        child['intimacy']=adult['intimacy']=1.
        u=dict(kind='EDEN',day=0,people=[child,adult],sites=[],settlements=[])
        for person in (child,adult):needs.meters(u,person,0,random.Random(1),needs.CONDITIONS['EDEN'])
        self.assertEqual(child['intimacy'],0.)
        self.assertEqual(adult['intimacy'],1.)

    def test_proposing_cannot_satisfy_a_personal_need_or_force_another_body(self):
        p=engine.person(1,'A','m',-18*360,1,10,10)
        q=engine.person(2,'B','f',-18*360,1,12,10)
        p.update(a=engine.A_REST,intimacy=1.)
        q.update(a=engine.A_SLEEP,intimacy=1.)
        u=dict(kind='EDEN',day=0,people=[p,q])
        before=copy.deepcopy(q)
        self.assertFalse(encounters.propose(u,p,q,'mate',0,(11,10)))
        self.assertEqual(p['intimacy'],1.)
        self.assertEqual(q,before)


if __name__ == '__main__':
    unittest.main()
