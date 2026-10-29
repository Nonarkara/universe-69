"""The animals of LAGOON: herds of deer and the big cats that follow them.

Before this, the animals were two numbers in a dictionary. Predation was a
dice roll against every person, wherever they stood; the big-cat hunt was
a dice roll against every hunter; and the viewer invented deer to wander
about so that the hunt had something to look at. None of it had a place.

Here every animal is somewhere. A herd grazes the woods and runs from
people. A cat holds a range, eats deer, and only turns on people when the
deer have failed it — and even then it takes the one who is alone, out of
the firelight, unarmed. People can fight back: a group drives a cat off,
an armed adult can kill one that attacks, and once the band has learned to
hunt it, the cat is meat. The ecosystem can exhaust prey and can kill a vulnerable band; learning
changes particular risks without guaranteeing survival.

Sources for the shape, not the numbers: big cats kill people mostly when
prey is short or the cat is old or hurt, and mostly people who are alone
(Packer et al. 2005, Nature 436:927, on Tanzanian lions); groups and fire
deter (Treves & Naughton-Treves 1999, J. Human Evolution 36:275). The
numbers are model calibration, recorded as such in DESIGN.md.

Standard library only, like the engine.
"""

from needs import carry_food

DEER, CAT = "deer", "cat"

DEER_START = 240           # the island's herds at genesis
DEER_PER_LAND = 0.08       # carrying capacity: deer per tile of grass or wood
DEER_R = 0.6               # yearly growth at low density
CATS_START = 3
PREY_PER_CAT = 120         # a cat needs this many deer around it to live
CAT_FEEDS = 8.0            # a lone big cat takes a deer-sized kill about once a week
CAT_HUNGRY = 16.0          # days without a kill before a cat looks at people
CAT_STARVES = 45.0         # days without food before it dies
MEAT_DEER = 36.0           # food from one deer, carried home
MEAT_CAT = 24.0

DEER_STEP = 3              # tiles a part; they flee faster
CAT_STEP = 4
FLEE = 4                   # a herd moves off when people are this close
STALK = 6                  # how far a cat sees prey or a person
CROWD = 3                  # this many adults together are not prey
FIRE_RANGE = 7             # a lit camp at night: cats keep out


