"""Engine behaviour tests.

The engine has no dependencies, so the suite has none either. Run it with:

    python3 -m unittest discover -s tests

Anything that changes sim/engine.py must keep this green.
"""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))

import engine  # noqa: E402


def run(world, days):
    events = []
    for _ in range(days):
        engine.tick_world(world, events)
    return events


def canon(world):
    """A stable string for a world, ignoring the wall clock.

    `summarize` stamps `wall` with time.time(), so two runs of the same seed
    differ there by construction. Everything else must match exactly.
    """
    snap = engine.summarize(world)
    snap.pop("wall", None)
    return json.dumps(snap, sort_keys=True, default=str)


class TestGenesis(unittest.TestCase):
    def test_two_universes_are_created(self):
        w = engine.genesis(seed=69)
        self.assertEqual(w["seed"], 69)
        self.assertEqual(w["sec_per_day"], 2.0)
        self.assertIn("epoch", w)
        for key, kind in (("eden", "EDEN"), ("lagoon", "LAGOON")):
            u = w[key]
            self.assertEqual(u["kind"], kind)
            self.assertEqual(u["day"], 0)
            self.assertEqual(u["iteration"], 1)
            self.assertEqual(len(u["people"]), 4)
            self.assertEqual(u["phase"], "strive")
            self.assertIsNone(u["extinct_day"])

    def test_founding_pairs_are_paired(self):
        w = engine.genesis(seed=69)
        for key in ("eden", "lagoon"):
            people = w[key]["people"]
            self.assertEqual(people[0]["p"], people[1]["id"])
            self.assertEqual(people[1]["p"], people[0]["id"])
            self.assertEqual(people[2]["p"], people[3]["id"])
            self.assertEqual(people[3]["p"], people[2]["id"])
            self.assertEqual({p["s"] for p in people}, {"m", "f"})

    def test_eden_founders_are_lab_ids_and_lagoon_founders_are_named(self):
        w = engine.genesis(seed=69)
        for p in w["eden"]["people"]:
            self.assertTrue(p["n"].startswith("E-"))
        for p in w["lagoon"]["people"]:
            self.assertFalse(p["n"].startswith("E-"))
            self.assertTrue(p["n"][0].isupper())

    def test_lagoon_starts_innocent_and_without_technology(self):
        w = engine.genesis(seed=69)
        lag = w["lagoon"]
        self.assertTrue(lag["innocent"])
        self.assertEqual(lag["tech"], [])
        self.assertEqual(len(lag["settlements"]), 1)


class TestDeterminism(unittest.TestCase):
    def test_same_seed_gives_the_same_world(self):
        a = engine.genesis(seed=69)
        b = engine.genesis(seed=69)
        run(a, 500)
        run(b, 500)
        self.assertEqual(canon(a), canon(b))

    def test_different_seeds_diverge(self):
        a = engine.genesis(seed=69)
        b = engine.genesis(seed=70)
        run(a, 500)
        run(b, 500)
        self.assertNotEqual(canon(a), canon(b))

    def test_day_advance_is_exactly_one_per_tick(self):
        w = engine.genesis(seed=69)
        run(w, 37)
        self.assertEqual(w["eden"]["day"], 37)
        self.assertEqual(w["lagoon"]["day"], 37)


