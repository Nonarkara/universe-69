"""The probe: are these people independent thinkers, and are these islands livable?

A watchable world needs three things proven, not assumed:

1. **Independence** — the same body in the same situation must be able to
   choose differently, and different bodies in the same situation must
   diverge. Clone one person many times at one moment of one world,
   varying only the identity that seeds their personal fuzzy
   sensitivities (`drives.midpoint`), holding the decision RNG fixed so
   no roulette noise hides the answer. Urgent bodies should converge
   (predictability where it matters: the starving go to food); idle
   minds should diverge (unpredictability where it belongs: nothing is
   urgent). A hive mind scores 0 divergence. The tool reports both ends,
   plus the designed tie-break noise from the 85% near-tie band.
2. **Habitability** — "islands not too bad to live on" is a verdict with
   thresholds, not a mood. Bounded arcs across seeds report what kills,
   how often, and whether the founding band survives its first decade.
3. **Drama** — the engineered components themselves: the rhythms a
   viewer can set a watch by and the hazards nobody in the pen can see
   coming, each with the constant that sizes it (scripture.py reads the
   same list from the record; this prints it from the source).

None of these readings can move a world: the probe ticks copies, never
the live state, and writes nothing the engine reads.

    python3 tools/probe.py                  # all three, quick
    python3 tools/probe.py --days 6000 --seeds 69,7,123,5
    python3 tools/probe.py --json out.json  # machine-readable verdicts
"""

import argparse
import copy
import json
import random
import sys

ROOT = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
sys.path.insert(0, ROOT + "/sim")

import engine  # noqa: E402
import needs  # noqa: E402
import minds  # noqa: E402
import drives  # noqa: E402
import scripture  # noqa: E402


# ------------------------------------------------------------------ 1

def _focus_pool(u, want=6):
    """Adults whose choice is a real decision, not a bodily reflex."""
    day = u["day"]
    return [p for p in u["people"]
            if engine.age_of(p, day) >= minds.ADULT_AGE and not p.get("w")
            and p.get("c", True) and p.get("a") not in (minds.A_SLEEP, minds.A_BIRTH)][:want]


def _choose(u, p, rng_seed):
    """One decision, from one copy, under one fixed decision stream."""
    w = copy.deepcopy(u)
    q = next(c for c in w["people"] if c["id"] == p["id"])
    return needs.assign(w, q, w["day"], random.Random(rng_seed)), w


