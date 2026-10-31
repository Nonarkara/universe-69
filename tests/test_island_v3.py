"""LAGOON's next island is a real island analogue, not a circle with a
lagoon punched into it — and its field cache never trusts a recycled id.

Covers engine 2026.10.31.1: the hill country (tile 5), the sand-spit
estuary, the islets, the resources that read the hill country, and the
land_field identity check that same_land already had.
"""

import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sim"))

import engine
import needs
import animals


def terrain_for(u):
    return engine.terrain_of(u)


class TestIslandV3(unittest.TestCase):
    def test_a_new_genesis_builds_the_v3_island(self):
        u = engine.genesis_universe("LAGOON", 9, iteration=2)
        self.assertEqual(u["terrain_version"], 3)

    def test_the_hill_country_exists_and_sits_on_the_land(self):
        u = engine.genesis_universe("LAGOON", 9, iteration=2)
        t = terrain_for(u)
        hills = [(x, y) for y in range(len(t)) for x in range(len(t))
                 if t[y][x] == 5]
        self.assertGreater(len(hills), 100, "a hill country, not a hillock")
        self.assertTrue(all(t[y][x] != 2 for x, y in hills))

    def test_hills_cannot_replace_woods_or_shore(self):
        t = engine.make_lagoon_terrain(69, 3)
        t2 = engine.make_lagoon_terrain(69, 2)
        for y in range(len(t)):
            for x in range(len(t)):
                if t[y][x] == 5:
                    self.assertEqual(t2[y][x], 0,
                                     "hills take only open grass")

    def test_the_spit_widens_the_north_east_shore(self):
        t2 = engine.make_lagoon_terrain(69, 3)
        t1 = engine.make_lagoon_terrain(69, 2)
        more_beach = sum(row.count(3) for row in t2) - sum(row.count(3) for row in t1)
        self.assertGreater(more_beach, 0, "the estuary gets its spit")

    def test_islets_sit_in_the_strait(self):
        t = engine.make_lagoon_terrain(69, 3)
        self.assertIn(t[22][46], (0, 3))
        self.assertIn(t[146][146], (0, 3))

    def test_deterministic_geometry(self):
        self.assertEqual(engine.make_lagoon_terrain(9, 3),
                         engine.make_lagoon_terrain(9, 3))
        self.assertNotEqual(engine.make_lagoon_terrain(9, 3),
                            engine.make_lagoon_terrain(10, 3))

    def test_the_running_world_keeps_its_own_geography(self):
        t2 = engine.make_lagoon_terrain(9, 2)
        t3 = engine.make_lagoon_terrain(9, 3)
        self.assertFalse(any(5 in row for row in t2))
        self.assertTrue(any(5 in row for row in t3))

    def test_the_hill_country_holds_plant_patches(self):
        u = engine.genesis_universe("LAGOON", 9, iteration=2)
        t = terrain_for(u)
        patches = [s for s in needs.make_sites(u) if s["kind"] == "plants"]
        on_hills = [s for s in patches if t[s["y"]][s["x"]] == 5]
        self.assertGreater(len(on_hills), 0,
                           "the hill country carries its own groves")

    def test_the_hill_country_counts_as_woods_for_animals(self):
        u = engine.genesis_universe("LAGOON", 9, iteration=2)
        t = terrain_for(u)
        woods = animals._woods(t)
        self.assertTrue(any(t[y][x] == 5 for x, y in woods))

    def test_freshwater_banks_prefer_the_hillside(self):
        u = engine.genesis_universe("LAGOON", 11, iteration=2)
        t = terrain_for(u)
        banks = needs.water_sources(u)
        self.assertTrue(banks)
        self.assertTrue(any(t[s["y"]][s["x"]] == 5 for s in banks),
                        "a hillside seep is preferred where there is one")


class TestLandFieldCache(unittest.TestCase):
    def test_the_cached_field_belongs_to_the_terrain_it_was_built_for(self):
        a = engine.make_lagoon_terrain(9, 1)
        b = engine.make_lagoon_terrain(10, 1)
        fa = engine.land_field(a, 5, 5)
        entry = engine._FIELDS.get((id(a), 5, 5))
        self.assertIsNotNone(entry)
        # simulate an id recycled by another terrain: the stored terrain is
        # b's, the caller asks for a's — the cache must refuse
        engine._FIELDS[(id(a), 5, 5)] = (b, fa)
        fb = engine.land_field(a, 5, 5)
        self.assertEqual(fb, fa,
                         "a rebuilt field for a's own tiles is a itself")
        self.assertNotEqual(engine._FIELDS[(id(a), 5, 5)][0], b,
                            "the poisoned entry is replaced by a's own")

    def test_a_field_is_built_around_water_not_through_it(self):
        t = engine.make_lagoon_terrain(9, 1)
        f = engine.land_field(t, 2, 2)
        S = len(t)
        for y in range(S):
            for x in range(S):
                if t[y][x] == 2:
                    self.assertGreaterEqual(f[y * S + x], S * S - 1)


class TestNearHopper(unittest.TestCase):
    def test_reach_is_inclusive_and_squares_are_boxes(self):
        u = engine.genesis_universe("EDEN", 1, iteration=1)
        hop = engine.hoppers(u)[0]
        p = {"x": hop[0] + 3, "y": hop[1] + 3}
        self.assertTrue(engine.near_hopper(u, p, reach=3))
        self.assertFalse(engine.near_hopper(u, {"x": hop[0] + 4, "y": hop[1] + 4}, reach=3))
        self.assertTrue(engine.near_hopper(u, {"x": hop[0], "y": hop[1]}))


class TestSummarizeEncounters(unittest.TestCase):
    def test_recent_animal_encounters_reach_the_record(self):
        import random
        u = engine.genesis_universe("LAGOON", 9, iteration=2)
        t = terrain_for(u)
        woods = animals._woods(t)
        # one person out in the woods, one fresh record of meeting an animal
        hunter = engine.person(1, "Test", "m", -20 * 360, 1, woods[0][0], woods[0][1])
        u["people"] = [hunter]
        u["next_id"] = 2
        u["encounters"] = [[hunter["x"], hunter["y"], "deer", 100, 0]]
        world = {"eden": engine.genesis_universe("EDEN", 1, iteration=1),
                 "lagoon": u,
                 "clock": {"epoch": 0.0, "parts": 0, "seconds": 0.6},
                 "sec_per_day": 2.4}
        snap = engine.summarize(world)
        self.assertIn("encounters", snap["u"]["lagoon"])
        self.assertEqual(snap["u"]["lagoon"]["encounters"],
                         [[hunter["x"], hunter["y"], "deer", 100, 0]])


if __name__ == "__main__":
    unittest.main()
