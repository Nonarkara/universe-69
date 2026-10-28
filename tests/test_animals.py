"""The animals have places (sim/animals.py; handoff A4).

Predation needs a cat that is there; a hunt needs a deer that is there; a
group is not prey; an armed person can kill the cat that attacks; and the
canvas is told where every animal is.
"""

import json
import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))

import animals  # noqa: E402
import engine  # noqa: E402


def lagoon():
    u = engine.genesis(69)["lagoon"]
    animals.ensure(u, random.Random(1), engine.terrain_of(u))
    return u


def ctx(u, armed=False, night=False):
    return {"day": u["day"], "part": 1, "night": night, "events": [],
            "adult": lambda q: engine.age_of(q, u["day"]) >= engine.ADULT_AGE,
            "has": lambda t: t in u["tech"], "armed": armed,
            "lessons": [], "A_HUNT": engine.A_HUNT}


class TestPlaces(unittest.TestCase):
    def test_animals_are_seeded_on_land_and_survive_json(self):
        u = lagoon()
        terr = engine.terrain_of(u)
        deer, cats = animals.counts(u)
        self.assertGreater(deer, 50)
        self.assertGreater(cats, 0)
        self.assertTrue(all(terr[q["y"]][q["x"]] != 2 for q in u["animals"]))
        json.loads(json.dumps(u["animals"]))

    def test_the_canvas_is_told_where_every_animal_is(self):
        w = engine.genesis(69)
        engine.tick_lagoon(w["lagoon"], random.Random(1), [])
        snap = engine.summarize(w)["u"]["lagoon"]
        self.assertEqual(len(snap["animals"]), len(w["lagoon"]["animals"]))
        deer, cats = animals.counts(w["lagoon"])
        self.assertEqual((snap["game"], snap["pred"]), (deer, cats))


class TestPredation(unittest.TestCase):
    def test_no_cat_no_predation(self):
        u = lagoon()
        u["animals"] = [q for q in u["animals"] if q["k"] != animals.CAT]
        real = animals._daily
        animals._daily = lambda *a: None          # and none wanders in
        try:
            for i in range(360 * engine.PARTS_PER_DAY):
                engine.tick_lagoon(u, random.Random(i), [])
        finally:
            animals._daily = real
        self.assertEqual(u["cod"].get("predator", 0), 0)

    def test_a_group_is_not_prey(self):
        u = lagoon()
        terr = engine.terrain_of(u)
        adults = [p for p in u["people"]][:3]
        for i, p in enumerate(adults):
            p["x"], p["y"] = 100 + i, 100
        cat = {"i": 999, "k": animals.CAT, "x": 101, "y": 102, "tx": 101, "ty": 102,
               "hx": 101, "hy": 102, "fed": 99.0}
        self.assertIsNone(animals._choose_person(
            u, cat, adults, False, lambda t: False, ctx(u)["adult"]))
        del terr

    def test_one_alone_is(self):
        u = lagoon()
        p = u["people"][0]
        p["x"], p["y"] = 100, 100
        cat = {"i": 999, "k": animals.CAT, "x": 101, "y": 102, "tx": 101, "ty": 102,
               "hx": 101, "hy": 102, "fed": 99.0}
        self.assertIs(animals._choose_person(u, cat, [p], False, lambda t: False,
                                             ctx(u)["adult"]), p)

    def test_an_armed_person_fights_back_better(self):
        u = lagoon()
        p = u["people"][0]
        cat = {"i": 999, "k": animals.CAT, "x": 0, "y": 0, "fed": 99.0}

        def rate(armed):
            rng = random.Random(7)
            killed = 0
            for _ in range(2000):
                p["inj"] = 0.0
                if animals._attack(u, cat, p, [p], rng, ctx(u, armed=armed)) == "killed":
                    killed += 1
            return killed

        self.assertGreater(rate(True), 2 * rate(False))


class TestRoofs(unittest.TestCase):
    def test_a_cat_does_not_go_in_after_someone_asleep_in_their_hut(self):
        u = lagoon()
        p = u["people"][0]
        st = u["settlements"][0]
        st["huts"] = [{"own": 1, "x": 100, "y": 100, "w": 10.0, "done": True}]
        p["x"], p["y"] = 100, 100
        cat = {"i": 999, "k": animals.CAT, "x": 101, "y": 101, "tx": 101, "ty": 101,
               "hx": 101, "hy": 101, "fed": 99.0}
        self.assertIsNone(animals._choose_person(u, cat, [p], True, lambda t: False,
                                                 ctx(u)["adult"]))


class TestHunting(unittest.TestCase):
    def test_a_kill_needs_a_deer_at_hand_and_comes_home_as_a_load(self):
        u = lagoon()
        u["tech"] = ["stone_tools"]
        u["animals"] = [{"i": 1, "k": animals.DEER, "x": 100, "y": 100, "tx": 100, "ty": 100}]
        hunters = u["people"][:4]
        for i, p in enumerate(hunters):
            p["a"], p["x"], p["y"], p["carry"] = engine.A_HUNT, 100 + (i % 2), 101, 0.0
            p["hun"] = 0.0
        rng = random.Random(3)
        terr = engine.terrain_of(u)
        for _ in range(40):
            animals.tick(u, rng, terr, hunters, ctx(u, armed=True))
            for p in hunters:
                engine.step_toward(p, terr, engine.LAGOON_WALK)
            if not any(q["k"] == animals.DEER for q in u["animals"]):
                break
        self.assertFalse(any(q["k"] == animals.DEER for q in u["animals"]))
        self.assertGreater(sum(p["carry"] for p in hunters), 0)


if __name__ == "__main__":
    unittest.main()
