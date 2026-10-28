"""Conservation, migration, and decision regressions from the October 29 audit."""
import copy
import json
import os
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "sim"))
import animals
import engine
import minds
import needs


class TestNamesAndMigration(unittest.TestCase):
    def test_names_follow_sex_and_never_change_the_shared_temperaments(self):
        w = engine.genesis()
        for kind in ("EDEN", "LAGOON"):
            rng = random.Random(10)
            for sex in ("m", "f"):
                for _ in range(30):
                    self.assertIn(minds.make_name(rng, minds.NAMES[kind], sex=sex), minds.NAMES[kind][sex])
        fields = lambda p: (p["s"], p["ef"], p["ag"], p["vg"], p["bmi"], p["sn"])
        self.assertEqual(list(map(fields, w["eden"]["people"])), list(map(fields, w["lagoon"]["people"])))
        self.assertEqual(len(w["eden"]["people"]), 16)

    def test_births_request_names_for_the_childs_actual_sex(self):
        for key, tick in (("eden", engine.tick_eden), ("lagoon", engine.tick_lagoon)):
            u = engine.genesis()[key]
            u["day"], u["part"] = 1, 1
            u["people"][1]["due"] = 1
            rng = random.Random(4)
            with patch.object(rng, "random", return_value=0.99), patch.object(engine, "make_name", wraps=minds.make_name) as naming:
                tick(u, rng, [])
            children = [p for p in u["people"] if p["g"] == 2]
            self.assertEqual(len(children), 1)
            child = children[0]
            self.assertIn(child["n"], minds.NAMES[u["kind"]][child["s"]])
            self.assertEqual(naming.call_args.kwargs["sex"], child["s"])

    def test_legacy_pooled_food_is_distributed_once_and_survives_json(self):
        w = engine.genesis()
        u = w["lagoon"]
        u["store"] = 123.5
        u["settlements"].append(dict(u["settlements"][0]))
        for st in u["settlements"]:
            st.pop("store", None)
        for p in u["people"][4:]:
            p["st"] = 1
        u.pop("names"); u.pop("named")
        u["gen_max"] = 2
        engine.migrate(w)
        self.assertEqual(sum(s["store"] for s in u["settlements"]), 123.5)
        self.assertAlmostEqual(u["settlements"][0]["store"], 123.5 / 4)
        self.assertTrue(u["named"])
        before = json.dumps(w, sort_keys=True)
        engine.migrate(w)
        self.assertEqual(json.dumps(w, sort_keys=True), before)
        self.assertEqual(engine.migrate(json.loads(before)), w)

    def test_migration_does_not_duplicate_food_already_kept_by_camps(self):
        w = engine.genesis()
        u = w["lagoon"]
        u["store"] = 100
        u["settlements"][0]["store"] = 40
        engine.migrate(w)
        self.assertEqual(u["settlements"][0]["store"], 40)

    def test_animal_ids_continue_above_existing_animals(self):
        w = engine.genesis()
        u = w["lagoon"]
        u["animals"] = [{"i": 99, "k": "deer", "x": 100, "y": 100}]
        u.pop("animal_id", None)
        engine.migrate(w)
        self.assertEqual(u["animal_id"], 100)


