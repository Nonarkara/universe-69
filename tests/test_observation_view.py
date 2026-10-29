"""Observer reading tests; Node is a workbench-only JavaScript test runner."""
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')


class Text(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.words = []
        self.tags = []
        self.feed(html)

    def handle_data(self, value):
        self.words.append(value)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)


@unittest.skipUnless(NODE, 'Node is required for workbench viewer tests')
class TestObservationView(unittest.TestCase):
    def render(self, observations=None, worlds=None):
        src = (ROOT / 'web/index.html').read_text()
        self.assertTrue('// ---- run observations' in src, 'Run observation renderer is missing')
        renderer = src[src.index('// ---- run observations'):src.index('var resTab=')]
        escape = src[src.index('function escapeHTML('):src.index('function resThreshold(')]
        script = escape + '\n' + renderer + '\nprocess.stdout.write(JSON.stringify(observationBlocks(' + json.dumps(observations) + ',' + json.dumps(worlds or {}) + ')));'
        result = subprocess.run([NODE, '-e', script], capture_output=True, text=True, check=True)
        blocks = json.loads(result.stdout)
        return Text(''.join(blocks))

    def test_first_living_iteration_has_honest_empty_state(self):
        text = self.render({'schema': 1, 'records': []}, {'eden': {'iter': 1, 'pop': 16}, 'lagoon': {'iter': 1, 'pop': 16}})
        words = ' '.join(text.words)
        self.assertIn('still running', words)
        self.assertIn('EDEN', words)
        self.assertIn('LAGOON', words)
        self.assertNotIn('No history', words)

    def test_legacy_absence_does_not_erase_history(self):
        words = ' '.join(self.render().words)
        self.assertIn('unavailable', words)
        self.assertIn('earlier runs', words.lower())

    def test_two_falls_preserve_facts_candidate_and_unknowns(self):
        records = []
        for iteration, world in [(1, 'LAGOON'), (2, 'LAGOON')]:
            records.append({'world': world, 'iteration': iteration, 'engine': 'test-engine',
                            'founded_day': None, 'day': 7200, 'peak': 83, 'gen_max': 4,
                            'dominant_cause': 'famine', 'cod': {'famine': 55, 'predator': 7},
                            'tech': ['fire', 'preservation'], 'lessons_held': ['vigilance'],
                            'lesson': 'preserve', 'scope': 'cumulative_iteration',
                            'interpretation': 'Candidate reading, still to test.',
                            'unknowns': ['Founding date is missing.', 'Final crisis is not isolated.']})
        words = ' '.join(self.render({'schema': 1, 'records': records}, {'eden': {'iter': 1, 'pop': 16}, 'lagoon': {'iter': 3, 'pop': 16}}).words)
        for phrase in ['LAGOON', 'EDEN', 'run 1', 'run 2', 'run 3', 'Still running', 'test-engine', '7200', '83', '55', '7',
                       'fire', 'preservation', 'vigilance', 'preserve', 'Candidate lesson',
                       'Candidate reading, still to test.', 'Founding date is missing.', 'Final crisis is not isolated.']:
            self.assertIn(phrase, words)
        self.assertIn('not recorded', words)
        self.assertIn('full iteration', words)

    def test_archive_failures_remain_visible_even_without_records(self):
        words = ' '.join(self.render({'schema': 1, 'records': [],
                                     'error': 'History unavailable',
                                     'warnings': ['Unreadable postmortem: lagoon-2']}).words)
        self.assertIn('Archive error:', words)
        self.assertIn('History unavailable', words)
        self.assertIn('Unreadable postmortem: lagoon-2', words)
        self.assertIn('Run records unavailable', words)

    def test_engine_transition_values_are_preserved(self):
        record = dict(world='LAGOON', iteration=2, engine='engine-b', engine_history=[
            {'from': 'engine-a', 'to': 'engine-b', 'day': 4321, 'part': 3}])
        words = ' '.join(self.render({'schema': 1, 'records': [record]}).words)
        for phrase in ['engine-a', 'engine-b', '4321', 'part 3', 'Lineage engine transition:']:
            self.assertIn(phrase, words)

    def test_every_external_string_is_literal(self):
        marker = '<i data-observation-probe>literal</i>'
        record = dict(world=marker, iteration=marker, engine=marker, founded_day=marker,
                      day=marker, peak=marker, gen_max=marker, dominant_cause=marker,
                      cod={marker: marker}, tech=[marker], lessons_held=[marker], lesson=marker,
                      interpretation=marker, unknowns=[marker], scope='cumulative_iteration')
        result = self.render({'schema': 1, 'records': [record]})
        self.assertNotIn('i', result.tags)
        self.assertGreaterEqual(' '.join(result.words).count(marker), 14)
