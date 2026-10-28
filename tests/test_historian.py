"""History and explicit restart artifacts obey the configured data boundary."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "sim"))
import engine
import historian

from scratch_space import scratch_root
SCRATCH = scratch_root()


class TestHistory(unittest.TestCase):
    def test_a_living_world_has_no_history_directory_side_effect(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            self.assertIsNone(historian.compile_book(engine.genesis(), data=d))
            self.assertEqual(os.listdir(d), [])

    def test_custom_data_book_uses_current_iterations_and_memory_postmortems(self):
        w = engine.genesis()
        for u in (w['eden'], w['lagoon']):
            u['founded_day'], u['extinct_day'], u['iteration'] = 100, 200, 2
            u['postmortems'] = [{'iteration': 2, 'day': 200, 'peak': 27, 'engine': 'fixture-engine'}]
        before = copy.deepcopy(w)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            Path(d, 'events.ndjson').write_text('\n'.join(json.dumps({'d': day, 'u': 'EDEN', 'msg': text}) for day, text in ((50, 'old iteration'), (150, 'current event'), (250, 'after death'))))
            result = historian.compile_book(w, data=d)
            text = Path(result).read_text()
            self.assertTrue(result.startswith(d))
            self.assertIn('current event', text)
            self.assertNotIn('old iteration', text)
            self.assertNotIn('after death', text)
            self.assertIn('fixture-engine', text)
            self.assertIn('27', text)
        self.assertEqual(w, before)

    def test_explicit_restart_archives_every_run_artifact_once(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            data = Path(d)
            for name in ('state.json', 'events.ndjson', 'web.json'):
                (data / name).write_text(name)
            for name in ('postmortems', 'history-books'):
                (data / name).mkdir()
                (data / name / 'old').write_text(name)
            a = Path(historian.archive_run(d))
            for name in ('state.json', 'events.ndjson', 'postmortems', 'history-books'):
                self.assertTrue((a / name).exists())
                self.assertFalse((data / name).exists())
            self.assertEqual((data / 'web.json').read_text(), 'web.json')
            self.assertIsNone(historian.archive_run(d))
            (data / 'state.json').write_text('next')
            b = Path(historian.archive_run(d))
            self.assertNotEqual(a, b)
            self.assertEqual((a / 'state.json').read_text(), 'state.json')
            self.assertEqual((b / 'state.json').read_text(), 'next')
