"""The inner life: tastes, projects, bonds, moods, omens, the long fuse
(2026.11.08.1 – 2026.11.09.1).

These mechanics exist so a viewer can follow a person — not a meter.
Each test pins a consequence of the record: a taste is stable and
bounded; a project is bent on, completes on the real outcome, and is
counted; a bond grows from actual completed contact and is named once;
a mood is a reading, never a state; an omen is strange at no one.
"""

import copy
import json
import random
import sys
import unittest

sys.path.insert(0, "sim")
sys.path.insert(0, "tools")

import engine      # noqa: E402
import needs       # noqa: E402
import drives      # noqa: E402
import minds       # noqa: E402
import scripture   # noqa: E402


def _world(parts=200):
    w = engine.genesis(69, 1)
    for _ in range(parts):
        engine.tick_world(w, [])
    return w


class TestTastes(unittest.TestCase):
    def setUp(self):
        self.w = _world(60)
        self.u = self.w["lagoon"]

    def test_tastes_differ_between_people_and_are_bounded(self):
        ts = [drives.taste(self.u, p, "company") for p in self.u["people"]]
        self.assertEqual(len(set(ts)), len(ts), "two people share one taste")
        for t in ts:
            self.assertGreaterEqual(t, -1.0)
            self.assertLessEqual(t, 1.0)

    def test_a_taste_is_for_life(self):
        p = self.u["people"][0]
        self.assertEqual(drives.taste(self.u, p, "work"),
                         drives.taste(self.u, p, "work"))

    def test_identity_changes_the_taste_not_the_world(self):
        p = self.u["people"][0]
        w2 = copy.deepcopy(self.w)
        q = next(c for c in w2["lagoon"]["people"] if c["id"] == p["id"])
        q["id"] = 123456
        self.assertNotEqual(drives.taste(self.u, p, "company"),
                            drives.taste(w2["lagoon"], q, "company"))


class TestProjects(unittest.TestCase):
    def test_goals_form_and_complete(self):
        w = _world(1200)                       # 300 days
        done = sum(p.get("goals_done", 0)
                   for k in ("eden", "lagoon") for p in w[k]["people"])
        self.assertGreater(done, 0, "nobody ever saw a project through")
        u = w["eden"]
        p = next((q for q in u["people"] if q.get("goal")), None)
        if p is not None:
            self.assertIn(p["goal"]["cat"], drives.TASTE_CATEGORIES)
            self.assertLess(p["goal"]["until"], u["day"] + 20)

    def test_a_project_bends_its_own_choices(self):
        w = _world(60)
        u = w["lagoon"]
        p = next(q for q in u["people"] if engine.age_of(q, u["day"]) >= minds.ADULT_AGE
                 and not q.get("w"))
        p["goal"] = {"what": "spend the days with people", "cat": "company",
                     "until": u["day"] + 30}
        counts = {"company": 0, "other": 0}
        for t in range(60):
            w2 = copy.deepcopy(w)
            q = next(c for c in w2["lagoon"]["people"] if c["id"] == p["id"])
            q["hun"] = 2.0; q["ene"] = 0.9; q["sol"] = 0.5; q["thirst"] = 0.0
            act = needs.assign(w2["lagoon"], q, w2["lagoon"]["day"], random.Random(1000 + t))
            counts["company" if needs.ACT_TASTE.get(act) == "company" else "other"] += 1
        self.assertGreater(counts["company"], 0,
                           "a company project never once bent a comfortable choice")


