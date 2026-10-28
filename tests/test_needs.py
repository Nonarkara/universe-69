"""The handoff plan's acceptance tests for real needs (HANDOFF-PLAN A1-A5).

A label on the canvas has to be the state the engine used: food arrives
only because somebody went and got it, a meal lowers the eater's own
hunger, the night is slept, and both worlds decide with one function.
"""

import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))

import engine  # noqa: E402
import needs  # noqa: E402


def run(u, tick, parts, seed=69):
    for i in range(parts):
        tick(u, random.Random(f"{seed}:{i}"), [])


class TestTheaterKill(unittest.TestCase):
    def test_a_band_that_only_sleeps_starves_and_its_store_stays_empty(self):
        # A1: nobody works, so nothing comes in — the store must not fill
        # from a headcount, and the band must starve on its own bodies.
        u = engine.genesis(69)["lagoon"]
        real = engine.lagoon_assign

        def sleep_only(u_, p, day, rng, shortfall):
            p["a"], p["ad"] = engine.A_SLEEP, engine.days(30)
            p["tx"], p["ty"] = p["x"], p["y"]

        engine.lagoon_assign = sleep_only
        try:
            peak_store = 0.0
            for i in range(120 * engine.PARTS_PER_DAY):
                engine.tick_lagoon(u, random.Random(i), [])
                peak_store = max(peak_store, u.get("store", 0.0))
                if not u["people"]:
                    break
        finally:
            engine.lagoon_assign = real
        self.assertEqual(peak_store, 0.0, "food appeared that nobody gathered")
        self.assertEqual(u["people"], [], "a band that never works did not starve")
        self.assertGreater(u["cod"].get("starvation", 0), 0)

    def test_a_working_band_does_not_starve_in_its_first_months(self):
        u = engine.genesis(69)["lagoon"]
        run(u, engine.tick_lagoon, 120 * engine.PARTS_PER_DAY)
        self.assertEqual(u["cod"].get("starvation", 0), 0)
        self.assertGreater(len(u["people"]), 10)


class TestEating(unittest.TestCase):
    def test_eating_lowers_the_eaters_own_hunger_and_empties_the_store(self):
        # A2
        u = engine.genesis(69)["lagoon"]
        st = u["settlements"][0]
        st["store"] = 50.0
        p, q = u["people"][0], u["people"][1]
        p["x"], p["y"] = st["x"], st["y"]
        p["hun"], q["hun"] = 20.0, 20.0
        got = needs.eat(u, p)
        self.assertGreater(got, 0)
        self.assertAlmostEqual(p["hun"], 20.0 - got)
        self.assertEqual(q["hun"], 20.0, "someone else's meal fed a bystander")
        self.assertAlmostEqual(st["store"], 50.0 - got)

    def test_nobody_eats_from_an_empty_camp(self):
        u = engine.genesis(69)["lagoon"]
        st = u["settlements"][0]
        st["store"] = 0.0
        p = u["people"][0]
        p["x"], p["y"], p["hun"] = st["x"], st["y"], 20.0
        self.assertEqual(needs.eat(u, p), 0.0)
        self.assertEqual(p["hun"], 20.0)

    def test_a_nursing_mother_pays_for_the_infants_meal(self):
        u = engine.genesis(69)["lagoon"]
        m = u["people"][1]
        baby = engine.person(999, "Baby", "f", u["day"] - 100, 2, m["x"], m["y"])
        baby["mom"], baby["hun"] = m["id"], 10.0
        u["people"].append(baby)
        before = m["hun"]
        got = needs.eat(u, baby)
        self.assertGreater(got, 0)
        self.assertGreater(m["hun"], before)


class TestNight(unittest.TestCase):
    def test_most_of_each_world_is_asleep_at_night(self):
        # A3
        for kind, tick in (("lagoon", engine.tick_lagoon), ("eden", engine.tick_eden)):
            u = engine.genesis(69)[kind]
            run(u, tick, 30 * engine.PARTS_PER_DAY)
            while u["part"] != engine.PART_NIGHT:
                run(u, tick, 1)
            run(u, tick, 1)          # simulate the night part itself
            people = [p for p in u["people"] if not p.get("w")]
            asleep = sum(1 for p in people if p["a"] in (engine.A_SLEEP, engine.A_TEND,
                                                         engine.A_WATCH, engine.A_MATE))
            self.assertGreater(asleep / len(people), 0.7, kind)

    def test_sleep_restores_energy(self):
        u = engine.genesis(69)["lagoon"]
        p = u["people"][0]
        p["ene"], p["a"] = 0.2, engine.A_SLEEP
        needs.meters(u, p, u["day"], random.Random(1), needs.CONDITIONS["LAGOON"])
        self.assertGreater(p["ene"], 0.2)


