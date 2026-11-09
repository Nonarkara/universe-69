"""The scripture of each world, read from its record.

BOOKS.md says what the books say. DESIGN.md says which findings became
mechanics. This file is the third voice: the world as its own testament —
the covenant its condition writes, the laws its dead left, the myths its
disasters earned, the cast a viewer follows like an ensemble.

Like `research.py`, this module **only ever reads**. It takes a universe
dict and returns plain JSON: no world state is created or changed, no RNG
is drawn, and every line it prints can be traced to a field the engine
already keeps. A scripture that could move a world would be a hymn the
observer wrote and blamed on the choir — the one dishonesty this file
will not commit.

Where the record is silent, the scripture says so. EDEN keeps no myths
and holds no laws; that emptiness is not a gap in the reading, it is the
experiment's own finding, stated out loud.

Standard library only, like the engine.
"""

import minds
from minds import (DAYS_PER_YEAR, ADULT_AGE, ELDER_AGE,
                   WK_HUDDLE, WK_BEAUTIFUL, WK_UPSTAIRS)

# The laws a dead LAGOON can leave its heirs. Each maps an inherited
# lesson tag (engine.LESSON_OF, taught to the next founding by
# tick_lagoon's reseed and the server's archive) to the law the living
# band now keeps — and to the tech whose discovery the lesson quickens
# (engine.LESSON_TECH, ×3). The law is a reading of the mechanic, not a
# new mechanic.
COMMANDMENTS_OF = {
    "preserve": ("Waste nothing. What the band kills, the band keeps.",
                 "preservation"),
    "vigilance": ("Keep the watch. The dark is when it comes.",
                  "stone_tools"),
    "cleanliness": ("Keep the camp clean. Sickness breeds where the rule is broken.",
                    "healing"),
    "unity": ("Hold together. A divided band buries its dead.", "lore"),
}

WK_WORDS = {WK_HUDDLE: "one of the placeless, pooled on the open floor",
            WK_BEAUTIFUL: "one of the beautiful ones: eats, sleeps, grooms, alone",
            WK_UPSTAIRS: "retreated to the highest boxes, and does not come down"}

# Bond thresholds, kept beside needs.py's own (a reading, not a second law)
FRIEND = 0.6
FEUD = -0.6

# The rhythms a viewer can set a watch by. Each row states a habit the
# engine really has, with the constant that makes it true. This is the
# engineered predictability — the reason a returning viewer knows what
# dawn will bring.
def rhythms(u):
    day = u.get("day", 0)
    rows = []
    rows.append(("Dawn, day, dusk, night", "the day is four parts; the dark half is for the fire and the bed"))
    if u.get("kind") == "LAGOON":
        rows.append(("The night watch", "one adult keeps it each night; the most vigilant take the most turns"))
        if (u.get("terrain_version", 1) or 0) >= 2:
            rows.append(("Two monsoons", "wet to day 180 and from day 270; the groves and the banks answer them"))
        else:
            rows.append(("Four seasons", "spring, summer, autumn, a winter that can starve the unprepared"))
        rows.append(("Midsummer", "a people with lore dances for its totem — when the year is not lean"))
        rows.append(("The fire", "a camp that keeps fire lit gathers at it after dark; stories are told there"))
        if u.get("tech") and "agriculture" in u["tech"]:
            rows.append(("The fields", "sown in the growing days; a field tended is a field that feeds"))
    else:
        rows.append(("The bars never close", "the hoppers are filled; eating needs no one's leave"))
        rows.append(("A post, once taken", "is held until death or withdrawal — the only scarce seats in the pen"))
        rows.append(("The dome", "opens onto new sand if the pen nears the sink; after two gifts, the walls are final"))
        rows.append(("Always spring", "no season, no storm; the climate is one of the provisions"))
    rows.append(("The reseed", "an empty world waits %d quiet years, then the Observers send eight pairs"
                 % __import__("engine").RESEED_YEARS))
    return rows