class TestBonds(unittest.TestCase):
    def test_completed_contact_grows_a_bond(self):
        w = _world(60)
        u = w["eden"]
        a, b = u["people"][0], u["people"][1]
        before = needs.aff_of(a, b["id"])
        now = u.get("parts", 0)
        engine.complete_social(u, [{"kind": "groom", "part": now, "ids": [a["id"], b["id"]]}])
        self.assertGreater(needs.aff_of(a, b["id"]), before)
        self.assertGreater(needs.aff_of(b, a["id"]), before)

    def test_a_fight_turns_two_names_cold(self):
        w = _world(60)
        u = w["lagoon"]
        men = [q for q in u["people"] if q["s"] == "m"
               and engine.age_of(q, u["day"]) >= minds.ADULT_AGE and not q.get("w")]
        a, b = men[0], men[1]
        rng = random.Random(5)
        before = needs.aff_of(a, b["id"])
        engine.pick_fight(u, a, u["people"], rng)
        self.assertLess(needs.aff_of(a, b["id"]), before)
        self.assertLess(needs.aff_of(b, a["id"]), before)

    def test_bonds_are_bounded_and_json_safe(self):
        w = _world(60)
        for k in ("eden", "lagoon"):
            for p in w[k]["people"]:
                aff = p.get("aff") or {}
                self.assertLessEqual(len(aff), needs.AFF_KEEP)
                for k2, v in aff.items():
                    self.assertIsInstance(k2, str)
                    json.dumps({k2: v})

    def test_friendship_is_said_once(self):
        w = engine.genesis(69, 1)
        u = w["eden"]
        a, b = u["people"][0], u["people"][1]
        for _ in range(6):
            needs.aff_touch(u, a, b["id"], 0.15)
        lines = [e for e in u.get("_buff", []) if e[1] == "bond"]
        self.assertEqual(len(lines), 1, "a friendship is named once, not every step")
        self.assertIn("have become close", lines[0][2])


class TestMoods(unittest.TestCase):
    def test_moods_are_read_from_the_record(self):
        w = _world(60)
        u = w["eden"]
        p = u["people"][0]
        self.assertTrue(needs.mood_word(u, p))
        p["hun"] = 30.0
        self.assertEqual(needs.mood_word(u, p), "hungry")
        p["hun"] = 0.0; p["gd"] = 0.9
        self.assertEqual(needs.mood_word(u, p), "grieving")
        p["gd"] = 0.0; p["aff"] = {"9": 0.9}
        self.assertEqual(needs.mood_word(u, p), "warm")

    def test_the_person_card_carries_the_inner_life(self):
        snap = engine.summarize(_world(200))
        d = next(iter(snap["u"]["eden"]["detail"].values()))
        self.assertEqual(len(d), 16, "person detail changed shape")
        self.assertIsInstance(d[13], str)          # mood
        self.assertIsInstance(d[14], str)          # project
        self.assertIsInstance(d[15], str)          # bond


class TestOmens(unittest.TestCase):
    def test_an_omen_is_strange_at_no_one(self):
        w = engine.genesis(69, 1)
        u = w["lagoon"]
        rng = random.Random(0)
        seen = 0
        for _ in range(4000):
            evts = []
            engine.omen(u, rng, evts)
            seen += len(evts)
            if seen:
                self.assertEqual(evts[0][2], "omen")
                break
        self.assertGreater(seen, 0, "no omen in 4000 rolls at p=0.004 is a broken roll")

    def test_lore_keeps_the_story(self):
        w = engine.genesis(69, 1)
        u = w["lagoon"]
        u["tech"] = ["lore"]
        u["stories"] = 0.0
        class FixedRng:
            def random(self):
                return 0.0                      # always fires
            def randrange(self, n):
                return 0
        evts = []
        engine.omen(u, FixedRng(), evts)
        self.assertEqual(len(evts), 1)
        self.assertGreater(u["stories"], 0.0, "a people with lore kept no story of it")


