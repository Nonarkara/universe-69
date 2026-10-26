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

LAGOON_SIZE = 96
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
    ("healing",       "lore",          0.10, 150),
    ("metallurgy",    "granary",       0.06, 250),
    ("writing",       "lore",          0.05, 400),
]
TECH_LABEL = {
    "fire": "fire is tamed", "stone_tools": "stone tools are knapped",
    "fishing": "fishing is learned", "shelter": "shelters are raised",
    "preservation": "food can be kept", "lore": "shared stories bind the bands",
    "agriculture": "seeds are sown on purpose", "domestication": "animals are tamed",
    "granary": "granaries hold the surplus", "healing": "healing lore spreads",
    "metallurgy": "metal is smelted", "writing": "marks begin to remember",
}


def make_name(rng):
    n = rng.choice([2, 2, 3])
    return "".join(rng.choice(SYLLABLES) for _ in range(n)).capitalize()


def person(uid, name, sex, born, gen, x, y, competent=True):
    return {"id": uid, "n": name, "s": sex, "b": born, "g": gen,
            "p": None, "x": x, "y": y, "c": competent, "w": False,
            "due": 0, "hun": 0.0}


def age_of(p, day):
    return day - p["b"]


# ---------------------------------------------------------------- world gen

def make_lagoon_terrain(seed):
    """0 grass, 1 woods, 2 water, 3 beach, 4 farm."""
    rng = random.Random(seed)
    s = LAGOON_SIZE
    t = [[0] * s for _ in range(s)]
    cx, cy, rad = 70, 68, 19  # the lagoon
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - cx, y - cy)
            if d < rad:
                t[y][x] = 2
            elif d < rad + 2.5:
                t[y][x] = 3
    for _ in range(9):  # woods: blobby random walks
        x, y = rng.randrange(4, 56), rng.randrange(4, 56)
        for _ in range(260):
            if t[y][x] == 0:
                t[y][x] = 1
            x = min(s - 1, max(0, x + rng.choice([-1, 0, 1])))
            y = min(s - 1, max(0, y + rng.choice([-1, 0, 1])))
    return t


def genesis_universe(kind, seed, iteration=1):
    rng = random.Random(seed)
    u = {"kind": kind, "seed": seed, "iteration": iteration, "day": 0,
         "people": [], "next_id": 1, "gen_max": 1, "phase": "strive",
         "peak": 0, "births_y": 0, "deaths_y": 0, "bad_years": 0,
         "extinct_day": None, "census": [], "year_flags": {}}
    if kind == "EDEN":
        cx = EDEN_SIZE // 2
        spots = [(cx - 2, cx), (cx - 2, cx + 1), (cx + 2, cx), (cx + 2, cx + 1)]
    else:
        u["terrain_seed"] = seed
        u["stocks"] = {"plants": 3000.0, "game": 2500.0,
                       "fish": 4000.0, "pred": 48.0}
        u["tech"] = []
        u["store"] = 0.0
        u["farms"] = []            # [x, y] tilled tiles
        u["settlements"] = [{"x": 58, "y": 52, "r": 5}]
        u["innocent"] = True       # Blue Lagoon: reproduction not yet discovered
        u["drought"] = 0           # years remaining
        u["harsh_winter"] = False
        spots = [(57, 51), (58, 51), (58, 53), (59, 52)]
    for i, (x, y) in enumerate(spots):
        sex = "m" if i % 2 == 0 else "f"
        name = f"E-{u['next_id']:04d}" if kind == "EDEN" else make_name(rng)
        p = person(u["next_id"], name, sex, -20 * DAYS_PER_YEAR, 1, x, y)
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

def base_mortality(p, day, rng, events, u, label_extra=""):
    """Senescence. Returns True if the person dies of old age."""
    age_y = age_of(p, day) / DAYS_PER_YEAR
    pr = 2e-6 + max(0.0, age_y - 55) * 1.2e-5
    if rng.random() < pr:
        return True
    return False


