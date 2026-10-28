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

SCRATCH = os.path.join(tempfile.gettempdir(), "universe69-audit-tests")
os.makedirs(SCRATCH, exist_ok=True)


def run(world, days):
    """Advance a world by whole days.

    The tick is a part of a day — dawn, day, dusk, night — and the day's
    counter turns when the night ends, so four ticks make a day.
    """
    events = []
    for _ in range(days * engine.PARTS_PER_DAY):
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
        self.assertEqual(w["sec_per_day"],
                         engine.SEC_PER_PART * engine.PARTS_PER_DAY)
        self.assertIn("epoch", w)
        for key, kind in (("eden", "EDEN"), ("lagoon", "LAGOON")):
            u = w[key]
            self.assertEqual(u["kind"], kind)
            self.assertEqual(u["day"], 0)
            self.assertEqual(u["iteration"], 1)
            self.assertEqual(len(u["people"]), 2 * engine.FOUNDER_PAIRS)
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

    def test_both_universes_receive_the_same_founders(self):
        """Same people, different world: the world is the only variable."""
        w = engine.genesis(seed=69)
        key = lambda p: (p["n"], p["s"], p["ef"], p["ag"])
        self.assertEqual([key(p) for p in w["eden"]["people"]],
                         [key(p) for p in w["lagoon"]["people"]])
        for p in w["eden"]["people"]:
            self.assertTrue(p["n"][0].isupper())

    def test_a_reseed_sends_eight_pairs_of_the_same_people(self):
        e = engine.genesis_universe("EDEN", 1, iteration=2, fseed=69)
        l = engine.genesis_universe("LAGOON", 2, iteration=2, fseed=69)
        self.assertEqual(len(e["people"]), 16)
        self.assertEqual([p["n"] for p in e["people"]], [p["n"] for p in l["people"]])
        for i in range(0, 16, 2):
            self.assertEqual(e["people"][i]["p"], e["people"][i + 1]["id"])

    def test_both_universes_start_innocent(self):
        w = engine.genesis(seed=69)
        self.assertTrue(w["eden"]["innocent"])
        self.assertTrue(w["lagoon"]["innocent"])

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

    def test_a_day_is_four_parts_and_turns_at_the_dawn(self):
        w = engine.genesis(seed=69)
        run(w, 37)
        self.assertEqual(w["eden"]["day"], 37)
        self.assertEqual(w["lagoon"]["day"], 37)
        self.assertEqual(w["eden"]["parts"], 37 * engine.PARTS_PER_DAY)

    def test_the_parts_run_dawn_day_dusk_night(self):
        w = engine.genesis(seed=69)
        seen = []
        for _ in range(engine.PARTS_PER_DAY):
            seen.append(w["eden"]["part"])
            engine.tick_world(w, [])
        self.assertEqual(seen, list(range(engine.PARTS_PER_DAY)))
        self.assertEqual(engine.PART_NAMES[w["eden"]["part"]], "dawn")


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
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
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
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
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
        # Two resort expansions postpone the sink; it still comes. On the
        # four-part day the sink arrives in year 133 rather than 83, so the
        # horizon has to be longer than it was (DESIGN.md, 2026.10.28.2).
        w = engine.genesis(seed=69)
        events = run(w, 160 * engine.DAYS_PER_YEAR)
        kinds = [e[3].lower() for e in events if e[2] == "phase"]
        self.assertTrue(any("exploit" in k for k in kinds))
        # Since 2026.10.28.3 the sink is not a phase reached but a thing
        # that happens: withdrawal and infant loss rise out of crowding.
        # The 35% label is the pen's design and may come later or not at all.
        u = w["eden"]
        self.assertTrue(any(p["w"] for p in u["people"]), "nobody withdrew")
        self.assertGreater(u["cod"].get("infant", 0), 0, "no infant was lost")

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

    def test_a_postmortem_says_which_engine_wrote_it(self):
        # A published figure must be traceable to the code that produced it.
        w = engine.genesis(seed=69)
        u = w["eden"]
        u["people"] = []
        engine.tick_eden(u, __import__("random").Random(1), [])
        pm = u["postmortems"][0]
        self.assertEqual(pm["engine"], engine.ENGINE_VERSION)
        self.assertRegex(pm["engine"], r"^\d{4}\.\d{2}\.\d{2}\.\d+$")

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
        # the lesson is a habit, not free food: their stores rot slower
        import needs
        u["settlements"][0]["store"] = 100.0
        needs.keep_stores(u)
        self.assertGreater(u["settlements"][0]["store"], 100.0 * (1 - needs.SPOIL["none"]))


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

    def test_a_fall_is_not_reported_as_old_age(self):
        # 6e-6 a person a day, so this takes a few decades of sim time.
        # The point is the bucket: a fall must not also be booked as old age.
        import random
        u = engine.genesis_universe("LAGOON", 69)
        rng = random.Random(69)
        before = {}
        for _ in range(40000 * engine.PARTS_PER_DAY):
            before = dict(u["cod"])
            engine.tick_lagoon(u, rng, [])
            if u["cod"].get("accident", 0) > before.get("accident", 0):
                break
        else:
            self.fail("no accident in 40000 days; the branch may be dead")
        self.assertEqual(u["cod"].get("age", 0), before.get("age", 0),
                         "a fall was also counted as old age")
        self.assertGreater(u["cod"]["accident"], before.get("accident", 0))


