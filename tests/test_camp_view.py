"""Local camp-state authority and active-job text, without a browser dependency."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'Node is a workbench-only viewer test runner')
class TestCampVisualState(unittest.TestCase):
    def run_helper(self, expression):
        src = (ROOT / 'web/index.html').read_text()
        self.assertTrue('// ---- local camp state' in src, 'Local camp-state helper missing')
        helpers = src[src.index('// ---- local camp state'):src.index('// ---- LAGOON ---')]
        js = helpers + '\nprocess.stdout.write(JSON.stringify(' + expression + '));'
        return json.loads(subprocess.run([NODE, '-e', js], check=True, capture_output=True, text=True).stdout)

    def test_global_technology_never_builds_an_authoritative_camp(self):
        result = self.run_helper("campVisualState({tech:['fire','granary','writing'],camp_state:[]},{x:2,y:3})")
        self.assertFalse(result['fire'])
        self.assertFalse(result['granary'])
        self.assertFalse(result['writing'])
        self.assertEqual(result['domestic'], 0)
        self.assertFalse(result['legacy'])

    def test_only_matching_local_camp_assets_and_work_are_used(self):
        result = self.run_helper("campVisualState({tech:[],camp_state:[{x:2,y:3,fire:false,granary:true,domestic:4,writing:true,work:{granary:1,domestication:0.4,writing:1}},{x:9,y:9,fire:true}]},{x:2,y:3})")
        self.assertFalse(result['fire'])
        self.assertTrue(result['granary'])
        self.assertTrue(result['writing'])
        self.assertEqual(result['domestic'], 4)
        self.assertEqual(result['work']['domestication'], 0.4)

    def test_legacy_global_fire_fallback_is_explicitly_unverified(self):
        result = self.run_helper("campVisualState({tech:['fire']},{x:2,y:3})")
        self.assertTrue(result['fire'])
        self.assertTrue(result['legacy'])
        self.assertFalse(result['granary'])

    def test_authoritative_no_fire_beats_global_discovery(self):
        result = self.run_helper("campVisualState({tech:['fire'],camp_state:[{x:2,y:3,fire:false}]},{x:2,y:3})")
        self.assertFalse(result['fire'])
        self.assertFalse(result['legacy'])

    def test_physical_cache_key_tracks_assets_not_global_discovery(self):
        result = self.run_helper("[campVisualKey({tech:['fire'],camp_state:[{x:2,y:3,fire:false}]}),campVisualKey({tech:[],camp_state:[{x:2,y:3,fire:true}]})]")
        self.assertNotEqual(*result)

    def test_craft_activity_is_person_specific(self):
        result = self.run_helper("[craftActivity({crafts:{7:'granary',8:'writing'}},7),craftActivity({crafts:{7:'granary',8:'writing'}},8),craftActivity({crafts:{7:'granary'}},9)]")
        self.assertEqual(result, ['building a grain store', 'making records', ''])