def try_conceive(u, rng, females, p_daily):
    day = u["day"]
    for p in females:
        if p["s"] != "f" or p["due"] or p["p"] is None or p["w"]:
            continue
        a = age_of(p, day)
        if not (ADULT_AGE <= a <= 45 * DAYS_PER_YEAR):
            continue
        if rng.random() < p_daily:
            p["due"] = day + GESTATION


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

def tick_eden(u, rng, events):
    day = u["day"] = u["day"] + 1
    people = u["people"]
    pop = len(people)

    if not people:
        if u["extinct_day"] and day - u["extinct_day"] > RESEED_YEARS * DAYS_PER_YEAR:
            fresh = genesis_universe("EDEN", u["seed"] + u["iteration"],
                                     u["iteration"] + 1)
            fresh["day"] = day
            u.clear()
            u.update(fresh)
            events.append((day, "EDEN", "reseed",
                           f"The Observers reseed the pen. Iteration {u['iteration']} begins."))
        return

    crowd = pop / EDEN_CAP
    dead, born = [], []

    # phase transitions
    if u["phase"] == "strive" and any(age_of(p, day) < ADULT_AGE for p in people):
        u["phase"] = "exploit"
        events.append((day, "EDEN", "phase", "First child born in the pen. The exploit phase begins."))
    if u["phase"] == "exploit" and crowd >= EDEN_STAGNATION:
        u["phase"] = "stagnate"
        events.append((day, "EDEN", "phase",
                       f"Crowding passes {int(EDEN_STAGNATION*100)}%. Stagnation: the behavioral sink emerges."))

    for p in people:
        if base_mortality(p, day, rng, events, u):
            dead.append(p)
            continue
        # violence appears only in the sink
        if (u["phase"] in ("stagnate", "death") and age_of(p, day) >= ADULT_AGE
                and rng.random() < 4.5e-5 * crowd):
            dead.append(p)
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
                continue
            competent = rng.random() >= p_incompetent
            sex = rng.choice("mf")
            c = person(u["next_id"], f"E-{u['next_id']:04d}", sex, day,
                       p["g"] + 1, p["x"], p["y"], competent)
            u["next_id"] += 1
            born.append(c)
            if c["g"] > u["gen_max"] and c["g"] % 5 == 0:
                events.append((day, "EDEN", "generation",
                               f"Generation {c['g']} is born in the pen."))
            u["gen_max"] = max(u["gen_max"], c["g"])
        # the beautiful ones: incompetent adults withdraw for good
        if not p["c"] and not p["w"] and age_of(p, day) >= ADULT_AGE:
            p["w"] = True
        # wander the pen
        p["x"] = min(EDEN_SIZE - 2, max(1, p["x"] + rng.choice([-1, 0, 1])))
        p["y"] = min(EDEN_SIZE - 2, max(1, p["y"] + rng.choice([-1, 0, 1])))

    for p in dead:
        people.remove(p)
    u["deaths_y"] += len(dead)
    u["births_y"] += len(born)
    people.extend(born)
    u["peak"] = max(u["peak"], len(people))

    if day % 30 == 0:
        adults = [p for p in people if ADULT_AGE <= age_of(p, day) and p["c"]]
        pair_singles(u, rng, adults)
    fertility = 1.0 / 180
    if u["phase"] in ("stagnate", "death"):
        fertility *= max(0.25, 1.0 - crowd)
    try_conceive(u, rng, people, fertility)

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

    if not people and u["extinct_day"] is None:
        u["extinct_day"] = day
        events.append((day, "EDEN", "extinction",
                       f"UNIVERSE 6 HAS DIED. The pen is empty. Peak population was {u['peak']}, "
                       f"generation {u['gen_max']}. The food hoppers are still full."))


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