def independence(seeds=(69,), focals=6, trials=12, verbose=True):
    """Divergence and convergence of choice, by identity and by urgency.

    Returns a dict of indices in [0,1]:
      idle_divergence   high is good: fed, rested clones disagree
      urgent_convergence high is good: starving clones agree on food
      tie_noise         choice flips attributable only to the 85% band
    """
    acts = []
    idle_div, asis_div, urg_conv, tie, person_div = [], [], [], [], []
    for seed in seeds:
        world = engine.genesis(seed, 1)
        for _ in range(40):
            engine.tick_world(world, [])
        u = world["lagoon"]          # the richest decision layer: work, water, company
        # interview at a daylight part: at dawn the band is still in bed
        while u["part"] not in (1, 2):
            engine.tick_world(world, [])
        focals_n = len(_focus_pool(u, focals))
        # -- across people: the same comfortable body, given to every
        # focal person in turn, under several fixed decision streams.
        # Traits, memories, skills and kin differ; if choices still
        # collapse to one, the world has a hive mind.
        stream_div = []
        for stream in range(6):
            picks_people = []
            for p in _focus_pool(u, focals):
                w = copy.deepcopy(u)
                q = next(c for c in w["people"] if c["id"] == p["id"])
                q["hun"] = 2.0; q["ene"] = 0.95; q["sol"] = 0.85
                q["thirst"] = 0.0; q["intimacy"] = 0.3
                picks_people.append(needs.assign(w, q, w["day"], random.Random(500 + stream)))
            if picks_people:
                share = max(picks_people.count(a) for a in set(picks_people)) / len(picks_people)
                stream_div.append(1.0 - share)
        if stream_div:
            person_div.append(sum(stream_div) / len(stream_div))
        for p in _focus_pool(u, focals):
            # -- across identities: one person, many synthetic identities,
            # across sampled comfortable states. The midpoints move scores
            # by at most ~0.06; this measures how often that reorders a
            # real choice.
            flips = 0
            n_states = 0
            for t in range(trials):
                w = copy.deepcopy(u)
                q0 = next(c for c in w["people"] if c["id"] == p["id"])
                q0["hun"] = 1.0 + (t * 7 % 50) / 10.0     # a spread of easy states
                q0["ene"] = 0.55 + (t * 11 % 40) / 100.0
                q0["sol"] = 0.45 + (t * 13 % 50) / 100.0
                q0["thirst"] = 0.0
                base_pick = needs.assign(w, copy.deepcopy(q0), w["day"], random.Random(1234))
                w2 = copy.deepcopy(w)
                q1 = next(c for c in w2["people"] if c["id"] == p["id"])
                q1["id"] = 90000 + t
                alt_pick = needs.assign(w2, q1, w2["day"], random.Random(1234))
                n_states += 1
                if alt_pick != base_pick:
                    flips += 1
            if n_states:
                idle_div.append(flips / n_states)
            # the body as the world left it (informational: hard times
            # are allowed to be predictable — that is what hunger is)
            base, _ = _choose(u, p, 1234)
            picks_a = [base]
            for t in range(trials - 1):
                w = copy.deepcopy(u)
                q = next(c for c in w["people"] if c["id"] == p["id"])
                q["id"] = 90000 + t
                picks_a.append(needs.assign(w, q, w["day"], random.Random(1234)))
            share = max(picks_a.count(a) for a in set(picks_a)) / len(picks_a)
            asis_div.append(1.0 - share)
            # urgency: the same clones, starving — they should agree
            w0 = copy.deepcopy(u)
            picks_u = []
            for t in range(trials):
                w = copy.deepcopy(w0)
                q = next(c for c in w["people"] if c["id"] == p["id"])
                q["hun"] = 30.0              # above HUNGRY: food is all there is
                q["id"] = 90000 + t
                picks_u.append(needs.assign(w, q, w["day"], random.Random(1234)))
            urg_conv.append(max(picks_u.count(a) for a in set(picks_u)) / len(picks_u))
            # the designed tie-break: same identity, fresh roulette streams
            picks_t = []
            for t in range(trials):
                picks_t.append(_choose(u, p, 1234 + t)[0])
            tie.append(1.0 - max(picks_t.count(a) for a in set(picks_t)) / len(picks_t))
        acts.append(focals_n)
    out = {
        "focals": int(sum(acts)),
        "person_divergence": round(sum(person_div) / max(1, len(person_div)), 3),
        "identity_flip_rate": round(sum(idle_div) / max(1, len(idle_div)), 3),
        "asis_divergence": round(sum(asis_div) / max(1, len(asis_div)), 3),
        "urgent_convergence": round(sum(urg_conv) / max(1, len(urg_conv)), 3),
        "tie_noise": round(sum(tie) / max(1, len(tie)), 3),
    }
    if verbose:
        print("\n== independence ==")
        print(f"  focal people probed:        {out['focals']}")
        print(f"  person divergence:          {out['person_divergence']}"
              f"   (same comfortable body, same dice, different people: 0 = hive mind)")
        print(f"  identity flip rate:         {out['identity_flip_rate']}"
              f"   (only the personal sensitivity differs, across sampled states)")
        print(f"  as-found divergence:        {out['asis_divergence']}"
              f"   (the body as the world left it)")
        print(f"  urgent-body convergence:    {out['urgent_convergence']}"
              f"   (the starving should agree on food)")
        print(f"  designed tie-break noise:   {out['tie_noise']}"
              f"   (the 85% near-tie roulette, by design)")
        for k, ok in (("identity_fingerprint", out["identity_flip_rate"] > 0.15),
                      ("as-found_or_same_state_divergence",
                       max(out["person_divergence"], out["asis_divergence"]) > 0.02),
                      ("urgent_convergence", out["urgent_convergence"] >= 0.6)):
            print(f"  [{'PASS' if ok else 'FAIL'}] {k}")
    return out


# ------------------------------------------------------------------ 2

