"""UNIVERSE 69 — simulation engine.

Two universes, one tick function each. 1 tick = one quarter of a simulated day.
Pure stdlib. State is a plain dict so it round-trips through JSON.

EDEN   (Universe 6): Calhoun's Universe 25 with humans. Unlimited provisioned
                     food, perfect climate, bounded space. Social-density
                     pathology ends it.
LAGOON (Universe 9): Blue Lagoon / first-sapiens ecology. Finite food webs,
                     predators, seasons, disasters, and a technology ladder.
"""

import json
import math
import os
import random
import time

import minds
import needs
import animals
from minds import (DAYS_PER_YEAR, ADULT_AGE, ELDER_AGE, make_name,  # noqa: F401
                   A_IDLE, A_WALK, A_FORAGE, A_HUNT, A_FISH, A_FARM, A_BUILD,
                   A_TALK, A_MATE, A_BIRTH, A_TEND, A_REST, A_EAT, A_WITHDRAW,
                   A_FIGHT, A_PLAY, A_RITE, A_SLEEP, A_WORK, A_SCOUT, A_WATCH, A_GROOM, A_DRINK,
                   WK_HUDDLE, WK_BEAUTIFUL, WK_UPSTAIRS)

GESTATION = 270

# The version of the model. Determinism holds per (seed, day, part) only *within* one
# version, so every published figure and every postmortem must say which
# version produced it.
ENGINE_VERSION = "2026.10.30.2"

# A day is four parts. The calendar still counts days, but a world now has a
# dark half and a light one, and the things people do at night are not the
# things they do at noon. The tick is a part, not a day.
PARTS_PER_DAY = 4

# How long a part of a day takes in real seconds. A day is four parts, so a
# sim-day is four times this. The value is here so the server and the engine
# agree; the server may override the pace with UNIVERSE69_SEC_PER_PART.
SEC_PER_PART = 86400.0 / (100 * DAYS_PER_YEAR * PARTS_PER_DAY)
SEC_PER_DAY = SEC_PER_PART * PARTS_PER_DAY

PART_NAMES = ("dawn", "day", "dusk", "night")
PART_NIGHT = 3

EDEN_SIZE = 48
EDEN_CAP = 900          # nominal capacity of the pen
EDEN_STAGNATION = 0.35  # crowding level where the behavioral sink begins
EDEN_BOX_CAP = 7        # how many may share one nest box

LAGOON_SIZE = 160   # an island off the coast of a greater land
RESEED_YEARS = 30       # quiet years before the Observers reseed (Ice Age cycle)
FOUNDER_PAIRS = 8       # eight pairs per world, matching every reseed
RESEED_PAIRS = 8        # after an extinction the Observers send eight pairs

TECH_LADDER = [
    # name, prerequisite, base chance per year, min population
    ("fire",          None,            0.50,  2),
    ("stone_tools",   None,            0.40,  2),
    ("fishing",       "stone_tools",   0.35,  6),
    ("predator_hunt", "fishing",       0.08,  25),  # the big cat becomes meat
    ("shelter",       "fire",          0.35,  6),
    ("preservation",  "fire",          0.20, 12),
    ("lore",          "shelter",       0.15, 40),   # shared fiction -> >150 coop
    ("agriculture",   "preservation",  0.10, 90),
    ("domestication", "agriculture",   0.12, 120),  # unlocks epidemics (germs)
    ("granary",       "agriculture",   0.20, 120),
    ("seacraft",      "fishing",       0.08, 140),
    ("healing",       "lore",          0.10, 150),
    ("metallurgy",    "granary",       0.06, 250),
    ("writing",       "lore",          0.05, 400),
]
ARTS = ["cave paintings", "drum songs", "the dance of the tides",
        "carved totems", "the story of the stars", "spirit masks",
        "tattoo rites", "the great feast", "shell jewelry", "the long game"]

# ---------------------------------------------------------------------------
# What Calhoun actually recorded in Universe 25.
#
# These are his numbers, not ours. They are here so the viewer can put our
# two universes against the experiment they are a reconstruction of, instead
# of against a memory of it.
#
# Source: Calhoun, J.B. (1973) "Death Squared: The Explosive Growth and
# Demise of a Mouse Population", Proc. Roy. Soc. Med. 66(1 Pt 2):80-88.
# See RESEARCH.md reference [1]. Days are counted from 9 July 1968.
# ---------------------------------------------------------------------------

# (day, population, note) — only populations Calhoun actually recorded.
CALHOUN_CENSUS = [
    (0,    8,    "four breeding pairs introduced"),
    (315,  620,  "Phase B ends; growth slows to a 145-day doubling"),
    (560,  2200, "peak; growth ceases, Phase D begins"),
    (1447, 122,  "22 male, 100 female remain"),
    (1588, 27,   "the paper is completed"),
    (1780, 0,    "the last male dies"),
]

# Events he dated but did not attach a population to.
CALHOUN_EVENTS = [
    (104,  "Phase A ends; the first litters"),
    (600,  "the last litters survive to weaning"),
    (920,  "the last conception"),
]

# (start_day, end_day, phase)
CALHOUN_PHASES = [
    (0,    104,  "A", "strive"),
    (104,  315,  "B", "exploit"),
    (315,  560,  "C", "stagnate"),
    (560,  1780, "D", "death"),
]

# The rest of what his pen was collecting. Each line is a data series he kept
# and the value he reported; `we` says whether this model records the same
# thing. Anything marked "no" is a gap, and the gaps are the honest part.
CALHOUN_SERIES = [
    {"what": "Population census", "his": "8 at day 0; 620 at day 315; 2,200 at day 560; "
     "122 on 22 Jun 1972; 27 on 13 Nov 1972", "we": "yes", "note": "our census is yearly, "
     "not weekly"},
    {"what": "Phase boundaries", "his": "A 104 d · B 315 d · C 560 d · D to the end",
     "we": "yes", "note": "detected from crowding, not from growth inflections"},
    {"what": "Growth rate", "his": "doubling every 55 days in B, every 145 in C",
     "we": "yes", "note": "derivable from our census"},
    {"what": "Last litter / last conception", "his": "weaning to day 600; conception to day 920",
     "we": "yes", "note": ""},
    {"what": "Nest-site occupancy", "his": "20% of the 256 sites unoccupied at the peak of 2,200",
     "we": "yes", "note": "ours shows as held / vacant boxes"},
    {"what": "Births per set of nest boxes", "his": "64 sets of four boxes tabulated",
     "we": "partial", "note": "we count occupants, not births per box"},
    {"what": "Brood-group asymmetry", "his": "13 young in 252 days NE vs 111 in the SW",
     "we": "no", "note": "no spatial reproduction bias in the model"},
    {"what": "Age structure of survivors", "his": "mean age 776 days by 1 Mar 1972",
     "we": "partial", "note": "we hold an age per person, not a mean"},
    {"what": "Sex ratio", "his": "22 male to 100 female at the end",
     "we": "yes", "note": ""},
    {"what": "Behavioural taxonomy", "his": "beautiful ones, withdrawn, aggressive, neglectful",
     "we": "yes", "note": "withdrawn, violence, infant abandonment"},
    {"what": "Distribution at the hoppers", "his": "the crowding that is the behavioural sink",
     "we": "yes", "note": "reported as a percentage of feed at one hopper"},
    {"what": "Husbandry", "his": "pen cleaned every four to eight weeks",
     "we": "no", "note": "no cleaning, no disease pressure"},
]


def culture_verb(art):
    """Plural arts 'appear'; a singular art, and anything called 'the …', 'appears'."""
    if art.endswith("s") and not art.startswith("the"):
        return "appear"
    return "appears"


def famine_line(names):
    """One line for the day, however many the lean season takes."""
    if len(names) == 1:
        return f"{names[0]} starves in the lean season."
    head = ", ".join(names[:3])
    more = f" and {len(names) - 3} others" if len(names) > 3 else ""
    return f"{len(names)} starve in the lean season: {head}{more}."

TECH_LABEL = {
    "fire": "fire is tamed", "stone_tools": "stone tools are knapped",
    "fishing": "fishing is learned", "shelter": "shelters are raised",
    "predator_hunt": "the hunters learn to kill the big cat",
    "preservation": "food can be kept", "lore": "shared stories bind the bands",
    "agriculture": "seeds are sown on purpose", "domestication": "animals are tamed",
    "granary": "granaries hold the surplus",
    "seacraft": "boats brave the open water", "healing": "healing lore spreads",
    "metallurgy": "metal is smelted", "writing": "marks begin to remember",
}


def person(uid, name, sex, born, gen, x, y, competent=True):
    return minds.new_mind({"id": uid, "n": name, "s": sex, "b": born, "g": gen,
                           "p": None, "x": x, "y": y, "c": competent, "w": False,
                           "due": 0, "hun": 0.0, "thirst": 0.0, "carry_water": 0.0,
                           # the personal meters: energy, company, and what
                           # this person is carrying home
                           "ene": 1.0, "sol": 0.7, "carry": 0.0, "carry_kind": None,
                           "a": 0, "tx": x, "ty": y, "ad": 0,   # activity, target, days left
                           "hx": x, "hy": y})                   # home: the place they return to


def age_of(p, day):
    return day - p["b"]


# ---------------------------------------------------------------- world gen

def make_lagoon_terrain(seed, version=1):
    """An island off a continental coast. 0 grass, 1 woods, 2 water, 3 beach,
    4 farm. The mainland runs down the west edge; a strait separates them
    until someone builds boats."""
    rng = random.Random(seed)
    s = LAGOON_SIZE
    t = [[2] * s for _ in range(s)]                       # ocean everywhere
    cx, cy, R = 112, 102, 40                              # the island
    coast = [rng.uniform(0.80, 1.0) for _ in range(72)]
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - cx, y - cy)
            a = int((math.atan2(y - cy, x - cx) % (2 * math.pi))
                    / (2 * math.pi) * 72) % 72
            r = R * coast[a]
            if d < r - 2.5:
                t[y][x] = 0
            elif d < r:
                t[y][x] = 3                               # beach ring
    lx, ly, lr = 124, 112, 10                             # the inner lagoon
    for y in range(s):
        for x in range(s):
            if t[y][x] != 0:
                continue
            d = math.hypot(x - lx, y - ly)
            if d < lr:
                t[y][x] = 2
            elif d < lr + 2:
                t[y][x] = 3
    # the mainland: a smoothed coast down the whole west edge
    edge = [rng.uniform(24, 34) for _ in range(s)]
    sm = [sum(edge[max(0, i - 2):i + 3]) / len(edge[max(0, i - 2):i + 3])
          for i in range(s)]
    for y in range(s):
        for x in range(s):
            if x < sm[y] - 3:
                t[y][x] = 0
            elif x < sm[y] and t[y][x] == 2:
                t[y][x] = 3
    for _ in range(26):                                   # woods on both lands
        x, y = rng.randrange(2, s - 2), rng.randrange(2, s - 2)
        for _ in range(300):
            if t[y][x] == 0:
                t[y][x] = 1
            x = min(s - 1, max(0, x + rng.choice([-1, 0, 1])))
            y = min(s - 1, max(0, y + rng.choice([-1, 0, 1])))
    if version >= 2:
        # A tropical coastal-forest analogue, not a surveyed map. Retain the
        # old coastline and seed geometry; new worlds have a forest mosaic
        # across both land masses rather than a few accidental random walks.
        forest = random.Random(f"{seed}:tropical-forest")
        for y in range(2, s - 2):
            for x in range(2, s - 2):
                if t[y][x] == 0 and forest.random() < 0.48:
                    t[y][x] = 1
    return t


LESSON_OF = {"starvation": "preserve", "predator": "vigilance",
             "epidemic": "cleanliness", "feud": "unity"}
LESSON_TECH = {"preserve": ("preservation", "fishing"),
               "vigilance": ("stone_tools",), "unity": ("lore",)}


