"""Properties of shared fuzzy rules and stable illustrative personal sensitivity."""
import copy
import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sim'))
import drives


class TestDrives(unittest.TestCase):
    def setUp(self):
        self.u = {'fseed': 69, 'seed': 489, 'iteration': 1, 'kind': 'EDEN'}
        self.p = {'id': 1}

    def test_endpoints_bounds_and_monotonicity_for_each_personal_curve(self):
        for pid in range(32):
            self.p['id'] = pid
            for need in ('food', 'rest', 'company', 'intimacy'):
                m = drives.midpoint(self.u, self.p, need)
                self.assertTrue(.40 <= m <= .60,
                                "the personal midpoint left its band")
                values = [drives.response(self.u, self.p, need, i/1000.) for i in range(1001)]
                self.assertEqual(values, sorted(values))
                self.assertEqual(values[0], 0.)
                self.assertEqual(values[-1], 1.)
                self.assertEqual(drives.response(self.u,self.p,need,-10),0.)
                self.assertEqual(drives.response(self.u,self.p,need,10),1.)

    def test_midpoint_and_continuity_follow_shared_sugeno_rule(self):
        for need in ('food','rest','company','intimacy'):
            m = drives.midpoint(self.u,self.p,need)
            self.assertEqual(drives.response(self.u,self.p,need,m),.5)
            self.assertAlmostEqual(drives.response(self.u,self.p,need,m/2),.25)
            self.assertAlmostEqual(drives.response(self.u,self.p,need,(m+1)/2),.75)
            self.assertLess(abs(drives.response(self.u,self.p,need,m-1e-8)-.5),2e-8)
            self.assertLess(abs(drives.response(self.u,self.p,need,m+1e-8)-.5),2e-8)

    def test_matched_founders_share_profile_across_worlds(self):
        other = dict(self.u,kind='LAGOON',seed=492)
        for need in ('food','rest','company','intimacy'):
            self.assertEqual(drives.midpoint(self.u,self.p,need),drives.midpoint(other,self.p,need))

    def test_identity_need_and_iteration_distinguish_illustrative_preferences(self):
        a = drives.midpoint(self.u,self.p,'food')
        self.assertNotEqual(a,drives.midpoint(self.u,{'id':2},'food'))
        self.assertNotEqual(a,drives.midpoint(self.u,self.p,'rest'))
        self.assertNotEqual(a,drives.midpoint(dict(self.u,iteration=2),self.p,'food'))
        # Existing inherited traits do not invent unsupported appetite genes.
        self.assertEqual(a,drives.midpoint(self.u,dict(self.p,ef=0.,vg=1.),'food'))

    def test_legacy_defaults_json_roundtrip_and_no_mutation_or_rng(self):
        u={'seed':69}; p={'id':7}; before=copy.deepcopy((u,p)); rng=random.getstate()
        a=drives.response(u,p,'food',.3)
        self.assertEqual(a,drives.response(json.loads(json.dumps(u)),json.loads(json.dumps(p)),'food',.3))
        self.assertEqual(a,drives.response({'fseed':69,'iteration':1},p,'food',.3))
        self.assertEqual((u,p),before)
        self.assertEqual(random.getstate(),rng)


if __name__ == '__main__':
    unittest.main()
