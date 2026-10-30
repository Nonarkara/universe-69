"""Procedure history, personal competence and material assets are distinct."""
import copy
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sim'))
import engine
import needs
import skills
import animals

PARENTS={t:p for t,p,_,_ in skills.TECH_LADDER}
def grant(person: dict, tech: str) -> None:
    if PARENTS[tech]:grant(person,PARENTS[tech])
    skills.invent(person,tech,0)

class TestProceduralWorld(unittest.TestCase):
    def setUp(self) -> None:
        self.land=[[0]*40 for _ in range(40)]
        mock=patch.object(engine,'terrain_of',return_value=self.land)
        mock.start();self.addCleanup(mock.stop)
        self.a=engine.person(1,'A','f',-18*360,1,10,10)
        self.b=engine.person(2,'B','m',-18*360,1,10,10)
        self.st=dict(x=10,y=10,r=5,store=100.,water=100.,mouths=2)
        self.site=dict(x=10,y=10,kind='fish',left=100.,max=100.)
        self.u=dict(kind='LAGOON',day=1,part=1,parts=5,people=[self.a,self.b],
                    settlements=[self.st],sites=[self.site],tech=['stone_tools','fishing'],farms=[])

    def test_global_history_does_not_enable_forced_fishing_or_raw_fish_eating(self) -> None:
        self.a.update(a=engine.A_FISH,hun=20.)
        self.st['store']=0.
        self.assertEqual(needs.fulfil(self.u,self.a,1,random.Random(1),engine.A_FISH),0.)
        self.assertEqual(needs.eat(self.u,self.a),0.)
        self.assertEqual(self.site['left'],100.)

    def test_only_the_person_who_knows_fishing_can_harvest(self) -> None:
        grant(self.a,'fishing')
        for p in (self.a,self.b):p.update(a=engine.A_FISH)
        self.assertGreater(needs.fulfil(self.u,self.a,1,random.Random(1),engine.A_FISH),0.)
        left=self.site['left']
        self.assertEqual(needs.fulfil(self.u,self.b,1,random.Random(1),engine.A_FISH),0.)
        self.assertEqual(self.site['left'],left)
        self.b.update(a=engine.A_EAT,hun=20.)
        self.assertGreater(needs.eat(self.u,self.b),0.) # caught food needs no fishing procedure

    def test_untrained_farmwork_cannot_plant_and_trained_tending_is_real_practice(self) -> None:
        self.site.update(kind='farm',left=0.,worked=None)
        self.a.update(a=engine.A_FARM)
        needs.fulfil(self.u,self.a,1,random.Random(1),engine.A_FARM)
        self.assertIsNone(self.site['worked'])
        grant(self.a,'agriculture')
        needs.fulfil(self.u,self.a,1,random.Random(1),engine.A_FARM)
        self.assertEqual(self.site['worked'],1)
        self.assertEqual(self.a['skills']['agriculture']['uses'],1)

    def test_forced_build_cannot_bypass_personal_construction_knowledge(self) -> None:
        self.a.update(p=2,a=engine.A_BUILD)
        h=needs.hut_of(self.u,self.a,make=True)
        self.a.update(x=h['x'],y=h['y'])
        needs.fulfil(self.u,self.a,1,random.Random(1),engine.A_BUILD)
        self.assertEqual(h['w'],0.)
        grant(self.a,'shelter')
        needs.fulfil(self.u,self.a,1,random.Random(1),engine.A_BUILD)
        self.assertGreater(h['w'],0.)
        self.assertEqual(self.a['skills']['shelter']['uses'],1)

    def test_instruction_is_not_mastery_and_does_not_reveal_unseen_sites(self) -> None:
        grant(self.a,'stone_tools')
        self.u['sites']=[dict(self.site,x=30,y=30)]
        for p in (self.a,self.b):p.update(a=engine.A_TALK,tx=10,ty=10)
        needs.exchange(self.u,[needs.capture_contact(self.u,p) for p in (self.a,self.b)])
        self.assertAlmostEqual(skills.level(self.b,'stone_tools'),.25)
        self.assertFalse(skills.can_teach(self.b,'stone_tools'))
        self.assertIsNone(needs.nearest_site(self.u,self.b,'fish',26)[0])
        self.u['day']=2
        needs.exchange(self.u,[needs.capture_contact(self.u,p) for p in (self.a,self.b)])
        self.assertAlmostEqual(skills.level(self.b,'stone_tools'),.25)

    def test_built_granary_is_local_and_survives_its_builder(self) -> None:
        other=dict(x=30,y=30,r=5,store=100.,water=0.)
        self.u['settlements'].append(other)
        self.st['works']={'granary':needs.CRAFT_WORK['granary']}
        self.u['people']=[]
        needs.keep_stores(self.u)
        self.assertAlmostEqual(self.st['store'],99.8)
        self.assertAlmostEqual(other['store'],96.)

    def test_prepared_food_persists_but_new_raw_food_is_not_magically_preserved(self) -> None:
        self.st['prepared']=50.
        self.u['people']=[]
        needs.keep_stores(self.u)
        self.assertAlmostEqual(self.st['store'],50*.992+50*.96)
        self.assertLessEqual(self.st['prepared'],self.st['store'])

    def test_fire_is_a_local_asset_not_a_world_history_bonus(self) -> None:
        self.u['tech']=['fire']
        cat=dict(x=10,y=10)
        self.assertFalse(animals._guarded(self.u,cat,True,lambda t:True))
        self.st['fire_until']=10
        self.assertTrue(animals._guarded(self.u,cat,True,lambda t:False))
        self.u['parts']=11
        self.assertFalse(animals._guarded(self.u,cat,True,lambda t:True))

    def test_dead_or_remote_healers_do_not_help_a_patient(self) -> None:
        grant(self.a,'healing')
        self.a.update(a=engine.A_TEND,tx=10,ty=10)
        self.assertTrue(needs.healing_near(self.u,self.b))
        self.a.update(x=30,y=30)
        self.assertFalse(needs.healing_near(self.u,self.b))
        self.a.update(x=10,y=10)
        self.u['people'].remove(self.a)
        self.assertFalse(needs.healing_near(self.u,self.b))

    def test_departed_healer_and_staged_dead_expert_do_not_count(self) -> None:
        grant(self.a,'healing')
        self.a.update(a=engine.A_TEND,tx=10,ty=10)
        self.assertTrue(needs.healing_near(self.u,self.b))
        self.a['a']=engine.A_SLEEP
        self.assertFalse(needs.healing_near(self.u,self.b))
        self.u['_ctx']={'dead':[self.a]}
        self.assertFalse(needs.camp_has(self.u,self.st,'healing'))

    def test_craft_requires_arrival_at_the_assigned_worksite(self) -> None:
        grant(self.a,'granary')
        self.a.update(a=engine.A_WORK,tx=11,ty=10,craft={'skill':'granary','x':11,'y':10})
        needs.perform_craft(self.u,self.a,1)
        self.assertFalse(self.st.get('works'))
        self.a.update(tx=10,ty=10,craft={'skill':'granary','x':30,'y':30})
        needs.perform_craft(self.u,self.a,1)
        self.assertFalse(self.st.get('works'))
        self.a['craft'].update(x=10,y=10)
        needs.perform_craft(self.u,self.a,1)
        self.assertGreater(self.st['works']['granary'],0.)

    def test_healing_dead_or_unreachable_patients_is_not_practice(self) -> None:
        grant(self.a,'healing')
        self.a.update(a=engine.A_TEND,tx=10,ty=10)
        self.b.update(inj=.5,x=11,y=11)
        self.u['_ctx']={'dead':[self.b]}
        needs.perform_craft(self.u,self.a,1)
        self.assertEqual(self.a['skills']['healing']['uses'],0)
        self.u['parts']+=1
        self.u['_ctx']['dead']=[]
        self.land[10][11]=self.land[11][10]=2
        needs.perform_craft(self.u,self.a,1)
        self.assertEqual(self.a['skills']['healing']['uses'],0)
        self.assertFalse(self.u.get('_demos'))

    def test_real_craft_conserves_food_and_can_be_witnessed(self) -> None:
        grant(self.a,'preservation')
        self.a.update(a=engine.A_WORK,tx=10,ty=10,craft={'skill':'preservation','x':10,'y':10})
        grant(self.b,'fire')
        self.b.update(a=engine.A_TALK,tx=10,ty=10)
        needs.perform_craft(self.u,self.a,1)
        self.assertEqual(self.st['store'],100.)
        self.assertGreater(self.st['prepared'],0.)
        needs.exchange(self.u,[])
        self.assertAlmostEqual(skills.level(self.b,'preservation'),.25)
        self.assertEqual(self.b['skills']['preservation']['basis'],'demonstration')

    def test_camp_guards_cannot_protect_across_water(self) -> None:
        self.st.update(watch=1,fire_until=20)
        self.land[10][11]=self.land[11][10]=2
        self.assertFalse(animals._guarded(self.u,dict(x=11,y=11),True,lambda t:True))

    def test_personal_seacraft_apprentice_practices_on_the_actual_boat(self) -> None:
        grant(self.a,'fishing')
        skills.expose(self.a,'seacraft',1)
        boat=dict(x=10,y=10,work=0.)
        self.u['boat']=boat
        self.a.update(a=engine.A_BUILD)
        needs.fulfil(self.u,self.a,1,random.Random(1),engine.A_BUILD)
        self.assertIn(self.a['id'],boat['builders'])
        self.assertAlmostEqual(skills.level(self.a,'seacraft'),.35)
        self.assertAlmostEqual(boat['work'],.25)

    def test_domestication_completion_requires_an_animal_in_reach(self) -> None:
        grant(self.a,'domestication')
        self.st['works']={'domestication':needs.CRAFT_WORK['domestication']-.1}
        self.a.update(a=engine.A_WORK,tx=10,ty=10,craft={'skill':'domestication','x':10,'y':10})
        animal=dict(i=1,k=animals.DEER,x=15,y=10)
        self.u['animals']=[animal]
        needs.perform_craft(self.u,self.a,1)
        self.assertFalse(needs.built(self.st,'domestication'))
        self.assertEqual(self.u['animals'],[animal])
        animal['x']=11
        self.a['craft']={'skill':'domestication','x':10,'y':10}
        self.u['parts']+=1
        needs.perform_craft(self.u,self.a,1)
        self.assertTrue(needs.built(self.st,'domestication'))
        self.assertEqual(self.st['domestic'],1)
        self.assertEqual(self.u['animals'],[])

    def test_same_part_contacts_cannot_teach_a_newly_received_procedure(self) -> None:
        grant(self.a,'stone_tools')
        c=engine.person(3,'C','m',-18*360,1,16,10)
        self.u['people'].append(c)
        self.a['x']=10
        self.b['x']=13
        for p in self.u['people']:p.update(a=engine.A_TALK,tx=p['x'],ty=p['y'])
        frames=[needs.capture_contact(self.u,p) for p in self.u['people']]
        needs.exchange(self.u,frames)
        self.assertTrue(skills.knows(self.b,'stone_tools'))
        self.assertFalse(skills.knows(c,'stone_tools'))

    def test_schema_migration_and_json_reload_preserve_personal_history(self) -> None:
        import tempfile
        w=engine.genesis(69)
        u=w['lagoon']
        u.pop('skill_schema')
        u['tech']=['fire','stone_tools','fishing']
        p=u['people'][0]
        p.pop('skills')
        child=engine.person(999,'Child','f',0,2,p['x'],p['y'])
        child.pop('skills')
        u['people'].append(child)
        engine.migrate(w)
        self.assertTrue(skills.qualified(p,'fishing'))
        self.assertIsNone(p['skills']['fishing']['learned_day'])
        self.assertEqual(p['skills']['fishing']['basis'],'legacy_global_capability')
        self.assertFalse(skills.can_teach(p,'fishing'))
        self.assertEqual(child['skills'],{})
        from tests.scratch_space import scratch_root
        with tempfile.TemporaryDirectory(dir=scratch_root()) as d:
            path=d+'/fixture.json'
            engine.save_state(w,path)
            restored=engine.load_state(path)
        self.assertEqual(restored['lagoon']['people'][0]['skills'],p['skills'])
        self.assertEqual(restored['lagoon']['people'][-1]['skills'],{})
        fresh=engine.genesis(69)['lagoon']
        self.assertTrue(all(not q['skills'] for q in fresh['people']))

    def test_healing_choices_ignore_dead_and_disconnected_patients(self) -> None:
        grant(self.a,'healing')
        self.a.update(sol=1.,hun=0.,ene=1.)
        self.b['inj']=.7
        self.u['_ctx']={'dead':[self.b]}
        act=needs.assign(self.u,self.a,1,random.Random(1),dict(needs.CONDITIONS['LAGOON'],must_work_to_eat=False,work_drive=0))
        self.assertNotEqual(act,engine.A_TEND)
        self.u['_ctx']['dead']=[]
        self.land[10][11]=self.land[11][10]=2
        self.b.update(x=11,y=11)
        # This bank has no dry route to the patient, even though it is nearby.
        with patch.object(engine,'same_land',return_value=False):
            act=needs.assign(self.u,self.a,1,random.Random(1),dict(needs.CONDITIONS['LAGOON'],must_work_to_eat=False,work_drive=0))
        self.assertNotEqual(act,engine.A_TEND)

    def test_global_tools_do_not_arm_a_person_against_a_cat(self) -> None:
        context={'adult':lambda p:True,'lessons':[],'day':1,'part':1,'events':[],'armed':True}
        cat=dict(i=1,k=animals.CAT,x=10,y=10)
        with patch.object(random.Random,'random',side_effect=[.15,.99]):
            result=animals._attack(self.u,cat,self.a,[self.a],random.Random(1),context,self.land)
        self.assertEqual(result,'fled')
        grant(self.a,'stone_tools')
        with patch.object(random.Random,'random',side_effect=[.15,.99]):
            result=animals._attack(self.u,cat,self.a,[self.a],random.Random(1),context,self.land)
        self.assertEqual(result,'killed')

    def test_only_a_present_living_arrived_sentry_protects_a_camp(self) -> None:
        self.st['watch']=self.a['id']
        cat=dict(x=10,y=10)
        self.assertFalse(animals._guarded(self.u,cat,False,lambda t:True))
        self.a.update(a=engine.A_WATCH,tx=10,ty=10)
        self.assertTrue(animals._guarded(self.u,cat,False,lambda t:True))
        self.u['_ctx']={'dead':[self.a]}
        self.assertFalse(animals._guarded(self.u,cat,False,lambda t:True))
        self.u['_ctx']['dead']=[]
        self.assertFalse(animals._guarded(self.u,cat,False,lambda t:True,[self.b]))

    def test_finishing_a_project_releases_the_stint(self) -> None:
        grant(self.a,'granary')
        self.st['works']={'granary':needs.CRAFT_WORK['granary']-.1}
        self.a.update(a=engine.A_WORK,ad=20,tx=10,ty=10,craft={'skill':'granary','x':10,'y':10})
        needs.perform_craft(self.u,self.a,1)
        self.assertTrue(needs.built(self.st,'granary'))
        self.assertIsNone(self.a['craft'])
        self.assertEqual(self.a['ad'],0)

    def test_real_engine_tick_accepts_actor_based_animal_context(self) -> None:
        # Use actual terrain/animals, unlike geometry fixtures in this class.
        terrain=engine.make_lagoon_terrain(69,2)
        with patch.object(engine,'terrain_of',return_value=terrain):
            w=engine.genesis(69)
            engine.tick_world(w,[])
        self.assertEqual(w['lagoon']['parts'],1)

    def test_a_lit_fire_does_not_monopolize_other_craft_practice(self) -> None:
        grant(self.a,'fire')
        skills.expose(self.a,'stone_tools',1)
        self.st['fire_until']=self.u['parts']+engine.PARTS_PER_DAY
        self.a.update(hun=0.,ene=1.,sol=1.,thirst=0.)
        needs.assign(self.u,self.a,1,random.Random(1),dict(needs.CONDITIONS['LAGOON'],work_drive=1.))
        self.assertEqual(self.a['a'],engine.A_WORK)
        self.assertEqual(self.a['craft']['skill'],'stone_tools')
        self.st['fire_until']=self.u['parts']+1
        needs.assign(self.u,self.a,1,random.Random(1),dict(needs.CONDITIONS['LAGOON'],work_drive=1.))
        self.assertEqual(self.a['craft']['skill'],'fire')

    def test_fire_priority_uses_remaining_life_without_processing_food_on_assignment(self) -> None:
        grant(self.a,'preservation')
        self.a.update(hun=0.,ene=1.,sol=1.,thirst=0.)
        for remaining,expected in ((4,'preservation'),(1,'fire'),(0,'fire')):
            self.st['fire_until']=self.u['parts']+remaining
            needs.assign(self.u,self.a,1,random.Random(1),dict(needs.CONDITIONS['LAGOON'],work_drive=1.))
            self.assertEqual(self.a['craft']['skill'],expected)
            self.assertEqual(self.st['store'],100.)
            self.assertEqual(self.st.get('prepared',0.),0.)