class TestMinds(unittest.TestCase):
    """The same Stone-Age brain in two worlds (DESIGN.md, 'Minds and bodies')."""

    @classmethod
    def setUpClass(cls):
        # LAGOON's first iteration dies in its fifth year and the world is
        # reseeded; its second lives to about year 140. So the two worlds
        # are compared in year 125, when both of them are alive, and the
        # pen is run on to year 160 so that the withdrawal has begun.
        cls.world = engine.genesis(seed=69)
        run(cls.world, 125 * engine.DAYS_PER_YEAR)
        cls.compared = {k: cls.means_of(k) for k in ("eden", "lagoon")}
        run(cls.world, 35 * engine.DAYS_PER_YEAR)

    @classmethod
    def means_of(cls, key):
        u = cls.world[key]
        a = [p for p in u["people"] if engine.age_of(p, u["day"]) >= engine.ADULT_AGE]
        if not a:
            return {}
        return {f: sum(p[f] for p in a) / len(a)
                for f in ("bmi", "sn", "pu")}

    def adults(self, key):
        u = self.world[key]
        return [p for p in u["people"] if engine.age_of(p, u["day"]) >= engine.ADULT_AGE]

    def mean(self, key, field):
        a = self.adults(key)
        return sum(p[field] for p in a) / len(a)

    def test_the_resort_fattens_and_weakens_its_people(self):
        eden, lagoon = self.compared["eden"], self.compared["lagoon"]
        self.assertTrue(eden and lagoon,
                        "both worlds must have adults in year 125 to compare")
        self.assertGreater(eden["bmi"], lagoon["bmi"] + 4)
        self.assertLess(eden["sn"], lagoon["sn"])

    def test_purpose_drains_where_nothing_is_asked(self):
        eden, lagoon = self.compared["eden"], self.compared["lagoon"]
        self.assertTrue(eden and lagoon,
                        "both worlds must have adults in year 125 to compare")
        self.assertLess(eden["pu"], lagoon["pu"] - 0.3)

    def test_the_withdrawn_keep_apart_from_the_living_pen(self):
        """Huddled men pool on the floor, women go to the top row of boxes,
        and none of them is in a circle, a couple or a fight."""
        u = self.world["eden"]
        top = min(b[1] for b in engine.eden_design(u)["boxes"])
        c = engine.eden_size(u) // 2
        w = [p for p in u["people"] if p["w"]]
        self.assertTrue(w, "no one has withdrawn in a hundred years of the pen")
        for p in w:
            self.assertNotIn(p["a"], (engine.A_TALK, engine.A_MATE, engine.A_FIGHT))
            self.assertIsNone(p["p"])
            if p["wk"] == engine.WK_UPSTAIRS:
                self.assertEqual(p["hy"], top)
            if p["wk"] == engine.WK_HUDDLE:
                self.assertLessEqual(abs(p["hx"] - c), 4)

    def test_children_inherit_from_both_parents(self):
        rng = engine.random.Random(1)
        mother = engine.person(1, "M", "f", 0, 1, 0, 0)
        mother["ef"], mother["fe"] = 0.9, [0.9, 0.5]
        kids = []
        for i in range(200):
            c = engine.person(10 + i, "C", "m", 0, 2, 0, 0)
            engine.minds.inherit(c, mother, rng)
            kids.append(c["ef"])
        self.assertGreater(sum(kids) / len(kids), 0.82)

    def test_mind_is_recorded_apart_from_culture(self):
        for key in ("eden", "lagoon"):
            m = self.world[key]["mind"]
            self.assertTrue(m)
            year, mean, tail, vg = m[-1]
            self.assertTrue(0 <= mean <= 1 and 0 <= tail <= 1 and 0 <= vg <= 1)


