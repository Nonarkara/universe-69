"""Record iteration falls independently and compile paired history volumes.

Reads state and files, writes observer volumes and a durable index. Never
changes how a world evolves. The record is not the experiment.
"""

import copy
import json
import os
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def archive_run(data):
    """Archive the artifacts of one explicit restart; retain runtime config."""
    names = [name for name in ("state.json", "events.ndjson", "postmortems", "history-books")
             if os.path.exists(os.path.join(data, name))]
    if not names:
        return None
    archive = os.path.join(data, "archive")
    os.makedirs(archive, exist_ok=True)
    folder = tempfile.mkdtemp(prefix="run-" + time.strftime("%Y%m%d-%H%M%S") + "-", dir=archive)
    for name in names:
        os.replace(os.path.join(data, name), os.path.join(folder, name))
    return folder


def compile_book(world, root=None, data=None):
    """Write a history book if both universes are extinct. Return path or None."""
    root = root or ROOT
    data = data or os.path.join(root, "data")
    pm_dir = os.path.join(data, "postmortems")
    events_path = os.path.join(data, "events.ndjson")
    book_dir = os.path.join(data, "history-books")

    eden = world.get("eden") or {}
    lagoon = world.get("lagoon") or {}
    if eden.get("extinct_day") is None or lagoon.get("extinct_day") is None:
        return None

    os.makedirs(book_dir, exist_ok=True)
    ei = eden.get("iteration", 1)
    li = lagoon.get("iteration", 1)
    out = os.path.join(book_dir, f"book-eden{ei:03d}-lagoon{li:03d}.md")
    if os.path.exists(out):
        return out

    epm = next((p for p in reversed(eden.get("postmortems", [])) if p.get("iteration") == ei), None)
    lpm = next((p for p in reversed(lagoon.get("postmortems", [])) if p.get("iteration") == li), None)
    # load from disk if present, else from in-memory
    p = os.path.join(pm_dir, f"u6-iteration-{ei:03d}.json")
    if os.path.exists(p):
        with open(p) as f:
            epm = json.load(f)
    p = os.path.join(pm_dir, f"u9-iteration-{li:03d}.json")
    if os.path.exists(p):
        with open(p) as f:
            lpm = json.load(f)

    extinct_days = {"eden": eden["extinct_day"], "lagoon": lagoon["extinct_day"]}

    # events
    evs = []
    if os.path.exists(events_path):
        hi = max(extinct_days.values())
        with open(events_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                key = {"EDEN": "eden", "LAGOON": "lagoon"}.get(e.get("u"))
                universe = world.get(key) if key else None
                if universe and universe.get("founded_day", 0) <= e.get("d", 0) <= extinct_days[key]:
                    evs.append(e)

    def pm_block(pm, name):
        if not pm:
            return f"### {name}\n\n(no postmortem recorded)\n"
        lines = [f"### {name} — iteration {pm.get('iteration')}", ""]
        lines.append(f"- Extinct on sim-day {pm.get('day')} "
                     f"(year {pm.get('day', 0) // 360})")
        lines.append(f"- Engine: {pm.get('engine', 'unknown')}")
        lines.append(f"- Peak population: {pm.get('peak')}")
        lines.append(f"- Highest generation: {pm.get('gen_max')}")
        lines.append(f"- Dominant cause of death: **{pm.get('dominant_cause')}**")
        cod = pm.get("cod") or {}
        if cod:
            lines.append("- Causes of death: " + ", ".join(
                f"{k}={v}" for k, v in sorted(cod.items(), key=lambda kv: -kv[1])))
        if pm.get("tech"):
            lines.append("- Technologies reached: " + ", ".join(pm["tech"]))
        if pm.get("lessons_held"):
            lines.append("- Lessons held: " + ", ".join(pm["lessons_held"]))
        if "lesson" in pm:
            lines.append(f"- Lesson recorded for the next castaways: "
                         f"{pm.get('lesson') or 'none recorded'}")
        if "preventable" in pm:
            lines.append(f"- Model preventability flag (untested): {pm.get('preventable')}")
        lines.append("")
        return "\n".join(lines)

    with open(out, "w") as f:
        f.write(f"# History Book — EDEN iteration {ei}, LAGOON iteration {li}\n\n")
        f.write("Both universes are dead. The Observers write down what happened, "
                "how, and what the living can carry forward. Nothing in these pages "
                "intervenes; the pen and the lagoon are already quiet.\n\n")
        f.write("## Postmortems\n\n")
        f.write(pm_block(epm, "Universe 6 — EDEN"))
        f.write("\n")
        f.write(pm_block(lpm, "Universe 9 — LAGOON"))
        f.write("\n## Record of events\n\n")
        if evs:
            cur_year = None
            for e in evs:
                y = e.get("y", e.get("d", 0) // 360)
                if y != cur_year:
                    cur_year = y
                    f.write(f"\n### Year {y}\n\n")
                f.write(f"- Y{y} [{e.get('u')}] ({e.get('t')}) {e.get('msg')}\n")
        else:
            f.write("(no events recorded)\n")
        f.write("\n## What the dead leave behind\n\n")
        if lpm and lpm.get("lesson"):
            f.write(f"The model assigns LAGOON's next castaways **{lpm['lesson']}**; its benefit remains a hypothesis.\n")
        else:
            f.write("LAGOON left no new lesson this iteration.\n")
        f.write("EDEN inherits no lesson by experimental design. Its next reseed "
                "repeats the controlled conditions; this record does not establish causality.\n")
    return out


def compile_iterations(world, data):
    """Record each fall independently. Observer I/O only; never mutate state.

    The index retains records after the engine's bounded postmortem tail rolls
    over. Explicit genesis archives this directory with the rest of the run.
    """
    book_dir = os.path.join(data, 'history-books')
    index = os.path.join(book_dir, 'iterations.json')
    records = {}
    warnings = []
    index_damaged = False
    if os.path.exists(index):
        try:
            with open(index) as f:
                content = json.load(f)
                if not isinstance(content, dict) or content.get('schema') != 1 or not isinstance(content.get('records'), list):
                    raise ValueError('Unknown iteration index schema')
                for record in content['records']:
                    if (not isinstance(record, dict) or record.get('world') not in ('EDEN', 'LAGOON')
                            or type(record.get('iteration')) is not int or record['iteration'] < 1):
                        raise ValueError('Invalid iteration record identity')
                    records[(record['world'], record['iteration'])] = record
        except (OSError, ValueError, KeyError, TypeError):
            index_damaged = True
            warnings.append('Iteration index unreadable; coverage may be incomplete')
    for key, number in (('eden', 6), ('lagoon', 9)):
        u = world.get(key) or {}
        postmortems = {}
        pm_dir = os.path.join(data, 'postmortems')
        if os.path.isdir(pm_dir):
            for name in sorted(os.listdir(pm_dir)):
                if name.startswith('u%d-iteration-' % number) and name.endswith('.json'):
                    try:
                        with open(os.path.join(pm_dir, name)) as f:
                            pm = json.load(f)
                        if not isinstance(pm, dict) or type(pm.get('iteration')) is not int or pm['iteration'] < 1:
                            raise ValueError('Invalid postmortem identity')
                        postmortems[pm['iteration']] = pm
                    except (OSError, ValueError, KeyError, TypeError):
                        warnings.append('Unreadable postmortem: ' + name)
        for pm in u.get('postmortems', []):
            if not isinstance(pm, dict) or type(pm.get('iteration')) is not int or pm['iteration'] < 1:
                warnings.append('Invalid in-memory postmortem identity: ' + key.upper())
                continue
            postmortems.setdefault(pm['iteration'], pm)
        for iteration, pm in postmortems.items():
            identity = (key.upper(), iteration)
            if identity in records:
                continue  # immutable evidence from the first observation
            founded = pm.get('founded_day')
            if founded is None and iteration == u.get('iteration'):
                founded = u.get('founded_day')
            unknowns = ['Seed and source revision were not captured in the postmortem',
                        'Death counts do not establish the cause of extinction']
            if founded is None:
                unknowns.append('Founding day unavailable')
            if not pm.get('engine'):
                unknowns.append('Engine version unavailable')
            r = dict(world=key.upper(), iteration=iteration,
                     engine=pm.get('engine') or 'unknown',
                     engine_history=pm.get('engine_history') or [], founded_day=founded,
                     day=pm.get('day'), peak=pm.get('peak'), gen_max=pm.get('gen_max'),
                     dominant_cause=pm.get('dominant_cause'), cod=pm.get('cod') or {},
                     tech=pm.get('tech') or [], lessons_held=pm.get('lessons_held') or [],
                     lesson=pm.get('lesson'), scope='cumulative_iteration',
                     interpretation='Inherited lessons are model hypotheses, not a causal test. '
                     'A missing lesson means no mapped lesson was recorded; it does not prove inevitability.',
                     unknowns=unknowns)
            if founded is not None and r['day'] is not None:
                if any(isinstance(change, dict) and change.get('day') is not None
                       and founded <= change['day'] <= r['day']
                       and change.get('from') != change.get('to')
                       for change in r['engine_history']):
                    r['unknowns'].append('Cumulative counts span multiple engine versions')
            elif r['engine_history']:
                r['unknowns'].append('Engine changes recorded; iteration exposure is unknown')
            if not r['engine_history']:
                r['unknowns'].append('No engine transitions recorded; earlier provenance may be incomplete')
            records[identity] = copy.deepcopy(r)
    report = {'schema': 1, 'records': sorted(records.values(),
              key=lambda r: (r['day'] if r['day'] is not None else -1, r['world'], r['iteration']),
              reverse=True)}
    if warnings:
        report['warnings'] = warnings
    if not records:
        return report
    if index_damaged:
        # Do not overwrite an incomplete index; keep damaged evidence available
        # for repair and expose the coverage gap to the observer.
        return report
    os.makedirs(book_dir, exist_ok=True)
    for r in report['records']:
        path = os.path.join(book_dir, '%s-%03d.md' % (r['world'].lower(), r['iteration']))
        if os.path.exists(path):
            continue
        fd, pending = tempfile.mkstemp(prefix='.volume-', dir=book_dir)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('# %s — iteration %s\n\n' % (r['world'], r['iteration']))
                f.write('## Recorded observations\n\n')
                f.write('Counts cover the cumulative iteration, not an annual rate.\n\n')
                for name in ('engine', 'engine_history', 'founded_day', 'day', 'peak', 'gen_max', 'dominant_cause', 'cod', 'tech', 'lessons_held'):
                    f.write('- %s: %s\n' % (name, json.dumps(r[name], ensure_ascii=False)))
                f.write('\n## Candidate lesson\n\n%s\n\n%s\n' % (r['lesson'] or 'No mapped lesson recorded', r['interpretation']))
                f.write('\n## Unknowns\n\n' + '\n'.join('- ' + item for item in r['unknowns']) + '\n')
            os.replace(pending, path)
        finally:
            if os.path.exists(pending):
                os.unlink(pending)
    # Atomic replacement avoids a half-written index on an interrupted save.
    fd, pending = tempfile.mkstemp(prefix='.iterations-', dir=book_dir)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        os.replace(pending, index)
    finally:
        if os.path.exists(pending):
            os.unlink(pending)
    return report


def observe(world, data, previous=None):
    """A damaged observer archive must never stop the instrument ticking."""
    try:
        return compile_iterations(world, data)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = dict(previous or {'schema': 1, 'records': []})
        result['error'] = 'Iteration archive unavailable: ' + str(exc)
        return result
