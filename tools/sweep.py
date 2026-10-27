"""Universe 69 — the study bench for the pen.

Calhoun did not run one experiment. He ran a series of universes that differed
in architecture: how many nest boxes, how many animals per box, how much
space. And the conclusion that came out of the series — not out of Universe 25
alone — is that the outcome tracks the *distribution* of space and social
roles, not crowding as a number. The Ramsden & Adams critique in RESEARCH.md
puts the same point the other way round: the pathology tracked how the
architecture funnelled animals into contact, and Calhoun's own later work
showed the outcome was design-dependent rather than an iron law.

So the pen has to be a variable. This tool runs the same seed across a range
of pens and reports what each one does.

    python3 tools/sweep.py                       # the default study
    python3 tools/sweep.py --study calhoun      # a pen built like Universe 25
    python3 tools/sweep.py --study boxes        # vary the box count
    python3 tools/sweep.py --study crowding     # vary the threshold
    python3 tools/sweep.py --json sweep.json

Every number below is produced by running the shipped engine. None of them is
quoted from a log, a paper or a previous bake.
"""

import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))

import engine  # noqa: E402

THRESHOLDS = [50, 100, 200, 500, 1000, 2000, 3000, 5000]


def run_pen(label, days, cap, stagnation, boxes, box_cap, seed=69,
            stop_pop=4000):
    """Run one pen to `days` and report its whole arc.

    `stop_pop` ends the run once the population passes the point of interest:
    a pen with the pathology removed grows without limit, and simulating past
    the answer only costs time.
    """
    world = engine.genesis(seed=seed)
    engine.set_pen_design(world["eden"], cap=cap, stagnation=stagnation,
                          boxes=boxes, box_cap=box_cap)
    u = world["eden"]

    hit = {}
    peak = 0
    peak_year = 0
    phases = []          # (year, phase) transitions
    reseeds = 0
    extinct_seen = None  # a reseed wipes extinct_day, so catch it first
    reseed_day = None
    last_phase = None
    t0 = time.time()

    for _ in range(days * engine.PARTS_PER_DAY):
        engine.tick_world(world, [])
        n = len(u["people"])
        if n > peak:
            peak, peak_year = n, u["day"] // engine.DAYS_PER_YEAR
        for t in THRESHOLDS:
            if t not in hit and n >= t:
                hit[t] = u["day"] // engine.DAYS_PER_YEAR
        if u["phase"] != last_phase:
            phases.append((u["day"] // engine.DAYS_PER_YEAR, u["phase"]))
            last_phase = u["phase"]
        if u["extinct_day"] is not None and extinct_seen is None:
            extinct_seen = u["extinct_day"]
        if u["iteration"] > 1:
            reseeds = u["iteration"] - 1
            reseed_day = u["day"]
            break                      # the pen was reseeded: this iteration is done
        if n >= stop_pop:
            break

    design = engine.eden_design(u)
    slots = len(design["boxes"]) * design["box_cap"]
    out = {
        "label": label,
        "cap": design["cap"],
        "boxes": len(design["boxes"]),
        "box_cap": design["box_cap"],
        "box_slots": slots,
        "stagnation": design["stagnation"],
        "peak": peak,
        "peak_year": peak_year,
        "peak_pct_of_cap": round(100.0 * peak / design["cap"], 1),
        "peak_pct_of_slots": round(100.0 * peak / slots, 1) if slots else 0,
        "reached": {str(t): hit.get(t) for t in THRESHOLDS},
        "phases": phases,
        "reseeds": reseeds,
        "iterations": u["iteration"],
        "extinct_day": extinct_seen,
        "extinct_year": (extinct_seen // engine.DAYS_PER_YEAR
                         if extinct_seen is not None else None),
        "reseed_year": (reseed_day // engine.DAYS_PER_YEAR
                        if reseed_day is not None else None),
        "postmortems": len(u["postmortems"]),
        "seconds": round(time.time() - t0, 1),
    }
    return out


# ------------------------------------------------------------------- studies

def study_default():
    """The pen as built, and the pen with the pathology taken out."""
    return [
        ("pen as built (cap 900, 32 boxes x 7)", 900, 0.35, None, 7),
        ("no sink — demography alone", 100000, 9.0, None, 7),
    ]


def study_calhoun():
    """Universe 25 as Calhoun actually built it, and near neighbours.

    Universe 25: 256 nest boxes, ~15 mice per box, ~3,840 nominal capacity.
    The colony peaked near 2,200 around day 560 and stagnation began around
    day 315 with roughly 600 animals — that is, the sink appeared at about
    16% of nominal capacity, and the peak sat near 57%.
    """
    return [
        ("Universe 25 as built (256 boxes x 15, cap 3840)",
         3840, 0.157, 256, 15),
        ("same boxes, sink at 35%", 3840, 0.35, 256, 15),
        ("same boxes, sink at 10%", 3840, 0.10, 256, 15),
        ("Calhoun's boxes, 8 per box (2048 slots)",
         3840, 0.157, 256, 8),
        ("half the boxes (128 x 15 = 1920 slots)",
         3840, 0.157, 128, 15),
    ]


def study_boxes():
    """Vary the architecture while holding the crowding threshold."""
    return [(f"{n} boxes x 15 per box", 3840, 0.157, n, 15)
            for n in (16, 32, 64, 128, 256)]


def study_crowding():
    """Vary only where the sink begins."""
    return [(f"stagnation at {int(p*100)}% of cap", 3840, p, 256, 15)
            for p in (0.05, 0.10, 0.157, 0.25, 0.35, 0.50, 0.70)]


STUDIES = {
    "default": study_default,
    "calhoun": study_calhoun,
    "boxes": study_boxes,
    "crowding": study_crowding,
}


# -------------------------------------------------------------------- report

def fmt_reached(reached):
    cells = []
    for t in THRESHOLDS:
        y = reached.get(str(t))
        cells.append(f"{t}:{y if y is not None else '—'}")
    return "  ".join(cells)


def report(results, days):
    print(f"\n{'pen':<52} {'peak':>6} {'pk yr':>6} {'%cap':>6} "
          f"{'%slot':>6} {'ext yr':>7} {'reseed':>7}  phases")
    print("-" * 140)
    for r in results:
        ph = "→".join(f"{y}:{p[:6]}" for y, p in r["phases"]) or "—"
        ex = r["extinct_year"] if r["extinct_year"] is not None else "—"
        rs = r["reseed_year"] if r["reseed_year"] is not None else "—"
        print(f"{r['label']:<52} {r['peak']:>6} {r['peak_year']:>6} "
              f"{r['peak_pct_of_cap']:>5}% {r['peak_pct_of_slots']:>5}% "
              f"{ex:>7} {rs:>7}  {ph}")

    print("\n--- year each population size was first reached ---")
    for r in results:
        print(f"  {r['label']}")
        print(f"    {fmt_reached(r['reached'])}")

    print("\n--- what it means ---")
    for r in results:
        reached = r["reached"]
        tw = reached.get("2000")
        if tw is not None:
            print(f"  {r['label']}: 2000 people by year {tw} "
                  f"({'yes' if tw <= 100 else 'NO — later than a century'})")
        else:
            print(f"  {r['label']}: 2000 people NEVER reached "
                  f"(peak {r['peak']})")


def main():
    ap = argparse.ArgumentParser(description="Study the pen.")
    ap.add_argument("--study", default="default", choices=sorted(STUDIES))
    ap.add_argument("--days", type=int, default=120000,
                    help="sim-days per pen (default 120000 ≈ 333 years)")
    ap.add_argument("--seed", type=int, default=69)
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    print(f"[sweep] study '{args.study}', {args.days} sim-days per pen, "
          f"seed {args.seed}")
    results = []
    for label, cap, stag, boxes, bcap in STUDIES[args.study]():
        print(f"  … {label}")
        r = run_pen(label, args.days, cap, stag, boxes, bcap, seed=args.seed)
        results.append(r)
        print(f"    peak {r['peak']} in year {r['peak_year']} "
              f"({r['seconds']}s)")

    report(results, args.days)

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump({"study": args.study, "days": args.days,
                       "seed": args.seed, "results": results}, f, indent=1)
        print(f"\n[sweep] written to {args.json_out}")


if __name__ == "__main__":
    main()
