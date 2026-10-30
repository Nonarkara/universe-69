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

from tests.scratch_space import scratch_root
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
            u['postmortems'] = [{'iteration': 2, 'day': 200, 'peak': 27, 'engine': 'fixture-engine', 'lesson': None}]
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
            self.assertIn('none recorded', text)
            self.assertNotIn('none (EDEN cannot learn)', text)
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

class TestIterationHistory(unittest.TestCase):
    def test_independent_fall_is_recorded_without_changing_the_world(self):
        w = engine.genesis()
        w['lagoon']['founded_day'] = 120
        w['lagoon']['postmortems'] = [{'iteration': 1, 'day': 300, 'peak': 19,
            'gen_max': 2, 'cod': {'dehydration': 12}, 'dominant_cause': 'dehydration'}]
        before = copy.deepcopy(w)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            report = historian.compile_iterations(w, d)
            r = report['records'][0]
            self.assertEqual((r['world'], r['founded_day'], r['engine']), ('LAGOON', 120, 'unknown'))
            self.assertIsNone(r['lesson'])
            self.assertIn('not a causal test', r['interpretation'])
            self.assertTrue(Path(d, 'history-books', 'lagoon-001.md').exists())
            self.assertEqual(historian.compile_iterations(w, d), report)
        self.assertEqual(w, before)

    def test_disk_history_survives_reseed_and_bounded_memory(self):
        w = engine.genesis()
        w['lagoon']['iteration'], w['lagoon']['founded_day'] = 30, 9000
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            pm = Path(d, 'postmortems')
            pm.mkdir()
            (pm / 'u9-iteration-001.json').write_text(json.dumps({'iteration': 1,
                'day': 200, 'engine': 'old-engine', 'lesson': 'preserve', 'preventable': True}))
            report = historian.compile_iterations(w, d)
            r = report['records'][0]
            self.assertIsNone(r['founded_day'])
            self.assertEqual(r['engine'], 'old-engine')
            self.assertIn('Founding day unavailable', r['unknowns'])
            self.assertIn('not a causal test', r['interpretation'])
            (pm / 'u9-iteration-001.json').unlink()
            self.assertEqual(historian.compile_iterations(w, d), report)
            archived = Path(historian.archive_run(d))
            self.assertTrue((archived / 'history-books' / 'iterations.json').exists())
            self.assertEqual(historian.compile_iterations(engine.genesis(), d)['records'], [])

    def test_corrupt_evidence_is_reported_and_not_replaced(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            books = Path(d, 'history-books'); books.mkdir()
            index = books / 'iterations.json'; index.write_text('{broken')
            pm = Path(d, 'postmortems'); pm.mkdir()
            (pm / 'u9-iteration-001.json').write_text('{truncated')
            report = historian.observe(engine.genesis(), d)
            self.assertEqual(report['records'], [])
            self.assertEqual(len(report['warnings']), 2)
            self.assertEqual(index.read_text(), '{broken')

    def test_failed_archive_write_keeps_previous_observations(self):
        from unittest.mock import patch
        previous = {'schema': 1, 'records': [{'world': 'EDEN', 'iteration': 1}]}
        before = copy.deepcopy(previous)
        with patch.object(historian, 'compile_iterations', side_effect=PermissionError('read only')):
            report = historian.observe(engine.genesis(), 'unused', previous)
        self.assertEqual(report['records'], before['records'])
        self.assertIn('unavailable', report['error'])
        self.assertEqual(previous, before)

    def test_snapshot_facts_are_detached_and_mixed_engines_are_flagged(self):
        w = engine.genesis()
        pm = {'iteration': 1, 'day': 300, 'cod': {'thirst': 3}, 'tech': ['fire'],
              'engine': 'b', 'engine_history': [{'from': 'a', 'to': 'b', 'day': 10, 'part': 0}]}
        w['lagoon']['postmortems'] = [pm]
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            record = historian.observe(w, d)['records'][0]
            self.assertIn('Cumulative counts span multiple engine versions', record['unknowns'])
            record['cod']['thirst'] = 99
            record['tech'].append('writing')
            self.assertEqual(pm['cod']['thirst'], 3)
            self.assertEqual(pm['tech'], ['fire'])

    def test_index_identity_cannot_write_outside_the_archive(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            books = Path(d, 'history-books'); books.mkdir()
            index = books / 'iterations.json'
            index.write_text(json.dumps({'schema': 1, 'records': [
                {'world': '../../outside', 'iteration': 1}]}))
            report = historian.observe(engine.genesis(), d)
            self.assertTrue(report['warnings'])
            self.assertFalse(Path(d, 'outside-001.md').exists())
            self.assertEqual(report['records'], [])

    def test_corrupt_postmortem_does_not_block_healthy_record_persistence(self):
        w = engine.genesis()
        w['eden']['postmortems'] = [{'iteration': 1, 'day': 300}]
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            pm = Path(d, 'postmortems'); pm.mkdir()
            (pm / 'u9-iteration-001.json').write_text('{truncated')
            report = historian.observe(w, d)
            self.assertEqual(len(report['records']), 1)
            self.assertTrue(report['warnings'])
            self.assertEqual(json.loads(Path(d, 'history-books', 'iterations.json').read_text()), report)

    def test_lineage_transitions_before_a_reseed_do_not_claim_mixed_iteration(self):
        w = engine.genesis()
        w['lagoon']['founded_day'] = 100
        w['lagoon']['postmortems'] = [{'iteration': 1, 'day': 300, 'engine': 'c',
            'engine_history': [{'from': 'a', 'to': 'b', 'day': 10, 'part': 0},
                               {'from': 'b', 'to': 'c', 'day': 50, 'part': 0}]}]
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            record = historian.observe(w, d)['records'][0]
            self.assertNotIn('Cumulative counts span multiple engine versions', record['unknowns'])
            self.assertEqual(len(record['engine_history']), 2)

    def test_invalid_postmortem_identity_cannot_poison_the_index(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
            pm = Path(d, 'postmortems'); pm.mkdir()
            for iteration in (0, -1):
                (pm / ('u9-iteration-%s.json' % iteration)).write_text(json.dumps({'iteration': iteration}))
            report = historian.observe(engine.genesis(), d)
            self.assertEqual(report['records'], [])
            self.assertEqual(len(report['warnings']), 2)
            self.assertFalse(Path(d, 'history-books', 'iterations.json').exists())
