"""Purposeful instruction must change an actual future action, not just labels."""
import copy
import random
import unittest
from unittest.mock import patch
from tests.test_procedural_world import grant
import engine
import learning
import needs
import skills


class TestInstruction(unittest.TestCase):
    def setUp(self) -> None:
        self.land=[[0]*40 for _ in range(40)]
        mock=patch.object(engine,'terrain_of',return_value=self.land)
        mock.start();self.addCleanup(mock.stop)
        self.w=engine.genesis(69);self.u=self.w['lagoon']
        self.t,self.p=self.u['people'][:2]
        self.u.update(day=1,part=1,parts=5,people=[self.t,self.p],animals=[],resource_version=2)
        self.u['settlements']=[dict(x=10,y=10,r=5,store=500.,water=100.,mouths=2)]
        self.u['sites']=[dict(x=10,y=10,kind='fish',left=100.,max=100.)]
        for p,x in ((self.t,10),(self.p,5)):
            p.update(x=x,y=10,tx=x,ty=10,hx=10,hy=10,sol=1.,ene=1.,hun=0.,thirst=0.,a=engine.A_REST)
            learning.migrate_person(p)
        grant(self.t,'fishing')

    def witness(self) -> None:
        self.t.update(a=engine.A_FISH)
        needs.fulfil(self.u,self.t,1,random.Random(1),engine.A_FISH)
        needs.exchange(self.u,[])

    def request(self) -> None:
        needs.assign(self.u,self.p,self.u['day'],random.Random(1),needs.CONDITIONS['LAGOON'])

    def arrive(self) -> None:
        while not engine.step_toward(self.p,self.land,1):pass

    def lesson(self) -> None:
        needs.assign(self.u,self.t,self.u['day'],random.Random(1),needs.CONDITIONS['LAGOON'])
        needs.exchange(self.u,[needs.capture_contact(self.u,p) for p in (self.t,self.p)])

    def test_witnessed_fishing_can_motivate_a_foundational_lesson_and_later_real_fishing(self) -> None:
        self.witness()
        notes=self.p['experience']['mentors']
        self.assertEqual([n['tech'] for n in notes],['fishing'])
        self.assertFalse(skills.knows(self.p,'stone_tools'))
        self.assertFalse(skills.knows(self.p,'fishing'))
        self.request()
        self.assertEqual(self.p['learning']['tech'],'fishing')
        self.assertEqual(self.p['a'],engine.A_TALK)
        self.assertNotEqual((self.p['x'],self.p['y']),(self.p['tx'],self.p['ty']))
        self.assertIsNone(needs.capture_contact(self.u,self.p))
        self.arrive();self.lesson()
        self.assertAlmostEqual(skills.level(self.p,'stone_tools'),.25)
        self.assertFalse(skills.knows(self.p,'fishing'))
        self.assertEqual(self.p['learning']['tech'],'fishing')
        self.assertEqual(self.p['skills']['stone_tools']['teacher'],self.t['id'])
        self.assertEqual(self.p['skills']['stone_tools']['uses'],0)
        self.u['day']=2;self.u['parts']+=4
        self.lesson()
        self.assertAlmostEqual(skills.level(self.p,'fishing'),.25)
        self.assertIsNone(self.p['learning'])
        self.assertFalse(skills.qualified(self.p,'fishing'))
        self.p.update(x=10,y=10,a=engine.A_FISH)
        before=self.u['sites'][0]['left']
        needs.fulfil(self.u,self.p,2,random.Random(1),engine.A_FISH)
        self.assertLess(self.u['sites'][0]['left'],before)
        self.assertAlmostEqual(skills.level(self.p,'fishing'),.35)
        self.assertEqual(self.p['skills']['stone_tools']['uses'],0)

    def test_unseen_expert_is_not_an_available_goal(self) -> None:
        self.request()
        self.assertIsNone(self.p['learning'])
        self.assertEqual(self.p['experience']['mentors'],[])

    def test_witnessed_expertise_does_not_track_a_remote_teacher(self) -> None:
        self.witness();self.request()
        remembered=copy.deepcopy(self.p['learning'])
        self.t.update(x=30,y=30)
        needs.update_learning(self.u,self.p)
        self.assertEqual(self.p['learning'],remembered)
        self.arrive();needs.update_learning(self.u,self.p)
        self.assertIsNone(self.p['learning'])
        self.assertGreater(self.p['experience']['mentors'][0]['retry_day'],self.u['day'])
        self.assertFalse(skills.knows(self.p,'fishing'))

    def test_selecting_a_request_cannot_move_or_reassign_the_teacher(self) -> None:
        self.witness();before=copy.deepcopy(self.t)
        self.request()
        self.assertEqual(self.t,before)

    def test_teacher_urgent_needs_refuse_instruction(self) -> None:
        self.witness();self.request();self.arrive()
        self.t.update(hun=25.,ene=.1,thirst=2.)
        self.lesson()
        self.assertFalse(skills.knows(self.p,'stone_tools'))
        self.assertIsNone(self.t['teaching'])
        self.assertNotEqual(self.t['a'],engine.A_TALK)

    def test_night_interrupts_a_goal_without_marking_failed_search(self) -> None:
        self.witness();self.request()
        self.u['part']=engine.PART_NIGHT
        needs.night(self.u,self.p,random.Random(1),engine.PART_NIGHT)
        needs.update_learning(self.u,self.p)
        self.assertIsNone(self.p['learning'])
        self.assertEqual(self.p['a'],engine.A_SLEEP)
        self.assertEqual(self.p['experience']['mentors'][0]['retry_day'],-1)

    def test_verbal_capacity_cannot_be_bypassed_by_requested_instruction(self) -> None:
        grant(self.t,'stone_tools');self.t.update(a=engine.A_TALK)
        pupils=[]
        for pid in range(10,15):
            q=engine.person(pid,'Pupil','m',-18*360,1,10,11)
            q.update(a=engine.A_TALK,tx=10,ty=11)
            learning.migrate_person(q);pupils.append(q)
        self.u['people']=[self.t]+pupils
        needs.exchange(self.u,[needs.capture_contact(self.u,p) for p in self.u['people']])
        self.assertEqual(sum(skills.knows(p,'stone_tools') for p in pupils),4)
        last=pupils[-1]
        learning.remember_work(last,self.t['id'],'stone_tools',10,10,1)
        learning.start(last,last['experience']['mentors'][0],self.u['parts'])
        self.t['teaching']={'student':last['id'],'tech':'stone_tools','desired':'stone_tools','until_part':self.u['parts']+1}
        needs.exchange(self.u,[needs.capture_contact(self.u,p) for p in (self.t,last)])
        self.assertFalse(skills.knows(last,'stone_tools'))
        self.assertEqual(len(self.t['teaching_ids']),4)
        needs.practice_work(self.u,self.t,'stone_tools',1,True)
        needs.exchange(self.u,[])
        self.assertTrue(skills.knows(last,'stone_tools')) # observation costs no tutor attention
        self.assertEqual(len(self.t['teaching_ids']),4)

    def test_engine_assignment_preserves_the_intended_meeting(self) -> None:
        self.witness()
        self.u['_ctx']=engine.day_context(self.u['people'],self.u['day'])
        engine.lagoon_assign(self.u,self.p,self.u['day'],random.Random(1),0.)
        self.assertIsNotNone(self.p['learning'])
        goal_target=needs.study_target(self.u,self.p,self.p['learning'])
        self.assertEqual((self.p['tx'],self.p['ty']),goal_target)
        self.arrive();engine.lagoon_assign(self.u,self.t,1,random.Random(1),0.)
        self.assertIsNotNone(self.t['teaching'])
        self.assertEqual((self.t['tx'],self.t['ty']),(self.t['x'],self.t['y']))

    def test_a_current_voluntary_lesson_is_not_reassigned_to_watch(self) -> None:
        self.witness();self.request();self.arrive()
        grant(self.t,'fire')
        needs.assign(self.u,self.t,1,random.Random(1),needs.CONDITIONS['LAGOON'])
        self.assertIsNotNone(self.t['teaching'])
        self.u['settlements'][0]['fire_until']=self.u['parts']+4
        engine.keep_watch(self.u,self.u['people'],1,[],part=1,rng=random.Random(1))
        self.assertEqual(self.t['a'],engine.A_TALK)
        self.assertEqual(self.p['a'],engine.A_TALK)
        self.assertFalse(self.u['settlements'][0]['watch'])

    def test_request_reconsideration_still_allows_a_teacher_to_choose_food(self) -> None:
        self.witness();self.request();self.arrive()
        self.t.update(a=engine.A_WATCH,ad=4,tx=9,ty=11,hun=10.,ene=.8)
        self.u['settlements'][0]['store']=0.
        needs.update_learning(self.u,self.t)
        self.assertEqual(self.t['ad'],0)
        self.assertEqual(self.t['a'],engine.A_WATCH)
        needs.assign(self.u,self.t,1,random.Random(1),needs.CONDITIONS['LAGOON'])
        self.assertNotEqual(self.t['a'],engine.A_TALK)
        self.assertIsNone(self.t['teaching'])

    def test_an_expired_search_is_bounded_and_does_not_restart_itself(self) -> None:
        self.witness();self.request()
        self.u['parts']=self.p['learning']['until_part']
        needs.update_learning(self.u,self.p)
        self.assertIsNone(self.p['learning'])
        self.request()
        self.assertIsNone(self.p['learning'])
        self.assertFalse(skills.knows(self.p,'fishing'))

    def test_knowledge_is_not_taught_across_a_water_corner(self) -> None:
        self.t.update(x=10,y=10,tx=10,ty=10,a=engine.A_TALK)
        self.p.update(x=11,y=11,tx=11,ty=11,a=engine.A_TALK)
        self.land[10][11]=self.land[11][10]=2
        learning.remember_work(self.p,self.t['id'],'fishing',10,10,1)
        learning.start(self.p,self.p['experience']['mentors'][0],5)
        self.lesson()
        self.assertFalse(skills.knows(self.p,'stone_tools'))
        self.assertIsNone(self.t['teaching'])

    def test_teacher_offer_uses_one_consistent_inclusive_last_part(self) -> None:
        self.witness();self.request();self.arrive()
        needs.assign(self.u,self.t,1,random.Random(1),needs.CONDITIONS['LAGOON'])
        deadline=self.t['teaching']['until_part']
        self.u['parts']=deadline
        needs.update_learning(self.u,self.t)
        self.assertIsNotNone(needs.instruction_state(self.u,self.t))
        self.u['parts']=deadline+1
        needs.update_learning(self.u,self.t)
        self.assertIsNone(needs.instruction_state(self.u,self.t))

    def test_sleep_cannot_refresh_a_known_teachers_location(self) -> None:
        self.witness()
        before=copy.deepcopy(self.p['experience']['mentors'])
        self.p['a']=engine.A_SLEEP
        self.t.update(x=9,y=10)
        needs.update_learning(self.u,self.p)
        self.assertEqual(self.p['experience']['mentors'],before)


    def test_record_describes_completed_requested_exposure_once(self) -> None:
        self.witness();self.request();self.arrive()
        needs.assign(self.u,self.t,1,random.Random(1),needs.CONDITIONS['LAGOON'])
        facts=[needs.capture_contact(self.u,p) for p in (self.t,self.p)]
        plain=copy.deepcopy(self.u);events=[]
        needs.exchange(self.u,facts,events)
        needs.exchange(plain,copy.deepcopy(facts))
        self.assertEqual(self.u,plain)
        self.assertEqual(self.p['skills']['stone_tools']['basis'],'requested_instruction')
        self.assertEqual(len(events),1)
        self.assertEqual(events[0][:3],(1,'LAGOON','culture'))
        self.assertIn('stone tools',events[0][3])
        self.assertIn(self.t['n'],events[0][3]);self.assertIn(self.p['n'],events[0][3])
        needs.exchange(self.u,facts,events)
        self.assertEqual(len(events),1)

    def test_an_expired_or_replaced_pupil_goal_cannot_keep_a_teacher_label(self) -> None:
        self.witness();self.request();self.arrive()
        needs.assign(self.u,self.t,1,random.Random(1),needs.CONDITIONS['LAGOON'])
        goal,offer=copy.deepcopy(self.p['learning']),copy.deepcopy(self.t['teaching'])
        for replacement in ('expired','changed'):
            self.p['learning'],self.t['teaching']=copy.deepcopy(goal),copy.deepcopy(offer)
            if replacement == 'expired':
                self.p['learning']['until_part']=self.u['parts']
            else:
                self.p['learning']['tech']='fire'
            self.assertIsNone(needs.instruction_state(self.u,self.t))
            needs.update_learning(self.u,self.t)
            self.assertIsNone(self.t['teaching'])