class TestTheLongFuse(unittest.TestCase):
    """A grudge is not only named, it walks; and peace is possible."""

    def setUp(self):
        self.w = _world(120)
        self.u = self.w["eden"]

    def test_peace_is_named_once(self):
        u = self.u
        a, b = u["people"][0], u["people"][1]
        needs.aff_touch(u, a, b["id"], -0.7)      # into the feud: named
        needs.aff_touch(u, a, b["id"], -0.1)      # deeper: not news
        needs.aff_touch(u, a, b["id"], 0.85)      # out and past friendship: named
        needs.aff_touch(u, a, b["id"], 0.1)       # warmer still: not news
        kinds = [e[1] for e in u.get("_buff", [])]
        self.assertEqual(kinds, ["feud", "peace"],
                         "a feud and its peace are each named once, not every step")

    def test_a_grudge_walks_toward_its_enemy(self):
        u = self.w["lagoon"]
        men = [q for q in u["people"] if q["s"] == "m" and not q.get("w")
               and engine.age_of(q, u["day"]) >= minds.ADULT_AGE]
        p, e = men[0], men[1]
        rival = needs.rival_of(u, {**p, "aff": {str(e["id"]): -0.95}})
        self.assertIsNotNone(rival, "a live adult enemy must be findable")
        aimed = walks = 0
        for t in range(24):
            w2 = copy.deepcopy(self.w)
            q = next(c for c in w2["lagoon"]["people"] if c["id"] == p["id"])
            q["aff"] = {str(e["id"]): -0.95}
            q["hun"] = 1.0; q["ene"] = 0.9; q["sol"] = 0.9; q["thirst"] = 0.0
            act = needs.assign(w2["lagoon"], q, w2["lagoon"]["day"], random.Random(500 + t))
            if q["tx"] == rival[1][0] and q["ty"] == rival[1][1]:
                aimed += 1
            if act == engine.A_WALK:
                walks += 1
        self.assertGreater(aimed, 0,
                           "in 24 calm draws a deep grudge never once aimed the walk")
        self.assertLess(aimed, 24,
                        "the grudge leaves room for the rest of a life")

    def test_rival_of_skips_the_dead_and_the_withdrawn(self):
        u = self.u
        men = [q for q in u["people"] if q["s"] == "m" and not q.get("w")
               and engine.age_of(q, u["day"]) >= minds.ADULT_AGE]
        p, dead_man, live = men[0], men[1], men[2]
        u["people"].remove(dead_man)              # the record loses the name
        p["aff"] = {str(dead_man["id"]): -1.0, str(live["id"]): -0.75}
        rival = needs.rival_of(u, p)
        self.assertEqual(rival[0], live["id"],
                         "a grudge walks only to someone still here")
        p["aff"] = {str(dead_man["id"]): -1.0}
        self.assertIsNone(needs.rival_of(u, p),
                          "no grudge walks with a gone name")
        p["aff"] = {str(live["id"]): -0.8}
        live["w"] = 1
        try:
            self.assertIsNone(needs.rival_of(u, p),
                              "no grudge walks to the withdrawn")
        finally:
            live["w"] = 0

    def test_a_quarrel_spent_gives_heat_back(self):
        u = self.u
        a, b = u["people"][0], u["people"][1]
        a["aff"] = {str(b["id"]): -0.9}
        a["a"] = minds.A_FIGHT
        a["fx"] = [b["id"], 1, u.get("parts", 0)]     # the brawl's time has run
        before = needs.aff_of(a, b["id"])
        needs.spend_quarrel(u, a)
        self.assertGreaterEqual(needs.aff_of(a, b["id"]) - before,
                                needs.AFF_SPEND - 1e-9)
        self.assertIsNone(a["fx"])
        lines = [e[2] for e in u.get("_buff", [])]
        self.assertTrue(any("made their peace" in x for x in lines),
                        "spending the last of a feud must be named")

    def test_a_brawl_settles_on_its_own_clock(self):
        """The full circuit: pick, stand, settle, and the record names the peace.

        A fighter's day can cut the brawl short in several ways (a fresh
        decision, a withdrawal). The quarrel's close is held by the brawl's
        own stint, so the record settles whatever the day did next."""
        u = self.u
        men = [q for q in u["people"] if q["s"] == "m" and not q.get("w")
               and engine.age_of(q, u["day"]) >= minds.ADULT_AGE]
        a, b = men[0], men[1]
        u["people"] = [a, b]                       # a pen of two
        a["aff"] = {str(b["id"]): -0.9}
        b["aff"] = {str(a["id"]): -0.9}
        for q in (a, b):
            q["x"] = 20; q["y"] = 20; q["tx"] = 20; q["ty"] = 20
        self.assertTrue(engine.pick_fight(u, a, u["people"], random.Random(3)))
        self.assertIsNotNone(a.get("fx"))
        evts = []
        for part in range(24):
            engine.tick_eden(u, random.Random(200 + part), evts)
            if not a.get("fx") and not b.get("fx"):
                break
        self.assertGreater(needs.aff_of(a, b["id"]), needs.AFF_FEUD,
                           "a feud-brawl spent settled nothing")
        kinds = [e[2] for e in evts]
        self.assertIn("peace", kinds)
        self.assertTrue(any("made their peace" in e[3] for e in evts),
                        "the record must name the peace once")

    def test_a_state_written_under_an_older_fx_shape_settles(self):
        """Migration safety: .09.1 wrote the two-field fx.

        The live instrument hit this as an IndexError on the first .09.2
        tick; a brawl that was under way when the file was written is
        over by definition and settles on sight."""
        u = self.u
        a, b = u["people"][0], u["people"][1]
        a["aff"] = {str(b["id"]): -0.9}
        a["fx"] = [b["id"], 1]
        before = needs.aff_of(a, b["id"])
        needs.spend_quarrel(u, a)
        self.assertGreaterEqual(needs.aff_of(a, b["id"]) - before,
                                needs.AFF_SPEND - 1e-9)
        self.assertIsNone(a["fx"])

    def test_strangers_who_brawl_are_nudged_feudward(self):
        u = self.u
        a, b = u["people"][0], u["people"][1]
        a["aff"] = {str(b["id"]): -0.15}
        a["a"] = minds.A_FIGHT
        a["fx"] = [b["id"], 0, u.get("parts", 0)]
        needs.spend_quarrel(u, a)
        self.assertEqual(needs.aff_of(a, b["id"]), 0.0,
                         "a stranger brawl cools by a scratch and is not a feud")

    def test_a_killing_turns_the_kin_cold(self):
        w = engine.genesis(7, 1)
        u = w["lagoon"]
        people = u["people"]
        adults = [q for q in people if engine.age_of(q, u["day"]) >= minds.ADULT_AGE
                  and not q.get("w")]
        killer = next(q for q in adults if q["s"] == "m")
        victim = next(q for q in adults if q is not killer)
        kin = next(q for q in adults if q is not killer and q is not victim)
        victim["p"] = kin["id"]                   # the kin: the victim's partner
        byid = {q["id"]: q for q in people}
        class Ledger:
            def random(self):
                return 0.0
            def sample(self, seq, k):
                return list(seq)[:k]
        ledger = Ledger()
        gone, dead = {}, []
        engine.lagoon_violence(u, killer, minds.ADULT_AGE, people, byid,
                               gone, dead, ledger, [])
        self.assertIn(victim["id"], gone)
        self.assertLessEqual(needs.aff_of(kin, killer["id"]), -0.85,
                             "the killing leaves the kin a cold name")
        feud_lines = [e for e in u.get("_buff", []) if e[1] == "feud"]
        self.assertTrue(any(kin.get("n", "") in e[2] for e in feud_lines),
                        "the record says who the feud belongs to")


