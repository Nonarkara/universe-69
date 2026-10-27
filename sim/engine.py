"""UNIVERSE 69 — simulation engine.

Two universes, one tick function each. 1 tick = 1 simulated day.
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

DAYS_PER_YEAR = 360
ADULT_AGE = 16 * DAYS_PER_YEAR
ELDER_AGE = 58 * DAYS_PER_YEAR
GESTATION = 270

EDEN_SIZE = 48
EDEN_CAP = 900          # nominal capacity of the pen
EDEN_STAGNATION = 0.35  # crowding level where the behavioral sink begins
EDEN_BOX_CAP = 7        # how many may share one nest box

LAGOON_SIZE = 160   # an island off the coast of a greater land
RESEED_YEARS = 30       # quiet years before the Observers reseed (Ice Age cycle)

SYLLABLES = ["ka", "ra", "no", "ta", "mi", "lu", "se", "an", "ko", "ri",
             "ve", "sha", "on", "ba", "ni", "tu", "ma", "ilo", "ess", "ur"]

TECH_LADDER = [
    # name, prerequisite, base chance per year, min population
    ("fire",          None,            0.50,  2),
    ("stone_tools",   None,            0.40,  2),
    ("fishing",       "stone_tools",   0.35,  6),
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

TECH_LABEL = {
    "fire": "fire is tamed", "stone_tools": "stone tools are knapped",
    "fishing": "fishing is learned", "shelter": "shelters are raised",
    "preservation": "food can be kept", "lore": "shared stories bind the bands",
    "agriculture": "seeds are sown on purpose", "domestication": "animals are tamed",
    "granary": "granaries hold the surplus",
    "seacraft": "boats brave the open water", "healing": "healing lore spreads",
    "metallurgy": "metal is smelted", "writing": "marks begin to remember",
}


def make_name(rng):
    n = rng.choice([2, 2, 3])
    return "".join(rng.choice(SYLLABLES) for _ in range(n)).capitalize()


def person(uid, name, sex, born, gen, x, y, competent=True):
    return {"id": uid, "n": name, "s": sex, "b": born, "g": gen,
            "p": None, "x": x, "y": y, "c": competent, "w": False,
            "due": 0, "hun": 0.0,
            "a": 0, "tx": x, "ty": y, "ad": 0,   # activity, target, days left
            "hx": x, "hy": y}                    # home: the place they return to


# Activity codes — shared verbatim with the renderer.
(A_IDLE, A_WALK, A_FORAGE, A_HUNT, A_FISH, A_FARM, A_BUILD, A_TALK,
 A_MATE, A_BIRTH, A_TEND, A_REST, A_EAT, A_WITHDRAW, A_FIGHT) = range(15)


def age_of(p, day):
    return day - p["b"]


# ---------------------------------------------------------------- world gen

def make_lagoon_terrain(seed):
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
    return t


LESSON_OF = {"starvation": "preserve", "predator": "vigilance",
             "epidemic": "cleanliness", "feud": "unity"}
LESSON_TECH = {"preserve": ("preservation", "fishing"),
               "vigilance": ("stone_tools",), "unity": ("lore",)}


def genesis_universe(kind, seed, iteration=1, postmortems=None, lessons=None):
    rng = random.Random(seed)
    u = {"kind": kind, "seed": seed, "iteration": iteration, "day": 0,
         "people": [], "next_id": 1, "gen_max": 1, "phase": "strive",
         "peak": 0, "births_y": 0, "deaths_y": 0, "bad_years": 0,
         "extinct_day": None, "census": [], "year_flags": {},
         "cod": {}, "cod_y": {}, "postmortems": postmortems or [],
         "lessons": lessons or []}
    if kind == "EDEN":
        u["ennui"] = 0.0      # hedonic adaptation: easy pleasure dulls appetite
        u["std_years"] = 0    # years an STD outbreak has left to run
        u["wary_years"] = 0   # post-outbreak generation keeps its distance
        cx = EDEN_SIZE // 2
        spots = [(cx - 2, cx), (cx - 2, cx + 1), (cx + 2, cx), (cx + 2, cx + 1)]
    else:
        u["terrain_seed"] = seed
        # sized as a *territory*, not a garden: max sustainable yield is
        # r*K/4 — plants alone sustain ~50-70 foragers, fish (with the
        # technology to take them) roughly as many again
        u["stocks"] = {"plants": 60000.0, "game": 2500.0,
                       "fish": 50000.0, "pred": 48.0}
        u["tech"] = []
        u["store"] = 0.0
        u["farms"] = []            # [x, y] tilled tiles
        u["settlements"] = [{"x": 137, "y": 109, "r": 5, "n": make_name(rng)}]
        u["innocent"] = True       # Blue Lagoon: reproduction not yet discovered
        u["culture"] = []          # arts appear when bellies stay full
        u["continent"] = False     # the greater land, waiting across the strait
        u["drought"] = 0           # years remaining
        u["harsh_winter"] = False
        spots = [(136, 108), (137, 108), (137, 110), (138, 109)]
    for i, (x, y) in enumerate(spots):
        sex = "m" if i % 2 == 0 else "f"
        name = f"E-{u['next_id']:04d}" if kind == "EDEN" else make_name(rng)
        p = person(u["next_id"], name, sex, -18 * DAYS_PER_YEAR, 1, x, y)
        if kind == "LAGOON":
            p["st"] = 0
        u["people"].append(p)
        u["next_id"] += 1
    # found the two pairs
    u["people"][0]["p"] = u["people"][1]["id"]
    u["people"][1]["p"] = u["people"][0]["id"]
    u["people"][2]["p"] = u["people"][3]["id"]
    u["people"][3]["p"] = u["people"][2]["id"]
    return u


def genesis(seed=69):
    return {"epoch": time.time(), "sec_per_day": 2.0, "seed": seed,
            "eden": genesis_universe("EDEN", seed * 7 + 6),
            "lagoon": genesis_universe("LAGOON", seed * 7 + 9)}


# ---------------------------------------------------------------- shared

def cod(u, cause, n=1):
    u["cod"][cause] = u["cod"].get(cause, 0) + n
    u["cod_y"][cause] = u["cod_y"].get(cause, 0) + n


def write_postmortem(u, events):
    """On extinction: record what happened, how, and the dominant cause.
    The next iteration of LAGOON inherits a lesson; EDEN, by design, cannot
    learn its way out — the pen itself is the cause (Calhoun's conclusion)."""
    total = sum(u["cod"].values()) or 1
    dominant = max(u["cod"], key=u["cod"].get) if u["cod"] else "unknown"
    pm = {"iteration": u["iteration"], "day": u["day"], "peak": u["peak"],
          "gen_max": u["gen_max"], "cod": dict(u["cod"]),
          "dominant_cause": dominant,
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


def try_conceive(u, rng, females, p_daily, require_pair=True):
    """Reproduction is free and pedestrian — until the world makes it not so.
    EDEN mates without pair-bonds (require_pair=False); LAGOON pairs up."""
    day = u["day"]
    for p in females:
        if p["s"] != "f" or p["due"] or p["w"]:
            continue
        if require_pair and p["p"] is None:
            continue
        a = age_of(p, day)
        if not (ADULT_AGE <= a <= 45 * DAYS_PER_YEAR):
            continue
        if rng.random() < p_daily:
            p["due"] = day + GESTATION


def clear_widows(people, dead):
    dead_ids = {p["id"] for p in dead}
    for p in people:
        if p["p"] in dead_ids:
            p["p"] = None


def pair_singles(u, rng, adults):
    singles_m = [p for p in adults if p["s"] == "m" and p["p"] is None and not p["w"]]
    singles_f = [p for p in adults if p["s"] == "f" and p["p"] is None and not p["w"]]
    rng.shuffle(singles_m)
    rng.shuffle(singles_f)
    for m, f in zip(singles_m, singles_f):
        m["p"], f["p"] = f["id"], m["id"]


def record_census(u):
    year = u["day"] // DAYS_PER_YEAR
    u["census"].append([year, len(u["people"]), u["births_y"], u["deaths_y"]])
    if len(u["census"]) > 400:
        u["census"] = u["census"][-400:]


# ---------------------------------------------------------------- EDEN

EDEN_HOPPERS = [(8, 8), (EDEN_SIZE - 10, 8),
                (8, EDEN_SIZE - 10), (EDEN_SIZE - 10, EDEN_SIZE - 10)]

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
        # the beautiful ones keep to a quiet box and never come down
        i = p["id"] % len(boxes)
        p["hx"], p["hy"] = boxes[i]
        return
    order = list(range(len(boxes)))
    rng.shuffle(order)
    cap = eden_design(u)["box_cap"]
    for i in order:
        if occ.get(str(i), 0) < cap:
            occ[str(i)] = occ.get(str(i), 0) + 1
            p["box"] = i
            p["hx"], p["hy"] = boxes[i]
            return
    p["box"] = -1                                   # no territory, no role
    c = EDEN_SIZE // 2
    p["hx"] = c + rng.randint(-7, 7)
    p["hy"] = c + rng.randint(-7, 7)


def eden_assign(u, p, day, rng, crowd):
    """Nothing in the pen must be worked for, so a day holds only food,
    company, sex, and — once the sink forms — violence and withdrawal."""
    a = age_of(p, day)
    if "hx" not in p or p.get("box") is None:
        eden_claim_home(u, p, rng)

    def home_spot(r=2):
        return (min(EDEN_SIZE - 3, max(2, p["hx"] + rng.randint(-r, r))),
                min(EDEN_SIZE - 3, max(2, p["hy"] + rng.randint(-r, r))))

    if p["w"]:          # withdrawn: eat, sleep, groom, and nothing else
        p["a"] = A_WITHDRAW if rng.random() < 0.7 else A_EAT
        p["ad"] = rng.randint(6, 16)
        p["tx"], p["ty"] = (home_spot(1) if p["a"] == A_WITHDRAW
                            else eden_feed_spot(u, rng))
        return
    if p["due"] and p["due"] - day <= 0:
        p["a"], p["ad"] = A_BIRTH, 2
        p["tx"], p["ty"] = home_spot(0)
        return
    def clamp(x, y):
        return (min(EDEN_SIZE - 3, max(2, x)), min(EDEN_SIZE - 3, max(2, y)))

    if a < ADULT_AGE:
        if a < 3 * DAYS_PER_YEAR:                    # infants: on the mother
            p["a"], p["ad"] = A_TEND, 3
            p["tx"], p["ty"] = home_spot(1)
        elif a < 12 * DAYS_PER_YEAR:                 # children play in packs
            play_with(u, p, kids_near(u["_ctx"], p), rng, clamp)
        else:                                        # adolescents eat and loiter
            p["a"] = A_EAT if rng.random() < 0.5 else A_TALK
            p["ad"] = rng.randint(3, 8)
            if p["a"] == A_EAT:
                p["tx"], p["ty"] = eden_feed_spot(u, rng)
            else:
                join_circle(u, p, *home_spot(3))
                p["tx"], p["ty"] = clamp(p["tx"], p["ty"])
        return

    homeless = (p.get("box") is None) or p["box"] < 0
    ctx = u["_ctx"]
    w = [(A_EAT, 3.2), (A_TALK, 2.4), (A_REST, 1.8)]
    if a <= 45 * DAYS_PER_YEAR:
        # mating in the pen is free of bonds; anyone nearby will do
        w.append((A_MATE, 2.5 * max(0.2, 1.0 - u.get("ennui", 0.0))))
    if p["s"] == "m" and u["phase"] in ("stagnate", "death"):
        # the dispossessed are the violent ones; those with territory defend it
        w.append((A_FIGHT, (4.5 if homeless else 1.2) * (0.5 + crowd)))
    if p["id"] in ctx["moms"]:
        w.append((A_TEND, 2.5))                      # a mother with an infant

    act = _weighted(w, rng)
    p["a"] = act
    p["ad"] = rng.randint(3, 8)
    if act == A_EAT:
        p["tx"], p["ty"] = eden_feed_spot(u, rng)
    elif act == A_MATE:
        pool = ctx["af"] if p["s"] == "m" else ctx["am"]
        near = [q for q in pool if q is not p and q.get("a") != A_MATE
                and abs(q["x"] - p["x"]) <= 6 and abs(q["y"] - p["y"]) <= 6]
        if near:
            q = rng.choice(near)
            couple_up(p, q, *clamp(q["x"], q["y"]))
        else:
            p["a"], (p["tx"], p["ty"]) = A_REST, home_spot(2)
    elif act == A_FIGHT:
        if not pick_fight(u, p, u["people"], rng):
            # nobody near: drift to where the crowd is and brood
            hx, hy = EDEN_HOPPERS[u.get("sink", 0)]
            p["a"] = A_REST
            p["tx"], p["ty"] = clamp(hx + rng.randint(-3, 4), hy + rng.randint(-3, 4))
    elif act == A_TALK:
        cx, cy = home_spot(3 if not homeless else 6)
        join_circle(u, p, cx, cy)
        p["tx"], p["ty"] = clamp(p["tx"], p["ty"])
    else:
        p["tx"], p["ty"] = home_spot(3 if not homeless else 6)


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
    hx, hy = EDEN_HOPPERS[pick]
    return (hx + rng.randint(-2, 3), hy + rng.randint(-2, 3))


def tick_eden(u, rng, events):
    day = u["day"] = u["day"] + 1
    people = u["people"]
    pop = len(people)

    if not people:
        if u["extinct_day"] is None:
            record_extinction(u, events)
        elif day - u["extinct_day"] > RESEED_YEARS * DAYS_PER_YEAR:
            fresh = genesis_universe("EDEN", u["seed"] + u["iteration"],
                                     u["iteration"] + 1,
                                     postmortems=u["postmortems"])
            fresh["day"] = day
            for p in fresh["people"]:
                p["b"] = day - 18 * DAYS_PER_YEAR  # young again
            u.clear()
            u.update(fresh)
            events.append((day, "EDEN", "reseed",
                           f"The Observers reseed the pen. Iteration {u['iteration']} begins "
                           f"under the same perfect, fatal conditions."))
        return

    crowd = pop / eden_design(u)["cap"]
    dead, born = [], []

    # how many are at each hopper today — the sink feeds on its own crowd
    if day % 3 == 0:
        counts = [0, 0, 0, 0]
        for q in people:
            if q.get("a") == A_EAT:
                for i, (hx, hy) in enumerate(EDEN_HOPPERS):
                    if abs(q["x"] - hx) <= 3 and abs(q["y"] - hy) <= 3:
                        counts[i] += 1
                        break
        u["hop_n"] = counts
        u["sink"] = counts.index(max(counts))

    # phase transitions
    if u["phase"] == "strive" and any(age_of(p, day) < ADULT_AGE for p in people):
        u["phase"] = "exploit"
        events.append((day, "EDEN", "phase", "First child born in the pen. The exploit phase begins."))
    if u["phase"] == "exploit" and crowd >= eden_design(u)["stagnation"]:
        u["phase"] = "stagnate"
        events.append((day, "EDEN", "phase",
                       f"Crowding passes {int(eden_design(u)['stagnation']*100)}%. "
                       f"Stagnation: the behavioral sink emerges."))

    byid = {q["id"]: q for q in people}
    u["_ctx"] = day_context(people, day)
    for p in people:
        if base_mortality(p, day, rng, events, u):
            dead.append(p)
            cod(u, "age")
            continue
        # violence appears only in the sink
        if (u["phase"] in ("stagnate", "death") and age_of(p, day) >= ADULT_AGE
                and rng.random() < 4.5e-5 * crowd):
            dead.append(p)
            cod(u, "violence")
            if rng.random() < 0.08:
                events.append((day, "EDEN", "violence",
                               f"{p['n']} is killed in a sudden brawl near the hoppers."))
            continue
        # births — the rearing environment, not current density, decides the
        # child's fate: once the sink has broken social roles it stays broken
        # (Calhoun: stagnation-reared mice never recovered, even moved to
        # empty universes).
        if p["due"] and day >= p["due"]:
            p["due"] = 0
            p_abandon = p_incompetent = 0.0
            if u["phase"] == "stagnate":
                p_abandon = min(0.8, crowd * 0.9)
                p_incompetent = min(0.9, crowd * 1.2)
            elif u["phase"] == "death":
                p_abandon = max(0.5, min(0.8, crowd * 0.9))
                p_incompetent = 0.95
            if rng.random() < p_abandon:
                u["deaths_y"] += 1  # the infant
                cod(u, "infant")
                continue
            competent = rng.random() >= p_incompetent
            sex = rng.choice("mf")
            c = person(u["next_id"], f"E-{u['next_id']:04d}", sex, day,
                       p["g"] + 1, p["x"], p["y"], competent)
            c["hx"], c["hy"] = p.get("hx", p["x"]), p.get("hy", p["y"])
            c["box"] = None                 # claims its own place at adulthood
            c["mom"] = p["id"]
            u["next_id"] += 1
            born.append(c)
            if c["g"] > u["gen_max"] and c["g"] % 5 == 0:
                events.append((day, "EDEN", "generation",
                               f"Generation {c['g']} is born in the pen."))
            u["gen_max"] = max(u["gen_max"], c["g"])
        # the beautiful ones: incompetent adults withdraw for good
        if not p["c"] and not p["w"] and age_of(p, day) >= ADULT_AGE:
            p["w"] = True
        # the day in the pen: eat, court, brawl, or withdraw
        if age_of(p, day) < 3 * DAYS_PER_YEAR:
            follow_mother(p, byid, lambda x, y: (min(EDEN_SIZE - 3, max(2, x)),
                                                 min(EDEN_SIZE - 3, max(2, y))))
        if p.get("ad", 0) <= 0 and p["x"] == p["tx"] and p["y"] == p["ty"]:
            eden_assign(u, p, day, rng, crowd)
        if step_toward(p):
            p["ad"] = p.get("ad", 0) - 1
            if p["ad"] <= 0:
                eden_assign(u, p, day, rng, crowd)
        p["x"] = min(EDEN_SIZE - 3, max(2, p["x"]))
        p["y"] = min(EDEN_SIZE - 3, max(2, p["y"]))

    occ = u.setdefault("box_occ", {})
    for p in dead:
        people.remove(p)
        b = p.get("box")
        if b is not None and b >= 0:        # the box falls vacant
            occ[str(b)] = max(0, occ.get(str(b), 0) - 1)
    u["deaths_y"] += len(dead)
    u["births_y"] += len(born)
    people.extend(born)
    u["peak"] = max(u["peak"], len(people))

    # mating in the pen is ambient and free — no bonds, no scarcity — as long
    # as any socially competent adult male remains
    male_ok = any(p["s"] == "m" and p["c"] and not p["w"]
                  and age_of(p, day) >= ADULT_AGE for p in people)
    fertility = 1.0 / 180
    if u["phase"] in ("stagnate", "death"):
        fertility *= max(0.25, 1.0 - crowd)
    fertility *= 1.0 - 0.5 * u.get("ennui", 0.0)   # boredom with easy pleasure
    if u.get("std_years", 0) > 0:
        fertility *= 0.4
        # the outbreak also takes adults directly
        victims = [p for p in people
                   if age_of(p, day) >= ADULT_AGE and rng.random() < 2e-5]
        for p in victims:
            people.remove(p)
        u["deaths_y"] += len(victims)
        cod(u, "plague", len(victims))
    if u.get("wary_years", 0) > 0:
        fertility *= 0.7                            # the wary generation
    if male_ok:
        try_conceive(u, rng, people, fertility, require_pair=False)

    # yearly: ennui creep and disease rolls in a world of free mating
    if day % DAYS_PER_YEAR == 7:
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
        elif len(people) > 100 and rng.random() < 0.025:
            u["std_years"] = rng.randint(3, 8)
            events.append((day, "EDEN", "disease",
                           "A sickness spread by mating moves through the pen — "
                           "the one cost free pleasure turned out to carry."))

    if day % DAYS_PER_YEAR == 0:
        if (u["phase"] == "stagnate" and u["deaths_y"] > u["births_y"]
                and len(people) > 0):
            u["bad_years"] += 1
            if u["bad_years"] >= 3:
                u["phase"] = "death"
                events.append((day, "EDEN", "phase",
                               "Deaths outnumber births for the third year. The death phase begins — and it will not reverse."))
        elif u["phase"] == "stagnate":
            u["bad_years"] = 0
        record_census(u)
        u["births_y"] = u["deaths_y"] = 0

    if not people:
        record_extinction(u, events)


# ---------------------------------------------------------------- LAGOON

def lagoon_season(day):
    """Returns (plant_mult, fish_mult, is_winter)."""
    d = day % DAYS_PER_YEAR
    if 240 <= d < 330:
        return 0.55, 0.7, True
    if 60 <= d < 150:
        return 1.15, 1.1, False
    return 0.9, 1.0, False


def has(u, tech):
    return tech in u["tech"]


_TERRAIN_CACHE = {}


def terrain_of(u):
    seed = u.get("terrain_seed", u["seed"])
    if seed not in _TERRAIN_CACHE:
        _TERRAIN_CACHE[seed] = make_lagoon_terrain(seed)
    return _TERRAIN_CACHE[seed]


# ------------------------------------------------- where work happens

_SITES = {}


def settlement_sites(u, si):
    """Tiles around a settlement where each kind of work gets done.
    Cached — the land does not move."""
    st = u["settlements"][min(si, len(u["settlements"]) - 1)]
    key = (u.get("terrain_seed", u["seed"]), st["x"], st["y"], int(st["r"]))
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
    if "hx" not in p or abs(p["hx"] - st["x"]) > st["r"] + 14:
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
    if p["due"] and p["due"] - day <= 0:
        p["a"], p["ad"] = A_BIRTH, 2
        p["tx"], p["ty"] = at_home(0)
        return
    if p["due"] and 0 < p["due"] - day < 21:
        p["a"], p["ad"] = A_REST, 6
        p["tx"], p["ty"] = at_home(1)
        return
    if a < 3 * DAYS_PER_YEAR:                  # infants: wherever mother is
        p["a"], p["ad"] = A_TEND, 3
        p["tx"], p["ty"] = at_home(1)
        return
    if a < 12 * DAYS_PER_YEAR:                 # children: packs at play
        if rng.random() < 0.7:
            play_with(u, p, kids_near(u["_ctx"], p), rng, clamp)
        else:                                  # or tag along foraging
            pat = band_patches(u, si, rng)
            p["a"], p["ad"] = A_FORAGE, rng.randint(3, 6)
            p["tx"], p["ty"] = _patch_for(pat, "open", rng, home)
        return

    near_home = (abs(p["x"] - p["hx"]) <= 3 and abs(p["y"] - p["hy"]) <= 3)
    if not near_home:
        p["a"], p["ad"] = A_WALK, 0            # the work is done: go home
        p["tx"], p["ty"] = home
        return

    # home days: the band's social life happens at the hearths
    elder = a >= ELDER_AGE
    has_infant = p["id"] in u["_ctx"]["moms"]
    if elder or has_infant or rng.random() < 0.55:
        w = [(A_TALK, 2.6 + (1.6 if has(u, "lore") else 0)), (A_REST, 1.6)]
        if has(u, "shelter") and not elder:
            w.append((A_BUILD, 1.0))
        if (p["p"] is not None and not u["innocent"] and shortfall < 0.25
                and ADULT_AGE <= a <= 45 * DAYS_PER_YEAR):
            w.append((A_MATE, 2.2))
        if has_infant:
            w.append((A_TEND, 4.0))
        act = _weighted(w, rng)
        p["a"], p["ad"] = act, rng.randint(4, 9)
        p["tx"], p["ty"] = at_home(2)
        if act == A_MATE:
            q = next((q for q in u["people"] if q["id"] == p["p"]), None)
            if q is not None:
                couple_up(p, q, *at_home(1))
            else:
                p["a"] = A_REST
        elif act in (A_TALK, A_REST):          # elders sit together, too
            cx, cy = (st["x"] + rng.randint(-3, 3), st["y"] + rng.randint(-3, 3))
            join_circle(u, p, cx, cy, size=5 if act == A_TALK else 4,
                        radius=1.6 if act == A_TALK else 1.3)
            p["tx"], p["ty"] = clamp(p["tx"], p["ty"])
        return
    if a < ADULT_AGE:                          # adolescents work with the band
        pat = band_patches(u, si, rng)
        p["a"], p["ad"] = A_FORAGE, rng.randint(4, 9)
        p["tx"], p["ty"] = _patch_for(pat, "open", rng, home)
        return

    # a working trip. Nobody sets out alone: if a party left in the last
    # few days, you go where they went and do what they are doing.
    pat = band_patches(u, si, rng)
    party = st.get("party")
    if party and day - party["d"] <= 3 and party["n"] < 14:
        party["n"] += 1
        p["a"] = party["a"]
        p["ad"] = rng.randint(7, 15)
        p["tx"], p["ty"] = clamp(party["x"] + rng.randint(-2, 2),
                                 party["y"] + rng.randint(-2, 2))
        return
    w = [(A_FORAGE, 3.0 + 6.0 * shortfall)]
    if has(u, "stone_tools"):
        w.append((A_HUNT, 2.0 + 4.0 * shortfall))
    if has(u, "fishing"):
        w.append((A_FISH, 2.5 + 3.0 * shortfall))
    if has(u, "agriculture") and u["farms"]:
        w.append((A_FARM, 6.0))
    act = _weighted(w, rng)
    p["a"] = act
    p["ad"] = rng.randint(7, 15)          # a proper stint at the patch
    if act == A_HUNT:
        p["tx"], p["ty"] = _patch_for(pat, "woods", rng, home)
    elif act == A_FISH:
        p["tx"], p["ty"] = _patch_for(pat, "shore", rng, home)
    elif act == A_FARM:
        f = rng.choice(u["farms"])
        p["tx"], p["ty"] = f[0], f[1]
    else:
        kind = "woods" if (has(u, "stone_tools") and rng.random() < 0.35) else "open"
        p["tx"], p["ty"] = _patch_for(pat, kind, rng, home)
    st["party"] = {"d": day, "a": act, "x": p["tx"], "y": p["ty"], "n": 1}


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

A_PLAY = 15


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
            kids.setdefault((q["x"] >> 3, q["y"] >> 3), []).append(q)
        elif a < 3 * DAYS_PER_YEAR and q.get("mom") is not None:
            moms[q["mom"]] = True
        elif ADULT_AGE <= a <= 45 * DAYS_PER_YEAR and not q["w"]:
            (adults_m if q["s"] == "m" else adults_f).append(q)
    return {"kids": kids, "moms": moms, "am": adults_m, "af": adults_f}


def kids_near(ctx, p):
    gx, gy = p["x"] >> 3, p["y"] >> 3
    out = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            out.extend(ctx["kids"].get((gx + dx, gy + dy), ()))
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
    p["ad"] = q["ad"] = 2
    return True


def couple_up(p, q, x, y):
    p["tx"], p["ty"], p["f"] = x, y, 1
    q["tx"], q["ty"], q["f"] = x + 1, y, -1
    p["a"] = q["a"] = A_MATE
    p["ad"] = q["ad"] = 2


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
    p["ad"] = rng.randint(1, 2)
    if near:
        k = rng.choice(near)
        p["tx"], p["ty"] = clamp(k["x"] + rng.randint(-1, 1), k["y"] + rng.randint(-1, 1))
        p["f"] = 1 if k["x"] >= p["x"] else -1
    else:
        p["tx"], p["ty"] = clamp(p["hx"] + rng.randint(-2, 2), p["hy"] + rng.randint(-2, 2))


WALK_SPEED = 3          # tiles covered in a day's travel


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
        if terr is not None and terr[ny][nx] == 2:   # don't walk into the sea
            if sx and terr[p["y"]][nx] != 2:
                ny = p["y"]
            elif sy and terr[ny][p["x"]] != 2:
                nx = p["x"]
            else:
                nx, ny = p["x"], p["y"]
        if nx == p["x"] and ny == p["y"]:
            # no way forward: the target is across water. Give it up, so the
            # person chooses something reachable instead of standing forever.
            p["tx"], p["ty"] = p["x"], p["y"]
            return True
        p["x"], p["y"] = nx, ny
    return p["x"] == p["tx"] and p["y"] == p["ty"]


def tick_lagoon(u, rng, events):
    day = u["day"] = u["day"] + 1
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
                                     lessons=lessons)
            fresh["day"] = day
            for p in fresh["people"]:
                p["b"] = day - 18 * DAYS_PER_YEAR  # young again
            if "preserve" in lessons:
                fresh["store"] = 30.0   # they cache food without being told why
            u.clear()
            u.update(fresh)
            carried = (" They carry the old lessons: " + ", ".join(lessons) + "."
                       if lessons else "")
            events.append((day, "LAGOON", "reseed",
                           f"New castaways reach the lagoon. Iteration {u['iteration']} "
                           f"begins.{carried}"))
        return

    stocks = u["stocks"]
    plant_mult, fish_mult, winter = lagoon_season(day)
    if u["drought"] > 0:
        plant_mult *= 0.45
    if winter and u["harsh_winter"]:
        plant_mult *= 0.5
        fish_mult *= 0.6

    # --- stocks regrow (logistic, daily rate)
    cont = 3.0 if u.get("continent") else 1.0   # a continent's bounty
    for key, cap, r in (("plants", 60000 * cont, 0.9), ("game", 2500 * cont, 0.5),
                        ("fish", 50000 * cont, 0.6)):
        x = stocks[key]
        stocks[key] = max(1.0, x + (r / DAYS_PER_YEAR) * x * (1 - x / cap))
    g = stocks["pred"]
    stocks["pred"] = max(2.0, g + (0.3 / DAYS_PER_YEAR) * g *
                         (1 - g / (20 + 30 * stocks["game"] / 2500)))

    # --- demography groups
    adults, kids, elders = [], [], []
    for p in people:
        a = age_of(p, day)
        (kids if a < ADULT_AGE else elders if a >= ELDER_AGE else adults).append(p)

    # --- food
    juveniles = sum(1 for p in kids
                    if age_of(p, day) >= 8 * DAYS_PER_YEAR)
    foragers = len(adults) + 0.3 * len(elders) + 0.35 * juveniles
    tool_mult = 1.25 if has(u, "stone_tools") else 1.0
    # desperation: a hungry band forages harder and ranges farther
    avg_hun = sum(p["hun"] for p in people) / len(people)
    effort = 1.0 + min(0.6, avg_hun / 30.0)
    yield_plants = min(foragers * 1.5 * plant_mult * tool_mult * effort,
                       stocks["plants"] * 0.004)
    stocks["plants"] -= yield_plants * 0.8
    yield_fish = 0.0
    if has(u, "fishing"):
        yield_fish = min(foragers * 0.5 * fish_mult, stocks["fish"] * 0.003)
        stocks["fish"] -= yield_fish * 0.7
    # trapping/scavenging works even before stone tools, just poorly
    hunt_eff = 0.4 if has(u, "stone_tools") else 0.25
    yield_game = min(foragers * hunt_eff * (stocks["game"] / 2500) * effort,
                     stocks["game"] * 0.002)
    stocks["game"] -= yield_game * 1.1
    # the shore always gives something: shellfish and tidal gathering,
    # winter-proof and the reason the lagoon was a good place to wash up
    yield_shore = foragers * 0.35 * effort
    yield_farm = 0.0
    if has(u, "agriculture"):
        season_farm = 0.25 if winter else 1.0
        if u["drought"] > 0:
            season_farm *= 0.3
        yield_farm = len(u["farms"]) * 2.1 * season_farm
    if has(u, "domestication"):
        yield_farm += len(u["farms"]) * 0.5

    need = len(adults) * 1.0 + len(kids) * 0.6 + len(elders) * 0.8
    total = (yield_plants + yield_fish + yield_game + yield_shore
             + yield_farm + u["store"])
    if total >= need:
        surplus = total - need
        cap_store = (need * 60 if has(u, "granary")
                     else need * 14 if has(u, "preservation") else 0)
        u["store"] = min(surplus, cap_store)
        shortfall = 0.0
    else:
        u["store"] = 0.0
        shortfall = (need - total) / max(1.0, need)  # 0..1 fraction unfed

    dead, born = [], []
    weapons = has(u, "stone_tools")
    healing = has(u, "healing")
    terr_l = terrain_of(u)
    byid = {q["id"]: q for q in people}
    u["_ctx"] = day_context(people, day)

    for p in people:
        a = age_of(p, day)
        # hunger — unevenly shared, so famine takes the weakest first
        # instead of the whole band at once
        if shortfall > 0:
            frail = 1.6 if (a < ADULT_AGE or a >= ELDER_AGE) else 1.0
            p["hun"] += shortfall * frail * rng.uniform(0.5, 1.5)
        else:
            p["hun"] = max(0.0, p["hun"] - 1.0)
        if p["hun"] > 40:
            dead.append(p)
            cod(u, "starvation")
            if rng.random() < 0.1:
                events.append((day, "LAGOON", "famine",
                               f"{p['n']} starves in the lean season."))
            continue
        # predation
        pr = 3e-5 * (stocks["pred"] / 48.0)
        if weapons:
            pr *= 0.3
        if "vigilance" in u["lessons"]:
            pr *= 0.6          # a lesson paid for in a previous iteration
        if a < ADULT_AGE:
            pr *= 2.0
        if rng.random() < pr:
            dead.append(p)
            cod(u, "predator")
            if rng.random() < 0.25:
                events.append((day, "LAGOON", "predator",
                               f"{p['n']} is taken by a predator at the wood's edge."))
            continue
        # accidents + senescence
        if rng.random() < 6e-6 or base_mortality(p, day, rng, events, u):
            dead.append(p)
            cod(u, "age")
            continue
        # births
        if p["due"] and day >= p["due"]:
            p["due"] = 0
            infant_loss = 0.06 if healing else 0.13
            mother_loss = 0.008 if healing else 0.02
            if rng.random() < mother_loss:
                dead.append(p)
                cod(u, "childbirth")
                events.append((day, "LAGOON", "childbirth",
                               f"{p['n']} dies bringing new life into the world."))
                continue
            if rng.random() >= infant_loss:
                sex = rng.choice("mf")
                c = person(u["next_id"], make_name(rng), sex, day,
                           p["g"] + 1, p["x"], p["y"])
                c["st"] = p.get("st", 0)
                c["hx"], c["hy"] = p.get("hx", p["x"]), p.get("hy", p["y"])
                c["mom"] = p["id"]
                u["next_id"] += 1
                born.append(c)
                if c["g"] > u["gen_max"] and c["g"] % 5 == 0:
                    events.append((day, "LAGOON", "generation",
                                   f"Generation {c['g']} — {c['n']} is born by the lagoon."))
                u["gen_max"] = max(u["gen_max"], c["g"])
            else:
                u["deaths_y"] += 1
                cod(u, "infant")
        # go about the day's work: travel to the site, then do the thing
        if age_of(p, day) < 3 * DAYS_PER_YEAR:
            follow_mother(p, byid, lambda x, y: (min(LAGOON_SIZE - 2, max(1, x)),
                                                 min(LAGOON_SIZE - 2, max(1, y))))
        if p.get("ad", 0) <= 0 and p["x"] == p["tx"] and p["y"] == p["ty"]:
            lagoon_assign(u, p, day, rng, shortfall)
        arrived = step_toward(p, terr_l)
        if arrived:
            p["ad"] = p.get("ad", 0) - 1
            if p["ad"] <= 0:
                lagoon_assign(u, p, day, rng, shortfall)
        p["x"] = min(LAGOON_SIZE - 2, max(1, p["x"]))
        p["y"] = min(LAGOON_SIZE - 2, max(1, p["y"]))

    for p in dead:
        if p in people:
            people.remove(p)
    clear_widows(people, dead)   # widows re-pair at the next monthly gathering
    u["deaths_y"] += len(dead)
    u["births_y"] += len(born)
    people.extend(born)
    u["peak"] = max(u["peak"], len(people))

    # Blue Lagoon: the founders discover how life begins
    if u["innocent"]:
        if day > 60 and rng.random() < 1 / 300:
            u["innocent"] = False
            events.append((day, "LAGOON", "discovery",
                           "The pairs discover, as all life does, how new life begins."))
    else:
        if day % 30 == 0:
            living_adults = [p for p in people
                             if ADULT_AGE <= age_of(p, day) < ELDER_AGE]
            pair_singles(u, rng, living_adults)
        fert = 1.0 / 300
        if u["store"] > need * 20:
            fert *= 1.3
        if shortfall > 0.3:
            fert *= 0.3
        if has(u, "agriculture"):
            fert *= 1.25  # the luxury trap: more mouths, more hands, more work
        try_conceive(u, rng, people, fert)

    # --- yearly rolls: tech, disasters, settlement dynamics
    if day % DAYS_PER_YEAR == 0 and people:
        pop = len(people)
        year = day // DAYS_PER_YEAR
        if u["drought"] > 0:
            u["drought"] -= 1
        u["harsh_winter"] = rng.random() < 0.06
        if u["harsh_winter"]:
            events.append((day, "LAGOON", "disaster",
                           f"Year {year}: a brutal ice-age winter grips the lagoon."))
        if rng.random() < 0.07:
            u["drought"] = 1
            events.append((day, "LAGOON", "disaster",
                           f"Year {year}: drought — the groves wither."))
        if rng.random() < 0.02 and u["store"] > 0:
            u["store"] *= 0.4
            events.append((day, "LAGOON", "disaster",
                           f"Year {year}: a storm off the lagoon destroys most of the stores."))
        p_epidemic = 0.02 if "cleanliness" in u["lessons"] else 0.04
        if has(u, "domestication") and rng.random() < p_epidemic and pop > 30:
            kill = rng.uniform(0.15, 0.35)
            victims = rng.sample(people, max(1, int(pop * kill)))
            for v in victims:
                people.remove(v)
            u["deaths_y"] += len(victims)
            cod(u, "epidemic", len(victims))
            events.append((day, "LAGOON", "epidemic",
                           f"Year {year}: a sickness born of the herds kills {len(victims)} "
                           f"({int(kill*100)}% of the people)."))

        # technology: discovery odds scale with population
        for name, prereq, base, min_pop in TECH_LADDER:
            if has(u, name) or pop < min_pop:
                continue
            if prereq and not has(u, prereq):
                continue
            p_disc = base * min(2.5, math.log(max(2, pop), 8))
            for lesson in u["lessons"]:
                if name in LESSON_TECH.get(lesson, ()):
                    p_disc *= 3.0  # inherited wisdom from a dead iteration
            if name == "agriculture" and shortfall == 0 and pop < 140:
                p_disc *= 0.3  # agriculture is born of pressure, not comfort
            if rng.random() < p_disc:
                u["tech"].append(name)
                discoverer = rng.choice(adults)["n"] if adults else "someone"
                events.append((day, "LAGOON", "discovery",
                               f"Year {year}: {TECH_LABEL[name]} — first by {discoverer}."))
                if name == "agriculture":
                    st = u["settlements"][0]
                    for _ in range(6):
                        u["farms"].append([st["x"] + rng.randint(-7, 7),
                                           st["y"] + rng.randint(-7, 7)])
                break  # at most one discovery a year

        # once boats exist and the island feels small, pioneers cross on
        # their own — no need to wait for a feud to push them out
        if (has(u, "seacraft") and not u.get("continent") and pop > 160
                and len(u["settlements"]) < 12 and rng.random() < 0.3):
            terr = terrain_of(u)
            for _ in range(40):
                ty = rng.randrange(40, LAGOON_SIZE - 40)
                tx = rng.randrange(8, 30)
                if terr[ty][tx] != 2:
                    tribe = make_name(rng)
                    u["settlements"].append({"x": tx, "y": ty, "r": 5, "n": tribe})
                    new_i = len(u["settlements"]) - 1
                    pioneers = rng.sample(people, max(8, pop // 5))
                    for p in pioneers:
                        p["st"] = new_i
                        p["x"], p["y"] = tx, ty
                        p["hx"] = tx + rng.randint(-2, 2)
                        p["hy"] = ty + rng.randint(-2, 2)
                        p["tx"], p["ty"], p["ad"] = p["hx"], p["hy"], 0
                    u["continent"] = True
                    events.append((day, "LAGOON", "migration",
                                   f"Year {year}: the boats cross the strait. The {tribe} tribe "
                                   f"lands on the greater shore — a land without end, the one "
                                   f"all their children's children will call home."))
                    break

        # full bellies and long evenings: surplus turns into art and pleasure
        if (has(u, "lore") and u["store"] > need * 20 and adults
                and len(u.get("culture", [])) < len(ARTS)
                and rng.random() < 0.2):
            art = next(a for a in ARTS if a not in u["culture"])
            u.setdefault("culture", []).append(art)
            maker = rng.choice(adults)["n"]
            events.append((day, "LAGOON", "culture",
                           f"Year {year}: with food enough and nothing to fear, "
                           f"{art} appear{'s' if not art.startswith('the') else ''} — "
                           f"first made by {maker}."))

        if has(u, "agriculture") and len(u["farms"]) < pop // 3:
            st = rng.choice(u["settlements"])
            u["farms"].append([st["x"] + rng.randint(-8, 8),
                               st["y"] + rng.randint(-8, 8)])

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
                crossing = has(u, "seacraft") and not u.get("continent")
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
                tribe = make_name(rng)
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
                    for v in losses:
                        if v in people:
                            people.remove(v)
                    u["deaths_y"] += len(losses)
                    cod(u, "feud", len(losses))
                    events.append((day, "LAGOON", "feud",
                                   f"Year {year}: too many strangers, no shared story — a feud splits "
                                   f"{old_tribe}; {len(losses)} die, the rest walk away and become "
                                   f"the {tribe} tribe."))
        # survivors of a near-wipe pass the fear down without words —
        # instinct, not writing, is the first archive
        for cause, n in u["cod_y"].items():
            lesson = LESSON_OF.get(cause)
            if (lesson and lesson not in u["lessons"]
                    and n > max(2, 0.2 * max(1, pop))):
                u["lessons"].append(lesson)
                events.append((day, "LAGOON", "lesson",
                               f"Year {year}: {cause} took {n} of them. The survivors carry a "
                               f"new instinct — '{lesson}' — passed on without a single word."))
        u["cod_y"] = {}
        record_census(u)
        u["births_y"] = u["deaths_y"] = 0

    if not people:
        record_extinction(u, events)


# ---------------------------------------------------------------- top level

def tick_world(world, events):
    """Advance both universes one day. Deterministic per (seed, day)."""
    for key in ("eden", "lagoon"):
        u = world[key]
        rng = random.Random((u["seed"] << 20) ^ (u["day"] + 1) ^ u["iteration"])
        (tick_eden if u["kind"] == "EDEN" else tick_lagoon)(u, rng, events)


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
            p.get("p") or 0, round(p.get("hun", 0.0), 1)]


def summarize(world):
    """Compact snapshot for the renderer / web mirror."""
    out = {"wall": time.time(), "sec_per_day": world["sec_per_day"], "u": {}}
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
            ppl.append([p["x"], p["y"], cls, 1 if p["s"] == "f" else 0,
                        p["id"], p.get("a", 0), p.get("f", 1)])
            detail[str(p["id"])] = person_detail(u, p, day, ctx)
        info = {"day": day, "year": day // DAYS_PER_YEAR, "pop": len(u["people"]),
                "gen": u["gen_max"], "peak": u["peak"], "phase": u["phase"],
                "iter": u["iteration"], "people": ppl, "detail": detail,
                "cod": dict(u.get("cod", {})),
                "census": u["census"][-120:]}
        if u["kind"] == "LAGOON":
            info["tech"] = u["tech"]
            info["settlements"] = u["settlements"]
            info["farms"] = u["farms"]
            info["store"] = round(u["store"], 1)
            info["lessons"] = u.get("lessons", [])
            info["culture"] = u.get("culture", [])
            d = day % DAYS_PER_YEAR
            info["season"] = ("winter" if 240 <= d < 330 else
                              "summer" if 60 <= d < 150 else "spring")
            info["harsh"] = bool(u.get("harsh_winter"))
            info["dry"] = u.get("drought", 0) > 0
            info["phase"] = ("innocence" if u["innocent"] else
                             u["tech"][-1] if u["tech"] else "foragers")
        else:
            info["ennui"] = round(u.get("ennui", 0.0), 3)
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
        out["u"][key] = info
    return out


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
    for key in ("eden", "lagoon"):
        u = world.get(key)
        if not u:
            continue
        u.setdefault("cod", {})
        u.setdefault("cod_y", {})
        u.setdefault("postmortems", [])
        u.setdefault("lessons", [])
        if u.get("kind") == "LAGOON":
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
        for p in u.get("people", []):
            p.setdefault("a", 0)
            p.setdefault("ad", 0)
            p.setdefault("tx", p["x"])
            p.setdefault("ty", p["y"])
            p.setdefault("hx", p["x"])
            p.setdefault("hy", p["y"])
            p.setdefault("f", 1)
            p.setdefault("mom", None)
            if u.get("kind") == "EDEN":
                p.setdefault("box", None)   # claims a nest box on next move
    return world