class TestPersistence(unittest.TestCase):
    def test_save_load_round_trip_preserves_the_world(self):
        """save -> load -> save must converge, then stay byte-identical.

        The first save of a world can differ from the second: `load_state`
        runs `migrate`, which fills in defaults the live dict may not have
        yet (`mom` on the founders, for one). That is a one-time convergence
        to the current on-disk format. From then on the file must not move —
        a state that changes shape every save is a state nobody can trust.
        """
        w = engine.genesis(seed=69)
        run(w, 400)
        with tempfile.TemporaryDirectory() as d:
            p1 = os.path.join(d, "state.json")
            p2 = os.path.join(d, "state2.json")
            p3 = os.path.join(d, "state3.json")
            engine.save_state(w, p1)
            loaded = engine.load_state(p1)
            engine.save_state(loaded, p2)
            reloaded = engine.load_state(p2)
            engine.save_state(reloaded, p3)
            with open(p2) as f:
                second = f.read()
            with open(p3) as f:
                third = f.read()
        self.assertEqual(second, third,
                         "the on-disk state format is not stable")
        # compare against the migrated world, not the pre-migration one:
        # `migrate` legitimately adds defaults such as `mom`
        for key in ("eden", "lagoon"):
            self.assertEqual(w[key]["day"], loaded[key]["day"])
            self.assertEqual(len(w[key]["people"]), len(loaded[key]["people"]))
            self.assertEqual(loaded[key]["people"][0],
                             reloaded[key]["people"][0])
            self.assertEqual(loaded[key]["people"][-1],
                             reloaded[key]["people"][-1])

    def test_state_is_json_serialisable(self):
        w = engine.genesis(seed=69)
        run(w, 200)
        json.dumps(w)  # must not raise

    def test_migrate_fills_in_fields_added_after_a_run_started(self):
        """A live world saved by an older engine must survive an upgrade."""
        w = engine.genesis(seed=69)
        run(w, 100)
        old = json.loads(json.dumps(w))
        for key in ("eden", "lagoon"):
            old[key].pop("lessons", None)
            old[key].pop("postmortems", None)
            old[key].pop("ennui", None)
            old[key].pop("std_years", None)
            old[key].pop("wary_years", None)
            old[key].pop("box_occ", None)
            old[key].pop("hop_n", None)
            old[key].pop("culture", None)
            old[key].pop("continent", None)
            for p in old[key]["people"]:
                p.pop("a", None)
                p.pop("ad", None)
                p.pop("box", None)
                p.pop("mom", None)
        fixed = engine.migrate(old)
        self.assertEqual(fixed["eden"]["lessons"], [])
        self.assertEqual(fixed["lagoon"]["culture"], [])
        self.assertFalse(fixed["lagoon"]["continent"])
        self.assertIn("box_occ", fixed["eden"])
        self.assertIn("ennui", fixed["eden"])
        for p in fixed["eden"]["people"]:
            self.assertIn("a", p)
            self.assertIn("box", p)

    def test_internal_context_is_not_persisted(self):
        w = engine.genesis(seed=69)
        run(w, 50)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "state.json")
            engine.save_state(w, path)
            with open(path) as f:
                raw = json.load(f)
        self.assertNotIn("_ctx", raw["eden"])
        self.assertNotIn("_ctx", raw["lagoon"])


class TestBounds(unittest.TestCase):
    def test_eden_people_stay_inside_the_pen(self):
        w = engine.genesis(seed=69)
        run(w, 1200)
        for p in w["eden"]["people"]:
            self.assertGreaterEqual(p["x"], 2)
            self.assertLessEqual(p["x"], engine.EDEN_SIZE - 3)
            self.assertGreaterEqual(p["y"], 2)
            self.assertLessEqual(p["y"], engine.EDEN_SIZE - 3)

    def test_lagoon_people_stay_on_land(self):
        w = engine.genesis(seed=69)
        run(w, 1200)
        terr = engine.terrain_of(w["lagoon"])
        for p in w["lagoon"]["people"]:
            self.assertNotEqual(terr[p["y"]][p["x"]], 2,
                                "someone walked into the sea")

    def test_people_stay_on_the_map(self):
        w = engine.genesis(seed=69)
        run(w, 900)
        for p in w["lagoon"]["people"]:
            self.assertGreaterEqual(p["x"], 1)
            self.assertLessEqual(p["x"], engine.LAGOON_SIZE - 2)
            self.assertGreaterEqual(p["y"], 1)
            self.assertLessEqual(p["y"], engine.LAGOON_SIZE - 2)


