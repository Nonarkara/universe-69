"""Read retained exact century endpoints; age cohorts are not viability estimates."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory', nargs='?', type=Path, default=Path(__file__).parent / 'arcs')
args = parser.parse_args()
report = {}
for seed in (7, 25, 69):
    folder = args.directory / ('seed-' + str(seed))
    compressed = folder / 'final-world.json.gz'
    path = compressed if compressed.exists() else folder / 'final-state.json'
    raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    world = json.loads(raw)
    provenance = json.loads((folder / 'provenance.json').read_text())
    assert provenance['sources_unchanged']
    rows = {}
    for key in ('eden', 'lagoon'):
        u = world[key]
        people = u['people']
        def age(p):
            return u['day'] - p['b']
        def count(sex, low, high=None):
            return sum(p['s'] == sex and age(p) >= low and
                       (high is None or age(p) <= high) for p in people)
        rows[key] = {
            'iteration': u['iteration'], 'day': u['day'], 'peak': u['peak'],
            'population': len(people), 'max_maternal_generation': u['gen_max'],
            'founders_alive': sum(p['g'] == 1 for p in people),
            'descendants_alive': sum(p['g'] > 1 for p in people),
            'clinical_age_females': count('f', 16*360, 45*360),
            'adult_males': count('m', 16*360),
            'children_female': count('f', 0, 16*360-1),
            'children_male': count('m', 0, 16*360-1),
            'pregnancies': sum(bool(p.get('due')) for p in people),
            'age_range_years': [round(min(map(age, people))/360, 2),
                                round(max(map(age, people))/360, 2)] if people else None,
            'withdrawn': sum(bool(p.get('w')) for p in people),
            'incompetent_model_flag': sum(not p.get('c', True) for p in people),
            'model_death_causes': u.get('cod', {}),
            'historical_discoveries': u.get('tech', []),
            'living_father_ids_recorded': sum(p.get('dad') is not None for p in people),
        }
    report[str(seed)] = {
        'state_sha256': hashlib.sha256(raw).hexdigest(),
        'engine': provenance['engine'], 'endpoint': rows,
        'qualifications': [
            'Female age band is the shipped clinical cycle gate; male adults have no behavioral upper-age cutoff.',
            'Age counts omit bodily readiness, locality, consent, kinship and partnership availability; they are not viable-mating estimates.',
            'Generation is the existing maternal-generation counter.',
            'Death counters do not identify causes of trajectory differences or forecast people.',
            'Positive headcount and young cohorts alone do not prove long-term viability.',
        ],
    }
print(json.dumps(report, indent=2))