class TestFoodAndNeeds(unittest.TestCase):
    def test_an_unworked_field_does_not_grow_during_its_first_month(self):
        u = engine.genesis()["lagoon"]
        u["farms"] = [[137, 109]]
        needs.ensure_sites(u)
        field = next(s for s in u["sites"] if s["kind"] == "farm")
        needs.regrow_sites(u)
        self.assertEqual(field["left"], 0)
        p = u["people"][0]
        p["x"], p["y"], p["a"] = 137, 109, minds.A_FARM
        needs.fulfil(u, p, 0, random.Random(1), minds.A_FARM)
        needs.regrow_sites(u)
        self.assertGreater(field["left"], 0)

    def test_fish_and_plants_follow_their_own_season(self):
        u = engine.genesis()["lagoon"]
        u["sites"] = [{"kind": k, "left": 0, "max": 100, "regrow": 10} for k in ("fish", "plants")]
        with patch.object(engine, "lagoon_season", return_value=(0.2, 0.8, True)):
            needs.regrow_sites(u)
        self.assertAlmostEqual(u["sites"][0]["left"], 8)
        self.assertAlmostEqual(u["sites"][1]["left"], 2)

    def test_a_hunt_does_not_harvest_an_unrelated_berry_patch(self):
        u = engine.genesis()["lagoon"]
        p = u["people"][0]
        u["sites"] = [{"kind": "plants", "x": p["x"], "y": p["y"], "left": 100, "max": 100}]
        p["a"] = minds.A_HUNT
        needs.fulfil(u, p, 0, random.Random(1), minds.A_HUNT)
        self.assertEqual(u["sites"][0]["left"], 100)
        self.assertEqual(p["carry"], 0)

    def test_food_lost_with_a_distant_carrier_does_not_teleport_home(self):
        u = engine.genesis()["lagoon"]
        u["part"] = 1
        p = u["people"][0]
        p["x"], p["y"], p["carry"] = 100, 100, 40
        p["tx"], p["ty"] = 100, 100
        p["hun"] = 0
        u["people"] = [p]
        rng = random.Random(1)
        with patch.object(animals, "tick", return_value=[]), patch.object(rng, "random", return_value=0):
            engine.tick_lagoon(u, rng, [])
        self.assertEqual(u["people"], [])
        self.assertEqual(u["store"], 0)

    def test_summary_store_tracks_meals_and_daily_spoilage(self):
        u = engine.genesis()["lagoon"]
        u["settlements"][0]["store"] = 100
        engine.tick_lagoon(u, random.Random(2), [])
        self.assertAlmostEqual(u["store"], sum(st["store"] for st in u["settlements"]))

    def test_purposeless_isolation_can_beat_seeking_company(self):
        u = engine.genesis()["eden"]
        p = u["people"][0]
        p["sol"], p["pu"], p["hun"], p["ene"] = 0, 0.05, 0, 1
        self.assertEqual(needs.assign(u, p, 0, random.Random(1)), minds.A_WITHDRAW)
        p["pu"] = 0.8
        self.assertNotEqual(needs.assign(u, p, 0, random.Random(1)), minds.A_WITHDRAW)

    def test_large_berry_loads_are_not_reported_as_carcasses(self):
        w = engine.genesis()
        p = w["lagoon"]["people"][0]
        needs.carry_food(p, 30, "plants")
        row = next(q for q in engine.summarize(w)["u"]["lagoon"]["people"] if q[4] == p["id"])
        self.assertEqual(row[12], 1)
        p["carry"] = 0
        needs.carry_food(p, 5, "deer")
        row = next(q for q in engine.summarize(w)["u"]["lagoon"]["people"] if q[4] == p["id"])
        self.assertEqual(row[12], 2)
        needs.carry_food(p, 2, "plants")
        self.assertEqual(p["carry_kind"], "mixed")

    def test_story_rates_are_divided_into_parts_once(self):
        u = engine.genesis()["lagoon"]
        u["tech"] = ["fire"]
        for p in u["people"]:
            p["a"] = engine.A_TALK
        for part in range(4):
            engine.keep_watch(u, u["people"], 0, [], part=part)
        talkers = len(u["people"]) - 1
        self.assertAlmostEqual(u["stories"], talkers * (3 * 0.01 + 0.02) / 4)

    def test_daily_hunger_is_four_quarter_day_updates(self):
        u = engine.genesis()["lagoon"]
        p = u["people"][0]
        p["hun"] = 0
        expected = needs.HUNGER_PER_DAY * (1 + 0.6 * needs._workload(u, p))
        for _ in range(4):
            needs.meters(u, p, 0, random.Random(1), needs.CONDITIONS["LAGOON"])
        self.assertAlmostEqual(p["hun"], expected)


class TestWildlife(unittest.TestCase):
    def test_a_taken_hunter_cannot_complete_a_later_cat_hunt(self):
        u = engine.genesis()["lagoon"]
        u["settlements"] = []
        hunters = u["people"][:3]
        for p, (x, y) in zip(hunters, ((100, 100), (104, 100), (104, 101))):
            p["a"], p["x"], p["y"] = minds.A_HUNT, x, y
        u["animals"] = [dict(i=i, k="cat", x=x, y=100, tx=x, ty=100, hx=x, hy=100, fed=fed)
                        for i, x, fed in ((1, 100, 20), (2, 103, 0))]
        context = {"part": 1, "day": 0, "night": False,
                   "has": lambda tech: tech == "predator_hunt", "adult": lambda _: True,
                   "armed": True, "lessons": [], "events": [], "A_HUNT": minds.A_HUNT}
        rng = random.Random(1)
        with patch.object(animals, "_attack", return_value="taken"), patch.object(animals, "_step"), patch.object(rng, "random", return_value=0):
            taken = animals.tick(u, rng, [[0] * 160 for _ in range(160)], hunters, context)
        self.assertEqual([p["id"] for p, _ in taken], [hunters[0]["id"]])
        self.assertEqual(u["kills"], 0)
        self.assertIn(2, [a["i"] for a in u["animals"]])
        self.assertEqual(sum(p["carry"] for p in hunters), 0)

    def test_two_cats_cannot_consume_the_same_person(self):
        u = engine.genesis()["lagoon"]
        p = u["people"][0]
        p["x"], p["y"] = 100, 100
        u["animals"] = [dict(i=i, k="cat", x=100, y=100, tx=100, ty=100, hx=100, hy=100, fed=20) for i in (1, 2)]
        context = {"part": 1, "day": 0, "night": False, "has": lambda _: False,
                   "adult": lambda _: True, "armed": False, "lessons": [], "events": [], "A_HUNT": minds.A_HUNT}
        terr = [[0] * 160 for _ in range(160)]
        with patch.object(animals, "_attack", return_value="taken"):
            taken = animals.tick(u, random.Random(1), terr, [p], context)
        self.assertEqual([q["id"] for q, _ in taken], [p["id"]])

    def test_a_person_taken_cannot_eat_and_die_again_in_the_same_part(self):
        u = engine.genesis()["lagoon"]
        p = u["people"][0]
        u["people"] = [p]
        u["part"] = 1
        p["hun"] = 39.99
        with patch.object(animals, "tick", return_value=[(p, "predator")]), patch.object(needs, "eat") as eat:
            engine.tick_lagoon(u, random.Random(1), [])
        eat.assert_not_called()
        self.assertEqual(u["cod"], {"predator": 1})
