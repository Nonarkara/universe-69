"""An actor's completed sleep and biography must not veto a fresh own choice."""
import copy
import itertools
import random
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sim'))
import engine
import encounters
import needs


def fixture(paired=False):
    u=engine.genesis()['eden']
    p,q=u['people'][:2]
    u.update(people=[p,q],day=0,part=0,parts=0,innocent=False,ennui=0.)
    for actor,x in ((p,10),(q,11)):
        actor.update(x=x,y=10,tx=x,ty=10,hx=x,hy=10,box=0,role=None,
                     a=engine.A_REST,ad=8,hun=0.,ene=1.,sol=1.,inj=0.,
                     intimacy=1.,p=None,social=None)
    if paired:p['p'],q['p']=q['id'],p['id']
    return u,p,q


class TestFreshChoice(unittest.TestCase):
    def test_finished_sleep_can_consider_social_choices_without_waking_peer(self):
        u,p,q=fixture()
        p.update(a=engine.A_SLEEP,ad=0)
        peer=copy.deepcopy(q)
        self.assertEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)
        self.assertEqual(q,peer)
        self.assertEqual(p['social']['other'],q['id'])
        self.assertIsNone(encounters.capture(u,p,{p['id']:p,q['id']:q},0))

    def test_midday_completed_nap_also_ends_its_own_sleep_label(self):
        u,p,q=fixture()
        u.update(part=1,parts=1)
        p.update(a=engine.A_SLEEP,ad=0)
        self.assertEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)
        self.assertEqual(q['a'],engine.A_REST)

    def test_actual_dawn_wakeup_without_resumed_work_can_choose_for_itself(self):
        u,p,q=fixture()
        p.update(a=engine.A_SLEEP,ad=1,slept=1)
        needs.night(u,p,random.Random(0),0)
        self.assertEqual(p['ad'],0)
        # The prior sleep label remains until the actor enters its own scorer.
        self.assertEqual(p['a'],engine.A_SLEEP)
        self.assertEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)

    def test_visible_offer_cannot_wake_ongoing_sleep(self):
        u,p,q=fixture()
        encounters.propose(u,p,q,'mate',0,(p['x'],p['y']))
        q.update(a=engine.A_SLEEP,ad=8,slept=1)
        before=copy.deepcopy(q)
        needs.update_social(u,q)
        self.assertEqual(q,before)
        self.assertFalse(encounters.available(u,q,'mate'))

    def test_finished_sleep_does_not_make_a_still_sleeping_peer_available(self):
        u,p,q=fixture()
        p.update(a=engine.A_SLEEP,ad=0)
        q.update(a=engine.A_SLEEP,ad=8)
        before=copy.deepcopy(q)
        self.assertNotEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)
        self.assertEqual(q,before)

    def test_own_wakeup_does_not_override_food_or_rest(self):
        for changes,expected in (({'hun':20.},engine.A_EAT),({'ene':.1},engine.A_SLEEP)):
            with self.subTest(changes=changes):
                u,p,q=fixture()
                p.update(a=engine.A_SLEEP,ad=0,**changes)
                before=copy.deepcopy(q)
                self.assertEqual(needs.assign(u,p,0,random.Random(0)),expected)
                self.assertEqual(q,before)
                self.assertIsNone(p.get('social'))

    def test_unfinished_sleep_and_unreached_bed_do_not_gain_social_readiness(self):
        for changes in ({'ad':8},{'ad':0,'tx':15}):
            with self.subTest(changes=changes):
                u,p,q=fixture()
                p.update(a=engine.A_SLEEP,**changes)
                self.assertNotEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)

    def test_same_body_choice_is_invariant_to_eden_biographical_bond_pointer(self):
        grid=itertools.product((.1,.3,.6,1.),(0.,.2,.5),(.5,1.),(0.,5.),(.5,1.))
        for purpose,ennui,energy,hunger,intimacy in grid:
            with self.subTest(purpose=purpose,ennui=ennui,energy=energy,hunger=hunger,intimacy=intimacy):
                outcomes=[]
                for paired in (False,True):
                    u,p,q=fixture(paired)
                    u['ennui']=ennui
                    p.update(pu=purpose,ene=energy,hun=hunger,intimacy=intimacy,role=0)
                    peer=copy.deepcopy(q)
                    rng=random.Random(0)
                    act=needs.assign(u,p,0,rng)
                    self.assertEqual(q,peer)
                    actor=copy.deepcopy(p);actor.pop('p')
                    outcomes.append((act,actor,rng.getstate()))
                self.assertEqual(*outcomes)

    def test_adult_intimacy_does_not_stop_at_age_45_for_actor_or_candidate(self):
        for male_age,female_age in ((46,25),(25,46),(70,62)):
            with self.subTest(male_age=male_age,female_age=female_age):
                u,p,q=fixture()
                p['b']=-male_age*360;q['b']=-female_age*360
                peer=copy.deepcopy(q)
                self.assertEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)
                self.assertEqual(q,peer)
                self.assertEqual(needs.assign(u,q,0,random.Random(0)),engine.A_MATE)

    def test_older_intimacy_does_not_remove_existing_clinical_age_gate(self):
        u,p,q=fixture()
        p['b']=-70*360;q['b']=-62*360
        needs.assign(u,p,0,random.Random(0));needs.assign(u,q,0,random.Random(0))
        for actor in (p,q):
            while not engine.step_toward(actor):pass
        u.update(part=3,parts=3)
        frame=encounters.capture(u,p,{p['id']:p,q['id']:q},3)
        self.assertIsNotNone(frame)
        engine.try_conceive(u,random.Random(0),[q],contacts=[frame])
        self.assertEqual(q['due'],0)
        self.assertIsNone(q['pregnancy_father'])
        self.assertIsNone(q['reproduction']['next_ovulation'])

    def test_adult_intimacy_retains_minor_and_urgency_guards(self):
        for changes in ({'b':-12*360},{'a':engine.A_BIRTH},{'inj':.8},{'hun':20.}):
            with self.subTest(changes=changes):
                u,p,q=fixture()
                p['b']=-70*360;q.update(changes)
                peer=copy.deepcopy(q)
                self.assertNotEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)
                self.assertEqual(q,peer)

    def test_finished_voluntary_care_or_social_stints_can_also_reconsider(self):
        for act in (engine.A_TEND,engine.A_FIGHT,engine.A_GROOM):
            with self.subTest(act=act):
                u,p,q=fixture()
                p.update(a=act,ad=0)
                before=copy.deepcopy(q)
                self.assertEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)
                self.assertEqual(q,before)

    def test_birth_and_withdrawal_are_not_cleared_as_finished_stints(self):
        for act in (engine.A_BIRTH,engine.A_WITHDRAW):
            with self.subTest(act=act):
                u,p,q=fixture()
                p.update(a=act,ad=0)
                self.assertNotEqual(needs.assign(u,p,0,random.Random(0)),engine.A_MATE)