class TestResortAndIsland(unittest.TestCase):
    """EDEN's lodgings, posts and growth; LAGOON's boats and fire."""

    def test_the_resort_grows_when_crowded_and_stops_growing(self):
        u = engine.genesis(seed=69)["eden"]
        events = []
        rng = engine.random.Random(1)
        for _ in range(engine.EDEN_MAX_EXPANSIONS + 2):
            engine.expand_pen(u, rng, events)
        self.assertEqual(u["size"], engine.EDEN_SIZE + 2 * engine.EDEN_EXPAND_STEP * engine.EDEN_MAX_EXPANSIONS)
        self.assertEqual(u["expansions"], engine.EDEN_MAX_EXPANSIONS)
        S = u["size"]
        for x, y in engine.eden_design(u)["boxes"]:
            self.assertTrue(2 <= x <= S - 3 and 2 <= y <= S - 3)

    def test_posts_are_finite_and_filled_once(self):
        w = engine.genesis(seed=69)
        run(w, 40 * engine.DAYS_PER_YEAR)
        u = w["eden"]
        held = [r["who"] for r in u["roles"] if r["who"]]
        self.assertEqual(len(held), len(set(held)))
        alive = {p["id"] for p in u["people"]}
        self.assertTrue(set(held) <= alive)
        for p in u["people"]:
            if p.get("role") is not None:
                self.assertEqual(u["roles"][p["role"]]["who"], p["id"])

    def test_a_boat_is_built_before_anyone_crosses(self):
        u = engine.genesis(seed=69)["lagoon"]
        events = []
        crossed_with_boat = False
        for _ in range(130 * engine.DAYS_PER_YEAR * engine.PARTS_PER_DAY):
            rng = engine.random.Random((u["seed"] << 20) ^ (u["day"] + 1) ^ u["iteration"])
            engine.tick_lagoon(u, rng, events)
            if u.get("voyage"):
                aboard = [p for p in u["people"] if p.get("ab")]
                self.assertTrue(aboard)
                crossed_with_boat = True
        if any("crosses the strait" in e[3] or "lands on the greater shore" in e[3] for e in events):
            self.assertTrue(crossed_with_boat, "people reached the mainland without a boat")
            self.assertTrue(u.get("boats") or u.get("voyage"))

    def test_fertility_follows_age_body_and_nursing(self):
        p = engine.person(1, "W", "f", 0, 1, 0, 0)
        Y = engine.DAYS_PER_YEAR
        self.assertEqual(engine.minds.fertility(p, 12 * Y, 0), 0.0)
        self.assertAlmostEqual(engine.minds.fertility(p, 25 * Y, 0), 1.0)
        self.assertLess(engine.minds.fertility(p, 42 * Y, 0), 0.5)
        self.assertEqual(engine.minds.fertility(p, 51 * Y, 0), 0.0)
        p["bmi"] = 15.0
        self.assertEqual(engine.minds.fertility(p, 25 * Y, 0), 0.0)
        p["bmi"] = 22.0
        p["nurse"], p["nurse_len"] = 1000, 1000
        self.assertLess(engine.minds.fertility(p, 25 * Y, 10), 0.1)