# What nobody in the pen can see coming. Each row names a hazard the
# engine really rolls, with the constant that sizes it — the engineered
# unpredictability. `cod` gives this world's own count so far, so the
# page reads as testament, not as documentation.
def hazards(u):
    kind = u.get("kind")
    cod = u.get("cod", {})
    rows = []
    def row(what, note, key):
        n = cod.get(key, 0)
        rows.append({"what": what, "note": note, "so_far": n})
    if kind == "LAGOON":
        row("A quarrel becomes a killing",
            "young unpaired men, hot temper, hungry camp; a grudge decays about 8% a year and is acted on when restraint fails",
            "violence")
        row("The big cat",
            "bolder in the dark (1.8x); a watched camp roughly halves it; the herd flees, the stalker waits",
            "predator")
        row("The lean season",
            "the groves do not fill; a camp that did not keep, buries", "starvation")
        row("Dry banks", "thirst beyond four days takes the young first", "dehydration")
        row("Childbirth",
            "about 1 in 50 mothers without a healer beside them; 13 in 100 births lost, 6 in 100 with",
            "childbirth")
        row("The lost", "a fall, a goring, a hunt gone wrong", "accident")
    else:
        row("A brawl near the hoppers",
            "temper times the crowd past eight faces; the placeless bleed for having no door to close",
            "violence")
        row("Harried nests",
            "a mother crowded at her bed may abandon or fail to raise what she bears",
            "infant")
        row("The sickness",
            "past a hundred people, free mating carries its own cost; a wary generation keeps its distance",
            "sickness")
        row("Starvation in a full pen",
            "it happens only to the withdrawn, who will not come to the bars", "starvation")
    row("Old age", "the one death the walls cannot hasten or refuse", "age")
    return rows


def _label_post(u, p):
    """A post's plain name from its place in the pen."""
    role = p.get("role")
    roles = u.get("roles") or []
    if role is None or role >= len(roles):
        return None
    k = roles[role].get("k")
    x, y = roles[role].get("x", 0), roles[role].get("y", 0)
    c = (u.get("size") or 48) / 2
    if k == "bar":
        wall = ("north" if y < c else "south") if abs(y - c) >= abs(x - c) else \
               ("west" if x < c else "east")
        return "bar staff, %s buffet" % wall
    if k == "pool":
        return "lifeguard"
    return "keeper of the lodgings"


def _kids_of(u):
    kids = {}
    for q in u.get("people", []):
        for key in ("mom", "dad"):
            pid = q.get(key)
            if pid is not None:
                kids[pid] = kids.get(pid, 0) + 1
    return kids


def _line(u, p, kids):
    """One line of the cast, every clause read from the record."""
    day = u.get("day", 0)
    a = (day - p.get("b", 0)) / DAYS_PER_YEAR
    bits = []
    post = _label_post(u, p)
    if post:
        bits.append(post)
    if p.get("w"):
        bits.append(WK_WORDS.get(p.get("wk"), "one of the withdrawn"))
    elif p.get("p") is not None:
        partner = next((q for q in u.get("people", []) if q.get("id") == p.get("p")), None)
        if partner is not None:
            bits.append("paired with %s" % partner.get("n", "?"))
    n = kids.get(p.get("id"), 0)
    if n:
        bits.append("%d %s" % (n, "child" if n == 1 else "children"))
    body = minds.body_words(p, day - p.get("b", 0))
    if body:
        bits.append(body)
    sk = [t for t, v in (p.get("skills") or {}).items() if (v or {}).get("level", 0) >= 0.5]
    if sk:
        bits.append("knows " + ", ".join(sorted(sk)[:3]))
    who = "; ".join(bits) if bits else "living their days"
    return {"name": p.get("n", "?"), "age": round(a, 1), "who": who}


def cast(u, limit=8):
    """The ensemble a viewer follows, chosen by the record's own weights.

    Every pick is a plain maximum over a field the engine keeps — eldest,
    most children, most skilled, the withdrawn by kind, the newest child —
    so the same state always names the same people, and the cast turns
    over exactly when the record says it should: by dying, pairing,
    learning or withdrawing.
    """
    day = u.get("day", 0)
    people = [q for q in u.get("people", []) if q.get("n")]
    if not people:
        return []
    kids = _kids_of(u)
    adults = [q for q in people if day - q.get("b", 0) >= ADULT_AGE]
    picked, seen = [], set()

    def take(q, why):
        if q is None or q["id"] in seen:
            return
        seen.add(q["id"])
        line = _line(u, q, kids)
        line["who"] = why + ": " + line["who"] if why else line["who"]
        picked.append(line)

    if adults:
        take(min(adults, key=lambda q: q.get("b", 0)), "the eldest")
    mothers = [q for q in adults if kids.get(q["id"], 0) > 0]
    if mothers:
        take(max(mothers, key=lambda q: kids.get(q["id"], 0)), "the most children")
    if u.get("kind") == "LAGOON":
        import skills
        qualified = [q for q in adults if not q.get("w")
                     and skills.qualified(q, "lore")]
        if qualified:
            take(max(qualified, key=lambda q: q.get("ef", .5)), "speaks for the band")
        skilled = [q for q in adults if not q.get("w") and len(q.get("skills") or {}) > 1]
        if skilled:
            take(max(skilled, key=lambda q: len(q.get("skills") or {})), "the most hands")
    else:
        posted = [q for q in adults if not q.get("w") and q.get("role") is not None]
        if posted:
            take(posted[0], "holds a post")
        if any(q.get("role") is not None for q in adults):
            second = [q for q in posted if q["id"] not in seen]
            if second:
                take(second[0], "holds a post")
    for kind in (WK_HUDDLE, WK_BEAUTIFUL, WK_UPSTAIRS):
        w = [q for q in adults if q.get("w") and q.get("wk") == kind]
        if w:
            take(w[0], None)
            break
    young = [q for q in people if u.get("named") and day - q.get("b", 0) < ADULT_AGE]
    if young:
        take(max(young, key=lambda q: q.get("b", 0)), "the youngest named")
    return picked[:limit]