class TestInstructionContinuation(unittest.TestCase):
    def test_real_tick_continues_an_existing_intent_and_reload_is_deterministic(self) -> None:
        import importlib.util
        import json
        from pathlib import Path
        import tempfile
        from tests.scratch_space import scratch_root
        spec=importlib.util.spec_from_file_location('instruction_fixture',Path(__file__).resolve().parents[1]/'tools/controlled_instruction.py')
        fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
        with tempfile.TemporaryDirectory(dir=scratch_root()) as d:
            folder=Path(d)
            fixture.build(folder)
            world=json.loads((folder/'raw-world.json').read_text())
            engine.migrate(world)
            path=str(folder/'saved.json');engine.save_state(world,path)
            a=engine.load_state(path);b=engine.load_state(path)
            pupil=a['lagoon']['people'][1]
            self.assertIsNotNone(pupil['learning'])
            self.assertFalse(skills.knows(pupil,'stone_tools'))
            ea,eb=[],[]
            engine.tick_world(a,ea);engine.tick_world(b,eb)
            self.assertTrue(skills.knows(pupil,'stone_tools'))
            self.assertFalse(skills.qualified(pupil,'stone_tools'))
            self.assertIsNotNone(pupil['learning'])
            for _ in range(31):
                engine.tick_world(a,ea);engine.tick_world(b,eb)
            engine.save_state(a,str(folder/'a.json'));engine.save_state(b,str(folder/'b.json'))
            self.assertEqual(json.loads((folder/'a.json').read_text()),json.loads((folder/'b.json').read_text()))
            self.assertEqual(ea,eb)

    def test_newborn_reseed_and_old_schema_have_no_invented_mentor_history(self) -> None:
        w=engine.genesis(69)
        for u in (w['eden'],w['lagoon']):
            for p in u['people']:
                self.assertEqual(p['experience']['mentors'],[])
                self.assertIsNone(p['learning']);self.assertIsNone(p['teaching'])
                del p['experience']['mentors']
                for field in ('learning','teaching','teaching_day','teaching_ids'):p.pop(field)
        engine.migrate(w)
        for u in (w['eden'],w['lagoon']):
            self.assertTrue(all(not p['experience']['mentors'] and not p['learning'] and not p['teaching_ids'] for p in u['people']))
        reseed=engine.genesis_universe('LAGOON',70)
        self.assertTrue(all(not p['experience']['mentors'] for p in reseed['people']))
