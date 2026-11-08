"""The scripture of each world, and the probe that keeps its people honest.

`sim/scripture.py` is a reader: it must never move a world, never draw
randomness, and always derive the same testament from the same state.
`tools/probe.py` measures independence and habitability; its quick
independence probe runs here so a regression in the decision layer — a
hive mind, or bodies that no longer agree when starving — fails the
suite rather than the show.
"""

import copy
import json
import sys
import unittest

sys.path.insert(0, "sim")
sys.path.insert(0, "tools")

import engine      # noqa: E402
import scripture   # noqa: E402
import minds       # noqa: E402


def _ticked_world(parts=40):
    w = engine.genesis(69, 1)
    for _ in range(parts):
        engine.tick_world(w, [])
    return w


class TestTheScripture(unittest.TestCase):
    """What the record's testament must always be."""

    def setUp(self):
        self.world = _ticked_world()
        self.scr = scripture.both(self.world)

    def test_it_reads_both_worlds_with_titles(self):
        self.assertEqual(self.scr["eden"]["kind"], "EDEN")
        self.assertEqual(self.scr["lagoon"]["kind"], "LAGOON")
        self.assertEqual(self.scr["eden"]["title"], "The Covenant of the Resort")
        self.assertEqual(self.scr["lagoon"]["title"], "The Way of the Lagoon")

    def test_it_is_json_safe(self):
        json.dumps(self.scr)                      # tuples, sets: none may escape

    def test_it_is_deterministic(self):
        again = scripture.both(_ticked_world())
        self.assertEqual(json.dumps(self.scr, sort_keys=True),
                         json.dumps(again, sort_keys=True))

    def test_reading_never_moves_the_world(self):
        before = json.dumps(self.world, sort_keys=True, default=str)
        scripture.both(copy.deepcopy(self.world))
        self.assertEqual(before,
                         json.dumps(self.world, sort_keys=True, default=str))

    def test_eden_keeps_no_law_because_nothing_is_asked(self):
        e = self.scr["eden"]
        self.assertEqual(e["commandments"], [])   # no dead have left EDEN a law
        self.assertEqual(e["myths"], [])
        self.assertIn("free", " ".join(e["creed"]).lower())
        self.assertIn("No one here has told a story that binds", " ".join(e["creed"]))

    def test_lagoon_lessons_become_laws(self):
        u = self.world["lagoon"]
        u["lessons"] = ["preserve", "unity"]
        s = scripture.for_world(u)
        self.assertEqual(len(s["commandments"]), 2)
        self.assertIn("Waste nothing", s["commandments"][0])
        self.assertIn("Hold together", s["commandments"][1])

    def test_a_disaster_earns_its_myth(self):
        u = self.world["lagoon"]
        u.setdefault("myths", []).append(
            ["starvation", "the groves withhold their fruit from the greedy", 12])
        s = scripture.for_world(u)
        self.assertEqual(s["myths"][0][1], "the groves withhold their fruit from the greedy")

    def test_the_cast_is_named_people_with_ages(self):
        for kind in ("eden", "lagoon"):
            cast = self.scr[kind]["cast"]
            self.assertTrue(cast, f"{kind} has people; the cast must name them")
            for c in cast:
                self.assertIn("name", c)
                self.assertIn("age", c)
                self.assertIn("who", c)
                self.assertIsInstance(c["age"], float)

    def test_the_eldest_is_the_eldest(self):
        u = self.world["eden"]
        day = u["day"]
        adults = [p for p in u["people"]
                  if day - p.get("b", 0) >= minds.ADULT_AGE]
        eldest = min(adults, key=lambda q: q.get("b", 0))
        named = {c["name"] for c in self.scr["eden"]["cast"]}
        self.assertIn(eldest["n"], named)

    def test_rhythms_and_hazards_are_declared(self):
        for kind in ("eden", "lagoon"):
            s = self.scr[kind]
            self.assertTrue(s["rhythms"], "the predictable must be named")
            self.assertTrue(s["hazards"], "the unpredictable must be named")
            self.assertTrue(any(h["what"] == "Old age" for h in s["hazards"]))

    def test_hazard_counts_come_from_this_worlds_cod(self):
        u = self.world["lagoon"]
        u["cod"] = dict(u.get("cod", {}))
        u["cod"]["violence"] = 7
        s = scripture.for_world(u)
        h = next(h for h in s["hazards"] if h["what"] == "A quarrel becomes a killing")
        self.assertEqual(h["so_far"], 7)


class TestTheProbe(unittest.TestCase):
    """The decision layer must make persons, not a hive."""

    @classmethod
    def setUpClass(cls):
        import probe
        cls.probe = probe
        cls.result = probe.independence(seeds=(69,), focals=4, trials=6, verbose=False)

    def test_people_in_the_same_state_choose_differently(self):
        self.assertGreater(self.result["person_divergence"], 0.02,
                           "identical comfortable bodies chose as one: a hive mind")

    def test_identity_leaves_a_fingerprint(self):
        self.assertGreater(self.result["identity_flip_rate"], 0.0,
                           "personal sensitivity never reordered a choice")

    def test_urgent_bodies_agree(self):
        self.assertGreaterEqual(self.result["urgent_convergence"], 0.6,
                                "the starving must agree on food")

    def test_the_designed_dice_exist(self):
        self.assertGreaterEqual(self.result["tie_noise"], 0.0)
        self.assertLessEqual(self.result["tie_noise"], 1.0)

    def test_the_drama_inventory_is_declared(self):
        d = self.probe.drama(verbose=False)
        kinds = {c["kind"] for c in d["components"]}
        self.assertIn("rhythm", kinds)
        self.assertIn("hazard", kinds)
        self.assertGreaterEqual(len(d["components"]), 10)


if __name__ == "__main__":
    unittest.main()
