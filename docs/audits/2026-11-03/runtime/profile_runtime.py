"""Bounded old-cohort continuation, never the live instrument. Standard library only."""
import argparse
import cProfile
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import pstats
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
INPUT = ROOT/'docs/audits/2026-10-30-agency/arcs/seed-69/final-world.json.gz'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources():
    return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted((ROOT/'sim').glob('*.py'))}


def canonical(value):
    # Use persisted state, then ignore only host timestamp metadata.
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items() if k not in ('epoch', 'wall')}
    if isinstance(value, list):
        return [canonical(v) for v in value]
    return value


def digest(value):
    return sha(json.dumps(canonical(value), sort_keys=True, separators=(',', ':')).encode())


def summary(world):
    return {k: {n: u.get(n) for n in ('engine', 'seed', 'fseed', 'iteration', 'day', 'part', 'parts', 'peak', 'gen_max')}
            | {'population': len(u['people'])} for k, u in world.items() if k in ('eden', 'lagoon')}


def worker(args):
    os.environ['UNIVERSE69_DATA'] = str(args.out/'unused-development-data')
    sys.path.insert(0, str(ROOT/'sim'))
    import engine
    assert 'server' not in sys.modules
    before = sources()
    compressed = args.input.read_bytes()
    raw = gzip.decompress(compressed)
    world = json.loads(raw)
    original = summary(world)
    engine.migrate(engine.validate_world(world))
    start = summary(world)
    events, samples = [], []
    profile = cProfile.Profile(timer=time.process_time) if args.worker == 'profile' else None
    process_start = time.process_time()
    load_start = os.getloadavg()
    checkpoint = None
    for i in range(200 if profile else 60):
        if profile:
            profile.enable()
        began = time.perf_counter()
        engine.tick_world(world, events)
        elapsed = time.perf_counter() - began
        if profile:
            profile.disable()
        samples.append(elapsed)
        if i == 59:
            path = args.out/(args.worker+'-60-persisted.json')
            engine.save_state(world, str(path))
            checkpoint = {'worldSHA256': digest(json.loads(path.read_text())),
                          'eventsSHA256': digest(events), 'events': len(events),
                          'summary': summary(world)}
    process_cpu = time.process_time() - process_start
    imported = sorted(str(Path(m.__file__).resolve().relative_to(ROOT))
                      for m in list(sys.modules.values())
                      if getattr(m, '__file__', None) and Path(m.__file__).resolve().parent == ROOT/'sim'
                      and Path(m.__file__).suffix == '.py')
    after = sources()
    result = {'mode': args.worker, 'python': sys.version, 'platform': platform.platform(),
              'machine': platform.machine(), 'engine': engine.ENGINE_VERSION,
              'input': str(args.input.relative_to(ROOT)), 'inputGzipSHA256': sha(compressed),
              'inputUncompressedSHA256': sha(raw), 'inputSummary': original,
              'migratedBefore': start, 'after': summary(world), 'parts': len(samples),
              'days': len(samples)/engine.PARTS_PER_DAY, 'tickWallSeconds': samples,
              'meanTickWallSeconds': sum(samples)/len(samples),
              'p95TickWallSeconds': sorted(samples)[math.ceil(.95*len(samples))-1],
              'maxTickWallSeconds': max(samples), 'processCPUSecondsIncludingCheckpointIO': process_cpu,
              'loadAverageStart': load_start, 'loadAverageEnd': os.getloadavg(),
              'checkpoint60': checkpoint, 'eventCount': len(events),
              'sourceBefore': before, 'sourceAfter': after,
              'importedSimulationSources': imported, 'serverImported': 'server' in sys.modules,
              'executedSourcesUnchanged': all(before[n] == after[n] for n in imported)}
    assert result['executedSourcesUnchanged']
    if profile:
        profile.dump_stats(str(args.out/'engine-200parts.prof'))
        stats = pstats.Stats(profile)
        def top(index):
            rows = sorted(stats.stats.items(), key=lambda item: item[1][index], reverse=True)[:10]
            return [{'file': key[0], 'line': key[1], 'function': key[2],
                     'primitiveCalls': val[0], 'totalCalls': val[1],
                     'selfCPUSeconds': val[2], 'cumulativeCPUSeconds': val[3]} for key, val in rows]
        result['top10SelfCPU'] = top(2)
        result['top10CumulativeCPU'] = top(3)
        text = io.StringIO()
        pstats.Stats(profile, stream=text).sort_stats('tottime').print_stats(10)
        pstats.Stats(profile, stream=text).sort_stats('cumulative').print_stats(10)
        (args.out/'profile-top10.txt').write_text(text.getvalue())
    (args.out/(args.worker+'.json')).write_text(json.dumps(result, indent=2)+'\n')
    print(args.worker, 'completed', len(samples), 'parts', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, default=INPUT)
    ap.add_argument('--out', type=Path, default=Path('/Volumes/Data/agent-scratch/u69-nov3-runtime'))
    ap.add_argument('--worker', choices=('profile', 'plain'))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.worker:
        worker(args)
        return
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')
    for mode in ('profile', 'plain'):
        subprocess.run([sys.executable, __file__, '--input', str(args.input), '--out', str(args.out), '--worker', mode],
                       check=True, env=env)
    prof = json.loads((args.out/'profile.json').read_text())
    plain = json.loads((args.out/'plain.json').read_text())
    comparison = {'parts': 60, 'separateProcesses': True, 'PYTHONHASHSEED': '0',
                  'worldMatches': prof['checkpoint60']['worldSHA256'] == plain['checkpoint60']['worldSHA256'],
                  'eventsMatch': prof['checkpoint60']['eventsSHA256'] == plain['checkpoint60']['eventsSHA256'],
                  'profiled': prof['checkpoint60'], 'unprofiled': plain['checkpoint60'],
                  'canonicalization': 'Actual engine.save_state omits universe runtime-cache keys; JSON key order canonicalized; only epoch/wall timestamp keys ignored.'}
    report = {'qualification': '50-day old-terrain/cohort .8 workbench continuation under current engine; not live data, a new-genesis century or MacBook throughput. Concurrent jobs and profiler overhead affect timings.',
              'runnerSHA256': sha(Path(__file__).read_bytes()), 'profile': prof, 'plain60': plain, 'parity60': comparison}
    (args.out/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    assert comparison['worldMatches'] and comparison['eventsMatch'], 'Profiling parity failed; inspect retained checkpoints'
    print('60-part persisted-world and event parity PASS', flush=True)


if __name__ == '__main__':
    main()