def _d2(a, b):
    return (a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2


def _land(terr, x, y):
    n = len(terr)
    return 1 <= x < n - 1 and 1 <= y < n - 1 and terr[y][x] != 2


def _woods(terr):
    return [(x, y) for y in range(len(terr)) for x in range(len(terr))
            if terr[y][x] == 1]


def ensure(u, rng, terr):
    """Seed the animals once: herds in the woods, cats among them."""
    if u.get("animals") is not None:
        return u["animals"]
    woods = _woods(terr)
    rng.shuffle(woods)
    animals, nid = [], 1
    herds = woods[:max(1, DEER_START // 8)]
    for hx, hy in herds:
        for _ in range(8):
            x, y = hx + rng.randint(-2, 2), hy + rng.randint(-2, 2)
            if _land(terr, x, y):
                animals.append({"i": nid, "k": DEER, "x": x, "y": y, "tx": x, "ty": y})
                nid += 1
    for hx, hy in woods[len(herds):len(herds) + CATS_START]:
        animals.append({"i": nid, "k": CAT, "x": hx, "y": hy, "tx": hx, "ty": hy,
                        "hx": hx, "hy": hy, "fed": 0.0})
        nid += 1
    u["animals"] = animals
    u["animal_id"] = nid
    return animals


def counts(u):
    a = u.get("animals") or []
    deer = sum(1 for q in a if q["k"] == DEER)
    return deer, len(a) - deer


def nearest(u, p, kind, reach, terr=None):
    from engine import terrain_of, same_land
    terr = terrain_of(u) if terr is None else terr
    best, bd = None, reach * reach
    for q in u.get("animals") or []:
        if q["k"] != kind:
            continue
        d = _d2(q, p)
        if d < bd and same_land(terr, p["x"], p["y"], q["x"], q["y"]):
            best, bd = q, d
    return best


def _step(q, terr, speed):
    for _ in range(speed):
        dx, dy = q["tx"] - q["x"], q["ty"] - q["y"]
        if not dx and not dy:
            return
        nx = q["x"] + (dx > 0) - (dx < 0)
        ny = q["y"] + (dy > 0) - (dy < 0)
        if not _land(terr, nx, ny) or (nx != q["x"] and ny != q["y"] and
                (terr[q["y"]][nx] == 2 or terr[ny][q["x"]] == 2)):
            q["tx"], q["ty"] = q["x"], q["y"]      # water: graze here instead
            return
        q["x"], q["y"] = nx, ny


def _people_near(people, q, r, terr=None):
    from engine import same_land
    r2 = r * r
    return [p for p in people if not p.get("ab") and _d2(p, q) <= r2 and
            (terr is None or same_land(terr, p["x"], p["y"], q["x"], q["y"]))]


def _sheltered(u, p):
    """Asleep under a finished roof of one's own."""
    for st in u.get("settlements") or []:
        for h in st.get("huts") or ():
            if h.get("done") and h["x"] == p["x"] and h["y"] == p["y"]:
                return True
    return False


def _seen(u, x, y, kind, ctx):
    """Keep the last few encounters, so the camera can find them."""
    enc = u.setdefault("encounters", [])
    enc.append([x, y, kind, ctx["day"], ctx["part"]])
    if len(enc) > 24:
        del enc[:-24]


def _guarded(u, q, night, has):
    """A lit camp at night, or a camp with a watch, keeps the cats out."""
    for st in u.get("settlements") or []:
        r = FIRE_RANGE + st.get("r", 5)
        if abs(st["x"] - q["x"]) <= r and abs(st["y"] - q["y"]) <= r:
            if (night and has("fire")) or st.get("watch"):
                return True
    return False


def tick(u, rng, terr, people, ctx):
    """One part of the animals' lives. Returns the people taken, as
    [(person, cause)], and appends to ctx["events"].

    ctx carries: day, part, night (bool), adult (callable p -> bool),
    has (callable tech -> bool), armed (bool), lessons (list).
    """
    from engine import same_land
    animals = ensure(u, rng, terr)
    night, has, adult = ctx["night"], ctx["has"], ctx["adult"]
    taken, dead_animals = [], set()
    events = ctx["events"]

    # --- the hunters strike first: they closed on the herd last part, and a
    # deer that has not yet bolted is the one that can be taken
    hunters = [p for p in people if not p.get("ab") and p.get("a") == ctx["A_HUNT"] and adult(p)]
    for p in hunters:
        if not ctx["armed"]:
            break
        if p.get("hun", 0.0) > 14.0:
            p["ad"] = 0              # too hungry to keep stalking: go and eat
            continue
        q = nearest(u, p, DEER, 12, terr)
        if has("predator_hunt"):
            # those who have learned to kill the big cat go after it, if it
            # is nearer than the herd: the danger is also the prize
            c = nearest(u, p, CAT, 12, terr)
            if c is not None and c["i"] not in dead_animals and (
                    q is None or _d2(c, p) < _d2(q, p)):
                p["tx"], p["ty"] = c["x"], c["y"]
                continue
        if q is None or q["i"] in dead_animals:
            continue
        p["tx"], p["ty"] = q["x"], q["y"]
        if _d2(p, q) <= 2:
            party = [h for h in hunters if h is not p and _d2(h, p) <= 9 and
                     same_land(terr, h["x"], h["y"], p["x"], p["y"])]
            # most stalks fail; more spears, better odds (Hadza: a big
            # kill every few weeks per hunter — Hawkes et al. 1991)
            if rng.random() < min(0.3, 0.05 + 0.05 * len(party)):
                dead_animals.add(q["i"])
                _seen(u, q["x"], q["y"], "deer_kill", ctx)
                share = MEAT_DEER / (1 + len(party))
                for h in [p] + party:
                    carry_food(h, share, DEER)
                    h["ad"] = 0                       # carry it home now

    # --- the herds: graze, drift together, run from people
    grid = {}                       # people by 4-tile cell, for the herds' alarm
    for p in people:
        if not p.get("ab"):
            grid.setdefault((p["x"] >> 2, p["y"] >> 2), []).append(p)
    for q in animals:
        if q["k"] != DEER:
            continue
        gx, gy = q["x"] >> 2, q["y"] >> 2
        near = [p for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                for p in grid.get((gx + dx, gy + dy), ()) if _d2(p, q) <= FLEE * FLEE]
        if near:
            p = near[0]
            q["tx"] = q["x"] + (q["x"] - p["x"]) * 2 + rng.randint(-1, 1)
            q["ty"] = q["y"] + (q["y"] - p["y"]) * 2 + rng.randint(-1, 1)
            _step(q, terr, DEER_STEP)
        elif rng.random() < 0.15:
            q["tx"], q["ty"] = q["x"] + rng.randint(-3, 3), q["y"] + rng.randint(-3, 3)
            _step(q, terr, 1)

    # --- the cats: hunt deer; when deer fail them, look at people
    deer_list = [q for q in animals if q["k"] == DEER]
    available_people = list(people)
    for c in animals:
        if c["k"] != CAT or c["i"] in dead_animals:
            continue
        c["fed"] = c.get("fed", 0.0) + 0.25           # a part is a quarter-day
        prey = None
        bd = STALK * STALK if c["fed"] >= CAT_FEEDS else 0
        for q in deer_list:
            if q["i"] in dead_animals:
                continue
            d = _d2(q, c)
            if d < bd and same_land(terr, q["x"], q["y"], c["x"], c["y"]):
                prey, bd = q, d
        if prey is not None:
            c["tx"], c["ty"] = prey["x"], prey["y"]
            _step(c, terr, CAT_STEP)
            if _d2(prey, c) <= 2 and rng.random() < 0.3:
                dead_animals.add(prey["i"])
                c["fed"] = 0.0
            continue
        if c["fed"] >= CAT_HUNGRY:
            target = _choose_person(u, c, available_people, night, has, adult, terr)
            if target is not None:
                c["tx"], c["ty"] = target["x"], target["y"]
                _step(c, terr, CAT_STEP)
                if _d2(target, c) <= 2:
                    outcome = _attack(u, c, target, available_people, rng, ctx, terr)
                    if outcome == "taken":
                        taken.append((target, "predator"))
                        available_people.remove(target)
                        c["fed"] = 0.0
                    elif outcome == "killed":
                        dead_animals.add(c["i"])
                continue
        # nothing to eat: roam the range, wider the hungrier
        if rng.random() < 0.25:
            r = 4 + int(c["fed"])
            c["tx"] = c.get("hx", c["x"]) + rng.randint(-r, r)
            c["ty"] = c.get("hy", c["y"]) + rng.randint(-r, r)
        _step(c, terr, 2)

    # --- the cat hunt, once they have learned it: a party with spears
    if has("predator_hunt"):
        alive_ids = {p["id"] for p in available_people}
        surviving_hunters = [p for p in hunters if p["id"] in alive_ids]
        for c in animals:
            if c["k"] != CAT or c["i"] in dead_animals:
                continue
            party = _people_near(surviving_hunters, c, 4, terr)
            if len(party) >= CROWD and rng.random() < 0.25:
                dead_animals.add(c["i"])
                _seen(u, c["x"], c["y"], "cat_hunt", ctx)
                for h in party:
                    carry_food(h, MEAT_CAT / len(party), CAT)
                u["kills"] = u.get("kills", 0) + 1
                events.append((ctx["day"], "LAGOON", "hunt",
                               "The hunters bring down a big cat. It is meat now, and "
                               "the carcass is brought back to camp."))

    if dead_animals:
        u["animals"] = [q for q in animals if q["i"] not in dead_animals]
    if ctx["part"] == 0:
        _daily(u, rng, terr, ctx)
    return taken


def _choose_person(u, c, people, night, has, adult, terr=None):
    """A hungry cat takes the easiest person it can see: alone, small, out of
    the firelight. A group is not prey."""
    if _guarded(u, c, night, has):
        return None
    best, bs = None, 0.0
    for p in _people_near(people, c, STALK, terr):
        if _sheltered(u, p):
            continue                                  # a roof and a door
        company = sum(1 for o in _people_near(people, p, 3, terr) if o is not p and adult(o))
        if company + (1 if adult(p) else 0) >= CROWD:
            continue
        ease = (2.0 if not adult(p) else 1.0) * (1.6 if night else 1.0)
        ease *= 1.3 - 0.6 * p.get("vg", 0.5)      # the watchful see it coming
        ease /= 1 + company
        if ease > bs:
            best, bs = p, ease
    return best


def _attack(u, c, p, people, rng, ctx, terr=None):
    """The cat strikes. 'taken', 'killed' (the people killed the cat), or
    'fled'."""
    adult = ctx["adult"]
    armed = ctx["armed"] and adult(p)
    defenders = [o for o in _people_near(people, p, 3, terr) if o is not p and adult(o)]
    kill_cat = (0.25 if armed else 0.05) + 0.2 * len(defenders)
    if "vigilance" in ctx["lessons"]:
        kill_cat += 0.1
    if rng.random() < min(0.8, kill_cat):
        _seen(u, p["x"], p["y"], "fought_off", ctx)
        u["kills"] = u.get("kills", 0) + 1
        carry_food(p, MEAT_CAT, CAT)
        if rng.random() < 0.5:
            ctx["events"].append((ctx["day"], "LAGOON", "hunt",
                                  f"A big cat springs at {p['n']}, who kills it."))
        return "killed"
    take = 0.55 if adult(p) else 0.85
    if armed:
        take *= 0.5
    take *= 1.0 - 0.5 * min(1.0, len(defenders) / 2.0)
    if rng.random() < take:
        _seen(u, p["x"], p["y"], "taken", ctx)
        if rng.random() < 0.3:
            ctx["events"].append((ctx["day"], "LAGOON", "predator",
                                  f"{p['n']} is taken by a big cat, alone at the wood's edge."))
        return "taken"
    _seen(u, p["x"], p["y"], "mauled", ctx)
    p["inj"] = min(1.0, p.get("inj", 0.0) + 0.35)    # mauled, and lives
    return "fled"


def _daily(u, rng, terr, ctx):
    """Once a day: cats starve, herds and cats breed toward what the land
    carries."""
    animals = u["animals"]
    deer, cats = counts(u)
    cap = max(20, int(DEER_PER_LAND * _grazing(u, terr)))
    survivors = []
    for q in animals:
        if q["k"] == CAT and q.get("fed", 0.0) >= CAT_STARVES:
            continue                                  # starved
        survivors.append(q)
    animals = survivors
    # births: logistic, spread over the year so nothing jumps
    born = 0
    p_deer = DEER_R / 360.0 * max(0.0, 1.0 - deer / cap)
    for q in list(animals):
        if q["k"] == DEER and rng.random() < p_deer:       # aggregate herd rate; sex is not tracked
            born += 1
            animals.append({"i": u["animal_id"], "k": DEER, "x": q["x"], "y": q["y"],
                            "tx": q["x"], "ty": q["y"]})
            u["animal_id"] += 1
    cat_cap = max(1, deer // PREY_PER_CAT)
    cats = sum(1 for q in animals if q["k"] == CAT)
    if cats < cat_cap and rng.random() < 0.3 / 360.0 * cats * 2:
        mother = next(q for q in animals if q["k"] == CAT)
        animals.append({"i": u["animal_id"], "k": CAT, "x": mother["x"], "y": mother["y"],
                        "tx": mother["x"], "ty": mother["y"],
                        "hx": mother["x"] + rng.randint(-15, 15),
                        "hy": mother["y"] + rng.randint(-15, 15), "fed": 0.0})
        u["animal_id"] += 1
    # Sealed land masses have no spontaneous replacement herds or cats.
    # Hunting/predation may eliminate a species; births need living parents.
    u["animals"] = animals


_WOODS = {}
_GRAZE = {}


def _grazing(u, terr):
    key = id(terr)
    if key not in _GRAZE:
        _GRAZE[key] = sum(1 for row in terr for v in row if v in (0, 1))
    return _GRAZE[key]


def _woods_cached(u, terr):
    key = id(terr)
    if key not in _WOODS:
        _WOODS[key] = _woods(terr)
    return _WOODS[key]
