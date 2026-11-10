"""A killing's feud is an inheritance: it waits for the children.

The kin bond from a killing (2026.11.09.3) reaches the victim's partner,
the victim's parents, and the victim's children. A child cannot act on it —
rival_of only walks adults — so the grudge sits in the record until the day
the child grows up. These tests pin that silence, and its end.
"""

import random
import sys
import unittest

sys.path.insert(0, "sim")

import engine  # noqa: E402
import minds   # noqa: E402
import needs   # noqa: E402


class TestTheInheritedFuse(unittest.TestCase):
    def _lagoon(self):
        w = engine.genesis(7, 1)
        u = w["lagoon"]
        for _ in range(120):
            engine.tick_world(w, [])
        return u

    def _kill(self, u, killer, victim):
        people = u["people"]
        byid = {q["id"]: q for q in people}
        evts = []
        killer["gd"], killer["gk"] = 0.0, 0     # no standing revenge: a quarrel, not an avenging

        class Ledger:
            def random(self):
                return 0.0

            def sample(self, seq, k):
                rest = [x for x in seq if x is not victim][:k - 1]
                return [victim] + rest

        engine.lagoon_violence(u, killer, minds.ADULT_AGE, people, byid,
                               {}, [], Ledger(), evts)
        return evts

    def _child(self, u, mom=None, dad=None, grown=False):
        """A child of this pen, made the way the engine makes them."""
        day = u["day"]
        age_years = minds.ADULT_AGE if grown else 3
        kid = engine.person(u["next_id"], "Childof" + str(u["next_id"]),
                            random.choice("mf"), day - age_years * engine.DAYS_PER_YEAR,
                            2, 20, 20)
        kid["mom"] = mom
        kid["dad"] = dad
        u["next_id"] += 1
        u["people"].append(kid)
        return kid

    def test_a_child_of_either_slain_parent_inherits_the_cold_bond(self):
        u = self._lagoon()
        adults = [q for q in u["people"]
                  if engine.age_of(q, u["day"]) >= minds.ADULT_AGE and not q.get("w")]
        killer = next(q for q in adults if q["s"] == "m")
        victim = next(q for q in adults if q is not killer)
        child_mom = self._child(u, mom=victim["id"], dad=killer["id"])
        child_dad = self._child(u, dad=victim["id"], mom=killer["id"])
        self._kill(u, killer, victim)
        self.assertLessEqual(needs.aff_of(child_mom, killer["id"]), -0.85,
                             "a child of the slain mother inherited nothing")
        self.assertLessEqual(needs.aff_of(child_dad, killer["id"]), -0.85,
                             "a child of the slain father inherited nothing")

    def test_the_child_holds_it_silently_and_walks_when_grown(self):
        u = self._lagoon()
        adults = [q for q in u["people"]
                  if engine.age_of(q, u["day"]) >= minds.ADULT_AGE and not q.get("w")]
        killer = next(q for q in adults if q["s"] == "m")
        victim = next(q for q in adults if q is not killer)
        child = self._child(u, mom=victim["id"], dad=killer["id"])
        self._kill(u, killer, victim)
        self.assertLessEqual(needs.aff_of(child, killer["id"]), -0.85)
        self.assertIsNone(needs.rival_of(u, child),
                          "a child does not walk his inheritance before his time")
        # the same record, once the body is grown: the fuse is lit
        child["b"] = u["day"] - minds.ADULT_AGE * engine.DAYS_PER_YEAR - 30
        child["x"], child["y"] = killer["x"], killer["y"]
        rival = needs.rival_of(u, child)
        self.assertIsNotNone(rival, "the grown child does not know his enemy")
        self.assertEqual(rival[0], killer["id"])


if __name__ == "__main__":
    unittest.main()
