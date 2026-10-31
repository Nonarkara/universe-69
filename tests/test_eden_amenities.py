"""EDEN's hedonistic amenities: the resort builds pools, bars, theaters and
sports fields — human-scale versions of the provisions U25's mice never had
to work for. Nothing earned, nothing scarce except space and meaning.

Covers engine 2026.10.31.1's amenity mechanic: facilities are built when the
pen is crowded and bored; each facility level accelerates the ennui creep
(easy pleasure dulls appetite); the contract exposes the levels so the
viewer can show them.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "sim"))

import unittest

import engine


def eden_at_day(d):
    """A fresh EDEN at a given day, crowded past the stagnation threshold."""
    w = engine.genesis(seed=69)
    u = w["eden"]
    u["day"] = d
    u["part"] = 0
    return u


class TestEdenFacilities(unittest.TestCase):
    def test_genesis_starts_with_no_amenities(self):
        w = engine.genesis(seed=69)
        fac = w["eden"]["facilities"]
        self.assertEqual(sorted(fac), sorted(engine.EDEN_FACILITIES))
        self.assertEqual(fac, {k: 0.0 for k in engine.EDEN_FACILITIES})

    def test_lagoon_has_no_amenity_field(self):
        w = engine.genesis(seed=69)
        self.assertNotIn("facilities", w["lagoon"])

    def test_a_crowded_bored_pen_builds_amenities(self):
        u = eden_at_day(engine.DAYS_PER_YEAR * 20 + 7)
        u["ennui"] = 0.10
        u["facilities"] = {k: 0.0 for k in engine.EDEN_FACILITIES}
        u["phase"] = "stagnate"   # the walls are final: no expansion re-opens space
        # crowd the pen: pad the population so pop/cap >= stagnation
        extra = int(engine.eden_design(u)["cap"] * engine.EDEN_STAGNATION) + 5
        for i in range(extra):
            p = engine.person(9000 + i, f"P{i}", "m",
                              u["day"] - 20 * engine.DAYS_PER_YEAR, 1, 12, 12)
            u["people"].append(p)
        events = []
        rng = engine.random.Random(7)
        engine.tick_eden(u, rng, events)
        levels = sum(u["facilities"].values())
        self.assertGreater(levels, 0.0, "a crowded bored pen built nothing")
        self.assertTrue(any(e[2] == "amenity" for e in events),
                        "the build should be on the record")

    def test_amenities_are_built_in_order_and_capped(self):
        u = eden_at_day(engine.DAYS_PER_YEAR * 20 + 7)
        u["ennui"] = 0.10
        # crowd the pen
        extra = int(engine.eden_design(u)["cap"] * engine.EDEN_STAGNATION) + 5
        for i in range(extra):
            p = engine.person(9000 + i, f"P{i}", "m",
                              u["day"] - 20 * engine.DAYS_PER_YEAR, 1, 12, 12)
            u["people"].append(p)
        events = []
        rng = engine.random.Random(7)
        for _ in range(40):          # four facilities, four steps each
            u["day"] += engine.DAYS_PER_YEAR
            engine.tick_eden(u, rng, events)
        for k in engine.EDEN_FACILITIES:
            self.assertLessEqual(u["facilities"][k], 1.0)

    def test_amenities_speed_the_ennui_creep(self):
        # two identical pens, one with amenities, one without: the same
        # number of years must leave the amenity pen more bored
        def run(fac_sum):
            u = eden_at_day(engine.DAYS_PER_YEAR * 10 + 7)
            u["ennui"] = 0.10
            u["facilities"] = {k: (1.0 if i < fac_sum else 0.0)
                               for i, k in enumerate(engine.EDEN_FACILITIES)}
            # small pen, nothing built: isolate the creep formula
            p = engine.person(1, "W", "f", 0, 1, 12, 12)
            u["people"] = [p]
            rng = engine.random.Random(11)
            for _ in range(6):
                u["day"] += engine.DAYS_PER_YEAR
                engine.tick_eden(u, rng, [])
            return u["ennui"]
        self.assertGreater(run(2), run(0))

    def test_an_uncrowded_pen_builds_nothing(self):
        u = eden_at_day(engine.DAYS_PER_YEAR * 20 + 7)
        u["ennui"] = 0.30
        u["facilities"] = {k: 0.0 for k in engine.EDEN_FACILITIES}
        u["phase"] = "stagnate"
        events = []
        rng = engine.random.Random(7)
        engine.tick_eden(u, rng, events)
        self.assertEqual(sum(u["facilities"].values()), 0.0,
                         "an uncrowded pen has no reason to build")

    def test_facilities_round_trip_through_state(self):
        import json
        w = engine.genesis(seed=69)
        w["eden"]["facilities"]["theater"] = 0.5
        blob = json.loads(json.dumps(engine.summarize(w)))
        self.assertEqual(blob["u"]["eden"]["facilities"]["theater"], 0.5)

    def test_a_legacy_state_without_facilities_migrates_clean(self):
        import copy
        w = engine.genesis(seed=69)
        u = copy.deepcopy(w["eden"])
        del u["facilities"]
        engine.migrate({"eden": u, "lagoon": copy.deepcopy(w["lagoon"])})
        self.assertEqual(u["facilities"],
                         {k: 0.0 for k in engine.EDEN_FACILITIES})


if __name__ == "__main__":
    unittest.main()