class TestEden(unittest.TestCase):
    def test_phase_progression_reaches_stagnation(self):
        w = engine.genesis(seed=69)
        events = run(w, 20000)
        kinds = [e[3].lower() for e in events if e[2] == "phase"]
        self.assertTrue(any("exploit" in k for k in kinds))
        self.assertTrue(any("stagnation" in k for k in kinds))

    def test_children_are_born_with_a_sequential_id(self):
        w = engine.genesis(seed=69)
        run(w, 3000)
        u = w["eden"]
        self.assertGreater(u["next_id"], 5)
        ids = [p["id"] for p in u["people"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_nest_boxes_are_a_finite_number(self):
        self.assertGreater(len(engine.EDEN_BOXES), 0)
        self.assertLess(len(engine.EDEN_BOXES), engine.EDEN_SIZE * 4)

    def test_census_is_recorded_and_bounded(self):
        w = engine.genesis(seed=69)
        run(w, engine.DAYS_PER_YEAR * 3)
        u = w["eden"]
        self.assertGreaterEqual(len(u["census"]), 2)
        self.assertLessEqual(len(u["census"]), 400)


class TestLagoon(unittest.TestCase):
    def test_technology_ladder_respects_prerequisites(self):
        w = engine.genesis(seed=69)
        run(w, 60000)
        tech = w["lagoon"]["tech"]
        for name, prereq, _base, _minpop in engine.TECH_LADDER:
            if name in tech and prereq:
                self.assertIn(prereq, tech,
                              f"{name} was discovered without {prereq}")

    def test_terrain_is_deterministic_for_a_seed(self):
        a = engine.make_lagoon_terrain(502)
        b = engine.make_lagoon_terrain(502)
        self.assertEqual(a, b)
        self.assertNotEqual(a, engine.make_lagoon_terrain(503))

    def test_terrain_has_land_water_and_beach(self):
        terr = engine.make_lagoon_terrain(502)
        kinds = {k for row in terr for k in row}
        self.assertIn(0, kinds)   # grass
        self.assertIn(1, kinds)   # woods
        self.assertIn(2, kinds)   # water
        self.assertIn(3, kinds)   # beach

    def test_the_settlement_starts_on_land(self):
        w = engine.genesis(seed=69)
        terr = engine.terrain_of(w["lagoon"])
        for s in w["lagoon"]["settlements"]:
            self.assertNotEqual(terr[s["y"]][s["x"]], 2)


class TestPenDesign(unittest.TestCase):
    """The pen's architecture is a parameter, so a study can vary it.

    Calhoun's own conclusion — and the critique recorded in RESEARCH.md — is
    that the outcome tracks the design of the pen, not crowding as a number.
    A design that cannot be changed cannot be studied.
    """

    def test_default_design_matches_the_pen_as_built(self):
        w = engine.genesis(seed=69)
        d = engine.eden_design(w["eden"])
        self.assertEqual(d["cap"], engine.EDEN_CAP)
        self.assertEqual(d["stagnation"], engine.EDEN_STAGNATION)
        self.assertEqual(d["box_cap"], engine.EDEN_BOX_CAP)
        self.assertEqual(d["boxes"], engine.EDEN_BOXES)

    def test_boxes_can_be_changed(self):
        boxes = engine.make_boxes(64)
        self.assertEqual(len(boxes), 64)
        for x, y in boxes:
            self.assertTrue(0 <= x < engine.EDEN_SIZE)
            self.assertTrue(0 <= y < engine.EDEN_SIZE)
        # every box is against a wall
        for x, y in boxes:
            on_wall = (x <= 5 or x >= engine.EDEN_SIZE - 6 or
                       y <= 5 or y >= engine.EDEN_SIZE - 6)
            self.assertTrue(on_wall, f"box {x},{y} is not against a wall")

    def test_make_boxes_reproduces_the_original_layout(self):
        self.assertEqual(engine.make_boxes(32), engine.EDEN_BOXES)

    def test_set_pen_design_changes_the_pen(self):
        w = engine.genesis(seed=69)
        engine.set_pen_design(w["eden"], cap=3840, stagnation=0.157,
                              boxes=256, box_cap=15)
        d = engine.eden_design(w["eden"])
        self.assertEqual(d["cap"], 3840)
        self.assertEqual(d["stagnation"], 0.157)
        self.assertEqual(len(d["boxes"]), 256)
        self.assertEqual(d["box_cap"], 15)

    def test_a_live_world_without_design_fields_keeps_its_pen(self):
        old = engine.genesis(seed=69)
        for p in old["eden"]["people"]:
            p.pop("mom", None)
        for k in ("cap", "stagnation", "box_cap"):
            old["eden"].pop(k, None)
        fixed = engine.migrate(old)
        d = engine.eden_design(fixed["eden"])
        self.assertEqual(d["cap"], engine.EDEN_CAP)
        self.assertEqual(d["boxes"], engine.EDEN_BOXES)


class TestExtinctionAndPostmortems(unittest.TestCase):
    def test_emptying_a_universe_writes_a_postmortem(self):
        w = engine.genesis(seed=69)
        u = w["eden"]
        u["people"] = []
        events = []
        engine.tick_eden(u, __import__("random").Random(1), events)
        self.assertIsNotNone(u["extinct_day"])
        self.assertEqual(len(u["postmortems"]), 1)
        pm = u["postmortems"][0]
        self.assertEqual(pm["iteration"], 1)
        self.assertIn("dominant_cause", pm)
        self.assertFalse(pm["preventable"])   # EDEN cannot learn

    def test_eden_postmortem_declares_the_pen_the_cause(self):
        w = engine.genesis(seed=69)
        u = w["eden"]
        u["people"] = []
        u["cod"] = {"violence": 10, "age": 2}
        events = []
        engine.tick_eden(u, __import__("random").Random(1), events)
        self.assertEqual(u["postmortems"][0]["dominant_cause"], "violence")
        self.assertIsNone(u["postmortems"][0]["lesson"])
        self.assertTrue(any("pen itself" in e[3] for e in events))

    def test_lagoon_postmortem_derives_a_lesson_from_the_dominant_cause(self):
        w = engine.genesis(seed=69)
        u = w["lagoon"]
        u["people"] = []
        u["cod"] = {"starvation": 20, "age": 1}
        events = []
        engine.tick_lagoon(u, __import__("random").Random(1), events)
        pm = u["postmortems"][0]
        self.assertEqual(pm["dominant_cause"], "starvation")
        self.assertEqual(pm["lesson"], "preserve")
        self.assertTrue(pm["preventable"])

    def test_lessons_map_to_known_instincts(self):
        for cause, lesson in engine.LESSON_OF.items():
            self.assertIn(lesson, ("preserve", "vigilance", "cleanliness", "unity"))

    def test_a_reseed_carries_the_lesson_forward(self):
        w = engine.genesis(seed=69)
        u = w["lagoon"]
        u["people"] = []
        u["cod"] = {"starvation": 20}
        events = []
        engine.tick_lagoon(u, __import__("random").Random(1), events)
        # force the reseed window open
        u["extinct_day"] = u["day"] - (engine.RESEED_YEARS * engine.DAYS_PER_YEAR + 1)
        u["people"] = []
        engine.tick_lagoon(u, __import__("random").Random(2), events)
        self.assertEqual(u["iteration"], 2)
        self.assertIn("preserve", u["lessons"])
        self.assertGreater(u["store"], 0)


class TestRecord(unittest.TestCase):
    def test_famine_is_one_line_for_the_day(self):
        self.assertEqual(engine.famine_line(["Nami"]),
                         "Nami starves in the lean season.")
        line = engine.famine_line(["A", "B", "C", "D", "E"])
        self.assertTrue(line.startswith("5 starve"))
        self.assertIn("and 2 others", line)

    def test_culture_verb_agrees_with_number(self):
        self.assertEqual(engine.culture_verb("cave paintings"), "appear")
        self.assertEqual(engine.culture_verb("drum songs"), "appear")
        self.assertEqual(engine.culture_verb("the dance of the tides"), "appears")
        self.assertEqual(engine.culture_verb("shell jewelry"), "appears")

    def test_new_fields_are_not_dug_in_the_water(self):
        import random
        u = engine.genesis_universe("LAGOON", 99)
        terr = engine.terrain_of(u)
        rng = random.Random(1)
        for _ in range(40):
            self.assertTrue(engine.till_near(u, rng, u["settlements"][0], 8))
        for x, y in u["farms"]:
            self.assertNotEqual(terr[y][x], 2, (x, y))


if __name__ == "__main__":
    unittest.main()
