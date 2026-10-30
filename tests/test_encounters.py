"""Own proposals and actual simultaneous contact, without remote parenthood."""
import copy
import json
import os
import sys
import unittest
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(__file__)),'sim'))
import encounters
import minds


class TestEncounters(unittest.TestCase):
    def setUp(self):
        self.u={'kind':'LAGOON','day':0}
        self.land=[[0]*20 for _ in range(20)]
        def person(pid,sex,x):
            return dict(id=pid,s=sex,b=-20*360,x=x,y=5,tx=x,ty=5,a=minds.A_REST,
                        c=True,w=False,ab=False,p=None,ene=1.,hun=0.,thirst=0.,inj=0.,
                        mom=None,dad=None,ef=.8,ag=.2,vg=.7)
        self.p=person(1,'f',5);self.q=person(2,'m',6)
        self.byid={1:self.p,2:self.q}

    def meet(self,kind='mate'):
        encounters.propose(self.u,self.p,self.q,kind,10,(5,5))
        encounters.propose(self.u,self.q,self.p,kind,10,(6,5))

    def test_proposal_changes_only_actor_and_oneway_is_not_completed_contact(self):
        before=copy.deepcopy(self.q)
        self.assertTrue(encounters.propose(self.u,self.p,self.q,'mate',10,(5,5)))
        self.assertEqual(self.q,before)
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))
        self.assertIs(encounters.offer(self.u,self.q,self.byid,'mate',self.land),self.p)

    def test_actual_reciprocal_contact_captures_actual_father_detached(self):
        self.meet()
        frame=encounters.capture(self.u,self.q,self.byid,10,self.land)
        self.assertEqual(frame['ids'],[1,2])
        self.assertEqual((frame['mother'],frame['father'],frame['traits']),(1,2,[.8,.2,.7]))
        self.assertFalse(frame['paired'])
        self.q['ef']=.1
        self.assertEqual(frame['traits'],[.8,.2,.7])
        self.assertEqual(json.loads(json.dumps(frame)),frame)
        # Completion facts survive a later own action change; caller commits
        # survivor eligibility separately, not a second current-action check.
        self.p['a']=minds.A_SLEEP
        self.assertEqual(frame['kind'],'mate')

    def test_same_contact_from_either_endpoint_has_canonical_identity(self):
        self.meet()
        a=encounters.capture(self.u,self.p,self.byid,10,self.land)
        b=encounters.capture(self.u,self.q,self.byid,10,self.land)
        self.assertEqual(a,b)
        self.assertEqual(len(encounters.deduplicate([a,b])),1)

    def test_invalid_current_participants_cannot_complete(self):
        cases=[{'a':minds.A_SLEEP},{'a':minds.A_BIRTH},{'w':True},{'ab':True},
               {'c':False},{'ene':.1},{'hun':14.},{'thirst':1.},{'inj':.6},
               {'x':10,'tx':10},{'tx':7},{'s':'f'},{'b':-10*360}]
        for changes in cases:
            with self.subTest(changes=changes):
                self.setUp();self.meet();self.q.update(changes)
                self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))

    def test_ghost_wrong_session_and_wrong_target_reject(self):
        self.meet()
        self.assertIsNone(encounters.capture(self.u,self.p,{1:self.p},10,self.land))
        self.q['social']['token'][0]=99
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))
        self.meet();self.q['social']['target']=[7,5]
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))

    def test_water_and_diagonal_water_corner_reject(self):
        self.meet();self.land[5][6]=2
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))
        self.land[5][6]=0;self.q.update(y=6,ty=6);self.q['social']['target']=[6,6]
        self.land[5][6]=self.land[6][5]=2
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10))

    def test_existing_lagoon_other_bond_is_not_replaced_and_eden_free(self):
        self.p['p']=99
        self.assertFalse(encounters.propose(self.u,self.p,self.q,'mate',10,(5,5)))
        self.u['kind']='EDEN'
        self.meet()
        self.assertIsNotNone(encounters.capture(self.u,self.p,self.byid,10))
        self.assertEqual(self.p['p'],99)
        self.assertIsNone(self.q['p'])

    def test_known_close_family_is_excluded_only_from_mating(self):
        self.p['mom']=self.q['id']
        self.assertEqual(encounters.candidates(self.u,self.p,[self.q],'mate',self.land),[])
        self.meet('groom')
        self.assertEqual(encounters.capture(self.u,self.p,self.byid,10,self.land)['kind'],'groom')

    def test_nearby_awake_candidates_and_existing_reciprocal_bond(self):
        self.p['p']=2;self.q['p']=1
        self.assertEqual(encounters.candidates(self.u,self.p,[self.q],'mate',self.land),[self.q])
        self.meet()
        self.assertTrue(encounters.capture(self.u,self.p,self.byid,10,self.land)['paired'])
        self.q.update(x=15,tx=15)
        self.assertEqual(encounters.candidates(self.u,self.p,[self.q],'mate',self.land),[])

    def test_migration_empty_independent_social_intent(self):
        a={'id':1};b={'id':2}
        encounters.migrate_person(a);encounters.migrate_person(b)
        self.assertIsNone(a['social']);self.assertIsNone(b['social'])
        self.assertEqual(json.loads(json.dumps(a)),a)
        self.assertFalse(encounters.propose(self.u,self.p,self.q,'fight',10,(5,5)))

    def test_staged_death_and_non_simultaneous_actions_never_make_a_frame(self):
        self.meet()
        self.u['_ctx']={'dead':[self.q]}
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))
        self.u.pop('_ctx')
        self.q['a']=minds.A_SLEEP
        self.assertIsNone(encounters.capture(self.u,self.p,self.byid,10,self.land))
        self.p['a']=minds.A_SLEEP;self.q['a']=minds.A_MATE
        self.assertIsNone(encounters.capture(self.u,self.q,self.byid,10,self.land))

    def test_acceptance_copies_session_and_does_not_edit_existing_proposer(self):
        encounters.propose(self.u,self.p,self.q,'mate',10,(5,5))
        before=copy.deepcopy(self.p)
        encounters.propose(self.u,self.q,self.p,'mate',11,(6,5))
        self.assertEqual(self.p,before)
        self.assertEqual(self.p['social']['token'],self.q['social']['token'])
        self.assertIsNot(self.p['social']['token'],self.q['social']['token'])
        self.assertIsNone(encounters.capture(self.u,self.q,self.byid,9,self.land))
        self.assertIsNotNone(encounters.capture(self.u,self.q,self.byid,11,self.land))

    def test_groom_completion_is_not_a_reproductive_pair(self):
        self.meet('groom')
        frame=encounters.capture(self.u,self.q,self.byid,10,self.land)
        self.assertIsNone(frame['mother']);self.assertIsNone(frame['father'])
        self.assertIsNone(frame['traits'])
        self.assertIsNone(self.p['p']);self.assertIsNone(self.q['p'])
