"""Mechanical daily chronicle: digests new events into data/chronicle/.

Run manually or on a schedule:  python3 tools/chronicle.py
(The narrative chronicle is written by the scheduled Claude job; this one
guarantees records are collected even if Claude never shows up.)
"""

import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS = os.path.join(ROOT, "data", "events.ndjson")
OUTDIR = os.path.join(ROOT, "data", "chronicle")
BOOKMARK = os.path.join(OUTDIR, ".bookmark")

os.makedirs(OUTDIR, exist_ok=True)
start = 0
if os.path.exists(BOOKMARK):
    with open(BOOKMARK) as f:
        start = int(f.read().strip() or 0)

if not os.path.exists(EVENTS):
    raise SystemExit("no events yet")

with open(EVENTS) as f:
    lines = f.readlines()

new = lines[start:]
if not new:
    raise SystemExit("nothing new")

today = datetime.date.today().isoformat()
path = os.path.join(OUTDIR, f"{today}.md")
by_u = {"EDEN": [], "LAGOON": []}
for line in new:
    try:
        e = json.loads(line)
        by_u.setdefault(e["u"], []).append(e)
    except (ValueError, KeyError):
        continue

with open(path, "a") as f:
    f.write(f"\n## Digest written {datetime.datetime.now().isoformat(timespec='minutes')}\n")
    for uni in ("EDEN", "LAGOON"):
        evts = by_u.get(uni, [])
        if not evts:
            continue
        f.write(f"\n### Universe {'6 — EDEN' if uni == 'EDEN' else '9 — LAGOON'} "
                f"(years {evts[0]['y']}–{evts[-1]['y']}, {len(evts)} records)\n\n")
        for e in evts:
            f.write(f"- Y{e['y']} [{e['t']}] {e['msg']}\n")

with open(BOOKMARK, "w") as f:
    f.write(str(len(lines)))
print(f"chronicled {len(new)} events -> {path}")