class TestOneMind(unittest.TestCase):
    def test_both_worlds_decide_with_the_same_function(self):
        # A5: the conditions differ; the decision does not
        calls = {"EDEN": 0, "LAGOON": 0}
        real = needs.assign

        def counted(u, p, day, rng, cond=None, engine=None):
            calls[u["kind"]] += 1
            return real(u, p, day, rng, cond, engine)

        needs.assign = counted
        try:
            w = engine.genesis(69)
            run(w["eden"], engine.tick_eden, 20 * engine.PARTS_PER_DAY)
            run(w["lagoon"], engine.tick_lagoon, 20 * engine.PARTS_PER_DAY)
        finally:
            needs.assign = real
        self.assertGreater(calls["EDEN"], 0)
        self.assertGreater(calls["LAGOON"], 0)

    def test_the_worlds_differ_only_in_named_conditions(self):
        self.assertEqual(set(needs.CONDITIONS["EDEN"]), set(needs.CONDITIONS["LAGOON"]))

    def test_eden_violence_needs_a_crowd(self):
        # no phase script: in an uncrowded pen nobody picks a fight
        u = engine.genesis(69)["eden"]
        u["innocent"] = False
        p = next(q for q in u["people"] if q["s"] == "m")
        u["people"] = [p]
        u["_ctx"] = engine.day_context(u["people"], u["day"])
        rng = random.Random(3)
        acts = {needs.assign(u, p, u["day"], rng, needs.CONDITIONS["EDEN"]) for _ in range(200)}
        self.assertNotIn(engine.A_FIGHT, acts)


class TestHuts(unittest.TestCase):
    def test_a_pair_raises_its_own_hut_by_work_and_sleeps_in_it(self):
        u = engine.genesis(69)["lagoon"]
        u["tech"] = ["fire", "shelter"]
        p = u["people"][0]
        h = needs.hut_of(u, p, make=True)
        self.assertIs(needs.hut_of(u, u["people"][1]), h, "a pair shares one hut")
        self.assertFalse(h["done"])
        p["x"], p["y"], p["a"] = h["x"], h["y"], engine.A_BUILD
        for _ in range(int(needs.HUT_WORK) + 2):
            needs.fulfil(u, p, u["day"], random.Random(1), engine.A_BUILD)
        self.assertTrue(h["done"], "ten days of work did not raise the hut")
        st = u["settlements"][0]
        p["x"], p["y"] = st["x"], st["y"]
        p["a"] = engine.A_TALK
        needs.night(u, p, random.Random(1), engine.PART_NIGHT)
        self.assertEqual((p["tx"], p["ty"]), (h["x"], h["y"]), "they did not sleep at home")

    def test_huts_stand_on_dry_ground(self):
        u = engine.genesis(69)["lagoon"]
        u["tech"] = ["fire", "shelter"]
        terr = engine.terrain_of(u)
        for i in range(0, len(u["people"]), 2):
            h = needs.hut_of(u, u["people"][i], make=True)
            self.assertNotEqual(terr[h["y"]][h["x"]], 2, "a hut on the water")

    def test_no_huts_before_shelter_is_known(self):
        u = engine.genesis(69)["lagoon"]
        run(u, engine.tick_lagoon, 60 * engine.PARTS_PER_DAY)
        if "shelter" not in u["tech"]:
            self.assertFalse(any(st.get("huts") for st in u["settlements"]))


class TestFounders(unittest.TestCase):
    def test_both_worlds_begin_with_eight_pairs(self):
        w = engine.genesis(69)
        for kind in ("eden", "lagoon"):
            self.assertEqual(len(w[kind]["people"]), 16)
            self.assertTrue(all(p["p"] is not None for p in w[kind]["people"]))


if __name__ == "__main__":
    unittest.main()