class TestDayAndNight(unittest.TestCase):
    """A day has four parts, and the dark is a different place.

    Engine 2026.10.27.4: the tick is a part, not a day. See DESIGN.md,
    "Engine 2026.10.27.4: the day has four parts".
    """

    def _lagoon(self, seed=69):
        u = engine.genesis_universe("LAGOON", seed)
        u["tech"] = list(u.get("tech") or []) + ["fire", "stone_tools"]
        return u

    def test_a_day_is_four_parts_and_turns_at_the_dawn(self):
        w = engine.genesis(seed=69)
        run(w, 3)
        self.assertEqual(w["eden"]["day"], 3)
        self.assertEqual(w["eden"]["parts"], 3 * engine.PARTS_PER_DAY)
        self.assertEqual(w["eden"]["part"], 0)      # a day begins in the dawn

    def test_the_parts_run_dawn_day_dusk_night(self):
        u = engine.genesis_universe("LAGOON", 69)
        seen = []
        rng = __import__("random").Random(1)
        for _ in range(engine.PARTS_PER_DAY):
            seen.append(u.get("part", 0))
            engine.tick_lagoon(u, rng, [])
        self.assertEqual(seen, list(range(engine.PARTS_PER_DAY)))
        self.assertEqual([engine.PART_NAMES[i] for i in seen],
                         ["dawn", "day", "dusk", "night"])

    def test_the_snapshot_says_which_part_of_the_day_it_is(self):
        w = engine.genesis(seed=69)
        snap = engine.summarize(w)
        for key in ("eden", "lagoon"):
            self.assertIn(snap["u"][key]["tod"], engine.PART_NAMES)
            self.assertEqual(snap["u"][key]["night"],
                             snap["u"][key]["tod"] == "night")

    def test_the_first_winter_does_not_starve_the_lagoon(self):
        """A day that is four parts must not make every rate four times
        faster.

        This is the regression test for the worst bug of the four-part day:
        the band's food, its activities and its conceptions were all
        written in days and were left running once a part, so LAGOON
        starved to death in its ninth year. The world has to still be a
        world in the fifteenth year.
        """
        import random
        u = engine.genesis_universe("LAGOON", 69)
        rng = random.Random(69)
        for _ in range(5000 * engine.PARTS_PER_DAY):
            engine.tick_lagoon(u, rng, [])
        if u["extinct_day"] is not None:
            self.fail("LAGOON died in year %d" % (u["extinct_day"] // 360))
        self.assertGreaterEqual(len(u["people"]), 3,
                                "the lagoon is empty in the fifteenth year")

    def test_a_person_keeps_the_same_job_for_the_length_of_a_day(self):
        """A stint of seven days is seven days, not seven ticks.

        If the durations are not converted, everybody changes what they
        are doing four times a day, and no activity means anything.
        """
        import random
        u = engine.genesis_universe("LAGOON", 69)
        rng = random.Random(69)
        for _ in range(60 * engine.PARTS_PER_DAY):
            engine.tick_lagoon(u, rng, [])
        before = {p["id"]: p.get("a") for p in u["people"]}
        for _ in range(engine.PARTS_PER_DAY):
            engine.tick_lagoon(u, rng, [])
        changed = sum(1 for p in u["people"]
                      if before.get(p["id"]) not in (None, p.get("a")))
        self.assertLessEqual(changed, max(1, len(u["people"]) // 4),
                              "%d of %d people changed their job inside one "
                              "day" % (changed, len(u["people"])))

    def test_at_night_the_band_comes_in_to_the_fire(self):
        import random
        u = self._lagoon()
        st = u["settlements"][0]
        fx, fy = st["x"] + 2, st["y"] + 1
        rng = random.Random(1)
        night = False
        for _ in range(engine.PARTS_PER_DAY * 4):
            part = u.get("part", 0)
            engine.tick_lagoon(u, rng, [])
            if part == engine.PART_NIGHT:
                night = True
                break
        self.assertTrue(night, "the night never came round")
        adults = [p for p in u["people"]
                  if engine.age_of(p, u["day"]) >= engine.ADULT_AGE and not p["w"]]
        near = [p for p in adults
                if abs(p["tx"] - fx) <= 3 and abs(p["ty"] - fy) <= 3]
        self.assertTrue(near, "nobody came in to the fire")

    def test_the_watch_turns_over(self):
        import random
        u = self._lagoon()
        rng = random.Random(1)
        watchers = []
        for _ in range(engine.PARTS_PER_DAY * 10):
            part = u.get("part", 0)
            engine.tick_lagoon(u, rng, [])
            if part == engine.PART_NIGHT:
                watchers.append(u["settlements"][0].get("watch"))
        self.assertTrue(any(w for w in watchers), "nobody ever stood watch")
        self.assertGreater(len(set(watchers)), 1,
                           "the watch never turned over — one person kept it")

    def test_the_watcher_pays_for_the_night(self):
        import random
        u = self._lagoon()
        rng = random.Random(1)
        for _ in range(engine.PARTS_PER_DAY * 10):
            part = u.get("part", 0)
            before = {p["id"]: p.get("hun", 0.0) for p in u["people"]}
            engine.tick_lagoon(u, rng, [])
            if part == engine.PART_NIGHT:
                wid = u["settlements"][0].get("watch")
                if not wid:
                    continue
                w = next((p for p in u["people"] if p["id"] == wid), None)
                self.assertIsNotNone(w, "the watcher was not in the band")
                self.assertGreater(w.get("hun", 0.0), before.get(wid, 0.0),
                                   "the watcher paid nothing for the night")
                return
        self.fail("nobody stood watch")

    def test_a_predator_becomes_food_once_they_can_hunt_it(self):
        # Since 2026.10.28.4 the cat is an animal with a place (animals.py):
        # a party of armed hunters next to it can bring it down, and it
        # comes home as a load of meat.
        import random
        import animals
        u = self._lagoon()
        u["tech"] = list(u["tech"]) + ["stone_tools", "predator_hunt"]
        terr = engine.terrain_of(u)
        animals.ensure(u, random.Random(1), terr)
        st = u["settlements"][0]
        cat = {"i": 9999, "k": animals.CAT, "x": st["x"], "y": st["y"],
               "tx": st["x"], "ty": st["y"], "hx": st["x"], "hy": st["y"], "fed": 0.0}
        u["animals"] = [cat]
        party = [p for p in u["people"] if engine.age_of(p, u["day"]) >= engine.ADULT_AGE][:4]
        for p in party:
            p["a"], p["x"], p["y"], p["carry"] = engine.A_HUNT, st["x"] + 1, st["y"], 0.0
        ctx = {"day": u["day"], "part": 1, "night": False, "events": [],
               "adult": lambda q: True, "has": lambda t: t in u["tech"], "armed": True,
               "lessons": [], "A_HUNT": engine.A_HUNT}
        rng = random.Random(3)
        for _ in range(40):
            animals.tick(u, rng, terr, party, ctx)
            for p in party:
                engine.step_toward(p, terr, engine.LAGOON_WALK)
            if not any(q["k"] == animals.CAT for q in u["animals"]):
                break
        self.assertGreater(u.get("kills", 0), 0, "the big cat was never brought down")
        self.assertGreater(sum(p["carry"] for p in party), 0, "the carcass was not food")

    def test_without_the_technology_the_predator_is_only_a_death(self):
        import random
        u = self._lagoon()
        rng = random.Random(3)
        for _ in range(engine.PARTS_PER_DAY * 60):
            for p in u["people"]:
                p["a"] = engine.A_HUNT
            engine.tick_lagoon(u, rng, [])
        self.assertEqual(u.get("kills", 0), 0,
                         "they hunted the big cat without knowing how")

    def test_eden_sleeps_at_night(self):
        w = engine.genesis(seed=69)
        run(w, 30)
        u = w["eden"]
        rng = __import__("random").Random(1)
        slept = False
        for _ in range(engine.PARTS_PER_DAY * 3):
            part = u.get("part", 0)
            engine.tick_eden(u, rng, [])
            if part == engine.PART_NIGHT:
                asleep = [p for p in u["people"]
                          if p.get("a") == engine.A_SLEEP
                          and engine.age_of(p, u["day"]) >= engine.ADULT_AGE]
                self.assertTrue(asleep, "nobody slept in the pen at night")
                slept = True
                break
        self.assertTrue(slept, "the night never came round")

    def test_an_old_state_file_knows_what_part_of_the_day_it_is(self):
        w = engine.genesis(seed=69)
        w["eden"].pop("part", None)
        w["eden"].pop("parts", None)
        back = engine.migrate(w)
        self.assertEqual(back["eden"]["part"], 0)
        self.assertEqual(back["eden"]["parts"], 0)


class TestQuarterDayAudit(unittest.TestCase):
    def test_empty_worlds_keep_time_and_reseed_without_resetting_the_clock(self):
        w = engine.genesis(seed=69)
        day = engine.RESEED_YEARS * engine.DAYS_PER_YEAR + 1
        for u in (w["eden"], w["lagoon"]):
            u["people"] = []
            u["extinct_day"] = 0
            u["day"], u["part"], u["parts"] = day, 3, day * 4 + 3
        engine.tick_world(w, [])
        for u in (w["eden"], w["lagoon"]):
            self.assertEqual(u["iteration"], 2)
            self.assertEqual((u["day"], u["part"], u["parts"]), (day + 1, 0, (day + 1) * 4))
            self.assertEqual(u["founded_day"], day)

    def test_extinction_wait_advances_in_both_worlds(self):
        w = engine.genesis(seed=69)
        for u in (w["eden"], w["lagoon"]):
            u["people"] = []
        run(w, 2)
        for u in (w["eden"], w["lagoon"]):
            self.assertEqual(u["day"], 2)
            self.assertEqual(u["parts"], 8)
            self.assertIsNotNone(u["extinct_day"])

    def test_legacy_clock_does_not_replay_existing_calendar_days(self):
        w = engine.genesis(seed=69)
        w.pop("clock")
        w["epoch"], w["sec_per_day"] = 1000, 2
        for u in (w["eden"], w["lagoon"]):
            u["day"] = 40000
            u.pop("part")
            u.pop("parts")
        engine.migrate(w)
        self.assertEqual(w["eden"]["parts"], 160000)
        self.assertEqual(engine.target_parts(w, now=81000), 160000)
        self.assertEqual(engine.target_parts(w, now=81012), 160004)
        self.assertEqual(w["sec_per_day"], 12)

    def test_pace_change_preserves_due_ticks_and_restart_anchor(self):
        w = engine.genesis(seed=69)
        w["clock"] = {"epoch": 1000, "parts": 400, "seconds": 3}
        engine.set_clock_pace(w, 1, now=1030)
        self.assertEqual(engine.target_parts(w, now=1030), 410)
        self.assertEqual(engine.target_parts(w, now=1034), 414)
        c = dict(w["clock"])
        engine.set_clock_pace(w, 1, now=1040)
        self.assertEqual(c, w["clock"])
        for seconds in (0, -1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                engine.set_clock_pace(w, seconds)

    def test_resumed_engine_stamp_records_the_transition_once(self):
        w = engine.genesis(seed=69)
        for u in (w["eden"], w["lagoon"]):
            u["engine"] = "2026.10.27.3"
        engine.tick_world(w, [])
        engine.tick_world(w, [])
        for u in (w["eden"], w["lagoon"]):
            self.assertEqual(u["engine"], engine.ENGINE_VERSION)
            self.assertEqual(u["engine_history"], [{"from": "2026.10.27.3", "to": engine.ENGINE_VERSION, "day": 0, "part": 0}])
        engine.write_postmortem(w["eden"], [])
        self.assertEqual(w["eden"]["postmortems"][-1]["engine_history"], w["eden"]["engine_history"])

    def test_snapshot_light_matches_the_part_just_simulated(self):
        w = engine.genesis(seed=69)
        for part in range(4):
            engine.tick_world(w, [])
            for u in engine.summarize(w)["u"].values():
                self.assertEqual(u["part"], part)
                self.assertEqual(u["tod"], engine.PART_NAMES[part])
                self.assertEqual(u["night"], part == engine.PART_NIGHT)

    def test_body_and_mortality_are_updated_once_per_calendar_day(self):
        from unittest.mock import patch
        w = engine.genesis(seed=69)
        with patch.object(engine.minds, "tend_body") as body, patch.object(engine, "base_mortality", return_value=False) as mortality:
            run(w, 1)
        founders = len(w["eden"]["people"]) + len(w["lagoon"]["people"])
        self.assertEqual(body.call_count, founders)
        self.assertEqual(mortality.call_count, founders)

    def test_predator_meat_is_not_also_kept_after_transfer_to_store(self):
        import random
        u = engine.genesis_universe("LAGOON", 69)
        u["tech"] = ["preservation"]
        u["meat"] = 40.0
        engine.tick_lagoon(u, random.Random(2), [])
        self.assertGreater(u["store"], 0)
        self.assertEqual(u["meat"], 0)

    def test_new_persistent_fields_have_migration_defaults(self):
        w = engine.genesis(seed=69)
        u = w["lagoon"]
        for field in ("meat", "kills", "founded_day", "engine_history"):
            u.pop(field)
        engine.migrate(w)
        self.assertEqual(u["meat"], 0.0)
        self.assertEqual(u["kills"], 0)
        self.assertEqual(u["founded_day"], 0)
        self.assertEqual(u["engine_history"], [])


if __name__ == "__main__":
    unittest.main()
