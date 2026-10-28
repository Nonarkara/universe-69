"""Needs, places, and one decision loop for both worlds.

Before this, each world had its own assigner: a roulette of activity
*labels*, weighted by crowd and shortfall. The food arrived because there
were adults, not because anyone went and got it. Hunger was a property of
the band and not of a person. The big cat was a number in a dictionary and
the hunt was a roll against it.

This is the other way round. A person has a body with meters. The world
has places with things in them. The person perceives what is within
reach, scores what it could do against what it needs and what the doing
would cost, commits, and the world changes when the work is done.

Both worlds run the same loop. What differs is the **condition**: how much
food is around, how crowded it is, how violent, what the floor of
technology is, whether you have to work for your dinner. EDEN's food is
provisioned — that is the premise of the experiment and it is not a bug.
LAGOON's food is wild, and it only arrives if somebody goes and gets it.

Standard library only, like the engine.
"""

import random

# The number of parts in a day. The engine owns the truth of this; it is
# repeated here so that this module stands alone.
PARTS_PER_DAY = 4

# ---- meters -------------------------------------------------------------
# Hunger is the old one: 0 is fed, 40 is death. Energy and solitude are
# new, and both are personal — you cannot be tired on someone else's
# behalf, which is the whole point.

HUNGER_MAX = 40.0        # at this, the person dies
ENERGY_MAX = 1.0
SOLITUDE_MAX = 1.0

HUNGER_PER_DAY = 0.9     # how fast an empty belly comes back
ENERGY_PER_WORK = 0.055  # a day of work costs this much
ENERGY_PER_TRAVEL = 0.012
ENERGY_PER_SOCIAL = 0.008
SLEEP_PER_PART = 0.2     # one night's sleep gives back three days of work
SOLITUDE_PER_DAY = 0.05  # isolation, if you are alone
SOLITUDE_CROWDED = 0.02  # and the pressure of too many people, if you are not

# ---- conditions ---------------------------------------------------------
# The two sealed worlds. Same people, same decision function; different
# conditions. Everything that used to be a separate story script lives
# here as a number.

CONDITIONS = {
    "EDEN": {
        "food": "provisioned",     # the resort fills the hoppers. It is free.
        "abundance": 1.0,          # how much a site gives
        "crowding": 1.0,           # how many share a space
        "violence": 0.45,          # how often a quarrel becomes a killing
        "tech_floor": ["fire", "stone_tools"],
        "must_work_to_eat": False,  # no: that is the whole point of EDEN
        "night_sleep": 0.75,       # share of the unurgent who turn in
        "work_drive": 0.0,         # nothing to build: the resort is finished
        "comfort_eat": 0.5,        # appetite fills a day nothing else fills
        "social": 1.5,             # how much a person wants company
        "posts": True,             # are there posts to keep?
        "party": False,            # do people work in parties?
        "mate": "free",            # free of bonds, or only with a partner
        "fight": 0.6,              # how readily a quarrel becomes a fight
    },
    "LAGOON": {
        "food": "wild",
        "abundance": 0.45,
        "crowding": 0.3,
        "violence": 1.0,
        "tech_floor": [],
        "must_work_to_eat": True,
        "night_sleep": 0.85,
        "work_drive": 0.6,
        "comfort_eat": 0.0,
        "social": 1.1,
        "posts": False,
        "party": True,
        "mate": "bonded",
        "fight": 0.0,      # LAGOON's violence is resolved by its own law
    },
}

HUNGRY = 14.0            # hunger at which food is all a body wants
CROWD_FACES = 8.0        # faces within five paces that still feel like company

# How far a person will walk for a meal, in tiles. LAGOON is a big island
# and food is scarce in it; EDEN's bars are close and always there.
REACH = {"EDEN": 18, "LAGOON": 26}

# A meal, and what it costs the body to eat it.
MEAL = 12.0              # hunger removed per meal
MEAL_CARRY = 24.0        # how much one trip brings home
CARRY_PER_DAY = 8.0      # what a worker brings back for the camp


def _cos(deg):
    import math
    return math.cos(math.radians(deg))


def _sin(deg):
    import math
    return math.sin(math.radians(deg))


def _age(u, p):
    """Age in years. A person carries a birth day, not an age."""
    return (u.get("day", 0) - p.get("b", 0)) / 360.0


