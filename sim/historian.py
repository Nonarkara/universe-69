"""Compile the history book of a dead pair of universes.

Pure-ish: reads state and files, writes one markdown volume. Never changes
how a world evolves. The book is the record, not the experiment.
"""

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
                         f"{pm.get('lesson') or 'none (EDEN cannot learn)'}")
        if "preventable" in pm:
            lines.append(f"- Preventable: {pm.get('preventable')}")
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
            f.write(f"LAGOON's next castaways inherit the instinct **{lpm['lesson']}**.\n")
        else:
            f.write("LAGOON left no new lesson this iteration.\n")
        f.write("EDEN leaves nothing it can use: the pen itself is the cause, "
                "and the next reseed begins under identical conditions.\n")
    return out
