"""The hearth passes: the eldest child keeps the dead's home (2026.11.12.4).

A place held across a generation, in the lagoon where homes are hearths.
Pure bookkeeping over the kinship the record already holds — no new
fields, no new RNG. Pins: the heir is the eldest, the line is said once,
and EDEN (whose homes are boxes, claimed and released) is untouched.
"""

import sys
import unittest

sys.path.insert(0, "sim")

import engine   # noqa: E402
import minds    # noqa: E402
import needs    # noqa: E402


def _family(world_key="lagoon"):
    w = engine.genesis(7, 1)
    for _ in range(2400):
        engine.tick_world(w, [])
    u = w[world_key]
    adults = [q for q in u["people"]
              if engine.age_of(q, u["day"]) >= minds.ADULT_AGE and not q.get("w")]
    for p in adults:
        kids = [r for r in u["people"]
                if not r.get("w") and r is not p
                and (r.get("mom") == p["id"] or r.get("dad") == p["id"])]
        if kids:
            return w, u, p, kids
    # a seed with no births yet: make the kinship the engine's own way
    p = adults[0]
    kid = engine.person(u["next_id"], "Heir", "f", u["day"] - 600, 3, p["x"], p["y"])
    kid["mom"] = p["id"]
    kid["dad"] = p["id"]
    u["people"].append(kid)
    u["next_id"] += 1
    return w, u, p, [kid]


class TestTheHearthPasses(unittest.TestCase):
    def test_the_eldest_child_keeps_the_hearth(self):
        w, u, p, kids = _family()
        hx, hy = p.get("hx"), p.get("hy")
        for k in kids:                           # the heirs live elsewhere first
            k["hx"], k["hy"] = 1, 1
        engine.remove_dead(u, [p])
        holder = [k for k in kids if (k.get("hx"), k.get("hy")) == (hx, hy)]
        self.assertEqual(len(holder), 1, "the hearth passed to no one, or to many")
        line = [e for e in u.get("_buff", []) if e[1] == "heir"]
        self.assertEqual(len(line), 1, "a passing is named once")
        self.assertIn("keeps", line[0][2])
        self.assertIn(p.get("n", "?"), line[0][2])

    def test_no_line_when_the_heir_already_lives_there(self):
        w, u, p, kids = _family()
        hx, hy = p.get("hx"), p.get("hy")
        for k in kids:
            k["hx"], k["hy"] = hx, hy
        engine.remove_dead(u, [p])
        self.assertFalse([e for e in u.get("_buff", []) if e[1] == "heir"],
                         "the record repeated what was already true")

    def test_the_eldest_child_not_the_youngest(self):
        w, u, p, kids = _family()
        # two heirs: the older one keeps the hearth
        younger = kids[0]
        older = engine.person(u["next_id"], "Elder", "f",
                              u["day"] - 900, 3, p["x"], p["y"])
        older["mom"] = p["id"]
        u["people"].append(older)
        u["next_id"] += 1
        hx, hy = p.get("hx"), p.get("hy")
        for k in kids + [older]:
            k["hx"], k["hy"] = 1, 1
        engine.remove_dead(u, [p])
        self.assertEqual((older.get("hx"), older.get("hy")), (hx, hy),
                         "the hearth passed to the younger child")
        self.assertEqual((younger.get("hx"), younger.get("hy")), (1, 1),
                         "the younger child was moved too")

    def test_eden_boxes_are_not_a_hearth(self):
        w = engine.genesis(7, 1)
        for _ in range(120):
            engine.tick_world(w, [])
        u = w["eden"]
        p = u["people"][0]
        hx, hy = p.get("hx"), p.get("hy")
        p["hx"], p["hy"] = 21, 21
        engine.remove_dead(u, [p])
        self.assertNotEqual((p.get("hx"), p.get("hy")), (None, None))
        self.assertFalse([e for e in u.get("_buff", []) if e[1] == "heir"],
                         "EDEN named a passing it does not have")


def _pair(u, a, b):
    """Bond two adults the way the engine's pairings do."""
    a["p"], b["p"] = b["id"], a["id"]


