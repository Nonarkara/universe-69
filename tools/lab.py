"""Universe 69 — the lab bench.

Runs a bounded arc locally instead of waiting on the 2016 MacBook, and prints
the one thing that matters: did the experiment actually produce its result?

    python3 tools/lab.py --days 60000
    python3 tools/lab.py --days 120000 --every 720 --json arc.json
    python3 tools/lab.py --from data/state.json --days 5000

Why this exists: a bounded local arc is faster than tuning against the live
run, which advances one sim-day every 2.4 real seconds by default. Arc runtime depends
on population and hardware; a century can take minutes. Use this harness
before touching the instrument.
"""

import argparse
import json
import os
import random
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))

import engine  # noqa: E402
import research  # noqa: E402


# ------------------------------------------------------------------ sampling

def sample(u, day):
    """One row of the arc for a universe."""
    people = u["people"]
    adults = [p for p in people if engine.age_of(p, day) >= engine.ADULT_AGE]
    row = {
        "day": day,
        "year": day // engine.DAYS_PER_YEAR,
        "pop": len(people),
        "peak": u["peak"],
        "gen": u["gen_max"],
        "iter": u["iteration"],
        "phase": u["phase"],
        "extinct_day": u["extinct_day"],
    }
    notes = [p.get('experience',{}).get('sites',[]) for p in people]
    row['knowledge'] = {
        'notes': sum(len(ns) for ns in notes),
        'reported_notes': sum(n.get('via') is not None for ns in notes for n in ns),
        'people_with_reports': sum(any(n.get('via') is not None for n in ns) for ns in notes),
        'max_hops': max((max(0,len(n.get('path',[]))-1) for ns in notes for n in ns),default=0),
    }
    if u["kind"] == "EDEN":
        row["withdrawn"] = sum(1 for p in people if p["w"])
        row["homeless"] = sum(1 for p in adults
                              if p.get("box") is None or p["box"] < 0)
        row["fertile_f"] = sum(
            1 for p in people if p["s"] == "f" and not p["w"]
            and engine.ADULT_AGE <= engine.age_of(p, day) <= 45 * engine.DAYS_PER_YEAR)
        row["competent_m"] = sum(
            1 for p in people if p["s"] == "m" and p["c"] and not p["w"]
            and engine.age_of(p, day) >= engine.ADULT_AGE)
        row["ennui"] = round(u.get("ennui", 0.0), 3)
    else:
        row["tech"] = list(u["tech"])
        row["tribes"] = len(u["settlements"])
        row["store"] = round(u.get("store", 0.0), 1)
        row["lessons"] = list(u.get("lessons", []))
        row["continent"] = bool(u.get("continent"))
        row["innocent"] = bool(u.get("innocent"))
    return row


# -------------------------------------------------------------------- verdict