def chronicle(u):
    """The storylines running right now, read from the people themselves.

    This is the page's answer to 'what is there to watch today': who is
    bent on what, whose bonds have grown into friendship, and which
    names the record has turned cold. Bounded and derived — no history
    is invented that the affinities and goals do not hold."""
    byid = {q["id"]: q for q in u.get("people", [])}
    bent, close, feuds = [], 0, 0
    seen = set()
    for q in u.get("people", []):
        if q.get("goal") and not q.get("w"):
            bent.append([q.get("n", "?"), q["goal"].get("what", "")])
        for k, v in (q.get("aff") or {}).items():
            try:
                other = int(k)
            except ValueError:
                continue
            pair = (min(q.get("id", 0), other), max(q.get("id", 0), other))
            if pair in seen:
                continue                     # each pair counted once
            seen.add(pair)
            other_p = byid.get(other)
            if v >= FRIEND:
                if other_p and not other_p.get("w"):
                    close += 1
            elif v <= FEUD:
                if other_p is not None:
                    feuds += 1               # names still warm on one side
    return {"bent_on": bent[:5], "close_pairs": close, "feuds": feuds}


def for_world(u):
    """The testament of one universe, as plain JSON. Reads only."""
    kind = u.get("kind")
    day = u.get("day", 0)
    year = day // DAYS_PER_YEAR
    if kind == "LAGOON":
        title = "The Way of the Lagoon"
        creed = ["Nothing is given; everything is earned.",
                 "The island feeds those who walk it, and starves those who wait.",
                 "The fire is the band; the night belongs to the watch."]
        tech = list(u.get("tech") or [])
        if "lore" in tech:
            creed.append("The stories bind: a band that shares its fictions can be "
                         "larger than the faces it knows.")
        if "agriculture" in tech:
            creed.append("The seed is kept back from the mouth that wants it.")
        myths = [list(m) for m in u.get("myths", [])]
        totem = None
        rites = 0
        for st in u.get("settlements", []):
            if st.get("totem"):
                totem = totem or st["totem"]
            rites += st.get("rites", 0)
        commandments = []
        for lesson in u.get("lessons", []):
            if lesson in COMMANDMENTS_OF:
                commandments.append(COMMANDMENTS_OF[lesson][0])
        return {
            "kind": kind, "year": year, "title": title, "creed": creed,
            "commandments": commandments,
            "myths": myths, "totem": totem, "rites": rites,
            "stories": round(u.get("stories", 0.0), 1),
            "gifts": tech,
            "chronicle": chronicle(u),
            "rhythms": [{"what": w, "note": n} for w, n in rhythms(u)],
            "hazards": hazards(u),
            "cast": cast(u),
            "note": "A reading of the record: the people did not write this down. "
                    "Their myths are real; the laws are the dead iterations' legacy; "
                    "the rest is the observer naming what the engine keeps.",
        }
    # EDEN: the covenant of the resort. Its scripture is thin on purpose —
    # nothing is asked, so nothing is written. That emptiness is the finding.
    fac = u.get("facilities") or {}
    built = [k for k, v in sorted(fac.items()) if v]
    creed = ["The food is free, and the bars never empty.",
             "The water is free.",
             "The walls are the law; the dome is the world.",
             "Nothing is asked. A post is a favor, not a need.",
             "No one here has told a story that binds."]
    return {
        "kind": kind, "year": year, "title": "The Covenant of the Resort",
        "creed": creed,
        "commandments": [],                      # no dead have left EDEN a law:
                                                 # each run repeats the conditions innocent
        "myths": [], "totem": None,
        "rites": 0, "stories": 0.0,
        "amenities": {k: round(v, 2) for k, v in fac.items()},
        "built": built,
        "ennui": round(u.get("ennui", 0.0), 3),
        "chronicle": chronicle(u),
        "rhythms": [{"what": w, "note": n} for w, n in rhythms(u)],
        "hazards": hazards(u),
        "cast": cast(u),
        "note": "A reading of the record. The resort wrote no scripture because "
                "nothing was ever asked of anyone; the covenant below is the "
                "observer naming the provisions and their price.",
    }


def both(world):
    """The testament of the pair, for the snapshot and the book."""
    return {key: for_world(world[key]) for key in ("eden", "lagoon")}