def _hut(u, owner_key, done=True):
    st = u["settlements"][0]
    h = {"own": owner_key, "x": st["x"] + 2, "y": st["y"] + 2,
         "w": needs.HUT_WORK if done else needs.HUT_WORK * 0.4,
         "done": done}
    st.setdefault("huts", []).append(h)
    return h


class TestTheRoofPasses(unittest.TestCase):
    """The roof passes with the hearth (2026.11.12.6): the dead pair's hut
    goes to the heir's pair when they have none, a widow keeps hers, a lone
    heir keeps the hearth but not a pair's bed."""

    def setUp(self):
        w = engine.genesis(7, 1)
        for _ in range(2400):
            engine.tick_world(w, [])
        self.w = w
        self.u = w["lagoon"]
        adults = [q for q in self.u["people"]
                  if engine.age_of(q, self.u["day"]) >= minds.ADULT_AGE
                  and not q.get("w")]
        # a founding couple with a finished hut, and their eldest child in
        # a pair of their own, living apart
        self.dad = adults[0]
        self.mom = adults[1]
        _pair(self.u, self.dad, self.mom)
        self.kid = adults[2]
        self.kidmate = adults[3]
        _pair(self.u, self.kid, self.kidmate)
        # the kinship, explicit: the eldest child of this couple, however
        # the generated world happened to arrange its families
        self.kid["mom"], self.kid["dad"] = self.dad["id"], self.mom["id"]
        for q in (self.kid, self.kidmate):
            q["hx"], q["hy"] = 3, 3
        self.hut = _hut(self.u, min(self.dad["id"], self.mom["id"]))

    def test_the_heirs_pair_takes_the_roof(self):
        _pair_key = min(self.dad["id"], self.mom["id"])
        engine.remove_dead(self.u, [self.dad, self.mom])
        self.assertEqual(self.hut["own"], min(self.kid["id"], self.kidmate["id"]),
                         "the roof did not pass to the heir's pair")
        line = [e for e in self.u.get("_buff", []) if e[1] == "heir"]
        self.assertTrue(any("hearth and roof" in e[2] for e in line),
                         "the record did not say the roof passed")

    def test_a_living_widow_keeps_her_roof(self):
        engine.remove_dead(self.u, [self.dad])
        self.assertEqual(self.hut["own"], min(self.dad["id"], self.mom["id"]),
                         "the widow's roof was taken")
        line = [e for e in self.u.get("_buff", []) if e[1] == "heir"]
        self.assertTrue(line and all("roof" not in e[2] for e in line),
                        "the record said a roof that did not pass")

    def test_an_heir_who_has_a_roof_does_not_take_another(self):
        own = _hut(self.u, min(self.kid["id"], self.kidmate["id"]))
        self.assertIsNot(own, self.hut, "sanity: two distinct huts")
        engine.remove_dead(self.u, [self.dad, self.mom])
        self.assertEqual(self.hut["own"], min(self.dad["id"], self.mom["id"]),
                         "the heir's pair took a roof they did not need")
        self.assertEqual(own["own"], min(self.kid["id"], self.kidmate["id"]))

    def test_a_lone_heir_keeps_the_hearth_not_the_bed(self):
        self.kid["p"] = None
        self.kidmate["p"] = None
        engine.remove_dead(self.u, [self.dad, self.mom])
        self.assertEqual(self.hut["own"], min(self.dad["id"], self.mom["id"]),
                         "a lone heir was given a pair's bed")
        self.assertEqual((self.kid["hx"], self.kid["hy"]),
                         (self.dad["hx"], self.dad["hy"]),
                         "the hearth still passed to the eldest child")
        line = [e for e in self.u.get("_buff", []) if e[1] == "heir"]
        self.assertTrue(line and all("roof" not in e[2] for e in line))

    def test_the_unfinished_roof_is_taken_and_continued(self):
        self.hut["w"] = needs.HUT_WORK * 0.4
        self.hut["done"] = False
        engine.remove_dead(self.u, [self.dad, self.mom])
        self.assertEqual(self.hut["own"], min(self.kid["id"], self.kidmate["id"]),
                         "an unfinished roof was left orphaned")
        # the heir's pair finds it as their own and continues the work
        h = needs.hut_of(self.u, self.kid)
        self.assertIs(h, self.hut, "the heir's pair does not find the roof")


if __name__ == "__main__":
    unittest.main()