def verdict(u, key):
    """Did this universe do the thing the design says it does?

    EDEN   must reach extinction and be reseeded — that is the whole point of
           the pen, and the postmortem that records it is the artifact.
    LAGOON must survive by learning: the lesson survives a wipe, the tech
           ladder advances, and the founders reach the greater shore.
    """
    name = "EDEN" if key == "eden" else "LAGOON"
    out = {"universe": name, "iteration": u["iteration"], "peak": u["peak"],
           "gen_max": u["gen_max"], "day": u["day"],
           "year": u["day"] // engine.DAYS_PER_YEAR}
    if key == "eden":
        out["phase"] = u["phase"]
        out["extinct_day"] = u["extinct_day"]
        out["postmortems"] = len(u["postmortems"])
        out["completed"] = bool(u["postmortems"]) or u["extinct_day"] is not None
        if u["extinct_day"] is None and u["postmortems"]:
            last = u["postmortems"][-1]
            out["verdict"] = (
                f"Pen emptied on day {last['day']} in iteration {last['iteration']}; "
                f"reseeded as iteration {u['iteration']} with {len(u['people'])} people. "
                f"{len(u['postmortems'])} postmortem(s) written.")
        elif not out["completed"]:
            out["verdict"] = (
                f"NEVER EMPTIED — still in phase '{u['phase']}' with "
                f"{len(u['people'])} people after {out['year']} years. "
                f"No postmortem, no reseed, no Ice-Age cycle.")
        else:
            out["verdict"] = (
                f"Pen emptied on day {u['extinct_day']} "
                f"(year {u['extinct_day'] // engine.DAYS_PER_YEAR}); "
                f"{len(u['postmortems'])} postmortem(s) written.")
    else:
        out["tech"] = list(u["tech"])
        out["lessons"] = list(u.get("lessons", []))
        out["tribes"] = len(u["settlements"])
        out["continent"] = bool(u.get("continent"))
        out["extinct_day"] = u["extinct_day"]
        out["postmortems"] = len(u["postmortems"])
        out["completed"] = u["extinct_day"] is not None
        missing = [name for name, _p, _b, _m in engine.TECH_LADDER
                   if name not in u["tech"]]
        out["tech_missing"] = missing
        if not out["completed"]:
            out["verdict"] = (
                f"Survived. {len(u['tech'])} technologies, "
                f"{len(u.get('lessons', []))} lesson(s) carried, "
                f"{len(u['settlements'])} tribe(s).")
        else:
            out["verdict"] = (
                f"Died on day {u['extinct_day']}; "
                f"{len(u['postmortems'])} postmortem(s) written.")
    return out


# ----------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Run a Universe 69 arc locally.")
    ap.add_argument("--days", type=int, default=60000,
                    help="sim-days to advance (default 60000 ≈ 166 years)")
    ap.add_argument("--seed", type=int, default=69)
    ap.add_argument("--every", type=int, default=engine.DAYS_PER_YEAR,
                    help="sample every N days (default: one year)")
    ap.add_argument("--from", dest="from_state", default=None,
                    help="continue from a saved state.json instead of genesis")
    ap.add_argument("--json", dest="json_out", default=None,
                    help="write the arc to this file")
    ap.add_argument("--quiet", action="store_true",
                    help="print only the verdict")
    args = ap.parse_args()

    if args.from_state:
        world = engine.load_state(args.from_state)
        print(f"[lab] continued from {args.from_state} at day "
              f"{world['eden']['day']}")
    else:
        world = engine.genesis(seed=args.seed)
        print(f"[lab] genesis, seed {args.seed}")

    arc = {"eden": [], "lagoon": []}
    milestones = []
    t0 = time.time()
    step = max(1, args.every)
    nxt = (world["eden"]["day"] // step + 1) * step
    events = []

    for d in range(args.days * engine.PARTS_PER_DAY):
        engine.tick_world(world, events)
        day = world["eden"]["day"]
        if day >= nxt:
            for key in ("eden", "lagoon"):
                arc[key].append(sample(world[key], day))
            nxt += step

    # the literature's hypotheses, tested against the arc just run
    research.record(world, research.evaluate(world))

    for key in ("eden", "lagoon"):
        arc[key].append(sample(world[key], world[key]["day"]))

    elapsed = time.time() - t0
    rate = args.days / elapsed if elapsed else 0

    # ---- the milestones, in order
    for e in events:
        day, uni, kind, msg = e
        if kind in ("phase", "extinction", "reseed", "lesson", "discovery",
                    "migration", "feud", "epidemic", "famine"):
            milestones.append({"day": day, "year": day // engine.DAYS_PER_YEAR,
                               "u": uni, "t": kind, "msg": msg})

    if not args.quiet:
        for key, label in (("eden", "UNIVERSE 6 · EDEN"),
                           ("lagoon", "UNIVERSE 9 · LAGOON")):
            u = world[key]
            print(f"\n=== {label} ===")
            print(f"{'yr':>5} {'pop':>5} {'peak':>5} {'gen':>4} {'phase':<10}"
                  f" {'extra':<28}")
            for row in arc[key]:
                if key == "eden":
                    extra = (f"withdrawn {row['withdrawn']:>3} "
                             f"fertF {row['fertile_f']:>3} "
                             f"compM {row['competent_m']:>3}")
                else:
                    extra = f"tech {len(row['tech'])} tribes {row['tribes']}"
                if row["extinct_day"] is not None:
                    extra += f"  EXTINCT d{row['extinct_day']}"
                print(f"{row['year']:>5} {row['pop']:>5} {row['peak']:>5} "
                      f"{row['gen']:>4} {row['phase']:<10} {extra:<28}")

    print("\n" + "=" * 64)
    print(f"[lab] {args.days} sim-days in {elapsed:.1f}s ({rate:,.0f} days/s)")
    print("=" * 64)
    verdicts = [verdict(world["eden"], "eden"),
                verdict(world["lagoon"], "lagoon")]
    for v in verdicts:
        print(f"\n{v['universe']}: {v['verdict']}")
        if v["universe"] == "LAGOON" and v.get("tech_missing"):
            print(f"  never discovered: {', '.join(v['tech_missing'])}")

    if milestones:
        print("\n--- milestones ---")
        for m in milestones:
            print(f"  Y{m['year']:<4} {m['u']:<7} [{m['t']}] {m['msg'][:96]}")

    # ---- the hypotheses the literature makes, and what this arc said
    rep = research.report(world)
    print("\n--- hypotheses ---")
    for r in rep["hypotheses"]:
        mark = {research.SUPPORTED: "yes", research.CONTRADICTED: "NO",
                research.UNDECIDED: ".."}[r["verdict"]]
        val = r["value"]
        val = ("%.3f" % val) if isinstance(val, float) else str(val)
        print(f"  {mark:>3} {r['id']:<26} {val:>10}  {r['statement'][:58]}")
    c = rep["counts"]
    print(f"  {c['supported']} supported, {c['contradicted']} contradicted, "
          f"{c['undecided']} undecided")

    if args.json_out:
        payload = {
            "seed": world["seed"],
            "days": args.days,
            "engine": engine.ENGINE_VERSION,
            "research": rep,
            "arc": arc,
            "milestones": milestones,
            "verdicts": verdicts,
            "postmortems": {k: world[k]["postmortems"]
                            for k in ("eden", "lagoon")},
        }
        with open(args.json_out, "w") as f:
            json.dump(payload, f, indent=1)
        print(f"\n[lab] arc written to {args.json_out}")


if __name__ == "__main__":
    main()
