"""The research layer: what the books say, and what the world says back.

`sim/research.py` holds the claims from the owner's shelf as numbers the
engine can produce. These tests pin the things that would silently rot:

- every hypothesis points at a metric that exists, and cites a source;
- a hypothesis that has not been measured says "undecided", never "false";
- measuring a world does not change the world — the layer only reads;
- the verdicts survive a save and load, so a run keeps its record;
- a state file written before the research layer existed still loads.
"""

import copy
import json
import os
import sys
import unittest
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))

import engine  # noqa: E402
import research  # noqa: E402
from scratch_space import scratch_root
SCRATCH = scratch_root()

RENDERER = os.path.join(ROOT, "web", "index.html")
MIRROR = os.path.join(ROOT, "docs", "index.html")


class TestTheRegistry(unittest.TestCase):
    """The table itself: no dangling names, no unsourced claims."""

    def test_every_hypothesis_is_well_formed(self):
        seen = set()
        for h in research.HYPOTHESES:
            self.assertIn("id", h)
            self.assertNotIn(h["id"], seen, f"duplicate hypothesis id {h['id']}")
            seen.add(h["id"])
            for field in ("statement", "source", "note", "world", "metric"):
                self.assertTrue(h.get(field), f"{h['id']} has no {field}")
            self.assertIn(h["world"], ("EDEN", "LAGOON"))
            self.assertIn(h["test"], ("gte", "lte", "eq", "between"))
            self.assertIn(h["metric"], research.METRICS,
                          f"{h['id']} points at a metric that does not exist")
            self.assertTrue(h["source"].strip(),
                            f"{h['id']} does not say where it came from")

    def test_every_metric_is_reachable_and_read_only(self):
        """A metric must produce a number or None — never raise, never write."""
        w = engine.genesis(seed=69)
        for name, fn in research.METRICS.items():
            for key in ("eden", "lagoon"):
                v = fn(w[key])
                self.assertTrue(v is None or isinstance(v, (int, float)),
                                f"{name} returned {v!r}")

    def test_a_metric_never_raises_on_an_empty_world(self):
        w = engine.genesis(seed=69)
        for key in ("eden", "lagoon"):
            u = w[key]
            u["people"] = []
            u["cod"] = {}
        for name, fn in research.METRICS.items():
            for key in ("eden", "lagoon"):
                fn(w[key])   # must not raise

    def test_every_hypothesis_is_measured_in_both_worlds(self):
        w = engine.genesis(seed=69)
        results = research.evaluate(w)
        self.assertEqual(len(results), len(research.HYPOTHESES))
        by_id = {r["id"]: r for r in results}
        for h in research.HYPOTHESES:
            self.assertIn(h["id"], by_id)
            self.assertEqual(by_id[h["id"]]["world"], h["world"])


class TestVerdicts(unittest.TestCase):
    def test_a_young_world_decides_nothing(self):
        """Day one cannot refute a claim about year eighty."""
        w = engine.genesis(seed=69)
        for r in research.evaluate(w):
            self.assertEqual(r["verdict"], research.UNDECIDED,
                             f"{r['id']} decided something on day one")
            self.assertFalse(r["ready"])

    def test_an_undecided_hypothesis_is_not_a_refutation(self):
        w = engine.genesis(seed=69)
        results = research.evaluate(w)
        store = research.record(w, results)
        for h in research.HYPOTHESES:
            t = store["h"][h["id"]]
            self.assertEqual(t["con"], 0, f"{h['id']} was counted as refuted")
            self.assertEqual(t["und"], 1)
            self.assertEqual(t["n"], 1)

    def test_a_world_with_no_deaths_cannot_be_judged_on_its_deaths(self):
        """A share of a dozen deaths is noise, not a finding."""
        w = engine.genesis(seed=69)
        for r in research.evaluate(w):
            if r["metric"] in ("lagoon_violent_share", "lagoon_dominant_cause"):
                self.assertEqual(r["verdict"], research.UNDECIDED)

    def test_a_new_iteration_is_not_judged_by_the_previous_lifetime(self):
        w = engine.genesis(seed=69)
        for u in (w["eden"], w["lagoon"]):
            u["day"] = u["founded_day"] = 50000
            u["iteration"] = 2
        for r in research.evaluate(w):
            self.assertEqual(r["verdict"], research.UNDECIDED)
            self.assertFalse(r["ready"])

    def test_dunbar_cannot_refute_a_no_lore_claim_after_lore_exists(self):
        w = engine.genesis(seed=69)
        u = w["lagoon"]
        u["day"] = 40 * engine.DAYS_PER_YEAR
        u["people"] = [dict(u["people"][0], id=i) for i in range(200)]
        u["tech"] = ["lore"]
        result = next(r for r in research.evaluate(w) if r["id"] == "H-LAGOON-DUNBAR")
        self.assertIsNone(result["value"])
        self.assertFalse(result["ready"])
        self.assertEqual(result["verdict"], research.UNDECIDED)

    def test_dunbar_still_tests_a_mature_world_without_lore(self):
        w = engine.genesis(seed=69)
        u = w["lagoon"]
        u["day"] = 40 * engine.DAYS_PER_YEAR
        u["people"] = [dict(u["people"][0], id=i) for i in range(200)]
        result = next(r for r in research.evaluate(w) if r["id"] == "H-LAGOON-DUNBAR")
        self.assertTrue(result["ready"])
        self.assertEqual(result["verdict"], research.CONTRADICTED)

    def test_the_comparisons_say_what_they_mean(self):
        self.assertEqual(research._compare("gte", 31.0, 30.0), research.SUPPORTED)
        self.assertEqual(research._compare("gte", 29.0, 30.0), research.CONTRADICTED)
        self.assertEqual(research._compare("lte", 0.2, 0.3), research.SUPPORTED)
        self.assertEqual(research._compare("lte", 0.4, 0.3), research.CONTRADICTED)
        self.assertEqual(research._compare("eq", "starvation", "starvation"),
                         research.SUPPORTED)
        self.assertEqual(research._compare("eq", "violence", "starvation"),
                         research.CONTRADICTED)
        self.assertEqual(research._compare("between", 83, [40, 140]),
                         research.SUPPORTED)
        self.assertEqual(research._compare("between", 200, [40, 140]),
                         research.CONTRADICTED)
        self.assertEqual(research._compare("gte", None, 30.0), research.UNDECIDED)

    def test_an_unknown_test_is_a_mistake_not_a_silent_pass(self):
        with self.assertRaises(ValueError):
            research._compare("roughly", 1.0, 2.0)