def habitability(seeds=(69, 7), days=3000, verbose=True):
    """Bounded arcs: what kills, and does the founding band last the decade.

    Verdict thresholds are explicit and conservative; they are the probe's
    own, not findings about real islands."""
    runs = []
    for seed in seeds:
        world = engine.genesis(seed, 1)
        ext = {"eden": None, "lagoon": None}
        first_year_pop = {}
        for d in range(days):
            engine.tick_world(world, [])
            for k in ("eden", "lagoon"):
                u = world[k]
                if ext[k] is None and u.get("extinct_day") is not None:
                    ext[k] = u["extinct_day"]
                if d == 360:
                    first_year_pop[k] = len(u["people"])
        row = {"seed": seed}
        for k in ("eden", "lagoon"):
            u = world[k]
            cod = u.get("cod", {})
            total = sum(cod.values()) or 1
            body = (cod.get("starvation", 0) + cod.get("dehydration", 0)) / total
            viol = cod.get("violence", 0) / total
            row[k] = {"deaths": total, "body": round(body, 3), "violence": round(viol, 3),
                      "extinct_day": ext[k], "iteration": u["iteration"],
                      "peak": u["peak"], "first_year_pop": first_year_pop.get(k)}
        runs.append(row)
    # verdicts
    lag = [r["lagoon"] for r in runs]
    ede = [r["eden"] for r in runs]
    v = {
        "lagoon_survives_decade": sum(1 for r in lag if r["iteration"] == 1) >= max(1, len(lag) // 2),
        "lagoon_not_a_deathtrap": all(r["body"] < 0.40 for r in lag),
        "lagoon_band_holds": all((r["first_year_pop"] or 0) >= 8 for r in lag),
        "eden_hoppers_feed": all(r["body"] < 0.15 for r in ede),
        "eden_grows": all(r["peak"] > 16 for r in ede),
    }
    if verbose:
        print("\n== habitability ==")
        for r in runs:
            print(f"  seed {r['seed']}: "
                  f"EDEN peak {r['eden']['peak']}, deaths {r['eden']['deaths']} "
                  f"(body {r['eden']['body']:.0%}, violence {r['eden']['violence']:.0%}), "
                  f"iter {r['eden']['iteration']} | "
                  f"LAGOON peak {r['lagoon']['peak']}, deaths {r['lagoon']['deaths']} "
                  f"(body {r['lagoon']['body']:.0%}, violence {r['lagoon']['violence']:.0%}), "
                  f"iter {r['lagoon']['iteration']}")
        for k, ok in v.items():
            print(f"  [{'PASS' if ok else 'FAIL'}] {k}")
    return {"runs": runs, "verdicts": v}


# ------------------------------------------------------------------ 2.5

def inner_life(seeds=(69,), days=1200, verbose=True):
    """Do the people have lives, or only needs?

    Over a bounded arc: how many personal projects are seen through, how
    many bonds grow to friendship, how many turn to feud. A world with
    none of these is a world of reflexes — watchable for an hour, not a
    day."""
    out = {}
    for seed in seeds:
        world = engine.genesis(seed, 1)
        friends = feuds = named_feuds = named_peace = 0
        for d in range(days):
            evts = []
            engine.tick_world(world, evts)
            for e in evts:
                if e[2] == "feud":
                    named_feuds += 1
                elif e[2] == "peace":
                    named_peace += 1
            if d == days - 1:
                for k in ("eden", "lagoon"):
                    for p in world[k]["people"]:
                        aff = p.get("aff") or {}
                        friends += sum(1 for v in aff.values() if v >= needs.AFF_FRIEND)
                        feuds += sum(1 for v in aff.values() if v <= needs.AFF_FEUD)
        total_done = sum(p.get("goals_done", 0)
                         for k in ("eden", "lagoon") for p in world[k]["people"])
        out[seed] = {"projects_seen_through": total_done, "friendships": friends,
                     "feuds": feuds, "feuds_named": named_feuds,
                     "reconciliations": named_peace}
    agg = {"projects_seen_through": sum(r["projects_seen_through"] for r in out.values()),
           "friendships": sum(r["friendships"] for r in out.values()),
           "feuds": sum(r["feuds"] for r in out.values()),
           "reconciliations": sum(r["reconciliations"] for r in out.values())}
    verdicts = {"projects_happen": agg["projects_seen_through"] > 0,
                "friendships_form": agg["friendships"] > 0}
    if verbose:
        print("\n== inner life ==")
        for seed, r in out.items():
            print(f"  seed {seed}: projects seen through {r['projects_seen_through']}, "
                  f"friendships {r['friendships']}, feuds {r['feuds']} "
                  f"({r['feuds_named']} named, {r['reconciliations']} settled)")
        for k, ok in verdicts.items():
            print(f"  [{'PASS' if ok else 'FAIL'}] {k}")
    return {"per_seed": out, "verdicts": verdicts}


# ------------------------------------------------------------------ 3

def drama(verbose=True):
    """The engineered components: rhythms to trust, hazards to fear."""
    world = engine.genesis(69, 1)
    scr = scripture.both(world)
    rows = []
    for k in ("eden", "lagoon"):
        for r in scr[k]["rhythms"]:
            rows.append(("rhythm", k, r["what"], r["note"]))
        for h in scr[k]["hazards"]:
            rows.append(("hazard", k, h["what"], h["note"]))
    rows.append(("hazard", "both", "Personal sensitivity",
                 "each need's midpoint sits in [.40,.60], fixed by identity: stable per person, unseen across the cast"))
    rows.append(("hazard", "both", "Tastes",
                 f"each person leans a stable +/-{needs.TASTE_WEIGHT:.2f} toward a kind of day (work, company, stillness, roaming, care); hunger outranks any taste"))
    rows.append(("hazard", "both", "Personal projects",
                 "a free mind may commit to a run-of-days project; it bends choices and completes on the real outcome"))
    rows.append(("hazard", "both", "Bonds and feuds",
                 f"actual contact moves a bounded affinity; {needs.AFF_FRIEND} is friendship, {needs.AFF_FEUD} is feud — both named once, in the record"))
    rows.append(("hazard", "both", "The long fuse",
                 f"a grudge walks at its enemy (a scored choice up to {0.16:.2f} × depth), a feud-brawl gives {needs.AFF_SPEND} back when it closes, and a killing leaves the kin a cold bond — peace is named the way feud is"))
    rows.append(("hazard", "both", "The near-tie roulette",
                 "choices within 15% of the best are broken by the world's dice: real noise, bounded"))
    rows.append(("hazard", "both", "Inheritance and drift",
                 f"mid-parent traits plus mutation (sd {minds.MUTATION_SD}); every child is a new temperament"))
    rows.append(("hazard", "both", "Private cycles",
                 "ovulation on private 24-35 day calendars; conception needs an actual exposed day"))
    rows.append(("hazard", "both", "Omens",
                 "about once in 250 days the world is strange at no one; a people with lore keeps the story"))
    if verbose:
        print("\n== drama: the components ==")
        for kind, k, what, note in rows:
            print(f"  [{kind:6}] {('EDEN' if k=='eden' else 'LAGOON')}: {what} — {note}")
    return {"components": [{"kind": a, "world": b, "what": c, "note": d} for a, b, c, d in rows]}


def main():
    ap = argparse.ArgumentParser(description="Probe the people and the islands.")
    ap.add_argument("--seeds", default="69,7")
    ap.add_argument("--days", type=int, default=3000)
    ap.add_argument("--focals", type=int, default=6)
    ap.add_argument("--trials", type=int, default=12)
    ap.add_argument("--only", choices=("independence", "habitability", "drama"))
    ap.add_argument("--json", dest="out")
    args = ap.parse_args()
    seeds = tuple(int(s) for s in args.seeds.split(",") if s)
    out = {}
    if args.only in (None, "independence"):
        out["independence"] = independence(seeds=(seeds[0],), focals=args.focals,
                                           trials=args.trials)
    if args.only in (None, "drama"):
        out["drama"] = drama()
    if args.only in (None, "inner"):
        out["inner_life"] = inner_life(seeds=seeds, days=min(args.days, 1200))
    if args.only in (None, "habitability"):
        out["habitability"] = habitability(seeds=seeds, days=args.days)
    if args.out:
        with open(args.out, "w") as f:
            json.dump(out, f, indent=1)
        print(f"\nwrote {args.out}")
    verdicts = []
    if "independence" in out:
        i = out["independence"]
        verdicts += [max(i["person_divergence"], i["asis_divergence"]) > 0.02,
                     i["urgent_convergence"] >= 0.6]
    if "inner_life" in out:
        verdicts += list(out["inner_life"]["verdicts"].values())
    if "habitability" in out:
        verdicts += list(out["habitability"]["verdicts"].values())
    if verdicts:
        print("\nPROBE:", "ALL PASS" if all(verdicts) else "FAILURES PRESENT")
        sys.exit(0 if all(verdicts) else 1)


if __name__ == "__main__":
    main()
