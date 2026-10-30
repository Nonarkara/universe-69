"""Cycle evaluation, actual calendar-day exposure and no invented history."""
import copy
import json
import os
import random
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(__file__)),'sim'))
import reproduction


class TestReproduction(unittest.TestCase):
    def setUp(self):
        self.p=dict(id=1,s='f',b=-25*360,due=0,fe=None,pregnancy_father=None)
        self.u=dict(seed=69,iteration=1,day=100,part=0,parts=400,people=[self.p])

    def frame(self,father=2,traits=None):
        return dict(kind='mate',part=self.u['parts'],mother=1,father=father,traits=traits or [.2,.3,.4])

    def ovulate(self,day=100):
        self.p['reproduction']=dict(next_ovulation=day,cycle_index=0,last_evaluated=None,exposures=[])

    def night(self):
        self.u.update(part=3,parts=self.u['day']*4+3)

    def test_benchmark_is_calendar_day_timing_and_modifier_once(self):
        for lag,q in zip(range(5,-1,-1),[.04,.13,.08,.29,.27,.08]):
            records=[dict(day=100-lag,father=2,traits=[.2,.3,.4])]
            self.assertAlmostEqual(reproduction.chance(records,100),q)
            self.assertAlmostEqual(reproduction.chance(records,100,.5),q*.5)
        self.assertEqual(reproduction.chance([dict(day=94)],100),0.)
        self.assertEqual(reproduction.chance([dict(day=101)],100),0.)
        self.assertEqual(reproduction.chance([dict(day=98)],100,10),.29)
        self.assertEqual(reproduction.chance([dict(day=98)],100,-1),0.)

    def test_repeated_parts_father_and_day_collapse_but_different_fathers_remain(self):
        self.assertEqual(reproduction.record(self.u,[self.frame(),self.frame()]),1)
        self.night()
        self.assertEqual(reproduction.record(self.u,[self.frame()]),0)
        self.assertEqual(reproduction.record(self.u,[self.frame(3)]),1)
        self.assertEqual(len(self.p['reproduction']['exposures']),2)
        self.u.update(day=101,part=0,parts=404)
        self.assertEqual(reproduction.record(self.u,[self.frame()]),1)
        self.assertEqual(len(self.p['reproduction']['exposures']),3)

    def test_no_same_session_or_multiple_day_trial_inflation(self):
        records=[dict(day=98,father=2,traits=[.2,.3,.4])]
        self.assertEqual(reproduction.chance(records*10,100),.29)
        records += [dict(day=99,father=3,traits=[.5,.6,.7])]
        self.assertEqual(reproduction.chance(records,100),.29)

    def test_records_are_detached_current_actual_mate_only(self):
        f=self.frame()
        reproduction.record(self.u,[dict(f,kind='groom'),dict(f,part=399),dict(f,mother=9)])
        self.assertIsNone(self.p.get('reproduction'))
        reproduction.record(self.u,[f]);f['traits'][0]=.99
        self.assertEqual(self.p['reproduction']['exposures'][0]['traits'],[.2,.3,.4])

    def test_living_mother_only_not_current_father_or_pair_is_required(self):
        self.p.update(p=None,w=True,ab=True)
        self.assertEqual(reproduction.record(self.u,[self.frame(999)]),1)
        self.u['_ctx']={'dead':[self.p]}
        self.assertEqual(reproduction.record(self.u,[self.frame(4)]),0)

    def test_max_four_fathers_per_day_and_six_calendar_bins(self):
        for day in range(94,101):
            self.u.update(day=day,parts=day*4)
            reproduction.record(self.u,[self.frame(i) for i in reversed(range(2,8))])
        records=self.p['reproduction']['exposures']
        self.assertEqual(len(records),24)
        self.assertEqual(min(r['day'] for r in records),95)
        self.assertTrue(all(sum(r['day']==d for r in records)==4 for d in range(95,101)))

    def test_record_order_does_not_change_capped_same_part_set(self):
        frames=[self.frame(i) for i in range(2,8)]
        other=copy.deepcopy(self.u)
        reproduction.record(self.u,frames)
        reproduction.record(other,list(reversed(frames)))
        self.assertEqual(self.p['reproduction'],other['people'][0]['reproduction'])

    def test_night_day_zero_exposure_is_available_and_evaluated_only_once(self):
        self.ovulate();self.u.update(day=100)
        for part in range(3):
            self.u.update(part=part,parts=400+part)
            self.assertIsNone(reproduction.advance(self.u,self.p))
        self.night();reproduction.record(self.u,[self.frame()])
        with patch.object(reproduction,'_rng',wraps=reproduction._rng) as rng:
            reproduction.advance(self.u,self.p)
            first=rng.call_count
            reproduction.advance(self.u,self.p)
            self.assertEqual(rng.call_count,first)
        self.assertEqual(self.p['reproduction']['last_evaluated'],100)
        self.assertGreaterEqual(self.p['reproduction']['next_ovulation'],124)
        self.assertLessEqual(self.p['reproduction']['next_ovulation'],135)

    def test_no_exposure_still_advances_cycle_without_conception_trial(self):
        self.ovulate();self.night()
        purposes=[];original=reproduction._rng
        def rng(u,p,index,purpose):
            purposes.append(purpose);return original(u,p,index,purpose)
        with patch.object(reproduction,'_rng',side_effect=rng):
            self.assertIsNone(reproduction.advance(self.u,self.p))
        self.assertNotIn('conception',purposes)
        self.assertEqual(self.p['reproduction']['last_evaluated'],100)

    def test_private_rng_unchanged_global_and_reload_midcycle_identical(self):
        reproduction.record(self.u,[self.frame()])
        global_before=random.getstate()
        reproduction.advance(self.u,self.p)
        self.assertEqual(random.getstate(),global_before)
        other=json.loads(json.dumps(self.u))
        self.u.update(day=self.p['reproduction']['next_ovulation'],part=3)
        self.u['parts']=self.u['day']*4+3
        other.update(day=self.u['day'],part=3,parts=self.u['parts'])
        self.assertEqual(reproduction.advance(self.u,self.p),reproduction.advance(other,other['people'][0]))
        self.assertEqual(self.p,other['people'][0])

    def test_father_chosen_only_best_day_records_even_after_death(self):
        self.ovulate();self.night()
        self.p['reproduction']['exposures']=[dict(day=95,father=9,traits=[.9,.9,.9]),
                 dict(day=98,father=2,traits=[.2,.3,.4]),dict(day=98,father=3,traits=[.5,.6,.7])]
        original=reproduction._rng
        def rng(u,p,index,purpose):
            obj=original(u,p,index,purpose)
            if purpose=='conception':obj.random=lambda:0.
            return obj
        with patch.object(reproduction,'_rng',side_effect=rng):
            result=reproduction.advance(self.u,self.p)
        self.assertIn(result['father'],[2,3])
        self.assertEqual(result['chance'],.29)
        self.assertEqual(result['traits'],[.2,.3,.4] if result['father']==2 else [.5,.6,.7])
        self.assertIsNone(self.p['pregnancy_father']) # engine commits pregnancy

    def test_migration_no_rng_no_contacts_and_existing_pregnancy_preserved(self):
        self.p.update(due=200,fe=[.1,.2,.3],pregnancy_father=9)
        with patch.object(random,'Random',side_effect=AssertionError('migration RNG')):
            reproduction.migrate_person(self.p)
        self.assertIsNone(self.p['reproduction'])
        self.ovulate();self.p['reproduction']['exposures']=[dict(day=100,father=2,traits=[.2,.3,.4])]
        reproduction.advance(self.u,self.p)
        self.assertEqual(self.p['reproduction']['exposures'],[])
        self.assertIsNone(self.p['reproduction']['next_ovulation'])
        self.assertEqual((self.p['due'],self.p['fe'],self.p['pregnancy_father']),(200,[.1,.2,.3],9))

    def test_existing_dict_defaults_independent_and_children_start_empty(self):
        a={'reproduction':{}};b={'reproduction':{}}
        reproduction.migrate_person(a);reproduction.migrate_person(b)
        self.assertIsNot(a['reproduction']['exposures'],b['reproduction']['exposures'])
        before=json.loads(json.dumps(a));reproduction.migrate_person(a);self.assertEqual(a,before)
        self.p['b']=-10*360
        reproduction.advance(self.u,self.p)
        self.assertIsNone(self.p.get('reproduction'))

    def test_dead_reference_and_age_limits_never_initialize_or_draw(self):
        self.u['people']=[]
        with patch.object(reproduction,'_rng',side_effect=AssertionError('dead draw')):
            self.assertIsNone(reproduction.advance(self.u,self.p))
        self.u['people']=[self.p];self.u['_ctx']={'dead':[self.p]}
        with patch.object(reproduction,'_rng',side_effect=AssertionError('staged dead draw')):
            self.assertIsNone(reproduction.advance(self.u,self.p))
        self.u.pop('_ctx')
        for age in (16*360-1,45*360+1):
            self.p['b']=self.u['day']-age
            with patch.object(reproduction,'_rng',side_effect=AssertionError('age draw')):
                self.assertIsNone(reproduction.advance(self.u,self.p))
            self.assertIsNone(self.p['reproduction'])
        for age in (16*360,45*360):
            self.p['reproduction']=None;self.p['b']=self.u['day']-age
            reproduction.advance(self.u,self.p)
            self.assertIsNotNone(self.p['reproduction']['next_ovulation'])

    def test_extra_part_calls_and_pace_do_not_change_cycle_outcomes(self):
        a=copy.deepcopy(self.u);b=copy.deepcopy(self.u)
        a['clock']={'seconds':.6};b['clock']={'seconds':3600}
        results=[[],[]]
        for day in range(100,220):
            for i,u in enumerate((a,b)):
                p=u['people'][0]
                for part in range(4):
                    u.update(day=day,part=part,parts=day*4+part)
                    if part==3 and day%3==0:
                        reproduction.record(u,[dict(kind='mate',part=u['parts'],mother=1,father=2,traits=[.2,.3,.4])])
                    if i==0 or part==3:
                        result=reproduction.advance(u,p)
                        if result:results[i].append(result)
        self.assertEqual(a['people'],b['people'])
        self.assertEqual(results[0],results[1])
        self.assertGreater(a['people'][0]['reproduction']['cycle_index'],0)

    def test_phase_is_a_stable_initialization_prior_not_an_inferred_old_cycle(self):
        other=copy.deepcopy(self.u)
        reproduction.advance(self.u,self.p)
        reproduction.advance(other,other['people'][0])
        state=self.p['reproduction']
        self.assertEqual(state,other['people'][0]['reproduction'])
        self.assertTrue(100<=state['next_ovulation']<=134)
        self.assertEqual(state['exposures'],[])
        self.assertIsNone(state['last_evaluated'])
        self.p['due']=200
        for part in range(4):
            self.u['part']=part
            with patch.object(reproduction,'_rng',side_effect=AssertionError('pregnancy draw')):
                reproduction.advance(self.u,self.p)
        self.p['due']=0
        reproduction.advance(self.u,self.p)
        self.assertIsNotNone(state['next_ovulation'])

    def test_pending_gestation_and_empty_existing_dict_are_safe_in_record(self):
        self.p['reproduction']={}
        reproduction.record(self.u,[self.frame()])
        self.p['due']=200
        self.night()
        self.assertEqual(reproduction.record(self.u,[self.frame(3)]),0)
        reproduction.advance(self.u,self.p)
        self.assertEqual(self.p['reproduction']['exposures'],[])
        self.assertIsNone(self.p['reproduction']['next_ovulation'])

    def test_nonfemale_or_nonreproductive_age_does_not_scan_world(self):
        class NoScan(list):
            def __iter__(self):raise AssertionError('unnecessary population scan')
        self.u['people']=NoScan()
        self.p['s']='m'
        self.assertIsNone(reproduction.advance(self.u,self.p))
        self.p.update(s='f',b=-10*360)
        self.assertIsNone(reproduction.advance(self.u,self.p))

    def test_evaluation_identity_survives_reload_after_an_unsuccessful_trial(self):
        self.ovulate();self.night();reproduction.record(self.u,[self.frame()])
        reproduction.advance(self.u,self.p,modifier=0.)
        restored=json.loads(json.dumps(self.u));p=restored['people'][0]
        with patch.object(reproduction,'_rng',side_effect=AssertionError('repeat evaluation')):
            self.assertIsNone(reproduction.advance(restored,p))
        self.assertEqual(p['reproduction']['last_evaluated'],100)

    def test_pending_pregnancy_can_cross_age_limit_without_losing_unknown_paternity(self):
        self.ovulate();self.p.update(b=self.u['day']-46*360,due=200,fe=[.2,.3,.4])
        self.p['reproduction']['exposures']=[dict(day=100,father=2,traits=[.2,.3,.4])]
        reproduction.advance(self.u,self.p)
        self.assertIsNone(self.p['reproduction']['next_ovulation'])
        self.assertEqual(self.p['reproduction']['exposures'],[])
        self.assertEqual(self.p['fe'],[.2,.3,.4])
        self.assertIsNone(self.p['pregnancy_father'])