class TestTheLayerReadsOnly(unittest.TestCase):
    """The layer must not be able to move a world."""

    def test_measuring_does_not_change_the_world(self):
        w = engine.genesis(seed=69)
        before = copy.deepcopy(w["eden"])
        before_l = copy.deepcopy(w["lagoon"])
        research.evaluate(w)
        research.record(w, research.evaluate(w))
        self.assertEqual(w["eden"], before, "the EDEN universe was changed")
        self.assertEqual(w["lagoon"], before_l, "the LAGOON universe was changed")

    def test_a_run_with_research_looks_exactly_like_one_without(self):
        """Adding a hypothesis must not move a single simulated outcome."""
        a = engine.genesis(seed=69)
        b = engine.genesis(seed=69)
        ev = []
        for _ in range(600):
            engine.tick_world(a, ev)
            engine.tick_world(b, ev)
            research.record(b, research.evaluate(b))
        self.assertEqual(a["eden"], b["eden"])
        self.assertEqual(a["lagoon"], b["lagoon"])


class TestTheRecordSurvives(unittest.TestCase):
    def test_verdicts_round_trip_through_json(self):
        w = engine.genesis(seed=69)
        research.record(w, research.evaluate(w))
        blob = json.dumps(w["research"])
        back = json.loads(blob)
        self.assertEqual(back["h"].keys(), w["research"]["h"].keys())

    def test_an_old_state_file_without_research_still_loads(self):
        """The universes have been running since before this layer existed."""
        w = engine.genesis(seed=69)
        w.pop("research", None)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            path = os.path.join(directory, "state.json")
            engine.save_state(w, path)
            back = engine.load_state(path)
            self.assertIn("research", back)
            self.assertEqual(back["research"]["h"], {})

    def test_the_history_is_bounded(self):
        w = engine.genesis(seed=69)
        for _ in range(research.VERDICT_HISTORY + 25):
            research.record(w, research.evaluate(w))
        for h in research.HYPOTHESES:
            self.assertLessEqual(len(w["research"]["h"][h["id"]]["hist"]),
                                 research.VERDICT_HISTORY)


class TestTheViewerShowsIt(unittest.TestCase):
    """The panel is the point of the layer; the renderer must actually have it."""

    def setUp(self):
        with open(RENDERER) as f:
            self.src = f.read()

    def test_there_is_a_research_button_and_a_panel(self):
        self.assertIn('id="resbtn"', self.src)
        self.assertIn('id="research"', self.src)
        self.assertIn('id="reslist"', self.src)

    def test_the_panel_reads_the_verdicts_from_the_snapshot(self):
        self.assertIn("state.research", self.src)
        self.assertIn("renderResearch", self.src)

    def test_the_panel_shows_the_long_story(self):
        """The story is the summary of the shelf the reader asked for."""
        self.assertIn("storyBlocks", self.src)     # paged since the 2026-10-28 redesign
        self.assertIn('id="resstory"', self.src)
        self.assertTrue(research.HISTORY, "the story is empty")
        seen = set()
        for e in research.HISTORY:
            for field in ("t", "when", "claim", "source"):
                self.assertTrue(e.get(field), f"a chapter of the story has no {field}")
            for hid in e.get("hypos") or []:
                self.assertIn(hid, {h["id"] for h in research.HYPOTHESES},
                              f"the story points at a hypothesis that does not exist: {hid}")
                seen.add(hid)
        self.assertGreater(len(seen), 5,
                           "the story does not lead to any of the tests")

    def test_the_mirror_is_identical(self):
        with open(MIRROR) as f:
            self.assertEqual(self.src, f.read(),
                             "web/index.html and docs/index.html have diverged")


class TestCensusRowsGrew(unittest.TestCase):
    def test_the_report_reads_census_rows_that_carry_gauges(self):
        # engine 2026.10.28.3 widened the yearly census row; the reading
        # of the shelf must not crash on it (it would 500 the /state page)
        import random
        import research
        w = engine.genesis(seed=69)
        for i in range(engine.DAYS_PER_YEAR * engine.PARTS_PER_DAY + 4):
            engine.tick_lagoon(w["lagoon"], random.Random(i), [])
            engine.tick_eden(w["eden"], random.Random(i), [])
        self.assertEqual(len(w["lagoon"]["census"][-1]), len(engine.CENSUS_FIELDS))
        research.report(w)       # must not raise


if __name__ == "__main__":
    unittest.main()
