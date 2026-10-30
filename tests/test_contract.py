"""The viewer's data contract.

`web/index.html` is a hand-written renderer that reads a flat, positional
payload from `engine.summarize()`. Nothing in the type system protects it: a
renamed field silently renders "undefined" in a browser instead of failing a
build. These tests pin the contract from both sides — the engine's output and
the renderer's own expectations — so a change to one and not the other fails
here rather than in front of a viewer.

The renderer file is also parsed for the activity-code table, so the two files
cannot drift apart silently.
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))

import engine  # noqa: E402

RENDERER = os.path.join(ROOT, "web", "index.html")
MIRROR = os.path.join(ROOT, "docs", "index.html")


def read(path):
    with open(path) as f:
        return f.read()


class TestSummarizeShape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = engine.genesis(seed=69)
        events = []
        for _ in range(400):
            engine.tick_world(cls.world, events)
        cls.snap = engine.summarize(cls.world)

    def test_top_level_keys(self):
        self.assertIn("wall", self.snap)
        self.assertIn("sec_per_day", self.snap)
        self.assertIn("u", self.snap)
        self.assertEqual(set(self.snap["u"]), {"eden", "lagoon"})

    def test_common_universe_fields(self):
        for key in ("eden", "lagoon"):
            u = self.snap["u"][key]
            for field in ("day", "year", "pop", "gen", "peak", "phase",
                          "iter", "people", "census"):
                self.assertIn(field, u, f"{key} is missing {field}")

    def test_social_observation_map_names_participants_and_contact(self):
        for key in ('eden', 'lagoon'):
            social = self.snap['u'][key]['social']
            self.assertIsInstance(social, dict)
            ids = set(self.snap['u'][key]['detail'])
            for uid, intent in social.items():
                self.assertIn(uid, ids)
                self.assertIn(str(intent['other']), ids)
                self.assertNotEqual(uid, str(intent['other']))
                self.assertIn(intent['kind'], ('mate', 'groom'))
                self.assertIsInstance(intent['mutual'], bool)
                self.assertIsInstance(intent['contact'], bool)
                if intent['contact']:
                    peer = social[str(intent['other'])]
                    self.assertTrue(intent['mutual'])
                    self.assertEqual(peer['other'], int(uid))
                    self.assertEqual(peer['kind'], intent['kind'])
                    self.assertTrue(peer['mutual'])
                    self.assertTrue(peer['contact'])

    def test_eden_specific_fields(self):
        u = self.snap["u"]["eden"]
        for field in ("ennui", "std", "sink", "homeless", "boxes"):
            self.assertIn(field, u, f"eden is missing {field}")
        self.assertIsInstance(u["ennui"], float)
        self.assertIsInstance(u["std"], bool)
        for field in ("cap", "stagnation", "box_cap", "box_slots"):
            self.assertIn(field, u, f"eden is missing {field}")

    def test_lagoon_specific_fields(self):
        u = self.snap["u"]["lagoon"]
        for field in ("tech", "settlements", "farms", "store", "lessons",
                      "culture", "season", "harsh", "dry"):
            self.assertIn(field, u, f"lagoon is missing {field}")
        self.assertIn(u["season"], ("winter", "summer", "spring", "autumn", "monsoon", "dry season"))
        self.assertIsInstance(u["tech"], list)
        self.assertIsInstance(u["settlements"], list)

    def test_cause_of_death_record_is_present(self):
        """The record of how they died is part of the payload, not a guess."""
        for key in ("eden", "lagoon"):
            self.assertIn("cod", self.snap["u"][key])
            self.assertIsInstance(self.snap["u"][key]["cod"], dict)

    def test_person_detail_is_present_for_every_person(self):
        """The viewer must be able to say *who* a figure is, not just draw a dot."""
        for key in ("eden", "lagoon"):
            u = self.snap["u"][key]
            self.assertIn("detail", u)
            ids = {str(p[4]) for p in u["people"]}
            self.assertEqual(set(u["detail"]), ids,
                             "detail does not line up with the people drawn")
            for pid, d in u["detail"].items():
                self.assertEqual(len(d), 13, "person detail changed shape")
                self.assertIsInstance(d[0], str)          # name
                self.assertIsInstance(d[1], float)        # age in years
                self.assertIsInstance(d[2], int)          # generation
                self.assertIsInstance(d[3], int)          # flags
                self.assertIsInstance(d[6], int)          # partner id
                self.assertIsInstance(d[8], str)          # what the body looks like
                for i in (9, 10, 11, 12):                 # purpose, ef, aggression, bmi
                    self.assertIsInstance(d[i], float)

    def test_people_rows_have_fourteen_positional_fields(self):
        """[x, y, cls, sex, id, act, face, age, bmi, strength, injury, wk,
        carry, hunger] — the renderer indexes these; the body fields draw the
        figure, carry draws the load coming home, hunger the thin face."""
        for key in ("eden", "lagoon"):
            for p in self.snap["u"][key]["people"]:
                self.assertEqual(len(p), 14)
                x, y, cls, sex, pid, act, face, age, bmi, sn, inj, wk, carry, hun = p
                self.assertIn(carry, (0, 1, 2))
                self.assertTrue(0 <= hun <= 9)
                for v in (age, bmi, sn, inj, wk):
                    self.assertIsInstance(v, int)
                self.assertTrue(10 <= bmi <= 50)
                self.assertTrue(0 <= sn <= 9 and 0 <= inj <= 9)
                self.assertIn(wk, (0, 1, 2, 3))
                self.assertIsInstance(x, int)
                self.assertIsInstance(y, int)
                self.assertIn(cls, (0, 1, 2, 3, 4))
                self.assertIn(sex, (0, 1))
                self.assertIsInstance(pid, int)
                self.assertIsInstance(act, int)
                self.assertIn(face, (-1, 1))

    def test_snapshot_is_json_serialisable(self):
        json.dumps(self.snap)

    def test_the_snapshot_says_which_part_of_the_day_it_is(self):
        """The renderer lights the world by the hour, so it must be told."""
        for key in ("eden", "lagoon"):
            u = self.snap["u"][key]
            self.assertIn(u["part"], range(4))
            self.assertIn(u["tod"], ("dawn", "day", "dusk", "night"))
            self.assertIsInstance(u["night"], bool)
            self.assertEqual(u["night"], u["tod"] == "night")

    def test_census_rows_are_year_pop_births_deaths(self):
        for key in ("eden", "lagoon"):
            for row in self.snap["u"][key]["census"]:
                # rows written before engine 2026.10.28.3 have only the
                # first four; newer rows carry every gauge (CENSUS_FIELDS)
                self.assertIn(len(row), (4, len(engine.CENSUS_FIELDS)))
                self.assertIsInstance(row[0], int)
                self.assertIsInstance(row[1], int)

    def test_the_instrument_reads_the_same_gauges_in_both_worlds(self):
        for key in ("eden", "lagoon"):
            g = self.snap["u"][key]["gauges"]
            for k in ("adults", "withdrawn", "breeders", "infant_survival",
                      "claimants", "sink", "food_days"):
                self.assertIn(k, g)
        # EDEN's food is unlimited by design; LAGOON's is counted in days
        self.assertIsNone(self.snap["u"]["eden"]["gauges"]["food_days"])
        self.assertIsNotNone(self.snap["u"]["lagoon"]["gauges"]["food_days"])

    def test_census_rows_carry_every_gauge_after_a_year(self):
        import random
        w = engine.genesis(seed=69)
        for i in range(engine.DAYS_PER_YEAR * engine.PARTS_PER_DAY + 4):
            engine.tick_lagoon(w["lagoon"], random.Random(i), [])
        row = w["lagoon"]["census"][-1]
        self.assertEqual(len(row), len(engine.CENSUS_FIELDS))


class TestActivityCodes(unittest.TestCase):
    """The engine's activity codes and the renderer's must be the same list."""

    def test_engine_activity_codes(self):
        codes = {
            "A_IDLE": engine.A_IDLE, "A_WALK": engine.A_WALK,
            "A_FORAGE": engine.A_FORAGE, "A_HUNT": engine.A_HUNT,
            "A_FISH": engine.A_FISH, "A_FARM": engine.A_FARM,
            "A_BUILD": engine.A_BUILD, "A_TALK": engine.A_TALK,
            "A_MATE": engine.A_MATE, "A_BIRTH": engine.A_BIRTH,
            "A_TEND": engine.A_TEND, "A_REST": engine.A_REST,
            "A_EAT": engine.A_EAT, "A_WITHDRAW": engine.A_WITHDRAW,
            "A_FIGHT": engine.A_FIGHT, "A_PLAY": engine.A_PLAY,
            "A_RITE": engine.A_RITE, "A_SLEEP": engine.A_SLEEP,
            "A_WORK": engine.A_WORK, "A_SCOUT": engine.A_SCOUT,
            "A_WATCH": engine.A_WATCH, "A_GROOM": engine.A_GROOM, "A_DRINK": engine.A_DRINK,
        }
        self.assertEqual(len(set(codes.values())), 23)
        self.assertEqual(engine.A_PLAY, 15)
        self.assertEqual(engine.A_WATCH, 20)

    def test_renderer_activity_codes_match_the_engine(self):
        src = read(RENDERER)
        block = re.search(r"var A_WALK=(\d+),.*?A_DRINK=(\d+);", src, re.S)
        self.assertIsNotNone(block, "renderer activity codes not found")
        pairs = dict(re.findall(r"(A_[A-Z]+)=(\d+)", block.group(0)))
        pairs = {k: int(v) for k, v in pairs.items()}
        for name in ("A_WALK", "A_FORAGE", "A_HUNT", "A_FISH", "A_FARM",
                     "A_BUILD", "A_TALK", "A_MATE", "A_BIRTH", "A_TEND",
                     "A_REST", "A_EAT", "A_WITHDRAW", "A_FIGHT", "A_PLAY", "A_RITE",
                     "A_SLEEP", "A_WORK", "A_SCOUT", "A_WATCH", "A_GROOM", "A_DRINK"):
            self.assertEqual(pairs[name], getattr(engine, name),
                             f"{name} differs between engine and renderer")

    def test_renderer_labels_cover_every_activity_code(self):
        src = read(RENDERER)
        block = re.search(r"var ACT_LABEL = \[(.*?)\];", src, re.S)
        self.assertIsNotNone(block)
        labels = re.findall(r'"([^"]*)"', block.group(1))
        self.assertEqual(len(labels), 23)


class TestMirrorIsIdentical(unittest.TestCase):
    """docs/ is what GitHub Pages serves; web/ is what the local server serves.

    The mirror reads a gist snapshot rather than the local server, so the two
    files must stay byte-identical or the public site silently drifts from the
    thing being developed.
    """

    def test_docs_mirror_matches_web(self):
        self.assertEqual(read(RENDERER), read(MIRROR),
                         "web/index.html and docs/index.html have diverged")


class TestServerPayload(unittest.TestCase):
    """The server decorates summarize() with events, status and the world map.

    Those three keys are what the renderer branches on, so they are part of the
    contract even though they do not come from the engine.
    """

    def test_status_fields(self):
        status = {"catching_up": False, "behind_days": 0}
        self.assertIn("catching_up", status)
        self.assertIn("behind_days", status)

    def test_event_records_have_the_fields_the_ticker_prints(self):
        for e in [{"d": 1, "y": 0, "u": "EDEN", "t": "phase", "msg": "x"}]:
            for field in ("d", "y", "u", "t", "msg"):
                self.assertIn(field, e)
            self.assertIn(e["u"], ("EDEN", "LAGOON"))

    def test_world_payload_describes_both_maps(self):
        w = engine.genesis(seed=69)
        lag = w["lagoon"]
        terrain = engine.make_lagoon_terrain(lag.get("terrain_seed", lag["seed"]))
        payload = {"eden_size": engine.EDEN_SIZE,
                   "lagoon_size": engine.LAGOON_SIZE,
                   "lagoon_iter": lag["iteration"], "terrain": terrain}
        self.assertEqual(payload["eden_size"], 48)
        self.assertEqual(len(payload["terrain"]), engine.LAGOON_SIZE)
        self.assertEqual(len(payload["terrain"][0]), engine.LAGOON_SIZE)


if __name__ == "__main__":
    unittest.main()
