"""Bounded independent mechanism check, not a population/clinical calibration.

Only calendar/ovulation timing and healthy adult contact setup are controlled.
Every exposure comes from real encounters.propose/capture -> reproduction.record.
Expected clinical probabilities are transcribed from primary Li et al.2015 §2.3,
not imported from production constants. No gestation or population arc is run.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'sim'))
import encounters
import minds
import reproduction

PRIMARY = {-5: .04, -4: .13, -3: .08, -2: .29, -1: .27, 0: .08}
OVULATION = 100


def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'sim').glob('*.py'))}


def person(uid, sex):
    return {'id': uid, 's': sex, 'b': OVULATION - 25 * 360, 'due': 0,
            'x': 10, 'y': 10, 'tx': 10, 'ty': 10, 'a': minds.A_REST,
            'ad': 2, 'p': None, 'c': True, 'w': False, 'ab': False,
            'hun': 0., 'thirst': 0., 'ene': 1., 'inj': 0.,
            'ef': .6, 'ag': .4, 'vg': .7}


def clock(u, day, part):
    u.update(day=day, part=part, parts=day * 4 + part)


def setup(seed, relative_day):
    mother, father = person(1, 'f'), person(2, 'm')
    mother['reproduction'] = {'next_ovulation': OVULATION, 'cycle_index': 0,
                              'last_evaluated': None, 'exposures': []}
    u = {'kind': 'EDEN', 'seed': seed, 'iteration': 1, 'people': [mother, father]}
    clock(u, OVULATION + relative_day, 0)
    assert encounters.propose(u, mother, father, 'mate', u['parts'], (10, 10))
    assert encounters.propose(u, father, mother, 'mate', u['parts'], (10, 10))
    return u


def capture_record(u):
    mother, father = u['people']
    frame = encounters.capture(u, mother, {p['id']: p for p in u['people']}, u['parts'])
    assert frame and frame['mother'] == 1 and frame['father'] == 2
    return reproduction.record(u, [frame])


def finish(u, modifier=1., earlier_result=None):
    mother = u['people'][0]
    clock(u, OVULATION, 3)
    payload = reproduction.advance(u, mother, modifier)
    if earlier_result is not None:
        assert payload is None, 'same cycle allocated twice'
        payload = earlier_result
    assert reproduction.advance(u, mother, modifier) is None, 'repeat advance allocated twice'
    if payload:
        assert payload['father'] == 2 and payload['traits'] == [.6, .4, .7]
        assert payload['ovulation_day'] == OVULATION
    return payload, mother['reproduction']


def geometry_preflight():
    u = setup(0, -2)
    mother, father = u['people']
    father['x'] = 13
    assert encounters.propose(u, father, mother, 'mate', u['parts'], (13, 10))
    assert encounters.capture(u, mother, {1: mother, 2: father}, u['parts']) is None
    father['x'] = 10
    assert encounters.propose(u, father, mother, 'mate', u['parts'], (11, 10))
    assert encounters.capture(u, mother, {1: mother, 2: father}, u['parts']) is None
    assert encounters.propose(u, father, mother, 'mate', u['parts'], (10, 10))
    assert encounters.capture(u, mother, {1: mother, 2: father}, u['parts']) is not None
    return {'separated_contact_rejected': True, 'travelling_contact_rejected': True,
            'arrived_mutual_contact_captured': True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--replicas', type=int, default=10000)
    ap.add_argument('--out', type=Path, default=Path(__file__).parent / 'results.json')
    args = ap.parse_args()
    assert 10000 <= args.replicas <= 20000, 'bounded final verification requires 10k–20k per lag'
    before = hashes()
    started = time.monotonic()
    result = {'kind': 'Controlled mechanism/unit verification; not a population or clinical fit',
              'pythonVersion': sys.version, 'pythonExecutable': sys.executable,
              'runnerSHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'sourcesBefore': before, 'replicasPerLag': args.replicas,
              'source': 'Li D, Wilcox AJ, Dunson DB. Contraception2015;91:344–349 §2.3',
              'sourceURL': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4374046/',
              'expectedClinicalVector': {str(k): v for k, v in PRIMARY.items()},
              'seedRule': 'u.seed = 0..N-1 independently in each lag; fixed actor IDs/cycle index',
              'timingFixture': 'Known model ovulation day100; source opportunity recorded on O+lag; resolve at O part3',
              'geometryPreflight': geometry_preflight(), 'lags': [], 'failures': []}
    for lag, expected in PRIMARY.items():
        allocated = 0
        fingerprint = hashlib.sha256()
        controls = {'repeatedPartDayIdentical': 0, 'jsonRoundTripIdentical': 0,
                    'modifierAboveOneIdentical': 0}
        for seed in range(args.replicas):
            u = setup(seed, lag)
            assert capture_record(u) == 1
            assert reproduction.advance(u, u['people'][0]) is None  # not NIGHT
            original = copy.deepcopy(u)
            actual = finish(u)
            fingerprint.update(json.dumps(actual, sort_keys=True, separators=(',', ':')).encode())
            if actual[0]:
                allocated += 1
                assert math.isclose(actual[0]['chance'], expected, abs_tol=1e-14)
            duplicate = copy.deepcopy(original)
            earlier = None
            for part in range(4):
                clock(duplicate, OVULATION + lag, part)
                for _ in range(3):
                    assert capture_record(duplicate) == 0
                payload = reproduction.advance(duplicate, duplicate['people'][0])
                if payload:
                    assert earlier is None
                    earlier = payload
            assert finish(duplicate, earlier_result=earlier) == actual
            controls['repeatedPartDayIdentical'] += 1
            restored = json.loads(json.dumps(original))
            assert finish(restored) == actual
            controls['jsonRoundTripIdentical'] += 1
            capped = copy.deepcopy(original)
            assert finish(capped, modifier=5.) == actual
            controls['modifierAboveOneIdentical'] += 1
        proportion = allocated / args.replicas
        expected_se = math.sqrt(expected * (1 - expected) / args.replicas)
        observed_se = math.sqrt(proportion * (1 - proportion) / args.replicas)
        z = (proportion - expected) / expected_se
        if abs(z) > 6:
            result['failures'].append('lag{} exceeds6 Monte Carlo SE'.format(lag))
        row = {'relativeDay': lag, 'expectedClinicalProbability': expected,
               'allocations': allocated, 'replicas': args.replicas, 'proportion': proportion,
               'binomialSEAtExpected': expected_se, 'binomialSEObserved': observed_se,
               'zAtExpected': z, 'pairedControls': controls,
               'outcomeAndCycleStateSequenceSHA256': fingerprint.hexdigest()}
        result['lags'].append(row)
        print('day {:+d}: {}/{} = {:.5f}; expected {:.2f}; SE {:.5f}; z {:.2f}; paired {}'.format(
            lag, allocated, args.replicas, proportion, expected, expected_se, z, controls), flush=True)
    negatives = {}
    for name, lag, expose in [('noExposure', 0, False), ('outsideWindowOminus6', -6, True)]:
        allocations = 0
        for seed in range(args.replicas):
            u = setup(seed, lag)
            if expose:
                assert capture_record(u) == 1
            else:
                for person_ in u['people']:
                    person_['social'] = None
                    person_['a'] = minds.A_REST
                assert encounters.capture(u, u['people'][0], {p['id']:p for p in u['people']}, u['parts']) is None
            allocations += finish(u)[0] is not None
        assert allocations == 0
        negatives[name] = {'allocations': allocations, 'replicas': args.replicas}
    result['negativeControls'] = negatives
    result['sourcesAfter'] = hashes()
    result['sourceChangedDuringRun'] = before != result['sourcesAfter']
    result['moduleInputsChangedDuringRun'] = any(before[name] != result['sourcesAfter'][name]
        for name in ('sim/reproduction.py','sim/encounters.py','sim/minds.py'))
    result['elapsedSeconds'] = time.monotonic() - started
    result['qualifications'] = [
        'Outputs are allocated clinical-endpoint payloads; no actual fertilization, gestation or live births measured.',
        'Healthy adult EDEN contact setup and ovulation timing are controlled; no model probability constant was changed.',
        'Real captured frame ingestion, private seed trials, deduplication, modifier cap and JSON state persistence exercised.',
        'Binomial SE describes finite-seed mechanism variation, not uncertainty in clinical source estimates or population validity.',
        'No claim about independent social choice, natural contact frequency, latent sperm competition or prehistoric demography.',
        'Module-level exposure handling only; full engine physiological modifiers and integration verified separately.']
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print('Negative controls:', negatives, flush=True)
    print('Elapsed {:.2f}s; sourceChanged={}; failures={}'.format(
        result['elapsedSeconds'], result['sourceChangedDuringRun'], result['failures']), flush=True)
    if result['failures'] or result['moduleInputsChangedDuringRun']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