def near_count(u, p):
    """How many others are within about five paces: the 3x3 block of
    4-tile cells around this person, from the tick's density grid."""
    dens = (u.get("_ctx") or {}).get("dens")
    if dens is None:
        return sum(1 for q in u.get("people", []) if q is not p
                   and abs(q.get("x", 0) - p.get("x", 0)) <= 5
                   and abs(q.get("y", 0) - p.get("y", 0)) <= 5)
    gx, gy = p.get("x", 0) >> 2, p.get("y", 0) >> 2
    n = sum(dens.get((gx + dx) * 4096 + gy + dy, 0) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    return max(0, n - 1)


def cond_of(u):
    return CONDITIONS.get(u.get("kind", "LAGOON"), CONDITIONS["LAGOON"])


# ---- places -------------------------------------------------------------

def make_sites(u, rng=None, camps=None):
    """The places in this world that hold food, and how much is in them.

    LAGOON gets wild places: berries in the woods, fish in the shallows,
    game in the deep woods. EDEN gets the four hoppers, which the resort
    keeps filled — that is the condition of the world, and it is written
    down as one rather than left to look like a coincidence.
    """
    rng = rng or random.Random(u.get("seed", 69))
    if u.get("kind") == "EDEN":
        from engine import hoppers, eden_size
        sites = []
        for i, (hx, hy) in enumerate(hoppers(u)):
            sites.append({"x": hx, "y": hy, "kind": "hopper", "left": 900.0,
                          "max": 900.0, "regrow": 0.0, "provisioned": True,
                          "id": i})
        return sites
    # LAGOON: wild places, taken from the ground the band actually lives
    # on — near the camp, not scattered across an island nobody walks.
    from engine import terrain_of
    terr = terrain_of(u)
    sites = []
    kinds = ((1, "plants", 150.0, 12.0),   # woods: berries
             (3, "fish", 180.0, 10.0))     # the shallows
    # (game is not a place: it is the herds in animals.py, which move)
    for i, st in enumerate(u.get("settlements") or []):
        if camps is not None and i not in camps:
            continue
        cx, cy = st["x"], st["y"]
        for kind_id, kind, amount, regrow in kinds:
            spots = []
            for r in range(4, 34, 3):
                for a in range(0, 360, 20):
                    x = int(cx + r * _cos(a)) + rng.randint(-1, 1)
                    y = int(cy + r * _sin(a)) + rng.randint(-1, 1)
                    if 2 <= x < len(terr) - 2 and 2 <= y < len(terr) - 2 \
                            and terr[y][x] == kind_id:
                        spots.append((x, y))
                if len(spots) >= 8:
                    break
            rng.shuffle(spots)
            for x, y in spots[:8]:
                sites.append({"x": x, "y": y, "kind": kind, "left": amount,
                              "max": amount, "regrow": regrow,
                              "provisioned": False, "st": i})
    return sites


FARM_YIELD = 10.0        # what a worked field gives back in a growing day
FARM_HOLD = 160.0        # what a field holds at harvest


def ensure_sites(u, rng=None):
    if not u.get("sites"):
        u["sites"] = make_sites(u, rng)
    if any(s["kind"] == "game" for s in u["sites"]):
        # a world saved before animals.py had game as fixed places
        u["sites"] = [s for s in u["sites"] if s["kind"] != "game"]
    if u.get("kind") != "EDEN":
        # a camp founded later finds the wild places around its own hearths
        have = {s.get("st", 0) for s in u["sites"] if s["kind"] != "farm"}
        new = [i for i in range(len(u.get("settlements") or [])) if i not in have]
        if new:
            u["sites"].extend(make_sites(u, rng, camps=set(new)))
    # every tilled field is a place that holds food once it is sown
    have = {(s["x"], s["y"]) for s in u["sites"] if s["kind"] == "farm"}
    for fx, fy in u.get("farms") or []:
        if (fx, fy) not in have:
            u["sites"].append({"x": fx, "y": fy, "kind": "farm", "left": 0.0,
                               "max": FARM_HOLD, "regrow": FARM_YIELD,
                               "provisioned": False, "worked": None})
    return u["sites"]


def regrow_sites(u, days=1):
    """Wild places come back. Slowly, and not in EDEN, which is provisioned.

    And not evenly: in the lean season the groves do not fill, which is
    why a year has a hungry half and a fed half. The season is the
    world's, not the band's.
    """
    from engine import lagoon_season
    plant_mult, fish_mult, winter = lagoon_season(u.get("day", 0))
    dry = 0.3 if u.get("drought", 0) > 0 else 1.0
    for s in u.get("sites") or []:
        if s.get("provisioned"):
            continue
        season = fish_mult if s["kind"] == "fish" else plant_mult
        k = season * (dry if s["kind"] in ("plants", "farm") else 1.0)
        if s["kind"] == "farm":
            # a field grows only if it was worked: tending is the sowing
            k *= 1.0 if s.get("worked") is not None and s["worked"] >= u.get("day", 0) - 30 else 0.0
            k *= 0.25 if season < 1.0 else 1.0
        s["left"] = min(s["max"], s["left"] + s["regrow"] * days * k)


def _field_to_work(u, p, reach):
    best, bd = None, reach * reach
    for s in u.get("sites") or []:
        if s["kind"] != "farm":
            continue
        d = (s["x"] - p.get("x", 0)) ** 2 + (s["y"] - p.get("y", 0)) ** 2
        if d < bd:
            best, bd = s, d
    return best


def nearest_site(u, p, kind, reach):
    """The best place of this kind within reach, by distance."""
    best = None
    bd = reach * reach
    px, py = p.get("x", 0), p.get("y", 0)
    for s in u.get("sites") or []:
        if s["kind"] != kind or s["left"] <= 0:
            continue
        d = (s["x"] - px) ** 2 + (s["y"] - py) ** 2
        if d < bd:
            bd = d
            best = s
    return best, (bd ** 0.5 if best else None)


# ---- the body -----------------------------------------------------------

def meters(u, p, day, rng, cond):
    """Update the personal meters. Nobody else's body is touched."""
    hun = p.get("hun", 0.0)
    ene = p.get("ene", 1.0)
    sol = p.get("sol", 1.0)

    # These are rates per day, and this runs once per part, so they are
    # divided by the number of parts in a day. (This is the bug that made
    # LAGOON starve in its ninth year, in a different engine.)
    D = PARTS_PER_DAY

    # hunger: it comes back whether or not the world is kind
    hun += HUNGER_PER_DAY * (1.0 + 0.6 * _workload(u, p)) / D
    # energy: work and travel cost it, and it does not come back by itself
    import minds
    act = p.get("a")
    if act in minds.WORK_ACTS:
        ene -= ENERGY_PER_WORK / D
    elif act in (minds.A_TALK, minds.A_GROOM, minds.A_PLAY, minds.A_FIGHT):
        ene -= ENERGY_PER_SOCIAL / D
    if (p.get("x"), p.get("y")) != (p.get("tx"), p.get("ty")):
        ene -= ENERGY_PER_TRAVEL / D

    # solitude: being alone in a crowd is worse than being alone in a wood
    near = near_count(u, p)
    # Company restores, up to a band's worth of faces. Past that the
    # contacts are unchosen, and they wear instead of mend: Calhoun read
    # his withdrawn mice as animals overwhelmed by encounters they could
    # not refuse (Calhoun 1962; RESEARCH.md §1).
    excess = max(0.0, near - CROWD_FACES) / CROWD_FACES
    if near <= 0:
        sol -= SOLITUDE_PER_DAY / D
    else:
        sol = min(SOLITUDE_MAX, sol + 0.12 * min(near, 4) * max(0.0, 1.0 - excess) / D)
    if p.get("p") is not None:
        # a bond is company, even when it is the only one there is
        sol = min(SOLITUDE_MAX, sol + 0.06 / D)
    if excess > 0:
        sol -= SOLITUDE_CROWDED * min(3.0, excess) * cond.get("crowding", 0.5) / D

    # sleep and rest give it back, part by part, wherever the body lies
    if act == minds.A_SLEEP:
        ene += SLEEP_PER_PART
    elif act == minds.A_REST:
        ene += SLEEP_PER_PART * 0.4

    p["hun"] = max(0.0, min(HUNGER_MAX * 1.2, hun))
    p["ene"] = max(0.0, min(ENERGY_MAX, ene))
    p["sol"] = max(0.0, min(SOLITUDE_MAX, sol))


def _workload(u, p):
    """How hard this person's body is working, for the cost of a meal."""
    a = _age(u, p)
    bmi = p.get("bmi", 22)
    sn = p.get("sn", 0.5)
    if a < 16:
        return 0.6
    if a > 55:
        return 0.8
    if bmi >= 30:
        return 0.5                       # fat is a burden
    if bmi < 18:
        return 0.7                       # thin is a burden
    if sn >= 0.7:
        return 0.8                       # strong is a gift
    return 1.0


def body_capacity(p):
    """How much a person can do, given what they are made of.

    This is the answer to "bodies must matter": a starved or injured body
    works less and eats less, and now it is a number in the model rather
    than a number in a picture.
    """
    cap = 1.0
    cap *= 0.55 + 0.9 * min(1.0, p.get("ene", 1.0))
    cap *= 1.0 - 0.35 * min(1.0, p.get("hun", 0.0) / HUNGER_MAX)
    cap *= 1.0 - 0.4 * min(1.0, p.get("inj", 0.0))
    if p.get("bmi", 22) >= 32:
        cap *= 0.85
    if p.get("bmi", 22) < 17:
        cap *= 0.9
    return max(0.15, min(1.0, cap))


# ---- the night ------------------------------------------------------------

NIGHT_WORK_HUNGER = 28.0   # only this hungry does anybody keep working in the dark
NIGHT_KEEP = None          # acts the night does not interrupt; set on first use


def night(u, p, rng, part):
    """At dusk the day's work ends; at night the body sleeps.

    Where it sleeps is where it is: at the hearth if it is home, out at the
    patch if the stint is far from camp. Only the starving keep at it, and
    the dark costs them (the engine makes the big cat bolder at night).
    In the morning everybody decides again: a stint is a run of days, not
    a vow.
    """
    import minds
    global NIGHT_KEEP
    if NIGHT_KEEP is None:
        NIGHT_KEEP = (minds.A_WATCH, minds.A_BIRTH, minds.A_WITHDRAW, minds.A_TEND,
                      minds.A_MATE)
    if part != PARTS_PER_DAY - 1:
        if part == 0 and p.get("slept") and p.get("a") != minds.A_SLEEP:
            p.pop("slept", None)      # something else got them up first
            p.pop("was", None)
        if part == 0 and p.get("a") == minds.A_SLEEP and p.get("slept"):
            p.pop("slept", None)
            was = p.pop("was", None)
            if was and p.get("hun", 0.0) < HUNGRY:
                # a stint is a run of days: they get up and go on with it
                p["a"], p["tx"], p["ty"], p["ad"] = was
            else:
                p["ad"] = 0      # morning: decide again
                p["tx"], p["ty"] = p["x"], p["y"]
        return
    if p.get("a") in NIGHT_KEEP:
        return
    if p.get("hun", 0.0) > NIGHT_WORK_HUNGER and p.get("a") in minds.WORK_ACTS:
        return
    if p.get("a") == minds.A_EAT and p.get("hun", 0.0) > EAT_AT:
        return                   # nobody goes to bed on the way to dinner
    if p.get("a") in minds.WORK_ACTS and p.get("ad", 0) > 0:
        p["was"] = [p["a"], p["tx"], p["ty"], p["ad"]]
    h = hut_of(u, p)
    if h is not None and h["done"] and at_camp(u, p):
        p["tx"], p["ty"] = h["x"], h["y"]      # their own roof
    elif at_camp(u, p) or camp_of(u, p) is None:
        p["tx"], p["ty"] = _home_of(u, p)
    else:
        p["tx"], p["ty"] = p["x"], p["y"]    # sleeping out
    p["a"], p["ad"], p["slept"] = minds.A_SLEEP, 2, 1   # outlasts the night part


# ---- the decision --------------------------------------------------------

def assign(u, p, day, rng, cond=None, engine=None):
    """One decision for one person, in either world.

    Read the body; perceive the places; score what it could do against
    what it needs and what the doing would cost; commit to one thing.

    The roulette survives only as noise inside the scoring, not as the
    policy itself. That is the whole difference: a weighted choice between
    labels is a story, and a score against a need is a life.
    """
    cond = cond or cond_of(u)
    E = engine  # the activity codes; passed in so this module stays alone
    if E is None:
        import engine as E

    a = _age(u, p)
    hun = p.get("hun", 0.0)
    ene = p.get("ene", 1.0)
    sol = p.get("sol", 1.0)
    reach = REACH.get(u.get("kind"), 24)

    # What the body wants, as three numbers between 0 and 1. Food is
    # wanted twice over: by this belly, and by a camp whose store is low.
    # Foragers do not wait to starve before they go out; they go because
    # the band will eat tomorrow what is brought in today, and the larder
    # is everyone's to keep (Lee and DeVore, Man the Hunter, 1968).
    want_food = min(1.0, hun / HUNGRY)
    if cond.get("must_work_to_eat") and a >= 12:
        want_food = max(want_food, 0.75 * larder_short(u, p))
    want_rest = 1.0 - ene
    want_company = 1.0 - sol

    options = []   # (score, activity, target)

    # --- food from the wild ------------------------------------------------
    if cond.get("must_work_to_eat"):
        if _has(u, "stone_tools"):
            # the hunt: the nearest deer, wherever the herd has gone
            import animals
            deer = animals.nearest(u, p, animals.DEER, reach)
            if deer is not None:
                dist = ((deer["x"] - p.get("x", 0)) ** 2 + (deer["y"] - p.get("y", 0)) ** 2) ** 0.5
                # gathering feeds a band; meat is the prize, not the diet
                # (!Kung: ~60-70% plant food — Lee 1979)
                score = want_food * 1.3 * (1.0 - 0.5 * dist / float(reach))
                if p.get("s") == "m" and 16 <= a <= 35:
                    score *= 1.3             # young men's prestige as much as meat
                options.append((score, E.A_HUNT, (deer["x"], deer["y"]), None))
        for kind, act in (("plants", E.A_FORAGE), ("fish", E.A_FISH)):
            if kind == "fish" and not _has(u, "fishing"):
                continue
            site, dist = nearest_site(u, p, kind, reach)
            if site is None:
                continue
            # Hunger is the strongest thing in a body: going to get food
            # beats everything else when the belly is empty. Beyond that the
            # further it is, the less it is worth, and the more there is
            # left, the better it is.
            score = want_food * 2.2 * (0.6 + 0.8 * cond.get("abundance", 0.5))
            score *= 1.0 - 0.5 * (dist / float(reach))
            score *= 0.4 + 0.6 * (site["left"] / max(1.0, site["max"]))
            options.append((score, act, (site["x"], site["y"]), site))

        if _has(u, "agriculture"):
            # a field wants work before it gives food: tend it while it
            # grows, and harvest when it is ripe (Diamond, ch. 6)
            field = _field_to_work(u, p, reach)
            if field is not None:
                ripe = field["left"] / field["max"]
                score = (0.5 + 0.9 * want_food) * (0.6 + 0.8 * ripe) * cond.get("work_drive", 0.5) * 1.6
                options.append((score, E.A_FARM, (field["x"], field["y"]), field))

    # --- food already in the camp -----------------------------------------
    store = camp_store(u, p)
    if store > 0 and at_camp(u, p):
        # what is in the camp is worth less than going to get more
        # eating is for this belly only: the larder does not make you hungry
        eat_w = min(1.0, hun / HUNGRY) * 1.6
        if cond.get("comfort_eat") and hun > 2:
            # with nothing asked of you, a meal is something to do
            # (BOOKS.md: Frankl's existential vacuum; Freud on substitutes)
            eat_w += cond["comfort_eat"] * (1.0 - p.get("pu", 0.5)) * 0.6
        options.append((eat_w, E.A_EAT, _home_of(u, p), None))

    # --- sleep -------------------------------------------------------------
    # The body asks for rest when it is tired, and at night it asks harder.
    night = u.get("part", 0) == PARTS_PER_DAY - 1
    rest = want_rest * (1.4 if night else 0.8) * cond.get("night_sleep", 0.8)
    if night:
        rest += 0.25 * cond.get("night_sleep", 0.8)
    # but an empty belly keeps you up
    rest *= 1.0 - 0.75 * want_food
    options.append((rest, E.A_SLEEP, _home_of(u, p), None))

    # --- company -----------------------------------------------------------
    if want_company > 0.25:
        soc = cond.get("social", 1.0)
        # a hungry person does not stand about talking
        held = 1.0 - 0.6 * want_food
        options.append((want_company * 1.1 * soc * held, E.A_TALK, _home_of(u, p), None))
        options.append((want_company * 0.8 * soc * held, E.A_GROOM, _home_of(u, p), None))

    # --- work --------------------------------------------------------------
    # EDEN's people work for a place to be needed, not for food; LAGOON's
    # work for food is already in the options above, so this is the rest:
    # the posts, the building, the boat.
    if cond.get("must_work_to_eat") and _has(u, "shelter") and p.get("p") is not None \
            and a >= 16:
        h = hut_of(u, p)
        if h is None or not h["done"]:
            h = h or hut_of(u, p, make=True)
            options.append((cond.get("work_drive", 0.5) * 0.9 * (1.0 - 0.8 * want_food)
                            * (0.5 + 0.5 * ene), E.A_BUILD, (h["x"], h["y"]), None))
    if cond.get("work_drive") > 0 and u.get("boat"):
        # the boat: work for a shore nobody has seen, when nothing is wrong
        options.append((cond.get("work_drive", 0.3) * 0.5
                        * (0.4 + 0.6 * _has(u, "lore")) * (1.0 - 0.7 * want_food),
                        E.A_BUILD, _home_of(u, p), None))
    if cond.get("posts") and p.get("role") is not None:
        # a post to keep: the only thing in EDEN that is worth doing
        options.append(((0.9 + 0.6 * (p.get("pu", 0.5))) * (1.0 - 0.9 * want_food),
                        E.A_WORK, _home_of(u, p), None))
    if cond.get("party") and want_food > 0.15:
        # nobody works alone: if a party left lately for a place that still
        # holds food, go where they went (the pull of company on the work)
        party = _party_of(u, p)
        if party is not None:
            site = next((s for s in u.get("sites") or [] if s["x"] == party["x"]
                         and s["y"] == party["y"] and s["left"] > 0), None)
            if site is not None:
                options.append((want_food * 2.0 + 0.2 * want_company, party["a"],
                                (site["x"], site["y"]), site))

    # --- mating, for those who can -----------------------------------------
    if p.get("p") is not None and not u.get("innocent") and 16 <= a <= 45:
        # an empty belly is not an invitation, and a tired body less of one
        options.append(((0.3 + 0.3 * want_company) * (1.0 - 0.85 * want_food)
                        * (0.4 + 0.6 * ene),
                        E.A_MATE, _home_of(u, p), None))

    if cond.get("mate") == "free" and p.get("p") is None and not u.get("innocent") \
            and 16 <= a <= 45:
        # the pen's mating is free of bonds: anyone near will do, while
        # easy pleasure has not yet dulled the wanting of it
        options.append(((0.3 + 0.3 * want_company) * (1.0 - 0.85 * want_food)
                        * (0.4 + 0.6 * ene) * (0.4 + p.get("pu", 0.5))
                        * max(0.2, 1.0 - u.get("ennui", 0.0)),
                        E.A_MATE, _home_of(u, p), None))

    # --- the placeless -----------------------------------------------------
    # No bed of one's own and no post: the floor is all there is. Milling
    # is the symptom Calhoun saw first, and here it is a consequence of
    # having no place, not of a phase having been reached.
    placeless = u.get("kind") == "EDEN" and (p.get("box") is None or p["box"] < 0) \
        and p.get("role") is None
    if placeless and a >= 16:
        options.append((0.45 * (1.2 - p.get("pu", 0.5)), E.A_WALK, None, None))

    # --- fighting ----------------------------------------------------------
    # A quarrel in a crowded pen is a fight; in a wood with two people in it,
    # it is a quarrel. This is the difference between the worlds, and it is a
    # number, not a script.
    if cond.get("fight", 0.0) > 0:
        temper = _aggression(p) * 2.0 * (1.3 - _self_control(p, a))
        # more than a band's worth of faces within five paces is a crowd
        excess = max(0.0, near_count(u, p) - CROWD_FACES) / CROWD_FACES
        weight = cond.get("fight") * excess * temper
        weight *= 1.0 - 0.6 * want_food
        # the dispossessed fight; those with a place defend it less often
        weight *= 1.0 if placeless else 0.35
        # almost all killers are men (Pinker, Better Angels, ch. 9)
        weight *= 1.0 if p.get("s") == "m" else 0.15
        if weight > 0.4:
            options.append((weight, E.A_FIGHT, (p.get("x", 0), p.get("y", 0)), None))

    # --- the withdrawal ----------------------------------------------------
    # A person with no company, no purpose and no work does not stay in the
    # middle of the pen. This is Calhoun's beautiful ones, and it is a
    # consequence here, not a script: it needs solitude, a low purpose and
    # a world that does not ask anything of you.
    if u.get("kind") == "EDEN" and sol < 0.25 and hun < 8 and p.get("pu", 0.5) < 0.25:
        options.append((2.0 + 1.4 * (0.25 - sol), E.A_WITHDRAW, None, None))

    if not options:
        options.append((0.3, E.A_REST, _home_of(u, p), None))

    # the score picks; the roulette only breaks near ties
    options.sort(key=lambda o: -o[0])
    best = options[0]
    if len(options) > 1 and options[1][0] > 0:
        top = [o for o in options if o[0] >= best[0] * 0.85]
        best = top[min(len(top) - 1, int(rng.random() * len(top)))]

    score, act, target, site = best
    p.pop("was", None)        # a fresh decision replaces any paused stint
    p["a"] = act
    p["ad"] = _duration(act, rng)
    if target is not None:
        p["tx"], p["ty"] = target
    if site is not None:
        p["site"] = [site["x"], site["y"]]
        st = camp_of(u, p)
        if cond.get("party") and st is not None:
            party = st.get("party")
            if not party or u.get("day", 0) - party.get("d", 0) > 3:
                st["party"] = {"d": u.get("day", 0), "a": act,
                               "x": site["x"], "y": site["y"], "n": 1}
            elif party["x"] == site["x"] and party["y"] == site["y"]:
                party["n"] = party.get("n", 0) + 1     # one more joins
    return act


def _duration(act, rng):
    """How long a stint lasts, in days, for the work that matters."""
    from engine import days
    if act == 3:                # hunt: a day or two on a herd's trail
        return days(rng.randint(1, 2))
    if act in (2, 4):           # forage, fish: a proper stint
        return days(rng.randint(7, 15))
    if act == 5:                # farm
        return days(rng.randint(5, 12))
    if act == 6:                # build
        return days(rng.randint(4, 9))
    if act == 12:               # eat
        return days(1)
    if act == 17:               # sleep
        return days(rng.randint(1, 2))
    if act in (8, 7, 21):       # mate, talk, groom: an hour, not a week
        return rng.randint(1, 2)
    return days(rng.randint(1, 3))


def _has(u, tech):
    return tech in (u.get("tech") or [])


def _aggression(p):
    try:
        import minds
        return minds.aggression(p)
    except Exception:
        return 0.5


def _self_control(p, age):
    try:
        import minds
        return minds.self_control(p, age)
    except Exception:
        return 0.5


def _party_of(u, p):
    """The working party this person could join, if one left recently."""
    st = camp_of(u, p)
    if st is None:
        return None
    party = st.get("party")
    if not party or u.get("day", 0) - party.get("d", 0) > 3 or party.get("n", 0) >= 14:
        return None
    return party       # read-only: joining is counted only on commitment


def _home_of(u, p):
    return p.get("hx", p.get("x", 0)), p.get("hy", p.get("y", 0))


LARDER_DAYS = 4.0        # how many days of food a band likes to have in

def larder_short(u, p):
    """How far the camp's store is from a few days' food: 0 full, 1 empty."""
    st = camp_of(u, p)
    if st is None:
        return 0.0
    mouths = st.get("mouths") or 1
    return max(0.0, 1.0 - st.get("store", 0.0) / (mouths * HUNGER_PER_DAY * 1.5 * LARDER_DAYS))


SPOIL = {"none": 0.04, "preservation": 0.008, "granary": 0.002}   # of the store, per day


def keep_stores(u):
    """Once a day: count the camps' mouths, and let food rot. Food does not
    keep without the craft to keep it, and a camp cannot hoard what spoils."""
    tech = u.get("tech") or []
    keeps = "preservation" in tech or "preserve" in (u.get("lessons") or [])
    rot = SPOIL["granary"] if "granary" in tech else (
        SPOIL["preservation"] if keeps else SPOIL["none"])
    count = {}
    for q in u.get("people", []):
        count[q.get("st", 0)] = count.get(q.get("st", 0), 0) + 1
    for i, st in enumerate(u.get("settlements") or []):
        st["mouths"] = count.get(i, 0)
        st["store"] = max(0.0, st.get("store", 0.0) * (1.0 - rot))


# ---- huts ---------------------------------------------------------------
# Once shelter is known, each bonded pair raises a hut of its own at the
# camp: days of cutting poles and thatching. A finished hut is where the
# pair sleeps, and a big cat does not go in after them (animals._guarded).

HUT_WORK = 10.0          # person-days to raise a hut


def hut_of(u, p, make=False):
    """The hut of this person's pair, made on first ask if make is True."""
    st = camp_of(u, p)
    if st is None:
        return None
    pair = p.get("p")
    if pair is None:
        return None
    key = min(p["id"], pair)
    huts = st.setdefault("huts", [])
    for h in huts:
        if h["own"] == key:
            return h
    if not make:
        return None
    import math
    from engine import terrain_of
    terr = terrain_of(u)
    n = len(terr)
    taken = {(h["x"], h["y"]) for h in huts}
    k = len(huts)
    x = y = None
    for tries in range(60):                   # dry ground, not on another hut
        ring = st.get("r", 5) + 1 + ((k + tries) // 10) * 2
        ang = (k + tries) * 2.39996           # the golden angle: no two huts on top
        cx = int(round(st["x"] + math.cos(ang) * ring))
        cy = int(round(st["y"] + math.sin(ang) * ring))
        if 1 <= cx < n - 1 and 1 <= cy < n - 1 and terr[cy][cx] != 2 \
                and (cx, cy) not in taken:
            x, y = cx, cy
            break
    if x is None:
        x, y = st["x"], st["y"]
    h = {"own": key, "x": x, "y": y, "w": 0.0, "done": False}
    huts.append(h)
    return h


# ---- the camp's store ----------------------------------------------------

def camp_of(u, p):
    """The camp a person belongs to."""
    if u.get("kind") == "EDEN":
        return None
    si = min(p.get("st", 0), max(0, len(u.get("settlements") or []) - 1))
    sts = u.get("settlements") or []
    return sts[si] if sts else None


def at_camp(u, p):
    """Is this person standing at their camp?"""
    st = camp_of(u, p)
    if st is None:
        return True          # EDEN: the resort is everywhere
    r = st.get("r", 5) + 3
    return (abs(p.get("x", 0) - st["x"]) <= r and
            abs(p.get("y", 0) - st["y"]) <= r)


def camp_store(u, p):
    """How much food this person's camp is holding."""
    st = camp_of(u, p)
    if st is None:
        # EDEN: the resort's provision. It is free and it is always there.
        return 900.0
    return st.get("store", 0.0)


def carry_food(p, amount, kind):
    """Keep the source of an actual load; weight alone is not a carcass."""
    previous = p.get("carry", 0.0)
    p["carry_kind"] = kind if previous <= 0 or p.get("carry_kind") == kind else "mixed"
    p["carry"] = previous + amount


def add_to_store(u, p, amount):
    """Put food in the camp's store, for a camp that keeps one."""
    st = camp_of(u, p)
    if st is None:
        return
    st["store"] = st.get("store", 0.0) + amount


# ---- the work ------------------------------------------------------------

EAT_AT = 6.0             # hunger at which a person with food at hand eats
NURSING_COST = 0.6       # what a nursing mother's body pays per unit the infant takes


def _take(pantry, amount):
    """Take up to amount out of a pantry: a site, or a camp. What is taken
    is gone from it; nothing is eaten that nobody had."""
    got = max(0.0, min(pantry.get("left", pantry.get("store", 0.0)), amount))
    if "left" in pantry:
        pantry["left"] -= got
    else:
        pantry["store"] = pantry.get("store", 0.0) - got
    return got


def _pantry_at(u, p):
    """The food within this person's reach right now: the site they stand
    on, or their camp's store. EDEN's hoppers are the resort's, and free."""
    import minds
    s = _site_at(u, p) if p.get("a") in KIND_OF_ACT else None
    if s is not None and (s["kind"] == "game" and not _has(u, "stone_tools")
                          or s["kind"] == "fish" and not _has(u, "fishing")):
        s = None
    if s is not None and s["left"] > 0:
        return s             # a gatherer eats as she gathers
    st = camp_of(u, p)
    if st is not None and at_camp(u, p) and st.get("store", 0.0) > 0:
        return st
    return None


def eat(u, p, age_years=None):
    """The reflex: a hungry body with food at hand eats it. Run every part
    for everybody. Infants are fed by their mothers, and the mother pays."""
    a = _age(u, p) if age_years is None else age_years
    if p.get("hun", 0.0) <= EAT_AT:
        return 0.0
    if a < 3:
        byid = (u.get("_ctx") or {}).get("byid")
        m = (byid.get(p.get("mom")) if byid is not None else
             next((q for q in u.get("people", []) if q["id"] == p.get("mom")), None))
        if m is not None and m.get("hun", 0.0) <= HUNGER_MAX * 0.75:
            got = min(p["hun"], MEAL * 0.5)
            p["hun"] -= got
            m["hun"] = m.get("hun", 0.0) + got * NURSING_COST
            return got
        if a < 0.5:
            return 0.0           # a newborn with no milk to be had
        # an orphan past six months is fed by the camp, as a band does
    if u.get("kind") == "EDEN":
        return 0.0               # EDEN eats at its hoppers; see fulfil
    if p.get("carry", 0.0) > 0:
        # nobody starves holding food: eat from the load first
        got = min(p["carry"], p["hun"], MEAL * body_capacity(p))
        p["carry"] -= got
        if p["carry"] <= 0:
            p["carry_kind"] = None
        p["hun"] -= got
        return got
    pantry = _pantry_at(u, p)
    if pantry is None:
        return 0.0
    got = _take(pantry, min(p["hun"], MEAL * body_capacity(p)))
    p["hun"] -= got
    return got


def fulfil(u, p, day, rng, act, E=None):
    """What actually happened when the person arrived and did the thing.

    This is where the world changes, and it is only here: a person who
    reaches a berry patch and works it takes berries and carries them home;
    a person who reaches a hopper eats from it; a person who sleeps is less
    tired. Nothing happens because there were adults.
    """
    if E is None:
        import engine as E
    cap = body_capacity(p)

    if act == E.A_EAT and u.get("kind") == "EDEN":
        # the resort's hoppers: free, and always full. That is the premise.
        p["hun"] = max(0.0, p.get("hun", 0.0) - MEAL)
        return MEAL

    if act in (E.A_FORAGE, E.A_FISH, E.A_FARM):
        site = _site_at(u, p)
        if site is None:
            return 0
        kind = site["kind"]
        if kind == "game" and not _has(u, "stone_tools"):
            return 0
        if kind == "fish" and not _has(u, "fishing"):
            return 0
        if kind == "farm":
            site["worked"] = u.get("day", 0)
        eat(u, p)                    # they eat there first, if hungry
        got = _take(site, CARRY_PER_DAY * cap)
        if got <= 0 and kind == "farm":
            return 0                 # tending a field that is not yet ripe
        if got <= 0:
            p["ad"] = 0              # picked over: decide again at once
            return 0
        carry_food(p, got, kind)
        return got

    if act == E.A_BUILD:
        h = hut_of(u, p)
        if h is not None and not h["done"] and abs(p["x"] - h["x"]) <= 1 \
                and abs(p["y"] - h["y"]) <= 1:
            h["w"] += cap
            if h["w"] >= HUT_WORK:
                h["done"] = True
                p["ad"] = 0
            return 1
        boat = u.get("boat")
        if boat and abs(p["x"] - boat["x"]) <= 3 and abs(p["y"] - boat["y"]) <= 3:
            boat["work"] = boat.get("work", 0) + cap    # a day's work, as strong as the body
            return 1
        return 0

    if act in (E.A_TALK, E.A_GROOM):
        p["sol"] = min(SOLITUDE_MAX, p.get("sol", 0.0) + 0.2)
        for q in u.get("people", []):
            if q is p:
                continue
            if abs(q.get("x", 0) - p.get("x", 0)) <= 4 and abs(q.get("y", 0) - p.get("y", 0)) <= 4:
                q["sol"] = min(SOLITUDE_MAX, q.get("sol", 0.0) + 0.1)
        return 1

    return 0


KIND_OF_ACT = {2: "plants", 4: "fish", 5: "farm"}   # forage, fish, farm (the hunt follows animals)


def _site_at(u, p, kind=None):
    """The site of this kind a person is standing on, if any. The kind is
    the work they are doing: a berry picker does not eat the deer."""
    kind = kind or KIND_OF_ACT.get(p.get("a"))
    best = None
    for s in u.get("sites") or []:
        if kind is not None and s["kind"] != kind:
            continue
        if abs(s["x"] - p.get("x", 0)) <= 1 and abs(s["y"] - p.get("y", 0)) <= 1:
            if best is None or s["left"] > best["left"]:
                best = s     # of two bushes at hand, the fuller one
    return best


def deposit(u, p, day):
    """Carry what you have gathered back to the camp and put it down."""
    carried = p.get("carry", 0.0)
    if carried <= 0:
        return 0
    st = camp_of(u, p)
    if st is None:
        p["carry"] = 0.0
        p["carry_kind"] = None
        return 0
    if abs(p.get("x", 0) - st["x"]) > st.get("r", 5) + 3 or \
       abs(p.get("y", 0) - st["y"]) > st.get("r", 5) + 3:
        return 0            # not home yet
    add_to_store(u, p, carried)
    p["carry"] = 0.0
    p["carry_kind"] = None
    return carried