def tick_lagoon(u, rng, events):
    day = u["day"] = u["day"] + 1
    people = u["people"]

    if not people:
        if u["extinct_day"] and day - u["extinct_day"] > RESEED_YEARS * DAYS_PER_YEAR:
            fresh = genesis_universe("LAGOON", u["seed"] + u["iteration"],
                                     u["iteration"] + 1)
            fresh["day"] = day
            u.clear()
            u.update(fresh)
            events.append((day, "LAGOON", "reseed",
                           f"New castaways reach the lagoon. Iteration {u['iteration']} begins."))
        return

    stocks = u["stocks"]
    plant_mult, fish_mult, winter = lagoon_season(day)
    if u["drought"] > 0:
        plant_mult *= 0.45
    if winter and u["harsh_winter"]:
        plant_mult *= 0.5
        fish_mult *= 0.6

    # --- stocks regrow (logistic, daily rate)
    for key, cap, r in (("plants", 3000, 0.9), ("game", 2500, 0.5),
                        ("fish", 4000, 0.6)):
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
    foragers = len(adults) + 0.3 * len(elders)
    tool_mult = 1.25 if has(u, "stone_tools") else 1.0
    yield_plants = min(foragers * 1.15 * plant_mult * tool_mult,
                       stocks["plants"] * 0.004)
    stocks["plants"] -= yield_plants * 0.8
    yield_fish = 0.0
    if has(u, "fishing"):
        yield_fish = min(foragers * 0.5 * fish_mult, stocks["fish"] * 0.003)
        stocks["fish"] -= yield_fish * 0.7
    # trapping/scavenging works even before stone tools, just poorly
    hunt_eff = 0.4 if has(u, "stone_tools") else 0.25
    yield_game = min(foragers * hunt_eff * (stocks["game"] / 2500),
                     stocks["game"] * 0.002)
    stocks["game"] -= yield_game * 1.1
    yield_farm = 0.0
    if has(u, "agriculture"):
        season_farm = 0.25 if winter else 1.0
        if u["drought"] > 0:
            season_farm *= 0.3
        yield_farm = len(u["farms"]) * 2.1 * season_farm
    if has(u, "domestication"):
        yield_farm += len(u["farms"]) * 0.5

    need = len(adults) * 1.0 + len(kids) * 0.6 + len(elders) * 0.8
    total = yield_plants + yield_fish + yield_game + yield_farm + u["store"]
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

    for p in people:
        a = age_of(p, day)
        # hunger
        if shortfall > 0:
            frail = 1.6 if (a < ADULT_AGE or a >= ELDER_AGE) else 1.0
            p["hun"] += shortfall * frail
        else:
            p["hun"] = max(0.0, p["hun"] - 1.0)
        if p["hun"] > 40:
            dead.append(p)
            if rng.random() < 0.1:
                events.append((day, "LAGOON", "famine",
                               f"{p['n']} starves in the lean season."))
            continue
        # predation
        pr = 3e-5 * (stocks["pred"] / 48.0)
        if weapons:
            pr *= 0.3
        if a < ADULT_AGE:
            pr *= 2.0
        if rng.random() < pr:
            dead.append(p)
            if rng.random() < 0.25:
                events.append((day, "LAGOON", "predator",
                               f"{p['n']} is taken by a predator at the wood's edge."))
            continue
        # accidents + senescence
        if rng.random() < 6e-6 or base_mortality(p, day, rng, events, u):
            dead.append(p)
            continue
        # births
        if p["due"] and day >= p["due"]:
            p["due"] = 0
            infant_loss = 0.06 if healing else 0.13
            mother_loss = 0.008 if healing else 0.02
            if rng.random() < mother_loss:
                dead.append(p)
                events.append((day, "LAGOON", "childbirth",
                               f"{p['n']} dies bringing new life into the world."))
                continue
            if rng.random() >= infant_loss:
                sex = rng.choice("mf")
                c = person(u["next_id"], make_name(rng), sex, day,
                           p["g"] + 1, p["x"], p["y"])
                c["st"] = p.get("st", 0)
                u["next_id"] += 1
                born.append(c)
                if c["g"] > u["gen_max"] and c["g"] % 5 == 0:
                    events.append((day, "LAGOON", "generation",
                                   f"Generation {c['g']} — {c['n']} is born by the lagoon."))
                u["gen_max"] = max(u["gen_max"], c["g"])
            else:
                u["deaths_y"] += 1
        # drift around home settlement
        st = u["settlements"][min(p.get("st", 0), len(u["settlements"]) - 1)]
        p["x"] += rng.choice([-1, 0, 1])
        p["y"] += rng.choice([-1, 0, 1])
        if math.hypot(p["x"] - st["x"], p["y"] - st["y"]) > st["r"]:
            p["x"] += 1 if st["x"] > p["x"] else -1
            p["y"] += 1 if st["y"] > p["y"] else -1
        p["x"] = min(LAGOON_SIZE - 2, max(1, p["x"]))
        p["y"] = min(LAGOON_SIZE - 2, max(1, p["y"]))

    for p in dead:
        if p in people:
            people.remove(p)
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
            pair_singles(u, rng, adults)
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
        if has(u, "domestication") and rng.random() < 0.04 and pop > 30:
            kill = rng.uniform(0.15, 0.35)
            victims = rng.sample(people, max(1, int(pop * kill)))
            for v in victims:
                people.remove(v)
            u["deaths_y"] += len(victims)
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
                ang = rng.uniform(0, 2 * math.pi)
                dist = rng.uniform(12, 24)
                nx = int(min(LAGOON_SIZE - 6, max(5, st["x"] + math.cos(ang) * dist)))
                ny = int(min(LAGOON_SIZE - 6, max(5, st["y"] + math.sin(ang) * dist)))
                u["settlements"].append({"x": nx, "y": ny, "r": 5})
                new_i = len(u["settlements"]) - 1
                movers = [p for p in people if p.get("st", 0) == si]
                rng.shuffle(movers)
                for p in movers[: int(n * 0.4)]:
                    p["st"] = new_i
                    p["x"], p["y"] = nx, ny
                if has(u, "lore"):
                    events.append((day, "LAGOON", "migration",
                                   f"Year {year}: a band departs in peace to found a new settlement."))
                else:
                    losses = rng.sample(movers, min(len(movers), max(1, n // 40)))
                    for v in losses:
                        if v in people:
                            people.remove(v)
                    u["deaths_y"] += len(losses)
                    events.append((day, "LAGOON", "feud",
                                   f"Year {year}: too many strangers, no shared story — a feud splits "
                                   f"the band; {len(losses)} die, the rest walk away."))
        record_census(u)
        u["births_y"] = u["deaths_y"] = 0

    if not people and u["extinct_day"] is None:
        u["extinct_day"] = day
        events.append((day, "LAGOON", "extinction",
                       f"UNIVERSE 9 HAS DIED. The lagoon is quiet again. Peak population {u['peak']}, "
                       f"generation {u['gen_max']}."))


# ---------------------------------------------------------------- top level

def tick_world(world, events):
    """Advance both universes one day. Deterministic per (seed, day)."""
    for key in ("eden", "lagoon"):
        u = world[key]
        rng = random.Random((u["seed"] << 20) ^ (u["day"] + 1) ^ u["iteration"])
        (tick_eden if u["kind"] == "EDEN" else tick_lagoon)(u, rng, events)


def summarize(world):
    """Compact snapshot for the renderer / web mirror."""
    out = {"wall": time.time(), "sec_per_day": world["sec_per_day"], "u": {}}
    for key in ("eden", "lagoon"):
        u = world[key]
        day = u["day"]
        ppl = []
        for p in u["people"][:2400]:
            a = age_of(p, day)
            cls = (0 if a < ADULT_AGE else
                   4 if p["w"] else
                   3 if a >= ELDER_AGE else
                   1 if p["s"] == "m" else 2)
            ppl.append([p["x"], p["y"], cls])
        info = {"day": day, "year": day // DAYS_PER_YEAR, "pop": len(u["people"]),
                "gen": u["gen_max"], "peak": u["peak"], "phase": u["phase"],
                "iter": u["iteration"], "people": ppl, "census": u["census"][-120:]}
        if u["kind"] == "LAGOON":
            info["tech"] = u["tech"]
            info["settlements"] = u["settlements"]
            info["farms"] = u["farms"]
            info["store"] = round(u["store"], 1)
            info["phase"] = ("innocence" if u["innocent"] else
                             u["tech"][-1] if u["tech"] else "foragers")
        out["u"][key] = info
    return out


# ---------------------------------------------------------------- persistence

def save_state(world, path):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(world, f, separators=(",", ":"))
    os.replace(tmp, path)


def load_state(path):
    with open(path) as f:
        return json.load(f)
