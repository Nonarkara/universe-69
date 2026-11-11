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


if __name__ == "__main__":
    unittest.main()