def genesis_universe(kind, seed, iteration=1, postmortems=None, lessons=None,
                     fseed=None):
    rng = random.Random(seed)
    fseed = seed if fseed is None else fseed
    u = {"kind": kind, "seed": seed, "iteration": iteration, "day": 0,
         "people": [], "next_id": 1, "gen_max": 1, "phase": "strive",
         "peak": 0, "births_y": 0, "deaths_y": 0, "bad_years": 0,
         "extinct_day": None, "census": [], "year_flags": {},
         "cod": {}, "cod_y": {}, "postmortems": postmortems or [],
         "lessons": lessons or [], "phases": [[0, "strive"]], "engine": ENGINE_VERSION,
         "part": 0, "parts": 0, "engine_history": [], "founded_day": 0,
         "fseed": fseed, "innocent": True, "modesty": 0.0, "mind": []}
    if kind == "EDEN":
        u["ennui"] = 0.0      # hedonic adaptation: easy pleasure dulls appetite
        u["std_years"] = 0    # years an STD outbreak has left to run
        u["wary_years"] = 0   # post-outbreak generation keeps its distance
        cx = cy = EDEN_SIZE // 2
    else:
        u["terrain_seed"] = seed
        u["terrain_version"] = 2
        # Legacy observer fields. Each tick mirrors the actual patch and
        # animal stocks; these initial values do not supply meals.
        u["stocks"] = {"plants": 60000.0, "game": 2500.0,
                       "fish": 50000.0, "pred": 48.0}
        u["tech"] = []
        u["store"] = 0.0           # the sum of the camps' stores
        u["meat"], u["kills"] = 0.0, 0
        u["farms"] = []            # [x, y] tilled tiles
        u["settlements"] = [{"x": 137, "y": 109, "r": 5,
                             "n": make_name(rng, minds.NAMES.get("LAGOON")),
                             "store": 0.0}]
        u["culture"] = []          # arts appear when bellies stay full
        u["continent"] = False     # the greater land, waiting across the strait
        u["drought"] = 0           # years remaining
        u["harsh_winter"] = False
        cx, cy = 137, 109
    # Both universes receive the same people. Eight pairs the first time —
    # young, and not yet knowing what their bodies are for — and eight pairs
    # on every reseed after an extinction.
    pairs = FOUNDER_PAIRS if iteration == 1 else RESEED_PAIRS
    pool = minds.NAMES.get(kind)
    u["names"] = kind
    u["named"] = False        # a name is a thing a world invents, and it has
                              # not invented one yet
    for i, f in enumerate(minds.founders(fseed, iteration, pairs, pool)):
        x = cx + (i % 4) - 2 + (1 if i % 4 >= 2 else 0)
        y = cy + (i // 4) - pairs // 4
        p = person(u["next_id"], f["n"], f["s"], -18 * DAYS_PER_YEAR, 1, x, y)
        p["ef"], p["ag"], p["vg"] = f["ef"], f["ag"], f["vg"]
        if kind == "LAGOON":
            p["st"] = 0
        u["people"].append(p)
        u["next_id"] += 1
    for i in range(0, len(u["people"]), 2):
        m, w = u["people"][i], u["people"][i + 1]
        m["p"], w["p"] = w["id"], m["id"]
    return u


def genesis(seed=69):
    now = time.time()
    return {"epoch": now, "sec_per_day": SEC_PER_DAY, "seed": seed,
            "clock": {"epoch": now, "parts": 0, "seconds": SEC_PER_PART},
            "eden": genesis_universe("EDEN", seed * 7 + 6, fseed=seed),
            "lagoon": genesis_universe("LAGOON", seed * 7 + 9, fseed=seed)}


# ---------------------------------------------------------------- shared

VIOLENT_CAUSES = ("violence", "feud")


def cod(u, cause, n=1):
    u["cod"][cause] = u["cod"].get(cause, 0) + n
    u["cod_y"][cause] = u["cod_y"].get(cause, 0) + n
    if cause in VIOLENT_CAUSES:
        u["viol_y"] = u.get("viol_y", 0) + n


def write_postmortem(u, events):
    """On extinction: record what happened, how, and the dominant cause.
    The next iteration of LAGOON inherits a lesson; EDEN, by design, cannot
    learn its way out — the pen itself is the cause (Calhoun's conclusion)."""
    total = sum(u["cod"].values()) or 1
    dominant = max(u["cod"], key=u["cod"].get) if u["cod"] else "unknown"
    pm = {"iteration": u["iteration"], "day": u["day"], "peak": u["peak"],
          "gen_max": u["gen_max"], "cod": dict(u["cod"]),
          "dominant_cause": dominant,
          "engine": ENGINE_VERSION, "engine_history": list(u.get("engine_history", [])),
          "tech": list(u.get("tech", [])),
          "census_tail": u["census"][-40:],
          "lessons_held": list(u["lessons"])}
    if u["kind"] == "LAGOON":
        lesson = LESSON_OF.get(dominant)
        pm["lesson"] = lesson
        pm["preventable"] = bool(lesson)
        if lesson and lesson not in u["lessons"]:
            events.append((u["day"], u["kind"], "lesson",
                           f"Postmortem, iteration {u['iteration']}: dominant cause of death was "
                           f"{dominant} ({u['cod'].get(dominant, 0)}/{total}). Lesson recorded: "
                           f"'{lesson}'. The next castaways will not make this mistake."))
    else:
        pm["lesson"] = None
        pm["preventable"] = False
        events.append((u["day"], u["kind"], "lesson",
                       f"Postmortem, iteration {u['iteration']}: dominant cause was {dominant}. "
                       f"Nothing within the walls could have prevented this — the pen itself "
                       f"is the cause. The experiment can only be escaped, not won."))
    u["postmortems"] = (u["postmortems"] + [pm])[-20:]


def record_extinction(u, events):
    """Note the death of a universe and write its postmortem.

    Two paths reach this and both must count. The usual one: the tick in which
    the last person dies. The other: a tick that begins with an empty
    population and no recorded death — a state saved mid-way through the end,
    or a hand-edited world. Without the second path an extinction can go
    unrecorded, and an unrecorded extinction loses the postmortem and the
    reseed that the whole experiment depends on.
    """
    if u["extinct_day"] is not None:
        return
    day = u["day"]
    u["extinct_day"] = day
    if u["kind"] == "EDEN":
        events.append((day, "EDEN", "extinction",
                       f"UNIVERSE 6 HAS DIED. The pen is empty. Peak population was {u['peak']}, "
                       f"generation {u['gen_max']}. The food hoppers are still full."))
    else:
        events.append((day, "LAGOON", "extinction",
                       f"UNIVERSE 9 HAS DIED. The lagoon is quiet again. Peak population {u['peak']}, "
                       f"generation {u['gen_max']}."))
    write_postmortem(u, events)


def base_mortality(p, day, rng, events, u, label_extra=""):
    """Senescence. Returns True if the person dies of old age."""
    age_y = age_of(p, day) / DAYS_PER_YEAR
    pr = 2e-6 + max(0.0, age_y - 55) * 1.2e-5
    if rng.random() < pr:
        return True
    return False


def days(n):
    """An activity's remaining time, in days, expressed in ticks.

    The tick is a quarter of a day, so a stint written down as seven days
    has to last twenty-eight ticks. Every duration in the model is in days;
    this helper is where that is converted once, so that no rate is quietly
    four times too fast because the day is now four parts.
    """
    if not n:
        return 0
    return max(1, int(round(n * PARTS_PER_DAY)))


def try_conceive(u, rng, females, p_daily, require_pair=True, byid=None, males=None):
    """Reproduction is free and pedestrian — until the world makes it not so.
    EDEN mates without pair-bonds (require_pair=False); LAGOON pairs up.
    The father's heritable values are carried with the pregnancy."""
    day = u["day"]
    for p in females:
        if p["s"] != "f" or p["due"] or p["w"]:
            continue
        if require_pair and p["p"] is None:
            continue
        a = age_of(p, day)
        if not (ADULT_AGE <= a <= 45 * DAYS_PER_YEAR):
            continue
        # p_daily is already a per-part rate: the caller divides it once,
        # for the number of parts in a day, and this is tried once a part
        if rng.random() < p_daily * minds.fertility(p, a, day):
            lost = rng.random() < minds.MISCARRIAGE
            p["due"] = day + (rng.randint(50, 90) if lost else GESTATION)
            p["mc"] = lost
            fa = (byid or {}).get(p["p"]) if require_pair else (
                rng.choice(males) if males else None)
            p["fe"] = [fa.get("ef", 0.5), fa.get("ag", 0.5), fa.get("vg", 0.5)] if fa else None


def clear_widows(people, dead):
    dead_ids = {p["id"] for p in dead}
    for p in people:
        if p["p"] in dead_ids:
            p["p"] = None


def remove_dead(u, dead):
    """Remove casualties and release their bonds and claims on social space."""
    if not dead:
        return
    ids = {p["id"] for p in dead}
    people = u["people"]
    removed = [p for p in people if p["id"] in ids]
    if u["kind"] == "EDEN":
        occ = u.setdefault("box_occ", {})
        roles = u.get("roles", [])
        for p in removed:
            role = p.get("role")
            if role is not None and role < len(roles) and roles[role]["who"] == p["id"]:
                roles[role]["who"] = 0
            box = p.get("box")
            if box is not None and box >= 0:
                occ[str(box)] = max(0, occ.get(str(box), 0) - 1)
    people[:] = [p for p in people if p["id"] not in ids]
    clear_widows(people, removed)
    if "_ctx" in u:
        u["_ctx"] = day_context(people, u["day"])


def pair_singles(u, rng, adults):
    singles_m = [p for p in adults if p["s"] == "m" and p["p"] is None and not p["w"]]
    singles_f = [p for p in adults if p["s"] == "f" and p["p"] is None and not p["w"]]
    rng.shuffle(singles_m)
    rng.shuffle(singles_f)
    for m, f in zip(singles_m, singles_f):
        m["p"], f["p"] = f["id"], m["id"]


# A census row, once a year. The first four are the old contract; the rest
# are the instrument's gauges (the researcher's console, web/index.html):
CENSUS_FIELDS = ("year", "pop", "births", "deaths", "adults", "withdrawn",
                 "breeders", "infant_survival", "claimants", "sink",
                 "food_days", "violent")


def gauges(u):
    """The measures Calhoun read his pen by, for either world, now.

    adults, withdrawn, breeders (competent, not withdrawn, 16-45);
    infant_survival (legacy field): capped rolling yearlings / last annual
    births, a proxy with unmatched cohorts, NOT measured infant survival
    (None until the last census has births); claimants: adults per place (EDEN:
    competent adults per post; LAGOON: adults per paired adult); sink:
    percent of eaters at the busiest food point; food_days: days of food
    in store per head (None in EDEN, where it is unlimited by design).
    """
    day = u["day"]
    people = u["people"]
    adults = [p for p in people if age_of(p, day) >= ADULT_AGE]
    withdrawn = sum(1 for p in adults if p.get("w"))
    breeders = sum(1 for p in adults if p.get("c", True) and not p.get("w")
                   and age_of(p, day) <= 45 * DAYS_PER_YEAR)
    last = u["census"][-1] if u["census"] else None
    infant = None
    if last and last[2] > 0:
        yearlings = sum(1 for p in people
                        if DAYS_PER_YEAR <= age_of(p, day) < 2 * DAYS_PER_YEAR)
        infant = round(min(1.0, yearlings / last[2]), 3)
    if u["kind"] == "EDEN":
        posts = len(u.get("roles") or []) or 1
        competent = sum(1 for p in adults if p.get("c", True) and not p.get("w"))
        claimants = round(competent / posts, 2)
        hop = u.get("hop_n") or [0]
        sink = round(100.0 * max(hop) / sum(hop)) if sum(hop) else 0
        food_days = None
    else:
        paired = sum(1 for p in adults if p.get("p") is not None)
        claimants = round(len(adults) / paired, 2) if paired else float(len(adults))
        at = {}
        for p in people:
            if p.get("a") in (A_FORAGE, A_HUNT, A_FISH, A_FARM):
                k = p.get("site") and tuple(p["site"])
                if k:
                    at[k] = at.get(k, 0) + 1
        sink = round(100.0 * max(at.values()) / sum(at.values())) if at else 0
        mouths = max(1, len(people))
        food_days = round(u.get("store", 0.0) / (mouths * needs.HUNGER_PER_DAY * 1.5), 1)
    return {"adults": len(adults), "withdrawn": withdrawn, "breeders": breeders,
            "infant_survival": infant, "claimants": claimants, "sink": sink,
            "food_days": food_days}


def record_census(u):
    year = u["day"] // DAYS_PER_YEAR
    g = gauges(u)
    u["census"].append([year, len(u["people"]), u["births_y"], u["deaths_y"]]
                       + [g[k] for k in CENSUS_FIELDS[4:11]] + [u.get("viol_y", 0)])
    u["viol_y"] = 0
    if len(u["census"]) > 400:
        u["census"] = u["census"][-400:]


# ---------------------------------------------------------------- EDEN

EDEN_HOPPERS = [(8, 8), (EDEN_SIZE - 10, 8),
                (8, EDEN_SIZE - 10), (EDEN_SIZE - 10, EDEN_SIZE - 10)]
EDEN_EXPAND_STEP = 8        # tiles added on every side when the resort grows
EDEN_MAX_EXPANSIONS = 2     # 48 → 64 → 80: then the walls are final


def eden_size(u):
    return u.get("size", EDEN_SIZE)


def hoppers(u):
    """The four buffet bars, one in each corner of the pen as built."""
    S = eden_size(u)
    return [(8, 8), (S - 10, 8), (8, S - 10), (S - 10, S - 10)]


def pen_clamp(u, x, y):
    S = eden_size(u)
    return (min(S - 3, max(2, x)), min(S - 3, max(2, y)))


def lodging_kind(i):
    """Even places are condos (households), odd ones capsule hotels (singles)."""
    return "condo" if i % 2 == 0 else "capsule"

# The nest boxes lining all four walls — the apartments of Universe 25, and
# the only socially meaningful real estate in the pen.
EDEN_BOXES = []
for _i in range(4, EDEN_SIZE - 6, 5):
    EDEN_BOXES.append((_i + 1, 4))                  # along the north wall
    EDEN_BOXES.append((_i + 1, EDEN_SIZE - 5))      # south
    EDEN_BOXES.append((4, _i + 1))                  # west
    EDEN_BOXES.append((EDEN_SIZE - 5, _i + 1))      # east
BOX_CAPACITY = EDEN_BOX_CAP


def make_boxes(count, size=EDEN_SIZE):
    """Nest boxes around the four walls of the pen, as evenly as the walls allow.

    Calhoun's Universe 25 had 256 boxes, each holding about 15 mice. The
    number and the arrangement are the experiment: change them and you are
    running a different universe, which is the whole point of being able to
    vary the pen.
    """
    per = max(1, count // 4)
    if per == 1:
        mid = size // 2
        return [(mid, 4), (mid, size - 5), (4, mid), (size - 5, mid)]
    step = (size - 13) / (per - 1)
    boxes = []
    for k in range(per):
        i = int(round(5 + step * k))
        boxes.append((i, 4))                      # north wall
        boxes.append((i, size - 5))              # south
        boxes.append((4, i))                      # west
        boxes.append((size - 5, i))              # east
    return boxes


def set_pen_design(u, cap=None, stagnation=None, boxes=None, box_cap=None):
    """Re-dress a universe's pen. Used by the study tools, never by the
    live run — the Observers provision the pen once and then do not touch it."""
    if cap is not None:
        u["cap"] = cap
    if stagnation is not None:
        u["stagnation"] = stagnation
    if boxes is not None:
        u["boxes"] = list(boxes) if not isinstance(boxes, int) else make_boxes(boxes)
        u["box_occ"] = {}
    if box_cap is not None:
        u["box_cap"] = box_cap
    return u


def eden_design(u):
    """The architecture of the pen, as numbers the experiment can vary.

    Calhoun's own conclusion — and the Ramsden & Adams critique recorded in
    RESEARCH.md — is that the outcome tracks the *distribution* of space,
    roles and resources, not crowding alone. So the architecture cannot live
    as a constant in the source: a study of Universe 25 has to be able to
    change the pen and watch what happens.

    A live world that predates these fields carries none of them; the
    defaults below are exactly the pen it was already running.
    """
    boxes = u.get("boxes")
    return {
        "cap": u.get("cap", EDEN_CAP),
        "stagnation": u.get("stagnation", EDEN_STAGNATION),
        "boxes": boxes if boxes else EDEN_BOXES,
        "box_cap": u.get("box_cap", EDEN_BOX_CAP),
    }


def eden_claim_home(u, p, rng):
    """A place to belong, if any is left. Calhoun's surplus animals had
    nowhere to emigrate to: when every box is held, they end up milling in
    the open centre of the floor, which is where the pathology pools."""
    occ = u.setdefault("box_occ", {})
    boxes = eden_design(u)["boxes"]
    if p["w"]:
        withdrawn_home(u, p, rng)
        return
    order = list(range(len(boxes)))
    rng.shuffle(order)
    # a household wants a condo, a single a capsule; either takes what is left
    want = "condo" if (p.get("p") or p["id"] in u.get("_ctx", {}).get("moms", {})) else "capsule"
    order.sort(key=lambda i: 0 if lodging_kind(i) == want else 1)
    cap = eden_design(u)["box_cap"]
    for i in order:
        if occ.get(str(i), 0) < cap:
            occ[str(i)] = occ.get(str(i), 0) + 1
            p["box"] = i
            p["hx"], p["hy"] = boxes[i]
            return
    # no place left: sleep on a mat in the open hall, jjimjilbang style — a
    # bed for the night, but no territory and no door of one's own
    p["box"] = -1
    c = eden_size(u) // 2
    ang = rng.uniform(0, 2 * math.pi)
    r = rng.uniform(5.5, 9.5)
    p["hx"], p["hy"] = pen_clamp(u, int(round(c + r * math.cos(ang))),
                                 int(round(c + r * math.sin(ang))))


def nurse(u, p, day):
    """She nurses the child on demand; ovulation is suppressed for most of it.
    Settled farmers wean sooner — births about two years apart against a
    nomad's four (Diamond ch.4)."""
    n = minds.LACTATION_DAYS[u["kind"]]
    if u["kind"] == "LAGOON" and has(u, "agriculture"):
        n = 2 * DAYS_PER_YEAR
    p["nurse"], p["nurse_len"] = day + n, n


def withdraw(u, p, rng):
    """One of the withdrawn, for good (Calhoun: no recovery).

    Universe 25's withdrawn were three kinds, and they kept apart from the
    living pen and from each other. Men without territory pooled listless
    on the open floor, where sporadic attacks wounded them. Men who still
    held a place became the beautiful ones, who only ate, slept and groomed,
    alone. Lone women retreated to the upper nest boxes (RESEARCH.md [2][3]).
    """
    p["w"] = True
    if p.get("role") is not None and u.get("roles"):
        u["roles"][p["role"]]["who"] = 0
        p["role"] = None
    homeless = p.get("box") is None or p["box"] < 0
    # born into the sink: a beautiful one; beaten and placeless: the floor
    p["wk"] = (WK_UPSTAIRS if p["s"] == "f" else
               WK_BEAUTIFUL if not p["c"] else
               WK_HUDDLE if homeless else WK_BEAUTIFUL)
    clear_widows(u["people"], [p])
    p["p"] = None
    withdrawn_home(u, p, rng)
    p["a"], p["ad"] = A_WITHDRAW, days(0)
    p["tx"], p["ty"] = p["hx"], p["hy"]


def withdrawn_home(u, p, rng):
    boxes = eden_design(u)["boxes"]
    c = eden_size(u) // 2
    wk = p.get("wk") or WK_BEAUTIFUL
    if wk == WK_HUDDLE:
        # one pool in the middle of the floor, bodies against bodies — not
        # rows: each takes a spot on a disc, packed toward the centre
        h = ((p["id"] * 2654435761) % 1000) / 1000.0
        r = 3.6 * math.sqrt(h)
        ang = p["id"] * 2.39996
        p["hx"] = int(round(c + r * math.cos(ang)))
        p["hy"] = int(round(c + r * math.sin(ang) * 0.7))
    elif wk == WK_UPSTAIRS:
        # the highest row of boxes — the far wall, as far from the floor as
        # the pen allows; one woman to a place
        top = [b for b in boxes if b[1] == min(bb[1] for bb in boxes)] or boxes
        bx, by = top[p["id"] % len(top)]
        p["hx"], p["hy"] = bx + (p["id"] // len(top)) % 3 - 1, by
    else:
        # a quiet corner of their own, off the paths to the hoppers
        bx, by = boxes[p["id"] % len(boxes)]
        p["hx"], p["hy"] = pen_clamp(u, bx + (2 if bx < c else -2), by + (2 if by < c else -2))


def quiet_hopper(u, rng):
    """The hopper the crowd is not using. The withdrawn feed alone."""
    counts = u.get("hop_n") or [0, 0, 0, 0]
    i = counts.index(min(counts))
    hx, hy = hoppers(u)[i]
    return (hx + rng.randint(-1, 2), hy + rng.randint(-1, 2))


def eden_assign(u, p, day, rng, crowd):
    """A day in the resort. Nothing must be worked for, so a life is a
    routine of sleep, food, company, sex and — for those who hold one — a
    role. Every activity has a place: a bed, a bar, a circle on the
    boardwalk, a lounger by the pool, a post. Only the placeless and the
    withdrawn are without one, and that is the pathology, not the default."""
    a = age_of(p, day)
    if "hx" not in p or p.get("box") is None:
        eden_claim_home(u, p, rng)
    S = eden_size(u)
    c = S // 2

    def clamp(x, y):
        return pen_clamp(u, x, y)

    def bed():
        return clamp(p["hx"], p["hy"] + 1)

    if p["w"]:
        # Withdrawn: stay put for weeks, then a short trip to the hopper no
        # one else is using, and straight back. Never a circle, a partner or
        # a fight of their own making.
        # Calhoun's beautiful ones were sleek and well fed: they eat alone,
        # at whatever hour the bar is empty, whenever they are hungry
        if p.get("hun", 0.0) > needs.EAT_AT:
            p["a"], p["ad"] = A_EAT, days(1)
            p["tx"], p["ty"] = quiet_hopper(u, rng)
        else:
            p["a"] = A_SLEEP if rng.random() < 0.3 else A_WITHDRAW
            p["ad"] = days(rng.randint(2, 5))
            p["tx"], p["ty"] = p["hx"], p["hy"]
        return
    if p["due"] and p["due"] - day <= 0:
        p["a"], p["ad"] = A_BIRTH, days(2)
        p["tx"], p["ty"] = bed()
        return
    if a < ADULT_AGE:
        if a < 3 * DAYS_PER_YEAR:                    # infants: on the mother
            p["a"], p["ad"] = A_TEND, days(3)
            p["tx"], p["ty"] = bed()
        elif p.get("hun", 0.0) > needs.EAT_AT:      # a hungry child goes to the bar
            p["a"], p["ad"] = A_EAT, days(1)
            p["tx"], p["ty"] = eden_feed_spot(u, rng)
        elif a < 12 * DAYS_PER_YEAR:                 # children play in packs, and sleep
            if rng.random() < 0.25:
                p["a"], p["ad"] = A_SLEEP, days(rng.randint(2, 4))
                p["tx"], p["ty"] = bed()
            else:
                play_with(u, p, kids_near(u["_ctx"], p), rng, clamp)
        else:                                        # adolescents eat, loiter, sleep
            r = rng.random()
            p["ad"] = days(rng.randint(3, 8))
            if r < 0.35:
                p["a"] = A_EAT
                p["tx"], p["ty"] = eden_feed_spot(u, rng)
            elif r < 0.55:
                p["a"] = A_SLEEP
                p["tx"], p["ty"] = bed()
            else:
                p["a"] = A_TALK
                join_circle(u, p, *clamp(c + rng.randint(-6, 6), c + rng.randint(-6, 6)))
                p["tx"], p["ty"] = clamp(p["tx"], p["ty"])
        return

    ctx = u["_ctx"]
    role = p.get("role")
    if p["id"] in ctx["moms"] and rng.random() < 0.35:
        # a mother with an infant: the child is not a choice among others
        p["a"], p["ad"] = A_TEND, days(1)
        p["tx"], p["ty"] = bed()
        return
    # The same decision LAGOON's people make, under the resort's condition:
    # the body's meters against what the pen offers. Where each act then
    # happens — the bar, the bed, the boardwalk, the post — is the place's.
    act = needs.assign(u, p, day, rng, needs.CONDITIONS["EDEN"])
    if act == A_EAT:
        p["tx"], p["ty"] = eden_feed_spot(u, rng)
    elif act == A_GROOM:
        near = [q for q in ctx["am"] + ctx["af"] if q is not p and q.get("a") not in (A_MATE, A_GROOM, A_FIGHT)
                and abs(q["x"] - p["x"]) <= 5 and abs(q["y"] - p["y"]) <= 5]
        if near:
            q = rng.choice(near)
            groom_with(p, q, *clamp(q["x"], q["y"]))
        else:
            p["a"], (p["tx"], p["ty"]) = A_REST, bed()
    elif act == A_SLEEP:
        p["tx"], p["ty"] = bed()
    elif act == A_WORK and role is not None:
        post = u["roles"][role]
        p["ad"] = days(rng.randint(4, 8))
        p["tx"], p["ty"] = clamp(post["x"] + rng.randint(-1, 1), post["y"] + rng.randint(0, 1))
    elif act == A_MATE:
        pool = ctx["af"] if p["s"] == "m" else ctx["am"]
        near = [q for q in pool if q is not p and q.get("a") != A_MATE
                and q.get("c", True) and not q.get("w")
                and abs(q["x"] - p["x"]) <= 6 and abs(q["y"] - p["y"]) <= 6]
        if near:
            q = rng.choice(near)
            couple_up(p, q, *clamp(q["x"], q["y"]))
        else:
            p["a"], (p["tx"], p["ty"]) = A_SLEEP, bed()
    elif act == A_FIGHT:
        if not pick_fight(u, p, u["people"], rng):
            # nobody near: drift to where the crowd is and brood
            hx, hy = hoppers(u)[u.get("sink", 0)]
            p["a"] = A_REST
            p["tx"], p["ty"] = clamp(hx + rng.randint(-3, 4), hy + rng.randint(-3, 4))
    elif act == A_TALK:
        # company gathers on the boardwalks and by the pool
        spot = rng.choice(((c, c - 6), (c - 6, c), (c + 6, c), (c, c + 6), (c, 4)))
        join_circle(u, p, *clamp(spot[0] + rng.randint(-2, 2), spot[1] + rng.randint(-2, 2)))
        p["tx"], p["ty"] = clamp(p["tx"], p["ty"])
    elif act == A_REST:
        # a lounger on the sand along the south wall, facing the painted sea
        p["tx"], p["ty"] = clamp(rng.randint(5, S - 6), S - 6 + rng.randint(0, 2))
    elif act == A_WALK:
        p["ad"] = days(rng.randint(1, 2))
        p["tx"], p["ty"] = clamp(c + rng.randint(-9, 9), c + rng.randint(-9, 9))
    elif act == A_WITHDRAW:
        # worn out by the crowd and wanting nothing: one of the withdrawn
        withdraw(u, p, rng)
    else:
        p["tx"], p["ty"] = bed()


def near_hopper(u, p, reach=4):
    return any(abs(p["x"] - hx) <= reach and abs(p["y"] - hy) <= reach
               for hx, hy in hoppers(u))


def rearing(u, mom):
    """What a birth in the pen comes to: (p_abandon, p_incompetent).

    Calhoun's finding was that the rearing environment, not the density of
    the day, decided a pup's fate: mothers harried at the nest abandoned
    litters, and young reared amid constant intrusion never learned the
    social repertoire (Calhoun 1962, 1973). So these are read from the
    mother's own nest and state — the crowd around her bed, how much of a
    life she has, whether she was herself reared to one — not from a
    phase label.
    """
    near = needs.near_count(u, mom)
    stress = max(0.0, near - needs.CROWD_FACES) / (2 * needs.CROWD_FACES)
    stress *= 1.3 - mom.get("pu", 0.5)
    if mom.get("inj", 0.0) > 0.3:
        stress *= 1.4
    if mom.get("w"):
        return 0.9, 0.95
    p_abandon = min(0.8, 0.9 * stress)
    p_incompetent = min(0.95, 1.1 * stress + (0.4 if not mom.get("c", True) else 0.0))
    return p_abandon, p_incompetent


def eden_feed_spot(u, rng):
    """The behavioural sink. Calhoun's mice came to associate eating with
    company and crowded into one or two hoppers while the others stood
    unused — so the more company a hopper already has, the more it draws."""
    counts = u.get("hop_n") or [1, 1, 1, 1]
    weights = [(1.0 + c) ** 1.7 for c in counts]
    tot = sum(weights)
    r = rng.random() * tot
    pick = 0
    for i, wt in enumerate(weights):
        r -= wt
        if r <= 0:
            pick = i
            break
    hx, hy = hoppers(u)[pick]
    return (hx + rng.randint(-2, 3), hy + rng.randint(-2, 3))


def make_roles(u):
    """The resort's posts: bar staff at each buffet, lifeguards at the pool,
    a keeper for every few lodgings. A fixed number of socially meaningful
    roles — the variable Calhoun said was really scarce (RESEARCH.md §1) —
    filled once, then vacated only by death."""
    S = eden_size(u)
    posts = []
    for hx, hy in hoppers(u):
        posts += [{"k": "bar", "x": hx + 1, "y": hy + 2}] * 3
    posts += [{"k": "pool", "x": S // 2 - 2, "y": 4}, {"k": "pool", "x": S // 2 + 2, "y": 4}]
    boxes = eden_design(u)["boxes"]
    for i in range(0, len(boxes), 4):
        posts.append({"k": "keeper", "x": boxes[i][0], "y": boxes[i][1] + 1})
    old = {i: r.get("who", 0) for i, r in enumerate(u.get("roles", []))}
    u["roles"] = [dict(r, who=old.get(i, 0)) for i, r in enumerate(posts)]


def fill_roles(u, rng, events):
    """Vacant posts go to competent adults who have none. Once every post is
    held, a newly grown adult has nowhere to be needed."""
    if "roles" not in u:
        make_roles(u)
    alive = {q["id"]: q for q in u["people"]}
    for i, r in enumerate(u["roles"]):
        if r["who"] and r["who"] not in alive:
            r["who"] = 0
    held = {r["who"] for r in u["roles"] if r["who"]}
    for q in u["people"]:
        if q.get("role") is not None and q["id"] not in held:
            q["role"] = None
    vacant = [i for i, r in enumerate(u["roles"]) if not r["who"]]
    if not vacant:
        return
    day = u["day"]
    cands = [q for q in u["people"] if q.get("role") is None and q["c"] and not q["w"]
             and ADULT_AGE <= age_of(q, day) < ELDER_AGE]
    rng.shuffle(cands)
    for i, q in zip(vacant, cands):
        u["roles"][i]["who"] = q["id"]
        q["role"] = i


def expand_pen(u, rng, events):
    """The Observers provision: when the pen nears the crowding at which the
    sink began, the resort grows — new floor on every side, new lodgings
    along the new walls, new posts. The old walls' lodgings stand on as
    blocks in the middle. Calhoun's later universes showed added rooms
    could hold pathology off at high density (RESEARCH.md [4][5]); whether
    a bigger pen escapes or only postpones is what this tests. Finite: after
    EDEN_MAX_EXPANSIONS the walls are final."""
    if u.get("expansions", 0) >= EDEN_MAX_EXPANSIONS:
        return False
    k = EDEN_EXPAND_STEP
    old_boxes = list(eden_design(u)["boxes"])
    S = eden_size(u) + 2 * k
    u["size"] = S
    for q in u["people"]:
        for a, b in (("x", "y"), ("tx", "ty"), ("hx", "hy")):
            q[a] += k
            q[b] += k
    for c in u.get("circles", []):
        c["x"] += k
        c["y"] += k
    shifted = [(x + k, y + k) for x, y in old_boxes]
    new_walls = make_boxes(len(old_boxes) + 16, S)
    u["boxes"] = shifted + new_walls
    u["cap"] = int(round(eden_design(u)["cap"] * (S / (S - 2 * k)) ** 2))
    u["expansions"] = u.get("expansions", 0) + 1
    make_roles(u)
    for q in u["people"]:
        if q["w"]:
            withdrawn_home(u, q, rng)      # the floor's middle and the top row moved
    events.append((u["day"], "EDEN", "phase",
                   f"The resort grows: the dome opens onto new sand, {len(new_walls)} new "
                   f"lodgings rise along the new walls. The pen is {S} paces across."))
    return True


def tick_eden(u, rng, events):
    part = u.get("part", 0)
    day = u["day"]
    people = u["people"]
    pop = len(people)

    if not people:
        if u["extinct_day"] is None:
            record_extinction(u, events)
        elif day - u["extinct_day"] > RESEED_YEARS * DAYS_PER_YEAR:
            fresh = genesis_universe("EDEN", u["seed"] + u["iteration"],
                                     u["iteration"] + 1,
                                     postmortems=u["postmortems"],
                                     fseed=u.get("fseed"))
            fresh["day"] = day
            fresh["founded_day"] = day
            fresh["part"], fresh["parts"] = part, u.get("parts", day * PARTS_PER_DAY + part)
            fresh["engine_history"] = list(u.get("engine_history", []))
            for p in fresh["people"]:
                p["b"] = day - 18 * DAYS_PER_YEAR  # young again
            u.clear()
            u.update(fresh)
            events.append((day, "EDEN", "reseed",
                           f"The Observers reseed the pen. Iteration {u['iteration']} begins "
                           f"under the same perfect, fatal conditions."))
        advance_part(u)
        return

    crowd = pop / eden_design(u)["cap"]
    if crowd >= 0.8 * eden_design(u)["stagnation"] and u["phase"] in ("strive", "exploit"):
        if expand_pen(u, rng, events):
            crowd = pop / eden_design(u)["cap"]
    if part == 0 and day % 30 == 0:
        fill_roles(u, rng, events)
    dead, born = [], []

    # how many are at each hopper today — the sink feeds on its own crowd
    if part == 0 and day % 3 == 0:
        counts = [0, 0, 0, 0]
        for q in people:
            if q.get("a") == A_EAT:
                for i, (hx, hy) in enumerate(hoppers(u)):
                    if abs(q["x"] - hx) <= 3 and abs(q["y"] - hy) <= 3:
                        counts[i] += 1
                        break
        u["hop_n"] = counts
        u["sink"] = counts.index(max(counts))

    # phase transitions
    if u["phase"] == "strive" and any(age_of(p, day) < ADULT_AGE for p in people):
        u["phase"] = "exploit"
        u["phases"].append([day // DAYS_PER_YEAR, "exploit"])
        events.append((day, "EDEN", "phase", "First child born in the pen. The exploit phase begins."))
    if u["phase"] == "exploit" and crowd >= eden_design(u)["stagnation"]:
        u["phase"] = "stagnate"
        u["phases"].append([day // DAYS_PER_YEAR, "stagnate"])
        events.append((day, "EDEN", "phase",
                       f"Crowding passes {int(eden_design(u)['stagnation']*100)}%. "
                       f"Stagnation: the behavioral sink emerges."))

    # Night in the resort. The doors never close and the food never runs
    # out — that is the experiment — but the pen still has a dark half, and
    # in the dark the adults go to their own beds. The placeless sleep on
    # the mats in the open hall, where they have always slept.
    # (needs.night, below, puts each of them to bed: the same rule as the
    # lagoon's, so the two worlds keep one clock.)

    byid = {q["id"]: q for q in people}
    u["_ctx"] = day_context(people, day)
    u["_ctx"]["dead"] = dead
    moms = u["_ctx"]["moms"]
    for p in people:
        if part == 0 and base_mortality(p, day, rng, events, u):
            dead.append(p)
            cod(u, "age")
            continue
        a = age_of(p, day)
        if part == 0:
            minds.tend_body(p, a, True, 0.0)
            minds.tend_purpose(p, a, 0.0, p["p"] is not None, p["id"] in moms,
                               p.get("box") is not None and p["box"] >= 0)
        if p.get("wk") == WK_HUDDLE and rng.random() < 0.004 / PARTS_PER_DAY:
            minds.hurt(p, 0.3)         # attacked on the floor, and does not resist
        if p.get("a") == A_FIGHT and rng.random() < 0.25 / PARTS_PER_DAY:
            minds.hurt(p, rng.uniform(0.08, 0.3))
            if (p["s"] == "m" and p["inj"] > 0.5 and not p["w"]
                    and (p.get("box") is None or p["box"] < 0) and rng.random() < 0.3):
                withdraw(u, p, rng)     # the loser with no place stops getting up
        # A killing is a fight that went too far: violence deaths come from
        # the fights people actually had, and the fights come from crowding
        # and temper in needs.assign — not from a phase having been reached.
        if p.get("inj", 0.0) >= 1.0:
            dead.append(p)
            cod(u, "violence")
            if rng.random() < 0.15:
                events.append((day, "EDEN", "violence",
                               f"{p['n']} does not get up from a brawl near the hoppers."))
            continue
        # the body: hunger, energy and company, as in the lagoon
        needs.night(u, p, rng, part)
        needs.meters(u, p, day, rng, needs.CONDITIONS["EDEN"])
        needs.eat(u, p, a / DAYS_PER_YEAR)
        needs.drink(u, p)
        if p["hun"] > needs.HUNGER_MAX:
            dead.append(p)
            cod(u, "starvation")      # in a resort with full hoppers: the withdrawn
            continue
        # births — the rearing environment, not current density, decides the
        # child's fate: once the sink has broken social roles it stays broken
        # (Calhoun: stagnation-reared mice never recovered, even moved to
        # empty universes).
        if p["due"] and day >= p["due"]:
            p["due"] = 0
            if p.pop("mc", False):
                continue          # lost early; nobody but she ever knew
            p_abandon, p_incompetent = rearing(u, p)
            if rng.random() < p_abandon:
                u["births_y"] += 1  # born and lost in the same part
                u["deaths_y"] += 1
                cod(u, "infant")
                continue
            nurse(u, p, day)
            for _twin in range(2 if rng.random() < minds.TWINS else 1):
                competent = rng.random() >= p_incompetent
                sex = rng.choice("mf")
                c = person(u["next_id"], make_name(rng, minds.NAMES.get("EDEN"), sex=sex),
                           sex, day, p["g"] + 1, p["x"], p["y"], competent)
                minds.inherit(c, p, rng)
                c["hx"], c["hy"] = p.get("hx", p["x"]), p.get("hy", p["y"])
                c["box"] = None                 # claims its own place at adulthood
                c["mom"] = p["id"]
                u["next_id"] += 1
                born.append(c)
                if not u.get("named"):
                    # the first name anyone gives: you name what you make
                    u["named"] = True
                    events.append((day, "EDEN", "discovery",
                                   f"The first child is named {c['n']}. "
                                   f"After this, everyone has a name."))
            if c["g"] > u["gen_max"] and c["g"] % 5 == 0:
                events.append((day, "EDEN", "generation",
                               f"Generation {c['g']} is born in the pen."))
            u["gen_max"] = max(u["gen_max"], c["g"])
        # the beautiful ones: incompetent adults withdraw for good
        if not p["c"] and not p["w"] and age_of(p, day) >= ADULT_AGE:
            withdraw(u, p, rng)
        # the day in the pen: eat, court, brawl, or withdraw
        if age_of(p, day) < 3 * DAYS_PER_YEAR:
            follow_mother(p, byid, lambda x, y: pen_clamp(u, x, y))
        if p.get("ad", 0) <= 0 and p["x"] == p["tx"] and p["y"] == p["ty"]:
            eden_assign(u, p, day, rng, crowd)
        arrived = step_toward(p)
        if (p.get("a") == A_EAT and u["day"] != p.get("day_done")
                and near_hopper(u, p)):
            p["day_done"] = u["day"]
            needs.fulfil(u, p, day, rng, A_EAT)       # a meal at the hopper
        if arrived:
            p["ad"] = p.get("ad", 0) - 1
            if p["ad"] <= 0:
                eden_assign(u, p, day, rng, crowd)
        p["x"], p["y"] = pen_clamp(u, p["x"], p["y"])

    remove_dead(u, dead)
    u["deaths_y"] += len(dead)
    u["births_y"] += len(born)
    people.extend(born)
    u["peak"] = max(u["peak"], len(people))

    # mating in the pen is ambient and free — no bonds, no scarcity — as long
    # as any socially competent adult male remains
    fertility = 1.0 / 180 / PARTS_PER_DAY
    if crowd >= eden_design(u)["stagnation"]:
        # density suppresses conception (Christian 1950s; Calhoun 1962)
        fertility *= max(0.25, 1.0 - crowd)
    fertility *= 1.0 - 0.5 * u.get("ennui", 0.0)   # boredom with easy pleasure
    if u.get("std_years", 0) > 0:
        fertility *= 0.4
        # the outbreak also takes adults directly
        victims = [p for p in people
                   if age_of(p, day) >= ADULT_AGE and rng.random() < 2e-5 / PARTS_PER_DAY]
        remove_dead(u, victims)
        u["deaths_y"] += len(victims)
        cod(u, "plague", len(victims))
    if u.get("wary_years", 0) > 0:
        fertility *= 0.7                            # the wary generation
    u["_ctx"] = day_context(people, day)
    males = [p for p in people if p["s"] == "m" and p["c"] and not p["w"]
             and age_of(p, day) >= ADULT_AGE]
    male_ok = bool(males)
    if male_ok and not u.get("innocent"):
        try_conceive(u, rng, people, fertility, require_pair=False,
                     males=males)
    elif u.get("innocent") and day > 60 and rng.random() < 1 / (200 * PARTS_PER_DAY):
        # the same discovery as the lagoon's, sooner: there is nothing else to do
        u["innocent"] = False
        events.append((day, "EDEN", "discovery",
                       "With every hour free, the pairs discover how new life begins."))

    # yearly: ennui creep and disease rolls in a world of free mating
    if part == 0 and day % DAYS_PER_YEAR == 7:
        old = u["ennui"]
        u["ennui"] = min(0.7, u["ennui"] + 0.004)
        for threshold, msg in ((0.25, "Easy pleasure begins to dull — the pen "
                                      "grows bored of what costs nothing."),
                               (0.5, "Whole cohorts now barely seek each other "
                                     "out. Abundance has made desire optional.")):
            if old < threshold <= u["ennui"]:
                events.append((day, "EDEN", "ennui", msg))
        if u["std_years"] > 0:
            u["std_years"] -= 1
            if u["std_years"] == 0:
                u["wary_years"] = 20
                events.append((day, "EDEN", "disease",
                               "The outbreak burns out. The generation that watched "
                               "it keeps its distance — desire now carries a memory "
                               "of death."))
        elif u["wary_years"] > 0:
            u["wary_years"] -= 1
            if u["wary_years"] == 0:
                events.append((day, "EDEN", "disease",
                               "The wary generation has aged out; the pen forgets."))
        elif len(people) > 100 and rng.random() < 0.025 / PARTS_PER_DAY:
            u["std_years"] = rng.randint(3, 8)
            events.append((day, "EDEN", "disease",
                           "A sickness spread by mating moves through the pen — "
                           "the one cost free pleasure turned out to carry."))

    if part == 0 and day > u.get("founded_day", 0) and day % DAYS_PER_YEAR == 0:
        if (u["phase"] == "stagnate" and u["deaths_y"] > u["births_y"]
                and len(people) > 0):
            u["bad_years"] += 1
            if u["bad_years"] >= 3:
                u["phase"] = "death"
                u["phases"].append([day // DAYS_PER_YEAR, "death"])
                events.append((day, "EDEN", "phase",
                               "Deaths outnumber births for the third year. The death phase begins."))
        elif u["phase"] == "stagnate":
            u["bad_years"] = 0
        elif u["phase"] == "death" and u["births_y"] > u["deaths_y"]:
            # The label describes; it does not decide. If births come back,
            # the pen is said to have come back — whether it does is the test.
            u["bad_years"] = 0
            u["phase"] = "stagnate"
            u["phases"].append([day // DAYS_PER_YEAR, "stagnate"])
            events.append((day, "EDEN", "phase",
                           "Births outnumber deaths again. The pen climbs back out of the death phase."))
        # being seen by strangers all day: covering begins as the pen fills
        if not u.get("innocent"):
            u["modesty"] = min(0.5, u.get("modesty", 0.0) + 0.01 * (0.3 + crowd))
        record_mind(u)
        record_census(u)
        u["births_y"] = u["deaths_y"] = 0

    if not people:
        record_extinction(u, events)
    advance_part(u)


def record_mind(u):
    """Two clocks, reported apart (BOOKS.md, 'Two clocks'): the genetic mean
    and tail of self-control, so nobody mistakes cultural change for a
    bigger brain. Culture's clock is the tech, arts and institutions."""
    adults = [q for q in u["people"] if age_of(q, u["day"]) >= ADULT_AGE]
    if not adults:
        return
    efs = [q.get("ef", 0.5) for q in adults]
    mean = sum(efs) / len(efs)
    tail = sum(1 for e in efs if e > 0.6) / len(efs)
    vg = sum(q.get("vg", 0.5) for q in adults) / len(adults)
    u.setdefault("mind", []).append([u["day"] // DAYS_PER_YEAR, round(mean, 3), round(tail, 3),
                                     round(vg, 3)])
    if len(u["mind"]) > 400:
        u["mind"] = u["mind"][-400:]


# ---------------------------------------------------------------- LAGOON

def lagoon_season(day, tropical=False):
    """Returns (plant_mult, fish_mult, is_winter)."""
    d = day % DAYS_PER_YEAR
    if tropical:
        # Two rainy seasons, with drier intervals. Multipliers are model
        # hypotheses; the analogy supplies seasonality, not measured yields.
        if 90 <= d < 180 or 270 <= d < 330:
            return 1.15, 0.85, False
        return 0.65, 1.0, False
    if 240 <= d < 330:
        return 0.55, 0.7, True
    if 60 <= d < 150:
        return 1.15, 1.1, False
    return 0.9, 1.0, False


def has(u, tech):
    return tech in u["tech"]


_TERRAIN_CACHE = {}


_LAND_COMPONENTS = {}     # bounded derived cache, never serialized


def dry_neighbors(terr, x, y):
    n = len(terr)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, -1), (1, -1), (-1, 1)):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < n and 0 <= ny < n) or terr[ny][nx] == 2:
            continue
        if dx and dy and (terr[y][nx] == 2 or terr[ny][x] == 2):
            continue                    # cannot cut diagonally across water
        yield nx, ny


def same_land(terr, ax, ay, bx, by):
    """Two dry positions share a walkable land mass, without a boat."""
    n = len(terr)
    if not all(0 <= v < n for v in (ax, ay, bx, by)):
        return False
    entry = _LAND_COMPONENTS.get(id(terr))
    if entry is None or entry[0] is not terr:
        labels, label = [-1] * (n * n), 0
        for y in range(n):
            for x in range(n):
                if terr[y][x] == 2 or labels[y*n+x] >= 0:
                    continue
                labels[y*n+x] = label
                queue = [(x, y)]
                for qx, qy in queue:
                    for nx, ny in dry_neighbors(terr, qx, qy):
                        if labels[ny*n+nx] < 0:
                            labels[ny*n+nx] = label
                            queue.append((nx, ny))
                label += 1
        if len(_LAND_COMPONENTS) >= 8:
            _LAND_COMPONENTS.pop(next(iter(_LAND_COMPONENTS)))
        entry = (terr, labels)
        _LAND_COMPONENTS[id(terr)] = entry
    labels = entry[1]
    return labels[ay*n+ax] >= 0 and labels[ay*n+ax] == labels[by*n+bx]


def terrain_of(u):
    seed = u.get("terrain_seed", u["seed"])
    key = (seed, u.get("terrain_version", 1))
    if key not in _TERRAIN_CACHE:
        _TERRAIN_CACHE[key] = make_lagoon_terrain(seed, key[1])
    return _TERRAIN_CACHE[key]


def till_near(u, rng, st, span):
    """Till one dry tile near camp. Water is not a field."""
    terr = terrain_of(u)
    for _ in range(12):
        x = int(st["x"] + rng.randint(-span, span))
        y = int(st["y"] + rng.randint(-span, span))
        if (1 <= x < LAGOON_SIZE - 1 and 1 <= y < LAGOON_SIZE - 1
                and terr[y][x] != 2 and [x,y] not in u["farms"]
                and same_land(terr,st["x"],st["y"],x,y)):
            u["farms"].append([x, y])
            return True
    return False


# ------------------------------------------------- where work happens

_SITES = {}


def settlement_sites(u, si):
    """Tiles around a settlement where each kind of work gets done.
    Cached — the land does not move."""
    st = u["settlements"][min(si, len(u["settlements"]) - 1)]
    key = (u.get("terrain_seed", u["seed"]), u.get("terrain_version",1), st["x"], st["y"], int(st["r"]))
    hit = _SITES.get(key)
    if hit:
        return hit
    terr = terrain_of(u)
    R = int(st["r"]) + 12
    woods, shore, open_ = [], [], []
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            x, y = st["x"] + dx, st["y"] + dy
            if not (1 <= x < LAGOON_SIZE - 1 and 1 <= y < LAGOON_SIZE - 1):
                continue
            k = terr[y][x]
            if k == 1:
                woods.append((x, y))
            elif k == 0:
                open_.append((x, y))
            elif k == 3:
                # a beach tile touching water is where you fish from
                if (terr[y - 1][x] == 2 or terr[y + 1][x] == 2
                        or terr[y][x - 1] == 2 or terr[y][x + 1] == 2):
                    shore.append((x, y))
                else:
                    open_.append((x, y))
    sites = {"woods": woods[:600], "shore": shore[:300], "open": open_[:600]}
    if len(_SITES) > 24:
        _SITES.clear()
    _SITES[key] = sites
    return sites


def _pick(rng, seq, fallback):
    return rng.choice(seq) if seq else fallback


def band_patches(u, si, rng):
    """The few places this band is working at the moment. A band does not
    scatter at random across its range — it works a patch together, strips
    it, and moves on. Shared patches are what make a foraging party look
    like a party."""
    st = u["settlements"][min(si, len(u["settlements"]) - 1)]
    pat = st.get("pat")
    if pat and st.get("patday", 0) > u["day"]:
        return pat
    sites = settlement_sites(u, si)
    pat = []
    for kind, pool in (("open", sites["open"]), ("woods", sites["woods"]),
                       ("shore", sites["shore"])):
        if not pool:
            continue
        for _ in range(2 if kind != "shore" else 1):
            x, y = rng.choice(pool)
            pat.append([x, y, kind])
    st["pat"] = pat
    st["patday"] = u["day"] + rng.randint(500, 1500)   # worked out in a year or two
    return pat


def _patch_for(pat, kind, rng, fallback):
    opts = [q for q in pat if q[2] == kind]
    if not opts:
        return fallback
    q = rng.choice(opts)
    return (q[0] + rng.randint(-2, 2), q[1] + rng.randint(-2, 2))


def lagoon_assign(u, p, day, rng, shortfall):
    """One step of a life: people live out of a home, go out to work a patch
    with the others, and come back. Nobody wanders to a random spot."""
    si = min(p.get("st", 0), len(u["settlements"]) - 1)
    st = u["settlements"][si]
    a = age_of(p, day)
    if ("hx" not in p or abs(p["hx"] - st["x"]) > st["r"] + 2
            or abs(p["hy"] - st["y"]) > st["r"] + 2):
        p["hx"] = st["x"] + rng.randint(-2, 2)       # a hearth of their own
        p["hy"] = st["y"] + rng.randint(-2, 2)
    home = (p["hx"], p["hy"])

    terr = terrain_of(u)

    def clamp(x, y):
        """Inside the map and on dry land — snap to the nearest land tile."""
        x = min(LAGOON_SIZE - 2, max(1, x))
        y = min(LAGOON_SIZE - 2, max(1, y))
        if terr[y][x] != 2:
            return (x, y)
        for r in (1, 2, 3):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    xx, yy = x + dx, y + dy
                    if 1 <= xx < LAGOON_SIZE - 1 and 1 <= yy < LAGOON_SIZE - 1 \
                            and terr[yy][xx] != 2:
                        return (xx, yy)
        return (p["hx"], p["hy"])

    def at_home(r=2):
        return clamp(p["hx"] + rng.randint(-r, r), p["hy"] + rng.randint(-r, r))

    # needs that override everything
    if p["due"] and p["due"] - day <= 0 and not p.get("mc"):
        p["a"], p["ad"] = A_BIRTH, days(2)
        p["tx"], p["ty"] = at_home(0)
        # Human birth is hard: the head is large, the pelvis narrow, the baby
        # emerges facing away — so women almost never deliver alone. Her
        # mother, or another woman of the band, kneels with her.
        helpers = [q for q in u["_ctx"]["af"] if q is not p and q.get("st", 0) == p.get("st", 0)
                   and abs(q["x"] - p["x"]) <= 8 and abs(q["y"] - p["y"]) <= 8]
        mom = next((q for q in helpers if q["id"] == p.get("mom")), None)
        h = mom or (helpers[0] if helpers else None)
        if h is not None and h.get("a") != A_BIRTH:
            h["a"], h["ad"] = A_TEND, days(2)
            h["tx"], h["ty"] = clamp(p["tx"] + 1, p["ty"])
            h["f"], p["f"] = -1, 1
        return
    if p["due"] and 0 < p["due"] - day < 21:
        p["a"], p["ad"] = A_REST, days(6)
        p["tx"], p["ty"] = at_home(1)
        return
    if p.get("thirst", 0.0) >= 1.0:
        target = needs.water_target(u, p)
        if target is not None:
            p["a"], p["ad"] = A_DRINK, days(1)
            p["tx"], p["ty"] = target
            return
    if a < 3 * DAYS_PER_YEAR:                  # infants: wherever mother is
        p["a"], p["ad"] = A_TEND, days(3)
        p["tx"], p["ty"] = at_home(1)
        return
    if a < 12 * DAYS_PER_YEAR:                 # children: packs at play
        if p.get("hun", 0.0) > needs.EAT_AT and needs.camp_store(u, p) > 0:
            # hungry children go to the camp and eat, like everyone else
            p["a"], p["ad"] = A_EAT, days(1)
            p["tx"], p["ty"] = at_home(1)
        elif rng.random() < 0.7:
            play_with(u, p, kids_near(u["_ctx"], p), rng, clamp)
        else:                                  # or tag along with mother
            m = next((q for q in u["people"] if q["id"] == p.get("mom")), None)
            if m is not None and m.get("a") == A_FORAGE:
                p["a"], p["ad"] = A_FORAGE, days(rng.randint(2, 4))
                p["tx"], p["ty"] = clamp(m["tx"] + rng.randint(-1, 1), m["ty"] + rng.randint(-1, 1))
            else:
                play_with(u, p, kids_near(u["_ctx"], p), rng, clamp)
        return

    near_home = (abs(p["x"] - p["hx"]) <= 3 and abs(p["y"] - p["hy"]) <= 3)
    if not near_home and (p.get("carry", 0.0) > 0 or p.get("carry_water", 0.0) > 0):
        p["a"], p["ad"] = A_WALK, days(0)            # a load to bring home
        p["tx"], p["ty"] = home
        return

    # A wound lies up until it closes. Tiredness is no longer a day-counter
    # here: it is the energy meter, and needs.assign reads it.
    if p.get("inj", 0) > 0.45:
        p["a"], p["ad"] = A_REST, days(rng.randint(3, 6))
        p["tx"], p["ty"] = at_home(1)
        return

    # The decision itself is shared with EDEN: read the body, perceive the
    # places that hold food, score them against the need and the cost, and
    # commit. What differs between the worlds is the condition, not the
    # mind. (needs.py)
    act = needs.assign(u, p, day, rng, needs.CONDITIONS["LAGOON"])

    if act == A_GROOM:
        kin = [q for q in u["people"] if q is not p and q.get("st", 0) == p.get("st", 0)
               and (q["id"] in (p.get("p"), p.get("mom")) or q.get("mom") == p["id"])
               and abs(q["x"] - p["x"]) <= 6 and abs(q["y"] - p["y"]) <= 6
               and q.get("a") not in (A_MATE, A_BIRTH, A_GROOM)]
        if kin:
            groom_with(p, kin[0], *at_home(1))
        else:
            p["a"] = A_TALK
    elif act == A_MATE:
        q = next((q for q in u["people"] if q["id"] == p.get("p")), None)
        if q is not None:
            couple_up(p, q, *at_home(1))
        else:
            p["a"] = A_REST
    elif act in (A_TALK, A_REST):
        # elders sit together, too
        cx, cy = (st["x"] + rng.randint(-3, 3), st["y"] + rng.randint(-3, 3))
        join_circle(u, p, cx, cy, size=5 if act == A_TALK else 4,
                    radius=1.6 if act == A_TALK else 1.3)
        p["tx"], p["ty"] = clamp(p["tx"], p["ty"])
    elif act == A_BUILD:
        # their own hut, if that is what they set out to raise; otherwise
        # the boat: weeks of work at the yard for a shore nobody has seen
        h = needs.hut_of(u, p)
        boat = u.get("boat")
        if h is not None and not h["done"] and (p["tx"], p["ty"]) == (h["x"], h["y"]):
            pass
        elif boat is not None:
            p["tx"], p["ty"] = clamp(boat["x"] + rng.randint(-2, 2),
                                     boat["y"] + rng.randint(-1, 1))
    return


def _weighted(w, rng):
    total = sum(x[1] for x in w)
    r = rng.random() * total
    for kind, weight in w:
        r -= weight
        if r <= 0:
            return kind
    return w[-1][0]


# ------------------------------------------------- how people are together
# Humans do almost nothing alone. These helpers turn solitary activity codes
# into dyads and circles: a conversation is a ring of people facing inward,
# a fight is two people squaring off, a couple stands together, children
# chase each other, infants stay on their mother.


def day_context(people, day):
    """Computed once per tick so the social helpers don't rescan everyone.
    Children are bucketed on an 8-tile grid so a playmate search is local."""
    # `moms` is a dict used as an ordered set: O(1) membership for
    # `p["id"] in ctx["moms"]`, and JSON-safe so the whole world stays
    # serialisable. A python set here silently breaks any tool that dumps
    # the world — the engine must never hold a value JSON cannot carry.
    kids, moms, adults_m, adults_f = {}, {}, [], []
    for q in people:
        a = day - q["b"]
        if 3 * DAYS_PER_YEAR <= a < 12 * DAYS_PER_YEAR:
            kids.setdefault((q["x"] >> 3) * 4096 + (q["y"] >> 3), []).append(q)
        elif a < 3 * DAYS_PER_YEAR and q.get("mom") is not None:
            moms[q["mom"]] = True
        elif ADULT_AGE <= a <= 45 * DAYS_PER_YEAR and not q["w"]:
            (adults_m if q["s"] == "m" else adults_f).append(q)
    dens = {}                     # heads per 4-tile cell: crowding, cheaply
    for q in people:
        k = (q["x"] >> 2) * 4096 + (q["y"] >> 2)    # an int key: JSON-safe
        dens[k] = dens.get(k, 0) + 1
    return {"kids": kids, "moms": moms, "am": adults_m, "af": adults_f, "dens": dens,
            "byid": {q["id"]: q for q in people}}


def kids_near(ctx, p):
    gx, gy = p["x"] >> 3, p["y"] >> 3
    out = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            out.extend(ctx["kids"].get((gx + dx) * 4096 + gy + dy, ()))
    return out


def join_circle(u, p, cx, cy, size=5, radius=1.6):
    """Stand in a ring with whoever is already talking nearby, facing in."""
    day = u["day"]
    circles = u.setdefault("circles", [])
    if len(circles) > 300:
        del circles[:150]
    best = None
    for c in circles:
        if (c["n"] < size and day - c["d"] < 30
                and abs(c["x"] - cx) <= 4 and abs(c["y"] - cy) <= 4):
            best = c
            break
    if best is None:
        best = {"x": cx, "y": cy, "n": 0, "d": day}
        circles.append(best)
    i = best["n"]
    best["n"] += 1
    ang = i * (2 * math.pi / size) + 0.5
    p["tx"] = int(round(best["x"] + math.cos(ang) * radius))
    p["ty"] = int(round(best["y"] + math.sin(ang) * radius))
    p["f"] = -1 if p["tx"] > best["x"] else 1


def square_off(p, q):
    """Two people face each other, a pace apart."""
    x, y = (p["x"] + q["x"]) // 2, (p["y"] + q["y"]) // 2
    p["tx"], p["ty"], p["f"] = x, y, 1
    q["tx"], q["ty"], q["f"] = x + 1, y, -1


def pick_fight(u, p, people, rng, reach=9):
    """Violence takes two. Find another man nearby, preferably one with
    nothing to lose, and go at each other."""
    pool = [q for q in people
            if q is not p and q["s"] == "m" and not q["w"]
            and q.get("a") != A_FIGHT
            and abs(q["x"] - p["x"]) <= reach and abs(q["y"] - p["y"]) <= reach
            and age_of(q, u["day"]) >= ADULT_AGE]
    if not pool:
        return False
    pool.sort(key=lambda q: 0 if (q.get("box") is None or q["box"] < 0) else 1)
    q = pool[0] if rng.random() < 0.7 else rng.choice(pool)
    square_off(p, q)
    p["a"] = q["a"] = A_FIGHT
    p["ad"] = q["ad"] = days(2)
    return True


def groom_with(p, q, x, y):
    """Primates keep their bonds by grooming; humans do it with hands and
    talk (Harari's gossip, Dunbar's grooming). Two sit together, one tending
    the other's hair or skin."""
    p["tx"], p["ty"], p["f"] = x, y, 1
    q["tx"], q["ty"], q["f"] = x + 1, y, -1
    p["a"] = q["a"] = A_GROOM
    p["ad"] = q["ad"] = days(2)


def couple_up(p, q, x, y):
    p["tx"], p["ty"], p["f"] = x, y, 1
    q["tx"], q["ty"], q["f"] = x + 1, y, -1
    p["a"] = q["a"] = A_MATE
    p["ad"] = q["ad"] = 2       # half a day together, not two


def follow_mother(p, byid, clamp):
    """Infants are carried; toddlers trail. Either way the child is where
    the mother is, not where the child's bed is."""
    m = byid.get(p.get("mom"))
    if m is None:
        return False
    ox = (p["id"] % 3) - 1
    oy = (p["id"] // 3) % 2
    tx, ty = clamp(m["x"] + ox, m["y"] + oy)
    if abs(p["x"] - tx) > 1 or abs(p["y"] - ty) > 1:
        p["tx"], p["ty"] = tx, ty
    p["f"] = 1 if m["x"] >= p["x"] else -1
    return True


def play_with(u, p, kids, rng, clamp):
    """Children chase each other: the target is another child, so the
    group keeps re-forming and running. `kids` is the local grid bucket."""
    near = [k for k in kids if k is not p
            and abs(k["x"] - p["x"]) <= 7 and abs(k["y"] - p["y"]) <= 7]
    p["a"] = A_PLAY
    p["ad"] = days(rng.randint(1, 2))
    if near:
        k = rng.choice(near)
        p["tx"], p["ty"] = clamp(k["x"] + rng.randint(-1, 1), k["y"] + rng.randint(-1, 1))
        p["f"] = 1 if k["x"] >= p["x"] else -1
    else:
        p["tx"], p["ty"] = clamp(p["hx"] + rng.randint(-2, 2), p["hy"] + rng.randint(-2, 2))


WALK_SPEED = 3          # tiles covered in a day's travel
LAGOON_WALK = 6         # foragers range farther in a day than resort guests
                        # stroll: travel should be a share of the day, not all of it


_FIELDS = {}          # (id of terrain, target) -> distance field; a cache, never saved
_FIELDS_MAX = 96


def land_field(terr, tx, ty):
    """Walking distance over land to (tx, ty) from every tile: a breadth-first
    flood, so a walk around the inner lagoon is a walk, not a dead end.
    Cached per target and rebuilt freely; it is derived, never state."""
    key = (id(terr), tx, ty)
    f = _FIELDS.get(key)
    if f is not None:
        return f
    n = len(terr)
    far = n * n
    f = [far] * (n * n)
    if terr[ty][tx] != 2:
        f[ty * n + tx] = 0
        q = [(tx, ty)]
        for x, y in q:
            d = f[y * n + x] + 1
            for nx, ny in dry_neighbors(terr, x, y):
                if 0 <= nx < n and 0 <= ny < n and terr[ny][nx] != 2 and f[ny * n + nx] > d:
                    f[ny * n + nx] = d
                    q.append((nx, ny))
    if len(_FIELDS) >= _FIELDS_MAX:
        _FIELDS.pop(next(iter(_FIELDS)))
    _FIELDS[key] = f
    return f


def step_toward(p, terr=None, speed=WALK_SPEED):
    """Travel toward the target; True once standing on it. A day is a long
    time to walk — covering only one tile per day would leave everyone
    permanently in transit and never anywhere."""
    for _ in range(speed):
        dx = p["tx"] - p["x"]
        dy = p["ty"] - p["y"]
        if dx == 0 and dy == 0:
            return True
        sx = (1 if dx > 0 else -1) if dx else 0
        sy = (1 if dy > 0 else -1) if dy else 0
        if sx:
            p["f"] = sx                                # face the way you walk
        nx, ny = p["x"] + sx, p["y"] + sy
        if terr is not None:
            # a target off the map is walked to its nearest edge, never past it
            n = len(terr)
            if not (1 <= p["tx"] < n - 1 and 1 <= p["ty"] < n - 1):
                p["tx"] = min(n - 2, max(1, p["tx"]))
                p["ty"] = min(n - 2, max(1, p["ty"]))
                continue
        if p.get("detour") and terr is not None:
            nx, ny = p["x"], p["y"]                    # already going round
        elif terr is not None and (terr[ny][nx] == 2 or
                (sx and sy and (terr[p["y"]][nx] == 2 or terr[ny][p["x"]] == 2))):   # don't walk into the sea
            if sx and terr[p["y"]][nx] != 2:
                ny = p["y"]
            elif sy and terr[ny][p["x"]] != 2:
                nx = p["x"]
            else:
                nx, ny = p["x"], p["y"]
        if nx == p["x"] and ny == p["y"] and terr is not None:
            # water in the way: walk round it, by the shortest way on land
            n = len(terr)
            f = land_field(terr, p["tx"], p["ty"])
            here = f[p["y"] * n + p["x"]]
            best = None
            for xx, yy in dry_neighbors(terr, p["x"], p["y"]):
                if 0 <= xx < n and 0 <= yy < n and f[yy * n + xx] < here:
                    if best is None or f[yy * n + xx] < f[best[1] * n + best[0]]:
                        best = (xx, yy)
            if best is not None:
                nx, ny = best
                p["detour"] = 1        # keep going round until arrival
        if nx == p["x"] and ny == p["y"]:
            p.pop("detour", None)
            # no way forward at all: the target is across the sea. Give it
            # up, so the person chooses something reachable instead.
            p["tx"], p["ty"] = p["x"], p["y"]
            return True
        p["x"], p["y"] = nx, ny
    if p["x"] == p["tx"] and p["y"] == p["ty"]:
        p.pop("detour", None)
        return True
    return False


TOTEMS = {"plants": "the fig", "game": "the boar", "fish": "the great fish"}


ISLAND_CAP = 95      # illustrative crowding trigger for boatbuilding, not measured food capacity
BOAT_WORK = 400      # person-days to build a boat that can cross the strait


def boatyard(u, y):
    """The island's west beach on row y — the shore that faces the mainland,
    not the inner lagoon — and the mainland shore straight across from it.
    Returns (yard_x, landing_x) or None if the row has no clear crossing."""
    terr = terrain_of(u)
    row = terr[y]
    x = 40
    while x < LAGOON_SIZE - 1 and row[x] != 2:          # leave the mainland
        x += 1
    while x < LAGOON_SIZE - 1 and row[x] == 2:          # cross the strait
        x += 1
    if x >= LAGOON_SIZE - 1:
        return None
    yard = x
    land = yard - 1
    while land > 1 and row[land] == 2:
        land -= 1
    if land <= 1 or yard - land < 4:
        return None
    return yard, land


def launch(u, people, boat, rng, events, day, year):
    """The boat is finished: young adults and their children board at the
    yard and paddle west across the strait, a few tiles a day, in sight."""
    xy = boatyard(u, boat["y"])
    if not xy:
        return
    yard, land = xy
    young = [q for q in people if ADULT_AGE <= age_of(q, day) < 35 * DAYS_PER_YEAR]
    rng.shuffle(young)
    go = {q["id"] for q in young[:max(6, len(people) // 5)]}
    go |= {q["p"] for q in people if q["id"] in go and q.get("p")}
    go |= {q["id"] for q in people if q.get("mom") in go and age_of(q, day) < ADULT_AGE}
    for q in people:
        if q["id"] in go:
            q["ab"] = 1
            q["a"], q["ad"] = A_REST, days(99)
    u["voyage"] = {"x0": yard, "x1": land, "y": boat["y"], "d0": day,
                   "days": max(4, (yard - land) // 3), "n": len(go)}
    events.append((day, "LAGOON", "migration",
                   f"Year {year}: the boat is finished. {len(go)} of them push off from the "
                   f"west beach toward the shore across the strait."))


def sail(u, people, rng, events, day):
    """One day of the crossing: everyone aboard sits where the boat is."""
    v = u["voyage"]
    t = min(1.0, (day - v["d0"]) / v["days"])
    bx = v["x0"] + (v["x1"] - v["x0"]) * t
    aboard = [q for q in people if q.get("ab")]
    for k, q in enumerate(aboard):
        q["x"] = int(round(bx)) + (k % 3) - 1
        q["y"] = v["y"] + (k // 3) % 2
        q["tx"], q["ty"] = q["x"], q["y"]
        q["a"], q["f"] = A_REST, -1
    if t < 1.0:
        return
    tribe = make_name(rng, minds.NAMES.get("LAGOON"))
    land = v["x1"]
    u["settlements"].append({"x": max(4, land - 3), "y": v["y"], "r": 5, "n": tribe})
    new_i = len(u["settlements"]) - 1
    for q in aboard:
        q.pop("ab", None)
        q["st"] = new_i
        q["x"], q["y"] = land, v["y"]
        q["hx"], q["hy"] = max(3, land - 3) + rng.randint(-2, 2), v["y"] + rng.randint(-2, 2)
        q["tx"], q["ty"], q["ad"] = q["hx"], q["hy"], 0
    u.setdefault("boats", []).append([land + 1, v["y"]])   # pulled up on the beach
    del u["voyage"]
    if not u.get("continent"):
        # land no one has harvested: full groves and naive game, the boom
        # every first landing in Diamond's island histories enjoys (ch.2)
        st = u["stocks"]
        st["plants"] += 120000.0
        st["game"] += 5000.0
    u["continent"] = True
    events.append((day, "LAGOON", "migration",
                   f"The boat lands on the greater shore. {len(aboard)} step off and become "
                   f"the {tribe} tribe — a land without end, the one all their children's "
                   f"children will call home."))


def keep_watch(u, people, day, events, part=0, rng=None):
    """Fire, a sentry, and the stories told around both.

    Once a band can keep a fire, the night is spent together at it: one
    adult sits watch facing the dark — the most watchful take the most
    turns — and the rest talk. That shared night is where stories come
    from, and stories are where shared lore comes from (BOOKS.md: Harari,
    gossip and fiction; Nexus ch.2). A day of talk at a fire adds to the
    store of stories; lore is discovered sooner the more there are.

    The watch is a turn taken in rotation, not a job one person keeps: the
    turn goes round the watchable ones, so the whole band learns to sit
    up in the dark. The watcher does not sleep that night and is hungrier
    for it in the morning.

    At night the band also *comes in*: the hunters who are still out stay
    out, but everyone else converges on the fire. A camp that has a fire
    is a camp that spends its dark hours together, which is the thing that
    turns a band into a society."""
    if not has(u, "fire"):
        return
    night = (part == PART_NIGHT)
    by_st = {}
    for q in people:
        if q.get("ab") or not (ADULT_AGE <= age_of(q, day) < ELDER_AGE):
            continue
        by_st.setdefault(q.get("st", 0), []).append(q)
    for i, st in enumerate(u["settlements"]):
        band = by_st.get(i)
        st["watch"] = 0
        if not band:
            continue
        band.sort(key=lambda q: -q.get("vg", 0.5))
        half = band[:max(1, len(band) // 2)]
        w = half[u.get("day", 0) % len(half)]
        if w.get("a") in (A_BIRTH, A_RITE) or w.get("due"):
            continue
        w["a"], w["ad"] = A_WATCH, days(1)
        fx, fy = st["x"] + 2, st["y"] + 1          # where the fire is
        w["tx"], w["ty"] = fx - 3, fy
        w["f"] = 1
        st["watch"] = w["id"]
        if night:
            w["hun"] = w.get("hun", 0.0) + 0.5     # a night on watch is a hungry one
            if rng is not None:
                for q in band:
                    if q is w or q.get("w"):
                        continue
                    if q.get("a") in minds.WORK_ACTS:
                        continue                  # anyone out at work: needs.night beds them there
                    q["tx"], q["ty"] = fx + rng.randint(-2, 2), fy + rng.randint(-1, 2)
                    if q.get("a") in (A_IDLE, A_WALK, A_TALK):
                        q["a"] = A_TALK if rng.random() < 0.6 else A_SLEEP
                        q["ad"] = days(2)
        talkers = sum(1 for q in band if q.get("a") == A_TALK)
        before = u.get("stories", 0.0)
        u["stories"] = before + talkers * (0.02 if night else 0.01) / PARTS_PER_DAY
        if before < 1.0 <= u["stories"]:
            events.append((day, "LAGOON", "culture",
                           f"Around the fire, with {w['n']} watching the dark, someone tells "
                           f"of a thing none of them saw. It is the first story."))


MYTHS = {
    "drought": "the rain has a keeper, and the keeper is angry with them",
    "harsh": "the cold comes down when the sky-hunter goes hungry",
    "storm": "the lagoon has a voice, and it wanted the stores",
    "epidemic": "the sickness is the herds' revenge for a broken rule",
    "predator": "the big cat is one of their dead, come back to walk",
    "starvation": "the groves withhold their fruit from the greedy",
    "feud": "the first fire was stolen, and the theft still divides them",
}


def tell_myth(u, cause, events, day):
    """Before any way of testing an explanation, a people with shared lore
    explains what it cannot understand with a story about someone's will
    (Harari's fictions; Durkheim's sacred). Each kind of disaster gets one."""
    if not has(u, "lore"):
        return
    myths = u.setdefault("myths", [])
    if cause in [m[0] for m in myths] or cause not in MYTHS:
        return
    myths.append([cause, MYTHS[cause], day // DAYS_PER_YEAR])
    events.append((day, "LAGOON", "culture",
                   f"A story spreads to explain the {cause}: {MYTHS[cause]}. It becomes "
                   f"something they all know, and teach."))


def lagoon_violence(u, p, a, people, byid, gone, dead, rng, events):
    """Killing among the people, and the revenge that follows it.

    Young unpaired men with hot tempers and little restraint kill; marriage,
    a third party with standing (the arbiter) and a shared rite damp it. A
    killing leaves the victim's kin a grudge against the killer that decays
    over years and is acted on when restraint fails (BOOKS.md: Pinker ch.2,
    ch.8; Freud §V on the narcissism of small differences). Returns True if
    p died here.
    """
    sts = u["settlements"]
    st = sts[min(p.get("st", 0), len(sts) - 1)]
    damp = (1 - 0.7 * st.get("arb", 0.0)) * (1 - 0.5 * st.get("coh", 0.0))
    ef = minds.self_control(p, a)
    victim = None
    if p.get("gd", 0) > 0.05:
        k = byid.get(p.get("gk"))
        if k is None or k["id"] in gone or k in dead:
            p["gd"] = 0.0
        elif rng.random() < 6e-4 * p["gd"] * (1.1 - ef) * damp:
            victim, why = k, "revenge"
    if (victim is None and p["s"] == "m" and ADULT_AGE <= a < 30 * DAYS_PER_YEAR
            and rng.random() < 1e-4 * (2.0 if p["p"] is None else 1.0)
            * minds.aggression(p) * 2 * (1.2 - ef) * damp):
        near = [q for q in rng.sample(people, min(12, len(people)))
                if q is not p and q["id"] not in gone and q not in dead
                and q.get("st", 0) == p.get("st", 0)
                and age_of(q, u["day"]) >= ADULT_AGE]
        if near:
            victim, why = near[0], "quarrel"
    if victim is None:
        return False
    gone[victim["id"]] = True
    dead.append(victim)
    cod(u, "violence")
    victim["gd"] = 0.0
    kin = [q for q in people if q["id"] not in gone and q is not p and (
        q["id"] == victim.get("p") or q.get("mom") == victim["id"]
        or q["id"] == victim.get("mom"))]
    for q in kin:
        q["gd"], q["gk"] = 1.0, p["id"]
    p["gd"] = 0.0
    if why == "revenge":
        events.append((u["day"], "LAGOON", "violence",
                       f"{p['n']} avenges a death: {victim['n']} is killed."))
    elif rng.random() < 0.5:
        events.append((u["day"], "LAGOON", "violence",
                       f"{p['n']} kills {victim['n']} in a quarrel."
                       + (f" {kin[0]['n']} will not forget." if kin else "")))
    # a third party with standing punishes the killer (Pinker ch.2: Leviathan)
    if rng.random() < st.get("arb", 0.0) * 0.8:
        others = [i for i in range(len(sts)) if i != p.get("st", 0)]
        if others:
            ni = rng.choice(others)
            p["st"] = ni
            p["hx"], p["hy"] = sts[ni]["x"], sts[ni]["y"]
            p["tx"], p["ty"], p["ad"] = p["hx"], p["hy"], 0
            clear_widows(people, [p])
            p["p"] = None
            events.append((u["day"], "LAGOON", "violence",
                           f"{st.get('n', 'The camp')} drives {p['n']} out for the killing."))
        else:
            gone[p["id"]] = True
            dead.append(p)
            cod(u, "violence")
            events.append((u["day"], "LAGOON", "violence",
                           f"{st.get('n', 'The camp')} puts {p['n']} to death for the killing."))
            return True
    return False


ORG_LADDER = (("band", 0), ("tribe", 50), ("chiefdom", 300))
ARBITER = {"band": 0.1, "tribe": 0.35, "chiefdom": 0.65}


def organise(u, people, rng, events):
    """Band, tribe, chiefdom (Diamond ch.14), with hysteresis so a stage does
    not flicker. A chiefdom needs stored food to feed a chief. The stage sets
    how much standing a third party has to stop a feud."""
    counts = {}
    for q in people:
        counts[q.get("st", 0)] = counts.get(q.get("st", 0), 0) + 1
    for i, st in enumerate(u["settlements"]):
        n = counts.get(i, 0)
        cur = st.get("org", "band")
        new = cur
        if cur == "band" and n >= 50:
            new = "tribe"
        elif cur == "tribe" and n >= 300 and has(u, "granary"):
            new = "chiefdom"
        elif cur == "tribe" and n < 40:
            new = "band"
        elif cur == "chiefdom" and (n < 240 or not has(u, "granary")):
            new = "tribe"
        st["arb"] = ARBITER[new] + (0.15 if has(u, "writing") else 0.0)
        st["coh"] = round(max(0.0, st.get("coh", 0.0) - 0.25), 3)
        if new != cur:
            st["org"] = new
            mine = [q for q in people if q.get("st", 0) == i
                    and age_of(q, u["day"]) >= 30 * DAYS_PER_YEAR]
            head = max(mine, key=lambda q: q.get("ef", 0.5))["n"] if mine else None
            grown = [k for k, _ in ORG_LADDER].index(new) > [k for k, _ in ORG_LADDER].index(cur)
            if grown:
                events.append((u["day"], "LAGOON", "phase",
                               f"{st.get('n', 'The camp')} is a {new} now, {n} strong"
                               + (f"; {head} speaks for it." if head else ".")))
            else:
                events.append((u["day"], "LAGOON", "phase",
                               f"{st.get('n', 'The camp')} falls back to a {new}."))
        else:
            st.setdefault("org", cur)


def hold_rites(u, people, shortfall, rng, events):
    """Collective effervescence (Durkheim, Elementary Forms): once a people
    has shared lore, each settlement gathers at midsummer and dances for its
    totem — the thing it lives on, set apart. The gathering is what renews
    cohesion; a hungry year skips it, and cohesion drains."""
    if not has(u, "lore"):
        return
    eaten = {"plants": 1.0, "fish": 0.8 if has(u, "fishing") else 0.0, "game": 0.6}
    for i, st in enumerate(u["settlements"]):
        if "totem" not in st:
            st["totem"] = TOTEMS[max(eaten, key=eaten.get) if i == 0
                                 else rng.choice(list(TOTEMS))]
        mine = [q for q in people if q.get("st", 0) == i]
        if not mine:
            continue
        if shortfall > 0.25:
            if rng.random() < 0.3:
                events.append((u["day"], "LAGOON", "culture",
                               f"Too hungry to dance: {st.get('n', 'the camp')} lets "
                               f"midsummer pass without honouring {st['totem']}."))
            continue
        first = not st.get("rites")
        st["rites"] = st.get("rites", 0) + 1
        st["coh"] = min(1.0, st.get("coh", 0.0) + 0.5)
        ring = len(mine)
        rad = 1.5 + math.sqrt(ring) * 0.6
        for k, q in enumerate(mine):
            if age_of(q, u["day"]) < 3 * DAYS_PER_YEAR or (q.get("due") and q["due"] - u["day"] < 3):
                continue
            ang = k * 2 * math.pi / ring
            q["a"], q["ad"] = A_RITE, days(3)
            q["tx"] = int(round(st["x"] + math.cos(ang) * rad))
            q["ty"] = int(round(st["y"] + math.sin(ang) * rad))
        if first:
            events.append((u["day"], "LAGOON", "culture",
                           f"{st.get('n', 'The camp')} gathers at midsummer and dances "
                           f"for {st['totem']} — the first rite. They go home closer "
                           f"than they came."))


def tick_lagoon(u, rng, events):
    part = u.get("part", 0)
    day = u["day"]
    people = u["people"]

    if not people:
        if u["extinct_day"] is None:
            record_extinction(u, events)
        elif day - u["extinct_day"] > RESEED_YEARS * DAYS_PER_YEAR:
            lessons = list(u["lessons"])
            for pm in u["postmortems"]:
                if pm.get("lesson") and pm["lesson"] not in lessons:
                    lessons.append(pm["lesson"])
            fresh = genesis_universe("LAGOON", u["seed"] + u["iteration"],
                                     u["iteration"] + 1,
                                     postmortems=u["postmortems"],
                                     lessons=lessons, fseed=u.get("fseed"))
            fresh["day"] = day
            fresh["founded_day"] = day
            fresh["part"], fresh["parts"] = part, u.get("parts", day * PARTS_PER_DAY + part)
            fresh["engine_history"] = list(u.get("engine_history", []))
            for p in fresh["people"]:
                p["b"] = day - 18 * DAYS_PER_YEAR  # young again
            # a "preserve" lesson is kept as a habit: their stores rot
            # slower (needs.keep_stores), not as food from nowhere
            u.clear()
            u.update(fresh)
            carried = (" They carry the old lessons: " + ", ".join(lessons) + "."
                       if lessons else "")
            events.append((day, "LAGOON", "reseed",
                           f"New castaways reach the lagoon. Iteration {u['iteration']} "
                           f"begins.{carried}"))
        advance_part(u)
        return

    stocks = u["stocks"]
    plant_mult, fish_mult, winter = lagoon_season(day, u.get("terrain_version", 1) >= 2)
    if u["drought"] > 0:
        plant_mult *= 0.45
    if winter and u["harsh_winter"]:
        plant_mult *= 0.5
        fish_mult *= 0.6

    # Stocks are an observer mirror of the actual patches and animals;
    # there is no second renewing global pool behind the places people work.
    stocks["game"], stocks["pred"] = (float(n) for n in animals.counts(u))

    # --- demography groups
    adults, kids, elders = [], [], []
    for p in people:
        a = age_of(p, day)
        (kids if a < ADULT_AGE else elders if a >= ELDER_AGE else adults).append(p)

    # --- food
    #
    # There is no food in this world that nobody went and got. The places
    # that hold it are the sites; a person who works one takes what is
    # there and carries it home, and a camp eats what its people brought
    # back. If everybody sleeps, the camps empty and the band starves:
    # that is the point, and it used to be false.
    daily_need = len(adults) * 1.0 + len(kids) * 0.6 + len(elders) * 0.8
    needs.ensure_sites(u, rng)
    # how much of the band is hungry — a fact about people, not about a ratio
    hungry = sum(1 for p in people if p.get("hun", 0.0) > 12)
    shortfall = hungry / max(1, len(people))
    # the carcass of a hunted predator: fresh meat, eaten or spoiled over the
    # days that follow. Without preservation it is gone in a couple of days.
    meat = u.get("meat", 0.0)
    if meat > 0:
        meat *= (0.85 if has(u, "preservation") else 0.55) ** (1 / PARTS_PER_DAY)
        u["meat"] = meat
    # The hunters carry the carcass home: it goes into the camp's store,
    # where it is eaten like anything else, and rots like anything else.
    if u.get("meat", 0.0) > 0 and u.get("settlements"):
        st0 = u["settlements"][0]
        st0["store"] = st0.get("store", 0.0) + u["meat"]
    u["meat"] = 0.0
    # the camps' stores, and their total
    for st in u.get("settlements") or []:
        st["store"] = max(0.0, st.get("store", 0.0))
    u["store"] = sum(st.get("store", 0.0) for st in u.get("settlements") or [])

    weapons = has(u, "stone_tools")
    healing = has(u, "healing")
    terr_l = terrain_of(u)
    byid = {q["id"]: q for q in people}
    u["_ctx"] = day_context(people, day)
    dead, born, starved = [], [], []
    u["_ctx"]["dead"] = dead
    moms = u["_ctx"]["moms"]
    gone = {}                     # ids killed by someone else earlier this tick

    if u.get("voyage"):
        sail(u, people, rng, events, day)
    keep_watch(u, people, day, events, part, rng)
    # the animals' part: herds graze and flee, cats hunt deer — and people,
    # when the deer fail them and someone is alone in the dark
    taken = animals.tick(u, rng, terr_l, people, {
        "day": day, "part": part, "night": part == PART_NIGHT, "events": events,
        "adult": lambda q: age_of(q, day) >= ADULT_AGE, "has": lambda t: has(u, t),
        "armed": weapons, "lessons": u.get("lessons", []), "A_HUNT": A_HUNT})
    # A person already taken cannot eat, work, or be killed again by a
    # quarrel later in this part.
    for p, _cause in taken:
        dead.append(p)
        cod(u, "predator")
        gone[p["id"]] = True
        byid.pop(p["id"], None)
    for p in people:
        if p["id"] in gone or p.get("ab"):
            continue
        a = age_of(p, day)
        # the body: hunger, energy and company, and they are this person's
        # own. Nobody else's dinner fills your belly, and nobody else's
        # tiredness makes you lie down.
        needs.night(u, p, rng, part)
        needs.meters(u, p, day, rng, needs.CONDITIONS["LAGOON"])
        needs.deposit(u, p, day)
        needs.eat(u, p, a / DAYS_PER_YEAR)
        needs.drink(u, p)
        if p.get("thirst", 0.0) > needs.THIRST_MAX:
            dead.append(p)
            cod(u, "dehydration")
            continue
        if p["hun"] > needs.HUNGER_MAX:
            dead.append(p)
            cod(u, "starvation")
            rng.random()  # the old per-death coin flip; kept so later rolls stay put
            starved.append(p["n"])
            continue
        # a fall is not old age — same rolls as before, different names
        if rng.random() < 6e-6 / PARTS_PER_DAY:
            dead.append(p)
            cod(u, "accident")
            continue
        if part == 0 and base_mortality(p, day, rng, events, u):
            dead.append(p)
            cod(u, "age")
            continue
        if part == 0:
            minds.tend_body(p, a, False, shortfall, healing)
            # Everything here must be earned. Physiology remains daily.
            minds.tend_purpose(p, a, 0.35, p["p"] is not None, p["id"] in moms, True)
        if p.get("a") == A_HUNT and rng.random() < 0.0015 / PARTS_PER_DAY:
            minds.hurt(p, rng.uniform(0.2, 0.6))     # gored, fallen, cut
        if part == 0 and lagoon_violence(u, p, a, people, byid, gone, dead, rng, events):
            continue
        # births
        if p["due"] and day >= p["due"]:
            p["due"] = 0
            if p.pop("mc", False):
                continue
            infant_loss = 0.06 if healing else 0.13
            mother_loss = 0.008 if healing else 0.02
            if rng.random() < mother_loss:
                dead.append(p)
                cod(u, "childbirth")
                events.append((day, "LAGOON", "childbirth",
                               f"{p['n']} dies bringing new life into the world."))
                continue
            if rng.random() >= infant_loss:
                nurse(u, p, day)
                for _twin in range(2 if rng.random() < minds.TWINS else 1):
                    sex = rng.choice("mf")
                    c = person(u["next_id"],
                               make_name(rng, minds.NAMES.get("LAGOON"), sex=sex),
                               sex, day, p["g"] + 1, p["x"], p["y"])
                    minds.inherit(c, p, rng)
                    c["st"] = p.get("st", 0)
                    c["hx"], c["hy"] = p.get("hx", p["x"]), p.get("hy", p["y"])
                    if not u.get("named"):
                        # the first name anyone gives: you name what you make
                        u["named"] = True
                        events.append((day, "LAGOON", "discovery",
                                       f"The first child is named {c['n']}. "
                                       f"After this, everyone has a name."))
                    c["mom"] = p["id"]
                    u["next_id"] += 1
                    born.append(c)
                if c["g"] > u["gen_max"] and c["g"] % 5 == 0:
                    events.append((day, "LAGOON", "generation",
                                   f"Generation {c['g']} — {c['n']} is born by the lagoon."))
                u["gen_max"] = max(u["gen_max"], c["g"])
            else:
                u["births_y"] += 1  # born and lost in the same part
                u["deaths_y"] += 1
                cod(u, "infant")
        # Thirst interrupts a long work stint before it becomes fatal.
        if p.get("thirst", 0.0) >= 1.25 and p.get("a") != A_BIRTH:
            target = needs.water_target(u, p)
            if target is not None:
                p["a"], p["ad"] = A_DRINK, days(1)
                p["tx"], p["ty"] = target
        # go about the day's work: travel to the site, then do the thing
        if age_of(p, day) < 3 * DAYS_PER_YEAR:
            follow_mother(p, byid, lambda x, y: (min(LAGOON_SIZE - 2, max(1, x)),
                                                 min(LAGOON_SIZE - 2, max(1, y))))
        if p.get("ad", 0) <= 0 and p["x"] == p["tx"] and p["y"] == p["ty"]:
            p["did"] = 0
            lagoon_assign(u, p, day, rng, shortfall)
        arrived = step_toward(p, terr_l, LAGOON_WALK)
        if arrived:
            # The work happens here and now, and it happens every day they
            # are here: they reach the place, they take what is there, they
            # eat what they need and carry the rest home.
            if u["day"] != p.get("day_done"):
                p["day_done"] = u["day"]
                needs.fulfil(u, p, day, rng, p.get("a"))
            p["ad"] = p.get("ad", 0) - 1
            if p["ad"] <= 0:
                p["did"] = 0
                lagoon_assign(u, p, day, rng, shortfall)
        # what you gathered, you carry home and put down
        needs.deposit(u, p, day)
        p["x"] = min(LAGOON_SIZE - 2, max(1, p["x"]))
        p["y"] = min(LAGOON_SIZE - 2, max(1, p["y"]))

    if starved:
        events.append((day, "LAGOON", "famine", famine_line(starved)))

    # Lost loads remain lost; the dead release their living partners.
    remove_dead(u, dead)
    u["deaths_y"] += len(dead)
    u["births_y"] += len(born)
    people.extend(born)
    u["peak"] = max(u["peak"], len(people))

    u["store"] = sum(st.get("store", 0.0) for st in u.get("settlements", []))
    if part == 0 and day % DAYS_PER_YEAR == 90:
        hold_rites(u, people, shortfall, rng, events)

    # Blue Lagoon: the founders discover how life begins
    if u["innocent"]:
        if day > 60 and rng.random() < 1 / (300 * PARTS_PER_DAY):
            u["innocent"] = False
            events.append((day, "LAGOON", "discovery",
                           "The pairs discover, as all life does, how new life begins."))
    else:
        if part == 0 and day % 30 == 0:
            living_adults = [p for p in people
                             if ADULT_AGE <= age_of(p, day) < ELDER_AGE]
            pair_singles(u, rng, living_adults)
        # Preserve the draft's food-sensitive conception hypothesis. These
        # coefficients are illustrative, not fitted demographic estimates;
        # the physical food/water budget constrains the resulting population.
        fert = 1.0 / 240 / PARTS_PER_DAY
        fed = 1.0 - min(1.0, shortfall * 1.6)
        fert *= 0.30 + 0.70 * fed
        if u["store"] > daily_need * 20:
            fert *= 1.15
        if shortfall > 0.3:
            fert *= 0.35
        if has(u, "agriculture"):
            fert *= 1.25  # the luxury trap: more mouths, more hands, more work
        try_conceive(u, rng, people, fert, byid=byid)

    # the wild places come back, slowly
    if part == 0:
        needs.regrow_sites(u, 1)
        needs.keep_stores(u)

    # --- yearly rolls: tech, disasters, settlement dynamics
    # (the cat hunt lives in animals.tick: a party with spears, near a cat)

    if part == 0 and day > u.get("founded_day", 0) and day % DAYS_PER_YEAR == 0 and people:
        pop = len(people)
        year = day // DAYS_PER_YEAR
        if u["drought"] > 0:
            u["drought"] -= 1
        u["harsh_winter"] = rng.random() < 0.06 and u.get("terrain_version", 1) < 2
        if u["harsh_winter"]:
            events.append((day, "LAGOON", "disaster",
                           f"Year {year}: a brutal ice-age winter grips the lagoon."))
            tell_myth(u, "harsh", events, day)
        if rng.random() < 0.07:
            u["drought"] = 1
            events.append((day, "LAGOON", "disaster",
                           f"Year {year}: drought — the groves wither."))
            tell_myth(u, "drought", events, day)
        if rng.random() < 0.02 and u["store"] > 0:
            for st in u["settlements"]:
                st["store"] = st.get("store", 0.0) * 0.4
            u["store"] *= 0.4
            events.append((day, "LAGOON", "disaster",
                           f"Year {year}: a storm off the lagoon destroys most of the stores."))
            tell_myth(u, "storm", events, day)
        p_epidemic = 0.02 if "cleanliness" in u["lessons"] else 0.04
        if has(u, "domestication") and rng.random() < p_epidemic and pop > 30:
            kill = rng.uniform(0.15, 0.35)
            victims = rng.sample(people, max(1, int(pop * kill)))
            remove_dead(u, victims)
            u["deaths_y"] += len(victims)
            cod(u, "epidemic", len(victims))
            events.append((day, "LAGOON", "epidemic",
                           f"Year {year}: a sickness born of the herds kills {len(victims)} "
                           f"({int(kill*100)}% of the people)."))
            tell_myth(u, "epidemic", events, day)

        pop = len(people)
        adults = [p for p in people if ADULT_AGE <= age_of(p, day) < ELDER_AGE]
        daily_need = sum(0.6 if age_of(p, day) < ADULT_AGE else
                         0.8 if age_of(p, day) >= ELDER_AGE else 1.0 for p in people)
        # technology: discovery odds scale with living population
        for name, prereq, base, min_pop in TECH_LADDER:
            if has(u, name) or pop < min_pop:
                continue
            if prereq and not has(u, prereq):
                continue
            # Invention needs people with the self-control to plan, and the
            # leisure and company to try (BOOKS.md: Pinker ch.3; Diamond ch.13)
            tail = sum(1 for q in adults if q.get("ef", 0.5) > 0.6) / max(1, len(adults))
            p_disc = (base * min(2.5, math.log(max(2, pop), 8))
                      * (0.5 + 2.0 * tail)
                      * (1.0 + min(0.5, u.get("scouted", 0) / 2000.0)))
            for lesson in u["lessons"]:
                if name in LESSON_TECH.get(lesson, ()):
                    p_disc *= 3.0  # inherited wisdom from a dead iteration
            if name == "lore":
                p_disc *= min(3.0, 0.2 + u.get("stories", 0.0) / 40.0)
            if name == "agriculture" and shortfall == 0 and pop < 140:
                p_disc *= 0.3  # agriculture is born of pressure, not comfort
            if rng.random() < p_disc:
                u["tech"].append(name)
                pick = rng.sample(adults, min(5, len(adults))) if adults else []
                discoverer = (max(pick, key=lambda q: q.get("ef", 0.5))["n"]
                              if pick else "someone")
                events.append((day, "LAGOON", "discovery",
                               f"Year {year}: {TECH_LABEL[name]} — first by {discoverer}."))
                if name == "agriculture":
                    st = u["settlements"][0]
                    for _ in range(6):
                        till_near(u, rng, st, 7)
                break  # at most one discovery a year

        # Crowding, not chance, puts people in boats. When the island holds
        # more than it comfortably feeds, the people who can plan start a
        # boat at the shore; when it is built, a party of young families
        # sails for the greater land (BOOKS.md; Diamond on Austronesian and
        # Polynesian expansion).
        crowd = pop / ISLAND_CAP
        if (not u.get("continent") and crowd > 0.85 and has(u, "fishing")
                and has(u, "shelter") and "boat" not in u):
            st0 = u["settlements"][0]
            spot = None
            for dy in range(0, 30):
                for yy in (st0["y"] + dy, st0["y"] - dy):
                    if 40 <= yy < LAGOON_SIZE - 40 and boatyard(u, yy):
                        spot = (boatyard(u, yy)[0], yy)
                        break
                if spot:
                    break
            if spot:
                u["boat"] = {"x": spot[0], "y": spot[1], "work": 0}
                events.append((day, "LAGOON", "discovery",
                               f"Year {year}: the island is full. {st0.get('n', 'The camp')} "
                               f"starts a boat at the shore."))
        boat = u.get("boat")
        if boat and boat["work"] >= BOAT_WORK and "voyage" not in u:
            del u["boat"]
            if not has(u, "seacraft"):
                u["tech"].append("seacraft")
            launch(u, people, boat, rng, events, day, year)

        # full bellies and long evenings: surplus turns into art and pleasure
        if (has(u, "lore") and u["store"] > daily_need * 20 and adults
                and len(u.get("culture", [])) < len(ARTS)
                and rng.random() < 0.2):
            art = next(a for a in ARTS if a not in u["culture"])
            u.setdefault("meat", 0.0)
            u.setdefault("kills", 0)
            u.setdefault("culture", []).append(art)
            maker = rng.choice(adults)["n"]
            events.append((day, "LAGOON", "culture",
                           f"Year {year}: with food enough and nothing to fear, "
                           f"{art} {culture_verb(art)} — "
                           f"first made by {maker}."))

        if has(u, "agriculture") and len(u["farms"]) < pop // 3:
            till_near(u, rng, rng.choice(u["settlements"]), 8)

        # Dunbar / fission: settlements over their social limit split
        limit = 500 if has(u, "granary") else 220 if has(u, "lore") else 80
        counts = {}
        for p in people:
            counts[p.get("st", 0)] = counts.get(p.get("st", 0), 0) + 1
        for si, n in list(counts.items()):
            st = u["settlements"][min(si, len(u["settlements"]) - 1)]
            st["r"] = max(5, int(4 + math.sqrt(n) * 1.3))
            if n > limit and len(u["settlements"]) < 12:
                terr = terrain_of(u)
                nx = ny = None
                crossing = False          # the strait is crossed only by boat (launch)
                if crossing:
                    # the boats cross the strait to the greater land
                    for _ in range(40):
                        ty = rng.randrange(40, LAGOON_SIZE - 40)
                        tx = rng.randrange(8, 30)
                        if terr[ty][tx] != 2:
                            nx, ny = tx, ty
                            break
                if nx is None:
                    crossing = False
                    for _ in range(12):  # find dry ground for the new camp
                        ang = rng.uniform(0, 2 * math.pi)
                        dist = rng.uniform(12, 24)
                        tx = int(min(LAGOON_SIZE - 6, max(5, st["x"] + math.cos(ang) * dist)))
                        ty = int(min(LAGOON_SIZE - 6, max(5, st["y"] + math.sin(ang) * dist)))
                        if terr[ty][tx] != 2:
                            nx, ny = tx, ty
                            break
                if nx is None:
                    continue
                tribe = make_name(rng, minds.NAMES.get("LAGOON"))
                u["settlements"].append({"x": nx, "y": ny, "r": 5, "n": tribe})
                new_i = len(u["settlements"]) - 1
                movers = [p for p in people if p.get("st", 0) == si]
                rng.shuffle(movers)
                for p in movers[: int(n * 0.4)]:
                    p["st"] = new_i
                    p["x"], p["y"] = nx, ny
                    p["hx"] = nx + rng.randint(-2, 2)   # new hearths
                    p["hy"] = ny + rng.randint(-2, 2)
                    p["tx"], p["ty"], p["ad"] = p["hx"], p["hy"], 0
                old_tribe = st.get("n", "the old camp")
                if crossing:
                    u["continent"] = True
                    events.append((day, "LAGOON", "migration",
                                   f"Year {year}: the boats cross the strait. The {tribe} tribe "
                                   f"lands on the greater shore — a land without end, the one "
                                   f"all their children's children will call home."))
                elif has(u, "lore"):
                    events.append((day, "LAGOON", "migration",
                                   f"Year {year}: a band leaves {old_tribe} in peace and founds "
                                   f"the {tribe} tribe."))
                else:
                    losses = rng.sample(movers, min(len(movers), max(1, n // 40)))
                    remove_dead(u, losses)
                    u["deaths_y"] += len(losses)
                    cod(u, "feud", len(losses))
                    events.append((day, "LAGOON", "feud",
                                   f"Year {year}: too many strangers, no shared story — a feud splits "
                                   f"{old_tribe}; {len(losses)} die, the rest walk away and become "
                                   f"the {tribe} tribe."))
        # survivors of a near-wipe pass the fear down without words —
        # instinct, not writing, is the first archive
        for cause, n in u["cod_y"].items():
            if n > max(2, 0.1 * max(1, pop)):
                tell_myth(u, cause, events, day)
            lesson = LESSON_OF.get(cause)
            if (lesson and lesson not in u["lessons"]
                    and n > max(2, 0.2 * max(1, pop))):
                u["lessons"].append(lesson)
                events.append((day, "LAGOON", "lesson",
                               f"Year {year}: {cause} took {n} of them. The survivors carry a "
                               f"new instinct — '{lesson}' — passed on without a single word."))
        u["cod_y"] = {}
        organise(u, people, rng, events)
        if not u["innocent"]:
            # having learned what bodies are for, they begin to cover them
            # (Peterson on Genesis 3: covering as the first cultural act)
            u["modesty"] = min(0.85, u.get("modesty", 0.0) + 0.04)
        record_mind(u)
        record_census(u)
        u["births_y"] = u["deaths_y"] = 0

    u["store"] = sum(st.get("store", 0.0) for st in u.get("settlements", []))
    stocks["game"], stocks["pred"] = (float(n) for n in animals.counts(u))
    for kind in ("plants", "fish"):
        stocks[kind] = sum(site["left"] for site in u.get("sites", []) if site["kind"] == kind)
    if not people:
        record_extinction(u, events)
    advance_part(u)


# ---------------------------------------------------------------- top level

def tick_world(world, events):
    """Advance both universes one part of a day.

    Deterministic per (seed, day, part) within one engine version. A day is four
    parts — dawn, day, dusk, night — and the day's counter turns when the
    night ends.
    """
    for key in ("eden", "lagoon"):
        u = world[key]
        if u.get("engine") != ENGINE_VERSION:
            u.setdefault("engine_history", []).append(
                {"from": u.get("engine", "unknown"), "to": ENGINE_VERSION,
                 "day": u["day"], "part": u.get("part", 0)})
            u["engine"] = ENGINE_VERSION
        part = u.get("part", 0)
        rng = random.Random((u["seed"] << 20) ^ (u["day"] + 1) ^ u["iteration"]
                            ^ (part * 7919))
        (tick_eden if u["kind"] == "EDEN" else tick_lagoon)(u, rng, events)


def advance_part(u):
    """Turn the clock one part. Returns the part that was just lived."""
    part = u.get("part", 0)
    u["parts"] = u.get("parts", 0) + 1
    if part >= PARTS_PER_DAY - 1:
        u["part"] = 0
        u["day"] = u.get("day", 0) + 1
    else:
        u["part"] = part + 1
    return part


def target_parts(world, now=None):
    """Cumulative ticks due, anchored independently of the calendar/reseeds."""
    c = world["clock"]
    now = time.time() if now is None else now
    return int(c["parts"] + (now - c["epoch"]) / c["seconds"])


def set_clock_pace(world, seconds, now=None):
    """Change pace without replaying elapsed history or losing pending ticks."""
    if seconds <= 0 or not math.isfinite(seconds):
        raise ValueError("seconds per part must be positive and finite")
    now = time.time() if now is None else now
    c = world["clock"]
    if c["seconds"] != seconds:
        pending = c["parts"] + (now - c["epoch"]) / c["seconds"]
        world["clock"] = {"epoch": now, "parts": pending, "seconds": seconds}
    world["sec_per_day"] = seconds * PARTS_PER_DAY


# Detail flags — what the viewer needs to say about one person.
F_WITHDRAWN = 1     # one of the beautiful ones: never pairs, never works
F_INCOMPETENT = 2   # born into the sink, cannot learn the roles
F_PREGNANT = 4
F_MOTHER = 8        # has an infant
F_HOMELESS = 16     # no nest box: no territory, no role
F_HUNGRY = 32
F_ELDER = 64


def person_detail(u, p, day, ctx):
    """Everything the viewer needs to say *who* this is and *what they are doing*.

    The renderer draws a person as a handful of pixels; without this it can
    only show anonymous dots. The record of what actually happened to these
    people is the point of the experiment, so it has to reach the screen.
    """
    a = age_of(p, day)
    flags = 0
    if p["w"]:
        flags |= F_WITHDRAWN
    if not p["c"]:
        flags |= F_INCOMPETENT
    if p.get("due"):
        flags |= F_PREGNANT
    if p["id"] in ctx["moms"]:
        flags |= F_MOTHER
    if u["kind"] == "EDEN":
        b = p.get("box")
        if b is None or b < 0:
            flags |= F_HOMELESS
    if p.get("hun", 0) > 25:
        flags |= F_HUNGRY
    if a >= ELDER_AGE:
        flags |= F_ELDER
    return [p["n"], round(a / DAYS_PER_YEAR, 1), p["g"], flags,
            p.get("hx", p["x"]), p.get("hy", p["y"]),
            p.get("p") or 0, round(p.get("hun", 0.0), 1),
            minds.body_words(p, a), round(p.get("pu", 0.5), 2),
            round(p.get("ef", 0.5), 2), round(minds.aggression(p), 2),
            round(p.get("bmi", 22.0), 1)]


def summarize(world):
    """Compact snapshot for the renderer / web mirror."""
    out = {"wall": time.time(), "sec_per_day": world["sec_per_day"],
           "engine": ENGINE_VERSION, "u": {}}
    seconds = (world.get("clock") or {}).get("seconds", world["sec_per_day"] / PARTS_PER_DAY)
    out["pace"] = {"seconds_per_part": seconds,
                   "years_per_real_day": 86400.0 / (seconds * PARTS_PER_DAY * DAYS_PER_YEAR)}
    for key in ("eden", "lagoon"):
        u = world[key]
        day = u["day"]
        ppl = []
        detail = {}
        ctx = u.get("_ctx") or {"moms": {}}
        for p in u["people"][:2400]:
            a = age_of(p, day)
            cls = (0 if a < ADULT_AGE else
                   4 if p["w"] else
                   3 if a >= ELDER_AGE else
                   1 if p["s"] == "m" else 2)
            # 0-6 as before; then what the body looks like: age in years,
            # BMI, strength and injury in tenths, and the withdrawn kind
            ppl.append([p["x"], p["y"], cls, 1 if p["s"] == "f" else 0,
                        p["id"], p.get("a", 0), p.get("f", 1),
                        a // DAYS_PER_YEAR, int(round(p.get("bmi", 22.0))),
                        min(9, int(p.get("sn", 0.5) * 10)),
                        min(9, int(p.get("inj", 0.0) * 10)), p.get("wk", 0),
                        # 12: carrying food home (0 none, 1 a load, 2 a carcass)
                        0 if p.get("carry", 0.0) <= 0 else 2 if p.get("carry_kind") in ("deer", "cat") else 1,
                        # 13: hunger in tenths of the way to starving
                        min(9, int(p.get("hun", 0.0) / needs.HUNGER_MAX * 10))])
            detail[str(p["id"])] = person_detail(u, p, day, ctx)
        # u.part is the next tick. Show the light of the activity we just
        # simulated, so a night on watch is seen at night rather than dawn.
        part = (u.get("part", 0) - 1) % PARTS_PER_DAY if u.get("parts", 0) else 0
        info = {"day": day, "year": day // DAYS_PER_YEAR, "pop": len(u["people"]),
                "part": part, "tod": PART_NAMES[part % len(PART_NAMES)],
                "night": part == PART_NIGHT,
                "gen": u["gen_max"], "peak": u["peak"], "phase": u["phase"],
                "iter": u["iteration"], "people": ppl, "detail": detail,
                "cod": dict(u.get("cod", {})),
                "phases": u.get("phases", []),
                "census": u["census"][-120:],
                "gauges": gauges(u),
                "modesty": round(u.get("modesty", 0.0), 3),
                "innocent": bool(u.get("innocent")),
                "named": bool(u.get("named")),
                "mind": u.get("mind", [])[-120:],
                "engine": u.get("engine", ENGINE_VERSION)}
        if u["kind"] == "LAGOON":
            info["tech"] = u["tech"]
            info["settlements"] = u["settlements"]
            info["farms"] = u["farms"]
            info["store"] = round(u["store"], 1)
            # the places that hold food, and how full: what the canvas may
            # draw because the model has it (handoff N3)
            info["sites"] = [{"x": q["x"], "y": q["y"], "k": q["kind"],
                              "f": round(q["left"] / max(1.0, q["max"]), 2)}
                             for q in u.get("sites") or []]
            info["lessons"] = u.get("lessons", [])
            info["culture"] = u.get("culture", [])
            info["boats"] = u.get("boats", [])
            deer, cats = animals.counts(u)
            info["game"], info["pred"] = deer, cats
            # every animal where it is: the canvas draws only what the model has
            info["animals"] = [[q["x"], q["y"], q["k"], q["i"]] for q in u.get("animals") or []]
            # what just happened between people and animals: [x, y, kind, day, part]
            # kind: deer_kill, cat_hunt, fought_off, taken, mauled
            info["encounters"] = [e for e in u.get("encounters") or [] if u["day"] - e[3] <= 3]
            # each pair's hut: [x, y, share of the work done 0..1]
            info["huts"] = [[h["x"], h["y"], round(min(1.0, h["w"] / needs.HUT_WORK), 2)]
                            for st in u["settlements"] for h in st.get("huts") or ()]
            info["myths"] = u.get("myths", [])
            info["stories"] = round(u.get("stories", 0.0), 1)
            info["kills"] = u.get("kills", 0)
            info["boat"] = u.get("boat")
            v = u.get("voyage")
            if v:
                t = min(1.0, (day - v["d0"]) / v["days"])
                info["voyage"] = {"x": round(v["x0"] + (v["x1"] - v["x0"]) * t, 2),
                                  "y": v["y"], "n": v["n"]}
            d = day % DAYS_PER_YEAR
            info["climate"] = "tropical" if u.get("terrain_version", 1) >= 2 else "legacy"
            info["season"] = (("monsoon" if 90 <= d < 180 or 270 <= d < 330 else "dry season")
                              if info["climate"] == "tropical" else
                              "winter" if 240 <= d < 330 else
                              "summer" if 60 <= d < 150 else
                              "autumn" if 150 <= d < 240 else "spring")
            info["thirst"] = {str(p["id"]): round(p.get("thirst", 0.0), 2) for p in u["people"]}
            info["water"] = round(sum(st.get("water", 0.0) for st in u["settlements"]), 1)
            info["harsh"] = bool(u.get("harsh_winter"))
            info["dry"] = u.get("drought", 0) > 0
            info["phase"] = ("innocence" if u.get("innocent") else
                             u["tech"][-1] if u["tech"] else "foragers")
        else:
            info["ennui"] = round(u.get("ennui", 0.0), 3)
            info["size"] = eden_size(u)
            roles = u.get("roles", [])
            info["roles"] = [sum(1 for r in roles if r["who"]), len(roles)]
            info["posts"] = [[r["x"], r["y"], r["k"]] for r in roles]
            info["std"] = u.get("std_years", 0) > 0
            hop = u.get("hop_n") or [0, 0, 0, 0]
            tot = sum(hop)
            info["sink"] = round(100.0 * max(hop) / tot) if tot else 0
            info["homeless"] = sum(
                1 for q in u["people"]
                if (q.get("box") is None or q["box"] < 0) and not q["w"]
                and age_of(q, day) >= ADULT_AGE)
            info["boxes"] = len(eden_design(u)["boxes"])
            design = eden_design(u)
            info["cap"] = design["cap"]
            info["stagnation"] = design["stagnation"]
            info["box_cap"] = design["box_cap"]
            info["box_slots"] = len(design["boxes"]) * design["box_cap"]
            # the pen's architecture and who holds what, so the viewer can
            # show territory rather than only counting it
            info["boxes_xy"] = [[x, y] for x, y in design["boxes"]]
            info["box_occ"] = {k: v for k, v in u.get("box_occ", {}).items()}
            occ = info["box_occ"]
            info["box_free"] = sum(max(0, design["box_cap"] - occ.get(str(i), 0))
                                   for i in range(len(design["boxes"])))
            info["box_vacant"] = sum(1 for i in range(len(design["boxes"]))
                                     if occ.get(str(i), 0) == 0)
        out["u"][key] = info
    out["calhoun"] = {
        "census": [[d, p, n] for d, p, n in CALHOUN_CENSUS],
        "census_fields": list(CENSUS_FIELDS),
        "events": [[d, n] for d, n in CALHOUN_EVENTS],
        "phases": [[a, b, c, nm] for a, b, c, nm in CALHOUN_PHASES],
        "series": CALHOUN_SERIES,
        "source": "Calhoun 1973, Proc. Roy. Soc. Med. 66(1 Pt 2):80-88",
    }
    out["recorded"] = load_recorded_arcs()
    return out


def load_recorded_arcs():
    """Arcs of experiments we ran ourselves and recorded, so the viewer can
    put them beside the live run. Kept beside the engine because they are
    only meaningful next to the version that produced them."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "recorded-arcs.json")
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


# ---------------------------------------------------------------- persistence

def save_state(world, path):
    tmp = path + ".tmp"
    slim = {k: ({kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                if isinstance(v, dict) else v)
            for k, v in world.items()}
    with open(tmp, "w") as f:
        json.dump(slim, f, separators=(",", ":"))
    os.replace(tmp, path)


def load_state(path):
    with open(path) as f:
        world = json.load(f)
    return migrate(world)


def migrate(world):
    """Bring a saved world up to the current schema. The universes have been
    running since before some fields existed; they must not die of it."""
    old_day = (world.get("eden") or {}).get("day", 0)
    old_seconds = world.get("sec_per_day", SEC_PER_DAY)
    world.setdefault("clock", {"epoch": world.get("epoch", time.time()) + old_day * old_seconds,
                               "parts": old_day * PARTS_PER_DAY,
                               "seconds": SEC_PER_PART})
    world["sec_per_day"] = world["clock"]["seconds"] * PARTS_PER_DAY
    for key in ("eden", "lagoon"):
        u = world.get(key)
        if not u:
            continue
        u.setdefault("cod", {})
        u.setdefault("cod_y", {})
        u.setdefault("viol_y", 0)
        u.setdefault("postmortems", [])
        u.setdefault("lessons", [])
        u.setdefault("phases", [[0, u.get("phase", "strive")]])
        u.setdefault("engine", ENGINE_VERSION)
        # a day is four parts now; a run that predates that has no part of
        # the day to speak of yet, so it starts at dawn
        u.setdefault("part", 0)
        u.setdefault("parts", u.get("day", 0) * PARTS_PER_DAY + u["part"])
        u.setdefault("engine_history", [])
        u.setdefault("founded_day", 0)
        # a run that predates the shared founders has long since stopped
        # being innocent, and keeps its own seed for any reseed
        u.setdefault("innocent", False)
        u.setdefault("modesty", 0.0)
        u.setdefault("mind", [])
        u.setdefault("fseed", u.get("seed", 69))
        u.setdefault("names", u.get("kind"))
        u.setdefault("named", any(p.get("g", 1) > 1 for p in u.get("people", [])) or u.get("gen_max", 1) > 1)
        u.setdefault("sites", [])
        if u.get("kind") == "LAGOON":
            u.setdefault("terrain_version", 1)
            u.setdefault("meat", 0.0)
            u.setdefault("kills", 0)
            u.setdefault("culture", [])
            u.setdefault("continent", False)
        else:
            u.setdefault("ennui", 0.0)
            u.setdefault("std_years", 0)
            u.setdefault("wary_years", 0)
        if u.get("kind") == "EDEN":
            u.setdefault("box_occ", {})
            u.setdefault("hop_n", [1, 1, 1, 1])
            u.setdefault("sink", 0)
            # the pen's architecture: a live world carries the pen it was
            # already running, and a study can carry a different one
            u.setdefault("cap", EDEN_CAP)
            u.setdefault("stagnation", EDEN_STAGNATION)
            u.setdefault("box_cap", EDEN_BOX_CAP)
        if u.get("kind") == "LAGOON":
            sts = u.get("settlements", [])
            if sts and all("store" not in st for st in sts):
                # Existing pooled food is redistributed once, never discarded
                # or copied into every camp on every restart.
                counts = [sum(p.get("st", 0) == i for p in u.get("people", []))
                          for i in range(len(sts))]
                if not sum(counts):
                    counts = [1] * len(sts)
                remaining = u.get("store", 0.0)
                for i, st in enumerate(sts):
                    st["store"] = (remaining if i == len(sts) - 1 else
                                   u.get("store", 0.0) * counts[i] / sum(counts))
                    remaining -= st["store"]
            for st in sts:
                st.setdefault("store", 0.0)
                st.setdefault("water", 0.0)
            u.setdefault("animals", None)     # None: animals.ensure seeds them on the next tick
            u.setdefault("animal_id", max((a["i"] for a in u.get("animals") or []), default=0) + 1)
            u.setdefault("encounters", [])
            for st in u.get("settlements", []):
                st.setdefault("huts", [])     # each pair's hut, raised by work
        for site in u.get("sites") or []:
            if site.get("kind") == "farm":
                site.setdefault("worked", None)
        for p in u.get("people", []):
            p.setdefault("a", 0)
            p.setdefault("ad", 0)
            p.setdefault("hun", 0.0)
            p.setdefault("thirst", 0.0)
            p.setdefault("carry_water", 0.0)
            p.setdefault("experience", {"sites": [], "trail": []})
            p.setdefault("ene", 1.0)          # the personal meters (needs.py)
            p.setdefault("sol", 0.7)
            p.setdefault("carry", 0.0)
            p.setdefault("carry_kind", None)
            p.setdefault("site", None)
            p.setdefault("day_done", None)
            p.setdefault("slept", 0)
            p.setdefault("was", None)
            p.setdefault("detour", 0)
            if isinstance(p.get("site"), tuple):
                p["site"] = list(p["site"])
            p.setdefault("tx", p["x"])
            p.setdefault("ty", p["y"])
            p.setdefault("hx", p["x"])
            p.setdefault("hy", p["y"])
            p.setdefault("f", 1)
            p.setdefault("mom", None)
            for k, v in (("ef", 0.5), ("ag", 0.5), ("vg", 0.5), ("pu", 0.5), ("bmi", 22.0),
                         ("sn", 0.5), ("inj", 0.0), ("gd", 0.0), ("gk", 0), ("fe", None)):
                p.setdefault(k, v)
            p.setdefault("wk", (WK_UPSTAIRS if p["s"] == "f" else WK_BEAUTIFUL) if p.get("w") else 0)
            if u.get("kind") == "EDEN":
                p.setdefault("box", None)   # claims a nest box on next move
        if u.get("kind") == "LAGOON":
            needs.reconcile_sites(u)
        byid = {p["id"]: p for p in u.get("people", [])}
        for p in byid.values():
            partner = byid.get(p.get("p"))
            if p.get("p") is not None and (partner is None or partner.get("p") != p["id"]):
                p["p"] = None
        if u["kind"] == "EDEN":
            # Repair legacy ghost claims as well as future deaths. Preserve
            # zero keys so already-valid JSON remains stable on reload.
            occ = {key: 0 for key in u.get("box_occ", {})}
            for p in byid.values():
                box = p.get("box")
                if box is not None and box >= 0:
                    key = str(box)
                    occ[key] = occ.get(key, 0) + 1
            u["box_occ"] = occ
            roles = u.get("roles", [])
            for role in roles:
                if role.get("who") and role["who"] not in byid:
                    role["who"] = 0
            for p in byid.values():
                role = p.get("role")
                if role is not None and (not 0 <= role < len(roles) or roles[role]["who"] != p["id"]):
                    p["role"] = None
    # the record of what the literature's hypotheses have been measured
    # against, in this world, so far. A run that predates the research
    # layer simply has no verdicts yet.
    world.setdefault("research", {"tested": 0, "h": {}})
    return world