class TestTheWholePerson(unittest.TestCase):
    def test_determinism_holds_with_the_inner_life(self):
        a, b = engine.genesis(69, 1), engine.genesis(69, 1)
        for _ in range(200):
            engine.tick_world(a, [])
            engine.tick_world(b, [])
        def norm(w):
            w = copy.deepcopy(w)
            w.pop("epoch", None); w.pop("clock", None)
            for k in ("eden", "lagoon"):
                for c in ("_ctx", "_demos", "_perception_grid", "_site_grid", "_buff"):
                    w[k].pop(c, None)
            return w
        self.assertEqual(json.dumps(norm(a), sort_keys=True),
                         json.dumps(norm(b), sort_keys=True))

    def test_migration_gives_old_people_an_inner_life(self):
        w = engine.genesis(69, 1)
        for k in ("eden", "lagoon"):
            for p in w[k]["people"]:
                for field in ("goal", "aff", "goals_done"):
                    p.pop(field, None)
        snap = json.loads(json.dumps(w))        # a legacy save on disk
        loaded = engine.migrate(engine.validate_world(snap))
        for k in ("eden", "lagoon"):
            for p in loaded[k]["people"]:
                self.assertIsNone(p["goal"])
                self.assertEqual(p["aff"], {})
                self.assertEqual(p["goals_done"], 0)

    def test_the_scripture_carries_the_chronicle(self):
        s = scripture.both(_world(1200))
        for k in ("eden", "lagoon"):
            ch = s[k].get("chronicle")
            self.assertIsNotNone(ch)
            self.assertIn("close_pairs", ch)
            self.assertIn("feuds", ch)
            self.assertIn("bent_on", ch)


if __name__ == "__main__":
    unittest.main()
