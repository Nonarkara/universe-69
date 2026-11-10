"""The gift between camps: goods move, a named pair keeps the partnership.

Engine 2026.11.11.1. A camp with lore and a full larder sends goods to the
nearest other camp on the same land once a year; the store really moves and
a partnership (st["gifts"], bounded at three, pruned deterministically)
grows both ways. Tests pin: the gate conditions, the goods really moving,
the partnership bounding, and the year-by-year growth toward trust.
"""

import copy
import random
import sys
import unittest

sys.path.insert(0, "sim")

import engine   # noqa: E402
import needs    # noqa: E402
import minds    # noqa: E402
import scripture  # noqa: E402


def _two_camps(days=100, store=6.0, lore=True):
    w = engine.genesis(7, 1)
    u = w["lagoon"]
    for _ in range(days):
        engine.tick_world(w, [])
    # a second camp on the same land, near the first
    st0 = u["settlements"][0]
    near = None
    for dx in range(-40, 41):
        for dy in range(-40, 41):
            if dx * dx + dy * dy > 900 or (dx == 0 and dy == 0):
                continue
            if needs_is_land(u, st0["x"] + dx, st0["y"] + dy):
                near = (st0["x"] + dx, st0["y"] + dy)
                break
        if near:
            break
    if near is None:
        near = (st0["x"] + 20, st0["y"])
    u["settlements"].append({"x": near[0], "y": near[1], "r": 4, "n": "Far Camp",
                             "store": store, "gifts": {}})
    for i, q in enumerate(u["people"]):
        q["st"] = 0 if i % 2 == 0 else 1
    if lore:
        u["tech"] = list(set((u.get("tech") or []) + ["lore"]))
    return u


def needs_is_land(u, x, y):
    from engine import terrain_of
    terr = terrain_of(u)
    n = len(terr)
    if not (0 < x < n - 1 and 0 < y < n - 1):
        return False
    return terr[y][x] != 2


class TestTheGift(unittest.TestCase):
    def test_a_genesis_camp_carries_the_ring(self):
        u = engine.genesis(69, 1)["lagoon"]
        self.assertEqual(u["settlements"][0].get("gifts"), {})

    def test_migration_gives_old_camps_the_ring(self):
        w = engine.genesis(69, 1)
        for st in w["lagoon"]["settlements"]:
            st.pop("gifts", None)
        loaded = engine.migrate(w)
        for st in loaded["lagoon"]["settlements"]:
            self.assertEqual(st.get("gifts"), {})

    def test_no_lore_no_gift(self):
        u = _two_camps(lore=False)
        before = [st["store"] for st in u["settlements"]]
        evts = []
        needs.kula(u, u["day"], random.Random(3), evts)
        self.assertEqual([st["store"] for st in u["settlements"]], before)
        self.assertFalse(evts)

    def test_an_empty_larder_gives_nothing(self):
        u = _two_camps()
        for st in u["settlements"]:
            st["store"] = 0.2
        evts = []
        needs.kula(u, u["day"], random.Random(3), evts)
        self.assertFalse(evts)

    def test_the_goods_really_move_and_the_pair_keeps_it(self):
        u = _two_camps()
        a, b = u["settlements"]
        a["store"], b["store"] = 8.0, 0.0
        stores_before = (a["store"], b["store"])
        gifts_before = (dict(a["gifts"]), dict(b["gifts"]))
        evts = []
        needs.kula(u, u["day"], random.Random(5), evts)
        gift_lines = [e for e in evts if e[2] == "gift"]
        self.assertTrue(gift_lines, "a camp with lore and a store sent nothing")
        self.assertLess(a["store"], stores_before[0])
        self.assertGreater(b["store"], stores_before[1])
        self.assertEqual(a["gifts"]["1"], needs.GIFT_SHARE)
        self.assertEqual(b["gifts"]["0"], needs.GIFT_SHARE)
        self.assertNotEqual(dict(a["gifts"]), gifts_before[0])
        self.assertIn("the exchange between the camps is kept", gift_lines[0][3])

    def test_the_ring_is_bounded(self):
        u = _two_camps()
        for st in u["settlements"]:
            st["gifts"] = {"9": 0.9, "8": 0.9, "7": 0.9, "6": 0.9}
        needs.kula(u, u["day"], random.Random(3), [])
        for st in u["settlements"]:
            self.assertLessEqual(len(st["gifts"]), needs.GIFT_PARTNERS)

    def test_years_of_gifts_reach_trust_and_the_scripture_counts_them(self):
        u = _two_camps()
        for st in u["settlements"]:
            st["store"] = 8.0
        for _ in range(4):                          # four yearly exchanges
            needs.kula(u, u["day"], random.Random(11), [])
        self.assertGreaterEqual(scripture.exchange_partners(u), 1,
                                "four exchanges did not make a partnership")
        s = scripture.for_world(u)
        self.assertGreaterEqual(s.get("exchange_partners", 0), 1)


if __name__ == "__main__":
    unittest.main()
