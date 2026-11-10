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


class TestTheBloodPrice(unittest.TestCase):
    """A killing's feud has one non-blood exit: the arbiter's price."""

    def _lagoon(self):
        w = engine.genesis(7, 1)
        u = w["lagoon"]
        for _ in range(120):
            engine.tick_world(w, [])
        return u

    def _scene(self, arb=0.0, store=5.0):
        u = self._lagoon()
        adults = [q for q in u["people"]
                  if engine.age_of(q, u["day"]) >= minds.ADULT_AGE and not q.get("w")]
        killer = next(q for q in adults if q["s"] == "m")
        victim = next(q for q in adults if q is not killer)
        widow = next(q for q in adults if q is not killer and q is not victim)
        victim["p"] = widow["id"]
        killer["gd"], killer["gk"] = 0.0, 0
        st = u["settlements"][killer.get("st", 0)]
        st["arb"] = arb
        st["store"] = store
        return u, killer, victim, widow, st

    def _ledger(self, victim, values):
        state = {"i": 0}

        class Ledger:
            def random(self):
                i = min(state["i"], len(values) - 1)
                state["i"] += 1
                return values[i]

            def sample(self, seq, k):
                return [victim] + [x for x in seq if x is not victim][:k - 1]

        return Ledger()

    def test_the_arbiter_exacts_a_price_and_the_feud_cools(self):
        u, killer, victim, widow, st = self._scene(arb=1.0, store=5.0)
        people = u["people"]
        byid = {q["id"]: q for q in people}
        evts = []
        engine.lagoon_violence(u, killer, engine.age_of(killer, u["day"]),
                               people, byid, {}, [],
                               self._ledger(victim, [0.0, 0.0, 0.0, 0.99, 0.99]), evts)
        laws = [e for e in evts if e[2] == "law"]
        self.assertTrue(laws, "a camp with an arbiter and a store named no price")
        self.assertIn("blood-price", laws[0][3])
        price = min(5.0, 0.8 + 0.6 * 1)                # the widow is the only kin
        self.assertEqual(st["store"], 5.0 - price,
                         "the price is paid in real goods")
        self.assertGreater(needs.aff_of(widow, killer["id"]), needs.AFF_FEUD,
                           "the paid feud did not settle")
        self.assertLess(widow["gd"], 1.0, "the revenge inclination is unmoved")
        kinds = [e[2] if len(e) == 4 else e[1]
                 for e in evts + u.get("_buff", [])]
        self.assertIn("peace", kinds, "a feud settled by goods is still named")

    def test_no_arbiter_no_store_no_price(self):
        u, killer, victim, widow, st = self._scene(arb=0.0, store=5.0)
        people = u["people"]
        byid = {q["id"]: q for q in people}
        evts = []
        engine.lagoon_violence(u, killer, engine.age_of(killer, u["day"]),
                               people, byid, {}, [],
                               self._ledger(victim, [0.0, 0.0, 0.99, 0.99, 0.99]), evts)
        self.assertFalse([e for e in evts if e[2] == "law"],
                         "no arbiter exacted a price")
        self.assertLessEqual(needs.aff_of(widow, killer["id"]), -0.85)
        self.assertEqual(st["store"], 5.0)

    def test_a_price_cannot_be_paid_from_an_empty_larder(self):
        u, killer, victim, widow, st = self._scene(arb=1.0, store=0.2)
        people = u["people"]
        byid = {q["id"]: q for q in people}
        evts = []
        engine.lagoon_violence(u, killer, engine.age_of(killer, u["day"]),
                               people, byid, {}, [],
                               self._ledger(victim, [0.0, 0.0, 0.0, 0.99, 0.99]), evts)
        self.assertFalse([e for e in evts if e[2] == "law"],
                         "a camp that cannot pay still 'paid'")
        self.assertEqual(st["store"], 0.2)


if __name__ == "__main__":
    unittest.main()
