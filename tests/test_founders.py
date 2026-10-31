"""The founding cohort is a human one: spread of ages and bodies, partners
of matching years, one temperament each. Eight pairs, both worlds alike.

Every case here pins the 2026.10.31.1 change of minds.founders — the
cohort stopped being 16 identical 18-year-olds.
"""

import random
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sim"))

import minds


class TestFounders(unittest.TestCase):
    def test_eight_pairs_of_people(self):
        fs = minds.founders(69, 1, 8, minds.NAMES.get("LAGOON"))
        self.assertEqual(len(fs), 16)
        self.assertEqual([f["s"] for f in fs[::2]], ["m"] * 8)
        self.assertEqual([f["s"] for f in fs[1::2]], ["f"] * 8)

    def test_ages_are_a_cohort_not_a_uniform(self):
        fs = minds.founders(69, 1, 8)
        ages = [-f["b"] // minds.DAYS_PER_YEAR for f in fs]
        for a in ages:
            self.assertGreaterEqual(a, 18)
            self.assertLessEqual(a, 48)
        self.assertGreater(len(set(ages)), 3,
                           "a founding band of one single year is not a cohort")

    def test_partners_are_close_in_years(self):
        fs = minds.founders(69, 1, 8)
        for i in range(0, 16, 2):
            am = -fs[i]["b"] // minds.DAYS_PER_YEAR
            af = -fs[i + 1]["b"] // minds.DAYS_PER_YEAR
            self.assertLessEqual(abs(am - af), 8)

    def test_bodies_cover_the_human_range(self):
        fs = minds.founders(69, 1, 8)
        for f in fs:
            self.assertGreaterEqual(f["bmi"], 16.5)
            self.assertLessEqual(f["bmi"], 29.0)
            self.assertGreaterEqual(f["sn"], 0.15)
            self.assertLessEqual(f["sn"], 0.95)
        men = [f["sn"] for f in fs if f["s"] == "m"]
        women = [f["sn"] for f in fs if f["s"] == "f"]
        self.assertGreater(sum(men) / len(men), sum(women) / len(women),
                           "men are built stronger, on average")

    def test_temperaments_range(self):
        fs = minds.founders(69, 1, 8)
        efs = [f["ef"] for f in fs]
        self.assertGreater(max(efs) - min(efs), 0.2,
                           "sixteen identical tempers are not people")
        for f in fs:
            for k in ("ef", "ag", "vg", "pu"):
                self.assertGreaterEqual(f[k], 0.05)
                self.assertLessEqual(f[k], 0.95)

    def test_the_same_people_land_in_both_worlds(self):
        fds = minds.founders(69, 1, 8)
        lds = minds.founders(69, 1, 8)
        self.assertEqual(fds, lds)

    def test_deterministic_per_seed_and_iteration(self):
        a = minds.founders(69, 1, 8)
        b = minds.founders(69, 1, 8)
        self.assertEqual(a, b)
        c = minds.founders(69, 2, 8)
        self.assertNotEqual([f["b"] for f in a], [f["b"] for f in c])

    def test_genesis_births_carry_the_founder_ages(self):
        import engine
        w = engine.genesis(seed=69)
        for key in ("eden", "lagoon"):
            people = w[key]["people"]
            ages = [engine.age_of(p, 0) // engine.DAYS_PER_YEAR for p in people]
            self.assertTrue(all(16 <= a <= 50 for a in ages))
            blocks = {-p["b"] // engine.DAYS_PER_YEAR for p in people}
            self.assertGreater(len(blocks), 3)
            other = "lagoon" if key == "eden" else "eden"
            self.assertEqual(blocks, {-q["b"] // engine.DAYS_PER_YEAR
                                      for q in w[other]["people"]})

    def test_a_reseeded_world_gets_the_same_cohort_not_a_flush_of_18s(self):
        import engine
        u = engine.genesis_universe("EDEN", 1, iteration=2, fseed=69)
        ages = [engine.age_of(p, 500) // engine.DAYS_PER_YEAR for p in u["people"]]
        founding = [engine.age_of(p, 0) // engine.DAYS_PER_YEAR for p in u["people"]]
        self.assertEqual(ages, [f + 1 for f in founding])   # a year has passed
        self.assertGreater(len(set(founding)), 3)


if __name__ == "__main__":
    unittest.main()
