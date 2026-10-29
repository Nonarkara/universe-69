"""Physical island resources and clock contracts; no population forecast."""
import copy
import json
import os
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sim'))
import engine
import needs


class IslandResources(unittest.TestCase):
    def world(self):
        return engine.genesis(69)['lagoon']

    def test_camps_do_not_create_wild_resources(self):
        u = self.world()
        first = needs.make_sites(u, random.Random(1))
        u['settlements'].append(dict(u['settlements'][0]))
        second = needs.make_sites(u, random.Random(2))
        self.assertEqual(first, second)
        u['sites'] = first
        needs.ensure_sites(u, random.Random(3))
        self.assertEqual(first, u['sites'])
        keys = [(s['x'], s['y'], s['kind']) for s in first]
        self.assertEqual(len(keys), len(set(keys)))

    def test_fishing_places_touch_water_not_just_beach(self):
        u = self.world()
        terr = engine.terrain_of(u)
        fish = [s for s in needs.make_sites(u) if s['kind'] == 'fish']
        self.assertTrue(fish)
        for s in fish:
            x, y = s['x'], s['y']
            self.assertNotEqual(terr[y][x], 2)
            self.assertTrue(any(terr[y+dy][x+dx] == 2 for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))))

    def test_nearest_food_cannot_cross_water(self):
        u = self.world()
        terr = [[2]*9 for _ in range(9)]
        for y in range(1,8):
            for x in (1,2,6,7):
                terr[y][x] = 1
        p = {'x':2, 'y':4}
        u['sites'] = [{'x':6,'y':4,'kind':'plants','left':20,'max':20}]
        with patch.object(engine, 'terrain_of', return_value=terr):
            self.assertIsNone(needs.nearest_site(u, p, 'plants', 20)[0])

    def test_depletion_and_regrowth_count_shared_patch_once(self):
        u = self.world()
        sites = needs.make_sites(u)
        u['sites'] = sites
        s = next(s for s in sites if s['kind'] == 'plants')
        s['left'] = 0.0
        needs.regrow_sites(u)
        after = s['left']
        self.assertGreater(after, 0)
        u['settlements'].append(dict(u['settlements'][0]))
        needs.ensure_sites(u)
        self.assertEqual(s['left'], after)
        self.assertEqual(sum(q['kind']=='plants' and (q['x'],q['y'])==(s['x'],s['y']) for q in u['sites']),1)

    def test_migration_preserves_terrain_repairs_duplicate_stocks_without_refill(self):
        w = engine.genesis(69)
        u = w['lagoon']
        u.pop('terrain_version', None)
        before = copy.deepcopy(engine.terrain_of(u))
        s = {'x':137, 'y':109, 'kind':'plants','left':5.,'max':90.,'regrow':3.,'provisioned':False,'st':0}
        u['sites'] = [s, dict(s, left=8., st=1)]
        engine.migrate(w)
        self.assertEqual(engine.terrain_of(u), before)
        patches = [q for q in u['sites'] if q['kind']=='plants' and q['x']==137 and q['y']==109]
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0]['left'], 5.)
        encoded = json.dumps(w, sort_keys=True)
        self.assertEqual(json.dumps(engine.migrate(json.loads(encoded)), sort_keys=True), encoded)

    def test_fresh_water_not_sea_water_satisfies_thirst(self):
        u = self.world()
        needs.ensure_sites(u)
        source = next(s for s in u['sites'] if s['kind']=='water')
        p = u['people'][0]
        p.update(x=source['x'], y=source['y'], thirst=2.0)
        before = source['left']
        self.assertGreater(needs.drink(u,p),0)
        self.assertLess(p['thirst'],2.)
        self.assertLess(source['left'],before)
        p.update(x=1,y=1,thirst=2.0)
        self.assertEqual(needs.drink(u,p),0)
        self.assertEqual(p['thirst'],2.)

    def test_clock_hundred_years_per_real_day_preserves_old_pending_parts(self):
        w = engine.genesis(69)
        self.assertAlmostEqual(engine.SEC_PER_PART, .6)
        self.assertAlmostEqual(86400/engine.SEC_PER_DAY/360, 100)
        w['clock'] = {'epoch':1000.,'parts':400.,'seconds':3.}
        engine.migrate(w)
        engine.set_clock_pace(w,engine.SEC_PER_PART,now=1030.)
        self.assertEqual(w['clock']['parts'],410.)
        self.assertEqual(engine.target_parts(w,1030.),410)
        self.assertEqual(engine.target_parts(w,1036.),420)

    def test_water_fetch_depletes_source_then_physically_reaches_camp(self):
        u = self.world()
        needs.ensure_sites(u)
        p = u['people'][0]
        source = next(s for s in u['sites'] if s['kind']=='water' and engine.same_land(engine.terrain_of(u),p['x'],p['y'],s['x'],s['y']))
        p.update(x=source['x'],y=source['y'],thirst=1.,a=engine.A_DRINK)
        before = source['left']
        needs.fulfil(u,p,0,random.Random(1),engine.A_DRINK)
        self.assertEqual(p['thirst'],0.)
        self.assertEqual(p['carry_water'],needs.WATER_CARRY)
        self.assertEqual(source['left'],before-1.-needs.WATER_CARRY)
        st = u['settlements'][0]
        p.update(x=st['x'],y=st['y'])
        needs.deposit(u,p,0)
        self.assertEqual(st['water'],needs.WATER_CARRY)
        self.assertEqual(p['carry_water'],0.)
        p['thirst'] = 2.
        # Camp reserves remain usable even standing on a depleted bank.
        u['sites'] = [dict(source,x=p['x'],y=p['y'],left=0.)]
        self.assertEqual(needs.drink(u,p),2.)
        self.assertEqual(st['water'],needs.WATER_CARRY-2.)

    def test_no_water_causes_dehydration_despite_food(self):
        u = self.world()
        u['people'] = [u['people'][0]]
        p = u['people'][0]
        p['p'] = None
        st = u['settlements'][0]
        st['store'] = 10000.
        u['animals'] = []
        u['resource_version'] = 2
        u['sites'] = []
        events = []
        for i in range(24):
            engine.tick_lagoon(u,random.Random(i),events)
        self.assertEqual(u['people'],[])
        self.assertEqual(u['cod'].get('dehydration'),1)
        self.assertEqual(u['cod'].get('starvation',0),0)

    def test_nursing_water_is_paid_by_mother(self):
        u = self.world()
        m = u['people'][1]
        baby = engine.person(99,'Infant','m',-30,2,m['x'],m['y'])
        baby.update(mom=m['id'],thirst=.5)
        u['people'].append(baby)
        self.assertEqual(needs.drink(u,baby),.5)
        self.assertEqual(baby['thirst'],0)
        self.assertEqual(m['thirst'],.3)

    def test_tropical_climate_has_two_monsoons_and_no_winter(self):
        u = self.world()
        self.assertEqual(u['terrain_version'],2)
        for day in (0,100,200,280,350):
            u['day'] = day
            self.assertFalse(engine.lagoon_season(day,True)[2])
            snap = engine.summarize({'eden':engine.genesis(1)['eden'],'lagoon':u,'sec_per_day':2.4})['u']['lagoon']
            self.assertIn(snap['season'],('monsoon','dry season'))
            self.assertFalse(snap['harsh'])
        self.assertGreater(engine.lagoon_season(100,True)[0],engine.lagoon_season(0,True)[0])
        self.assertGreater(engine.lagoon_season(280,True)[0],engine.lagoon_season(200,True)[0])

    def test_staged_dead_mother_cannot_supply_food_or_water(self):
        u = self.world()
        m = u['people'][1]
        baby = engine.person(99,'Infant','m',-30,2,m['x'],m['y'])
        baby.update(mom=m['id'],thirst=.5,hun=10.)
        u['people'].append(baby)
        u['_ctx'] = {'byid':{m['id']:m}, 'dead':[m]}
        m.update(thirst=0.,hun=0.)
        self.assertEqual(needs.drink(u,baby),0.)
        self.assertEqual(needs.eat(u,baby),0.)
        self.assertEqual(baby['thirst'],.5)
        self.assertEqual(baby['hun'],10.)

    def test_predator_casualty_cannot_nurse_later_in_part(self):
        import animals
        u = self.world()
        m = u['people'][1]
        baby = engine.person(99,'Infant','m',-30,2,m['x'],m['y'])
        baby.update(mom=m['id'],thirst=.5,hun=10.)
        u['people'] = [m,baby]
        u['settlements'][0].update(store=0.,water=0.)
        u['resource_version'],u['sites'] = 2,[]
        with patch.object(animals,'tick',return_value=[(m,'predator')]):
            engine.tick_lagoon(u,random.Random(1),[])
        self.assertGreater(baby['hun'],10.)
        self.assertGreater(baby['thirst'],.5)
        self.assertEqual(m['thirst'],0.)

    def test_farm_and_animals_cannot_be_targeted_across_sea(self):
        import animals
        u = self.world()
        terr = [[2]*9 for _ in range(9)]
        for y in range(1,8):
            for x in (1,2,6,7):
                terr[y][x] = 1
        p = {'x':2,'y':4}
        u['sites'] = [{'x':6,'y':4,'kind':'farm','left':0,'max':20}]
        u['animals'] = [{'x':6,'y':4,'i':1,'k':'deer'}]
        with patch.object(engine,'terrain_of',return_value=terr):
            self.assertIsNone(needs._field_to_work(u,p,20))
            self.assertIsNone(animals.nearest(u,p,'deer',20))

    def test_real_cat_attack_uses_only_connected_defenders(self):
        import animals
        u = self.world()
        p = u['people'][0]
        p.update(x=2,y=4)
        cat = dict(x=2,y=4)
        defender = u['people'][2]
        defender.update(x=6,y=4)
        terr = [[2]*9 for _ in range(9)]
        for y in range(1,8):
            for x in (1,2,6,7):terr[y][x]=1
        ctx = dict(adult=lambda _:True,armed=False,lessons=[],day=0,part=0,events=[])
        with patch.object(random.Random,'random',return_value=.15):
            result = animals._attack(u,cat,p,[p,defender],random.Random(1),ctx,terr)
        self.assertEqual(result,'taken')
        self.assertEqual(u['kills'],0)

    def test_extinct_wildlife_does_not_respawn_from_nothing(self):
        import animals
        u = self.world()
        u['animals'] = []
        with patch.object(random.Random,'random',return_value=0):
            animals._daily(u,random.Random(1),engine.terrain_of(u),{})
        self.assertEqual(u['animals'],[])

    def test_pace_summary_reads_clock_and_does_not_move_world(self):
        w = engine.genesis(69)
        w['clock']['seconds'] = 3600.
        before = copy.deepcopy(w)
        pace = engine.summarize(w)['pace']
        self.assertEqual(pace['seconds_per_part'],3600.)
        self.assertAlmostEqual(pace['years_per_real_day'],1/60)
        self.assertEqual(w,before)

    def test_camp_pantry_and_water_cannot_bridge_a_strait(self):
        u = self.world()
        terr = [[2]*9 for _ in range(9)]
        for y in range(1,8):
            for x in (1,2,6,7):terr[y][x]=1
        st = u['settlements'][0]
        st.update(x=2,y=4,r=5,water=20.,store=20.)
        p = u['people'][0]
        p.update(x=6,y=4,thirst=2.,hun=10.)
        u['sites'] = []
        with patch.object(engine,'terrain_of',return_value=terr):
            self.assertFalse(needs.at_camp(u,p))
            self.assertEqual(needs.drink(u,p),0.)
            self.assertEqual(needs.eat(u,p),0.)
            # No known water now triggers scouting, never a route to the
            # pantry across the strait or a virtual drink from its reserves.
            target = needs.water_target(u,p)
            self.assertIsNotNone(target)
            self.assertNotEqual(target,(st['x'],st['y']))
            self.assertTrue(engine.same_land(terr,p['x'],p['y'],*target))
            self.assertEqual(st['water'],20.)
            self.assertEqual(st['store'],20.)

    def test_server_world_payload_uses_the_simulated_terrain_version(self):
        # Compile the real pure payload function without importing the server's
        # startup side effects or ever selecting the runtime data directory.
        import ast
        from pathlib import Path
        source = Path(engine.__file__).with_name('server.py').read_text()
        function = next(n for n in ast.parse(source).body
                        if isinstance(n,ast.FunctionDef) and n.name=='world_payload')
        namespace = {'engine':engine,'world':engine.genesis(69)}
        exec(compile(ast.Module(body=[function],type_ignores=[]),'server.py','exec'),namespace)
        for version in (1,2):
            u = namespace['world']['lagoon']
            u['terrain_version'] = version
            self.assertIs(namespace['world_payload']()['terrain'],engine.terrain_of(u))

    def test_hydration_site_index_remains_plain_json(self):
        w = engine.genesis(69)
        u = w['lagoon']
        needs.ensure_sites(u)
        p = u['people'][0]
        source = next(s for s in u['sites'] if s['kind']=='water')
        p.update(x=source['x'],y=source['y'],thirst=1.)
        needs.drink(u,p)  # fills the derived lookup cache
        encoded = json.dumps(w)
        loaded = json.loads(encoded)
        self.assertEqual(loaded['lagoon']['people'][0]['thirst'],0.)
        self.assertEqual(loaded['lagoon']['sites'],u['sites'])

    def test_child_play_context_remains_json_and_preserves_neighbor_order(self):
        w = engine.genesis(69)
        u = w['lagoon']
        children = [engine.person(100+i,'Child','m',-4*360,2,136,104) for i in range(3)]
        u['people'].extend(children)
        u['_ctx'] = engine.day_context(u['people'],0)
        self.assertEqual([p['id'] for p in engine.kids_near(u['_ctx'],children[0])],[100,101,102])
        json.dumps(w)

    def test_a_nursing_toddler_receives_the_water_in_milk(self):
        u = self.world()
        mother = u['people'][1]
        baby = engine.person(99,'Toddler','m',-360,2,mother['x'],mother['y'])
        baby.update(mom=mother['id'],thirst=2.,hun=10.)
        u['people'] = [mother,baby]
        u['sites'] = []
        u['settlements'][0].update(store=0.,water=0.)
        mother.update(thirst=0.,hun=0.)
        self.assertGreater(needs.eat(u,baby),0.)
        self.assertGreater(needs.drink(u,baby),0.)
        self.assertEqual(baby['thirst'],0.)
        self.assertGreater(mother['thirst'],0.)
