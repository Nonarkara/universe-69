"""Hypotheses from the literature, and the run that tests them.

BOOKS.md says what the books say. DESIGN.md says which of those findings
became a mechanic. This file is the third step: the findings that can be
*falsified*.

A hypothesis here is a number the model can produce, a threshold, and a
direction. Nothing in this file can change how a world evolves — it only
reads. That is deliberate: adding or retiring a hypothesis must not move
a single simulated outcome, or the record of what the model showed would
depend on what the model had been asked to show.

The verdicts are written into the world, so they survive a restart and
accumulate across runs. A claim the model keeps contradicting stays on
the board. Either the model is wrong or the reading of the book is, and
neither is settled by hiding the number.

The thresholds are implementation choices inspired by the reading, not
empirical calibrations. A model agreeing with them cannot validate a book
or a claim about human beings.

Every row cites where it came from. The corpus behind these rows is the
owner's shelf (`~/Downloads/books`); BOOKS.md is the reading of it, and
RESEARCH.md is the verified secondary literature.

Standard library only, like the engine.
"""

import minds  # for DAYS_PER_YEAR and ADULT_AGE only

DAYS_PER_YEAR = minds.DAYS_PER_YEAR
ADULT_AGE = minds.ADULT_AGE

# How often the live run re-tests the hypotheses, in sim-days. Monthly in
# sim-time: often enough to see a trend, rare enough that the numbers are
# not noise.
CADENCE = 30

# How many past verdicts to keep per hypothesis. Enough to see a trend,
# small enough that a 114-year-old state file stays small.
VERDICT_HISTORY = 40


# ------------------------------------------------------------------ metrics
# Every metric reads a universe and returns a number, or None when the
# world has not lived long enough for the number to mean anything. None is
# "undecided", never "false": a hypothesis is not refuted by a world that
# has not yet got around to testing it.

def _people(u):
    return u.get("people") or []


def _adults(u):
    day = u.get("day", 0)
    return [p for p in _people(u) if day - p.get("b", 0) >= ADULT_AGE]


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _share(num, den):
    return (num / den) if den else None


def _year_of(u, phase):
    """The year a phase began, from the world's own record of its phases."""
    for row in reversed(u.get("phases") or []):
        if len(row) >= 2 and row[1] == phase:
            return row[0] - u.get("founded_day", 0) // DAYS_PER_YEAR
    return None


def _cod(u, cause):
    return (u.get("cod") or {}).get(cause, 0)


def _cod_total(u):
    return sum((u.get("cod") or {}).values())


def m_eden_bmi(u):
    return _mean([p.get("bmi") for p in _adults(u)])


def m_eden_purpose(u):
    return _mean([p.get("pu") for p in _adults(u)])


def m_eden_withdrawn(u):
    a = _adults(u)
    return _share(sum(1 for p in a if p.get("w")), len(a))


def m_eden_placeless(u):
    a = _adults(u)
    return _share(sum(1 for p in a if p.get("box") is None or p["box"] < 0), len(a))


def m_eden_incompetent(u):
    a = _adults(u)
    return _share(sum(1 for p in a if not p.get("c", True)), len(a))


def m_eden_paired(u):
    a = _adults(u)
    return _share(sum(1 for p in a if p.get("p") is not None), len(a))


def m_eden_crowding(u):
    cap = u.get("cap", 900)
    return (len(_people(u)) / cap) if cap else None


def m_eden_peak_crowding(u):
    cap = u.get("cap", 900)
    return (u.get("peak", 0) / cap) if cap else None


def m_eden_sink_year(u):
    return _year_of(u, "stagnate")


def m_eden_death_year(u):
    return _year_of(u, "death")


def m_eden_sink_gap(u):
    """Years between the behavioural sink and the death phase.

    Calhoun's phases do not overlap: once the sink appears, the end is
    already on its way. The model's own gap is the number to compare.
    """
    s, d = m_eden_sink_year(u), m_eden_death_year(u)
    return (d - s) if (s is not None and d is not None) else None


def m_eden_post_fill(u):
    roles = u.get("roles") or []
    if not roles:
        return None
    return _share(sum(1 for r in roles if r.get("who")), len(roles))


def m_eden_ennui(u):
    v = u.get("ennui")
    return float(v) if v is not None else None


def m_lagoon_bmi(u):
    return _mean([p.get("bmi") for p in _adults(u)])


def m_lagoon_purpose(u):
    return _mean([p.get("pu") for p in _adults(u)])


def m_lagoon_violent_share(u):
    t = _cod_total(u)
    return _share(_cod(u, "violence"), t)


def m_lagoon_starve_share(u):
    t = _cod_total(u)
    return _share(_cod(u, "starvation"), t)


def m_lagoon_infant_share(u):
    t = _cod_total(u)
    return _share(_cod(u, "infant"), t)


def m_lagoon_dominant_cause(u):
    cod = u.get("cod") or {}
    if not cod:
        return None
    return max(cod, key=cod.get)


def m_lagoon_tech(u):
    return float(len(u.get("tech") or []))


def m_lagoon_pop(u):
    return float(len(_people(u)))


def m_lagoon_settlements(u):
    return float(len(u.get("settlements") or []))


def m_lagoon_farms(u):
    return float(len(u.get("farms") or []))


def m_lagoon_max_settlement(u):
    """Largest band while the no-lore hypothesis applies.

    A society with lore cannot refute a claim explicitly about its absence.
    """
    if "lore" in (u.get("tech") or []):
        return None
    counts = {}
    for p in _people(u):
        k = p.get("st", 0)
        counts[k] = counts.get(k, 0) + 1
    return float(max(counts.values())) if counts else None


def m_lagoon_paired(u):
    a = _adults(u)
    return _share(sum(1 for p in a if p.get("p") is not None), len(a))


def m_lagoon_hunger(u):
    return _mean([p.get("hun") for p in _adults(u)])


def m_lagoon_ef_mean(u):
    mind = u.get("mind") or []
    return float(mind[-1][1]) if mind else None


def m_lagoon_ef_tail(u):
    mind = u.get("mind") or []
    return float(mind[-1][2]) if mind else None


def m_lagoon_births_per_100(u):
    """Children born per hundred adults per year, from the yearly record."""
    census = u.get("census") or []
    if not census:
        return None
    year, pop, births, _deaths = census[-1][:4]   # rows grew gauges in 2026.10.28.3
    adults = len(_adults(u))
    if not adults:
        return None
    return 100.0 * births / adults


METRICS = {
    "eden_bmi": m_eden_bmi,
    "eden_purpose": m_eden_purpose,
    "eden_withdrawn": m_eden_withdrawn,
    "eden_placeless": m_eden_placeless,
    "eden_incompetent": m_eden_incompetent,
    "eden_paired": m_eden_paired,
    "eden_crowding": m_eden_crowding,
    "eden_peak_crowding": m_eden_peak_crowding,
    "eden_sink_year": m_eden_sink_year,
    "eden_death_year": m_eden_death_year,
    "eden_sink_gap": m_eden_sink_gap,
    "eden_post_fill": m_eden_post_fill,
    "eden_ennui": m_eden_ennui,
    "lagoon_bmi": m_lagoon_bmi,
    "lagoon_purpose": m_lagoon_purpose,
    "lagoon_violent_share": m_lagoon_violent_share,
    "lagoon_starve_share": m_lagoon_starve_share,
    "lagoon_infant_share": m_lagoon_infant_share,
    "lagoon_dominant_cause": m_lagoon_dominant_cause,
    "lagoon_tech": m_lagoon_tech,
    "lagoon_pop": m_lagoon_pop,
    "lagoon_settlements": m_lagoon_settlements,
    "lagoon_farms": m_lagoon_farms,
    "lagoon_max_settlement": m_lagoon_max_settlement,
    "lagoon_paired": m_lagoon_paired,
    "lagoon_hunger": m_lagoon_hunger,
    "lagoon_ef_mean": m_lagoon_ef_mean,
    "lagoon_ef_tail": m_lagoon_ef_tail,
    "lagoon_births_per_100": m_lagoon_births_per_100,
}


# -------------------------------------------------------------- hypotheses
# Each row is a claim from the shelf, written so a simulation can disagree
# with it. "test" is the comparison; "value" is the threshold the claim
# implies. A hypothesis with no measurable yet is a promise, not a test.

HYPOTHESES = [
    {
        "id": "H-EDEN-BMI",
        "world": "EDEN",
        "statement": "EDEN's adults fatten: their BMI reaches 30 or more.",
        "source": "BOOKS.md, 'Minds and development' — Frankl: when the demands "
                  "stop, the appetite answers the emptiness.",
        "metric": "eden_bmi", "test": "gte", "value": 30.0,
        "note": "The resort removes hunger but not the need to be needed. "
                "Earlier engines produced BMI 32; those figures do not validate this engine.",
        "min_year": 40, "min_pop": 20,
    },
    {
        "id": "H-EDEN-PURPOSE",
        "world": "EDEN",
        "statement": "EDEN's adults have almost nothing to live for: purpose "
                     "falls to 0.3 or below.",
        "source": "BOOKS.md, 'Minds and development' — Frankl, part 2: the "
                  "existential vacuum shows as boredom and aggression.",
        "metric": "eden_purpose", "test": "lte", "value": 0.30,
        "note": "The same brain, the same people, a world that asks nothing.",
        "min_year": 40, "min_pop": 20,
    },
    {
        "id": "H-EDEN-WITHDRAWN",
        "world": "EDEN",
        "statement": "In EDEN some adults withdraw for good and never come back.",
        "source": "RESEARCH.md §1 — Calhoun's beautiful ones and the withdrawn "
                  "huddles; the social death that precedes the physical one.",
        "metric": "eden_withdrawn", "test": "gte", "value": 0.01,
        "note": "One adult in a hundred is enough to be a pathology, not a rounding error.",
        "min_year": 40, "min_pop": 20,
    },
    {
        "id": "H-EDEN-SINK-YEAR",
        "world": "EDEN",
        "statement": "EDEN's behavioural sink appears between 40 and 140 years "
                     "after the founders arrive.",
        "source": "DESIGN.md, 'Universe 6 — EDEN': the sink begins in year 83 "
                  "with expansion, about year 42 without it.",
        "metric": "eden_sink_year", "test": "between", "value": [40, 140],
        "note": "A date, not a number of people: when the pathology arrives is "
                "the shape of the whole arc.",
        "min_year": 40,
    },
    {
        "id": "H-EDEN-SINK-GAP",
        "world": "EDEN",
        "statement": "Once the sink appears, the death phase follows within 30 years.",
        "source": "RESEARCH.md §1 — Calhoun's phases C and D do not overlap.",
        "metric": "eden_sink_gap", "test": "lte", "value": 30,
        "note": "The pen does not recover. If the gap widens, the pen has a "
                "reprieve Calhoun's mice never got.",
        "min_year": 60,
    },
    {
        "id": "H-EDEN-COLLAPSE-BELOW-CAP",
        "world": "EDEN",
        "statement": "EDEN's peak population stays below the pen's nominal capacity.",
        "source": "RESEARCH.md §1 — collapse began at about 57% of the 3,840 "
                  "nominal capacity, long before the space ran out.",
        "metric": "eden_peak_crowding", "test": "lte", "value": 1.0,
        "note": "Space was never the binding constraint; roles were.",
        "min_year": 30,
    },
    {
        "id": "H-EDEN-POSTS",
        "world": "EDEN",
        "statement": "EDEN's fixed posts fill up, and stay filled.",
        "source": "BOOKS.md, 'Economy and captivity' — Bestor ch.6: seats are a "
                  "fixed count, refilled only on a holder's death.",
        "metric": "eden_post_fill", "test": "gte", "value": 0.99,
        "note": "Every role held is one fewer reason for a new adult to be needed.",
        "min_year": 10, "min_pop": 10,
    },
    {
        "id": "H-LAGOON-VIOLENCE",
        "world": "LAGOON",
        "statement": "Violence accounts for at most 30% of LAGOON's deaths.",
        "source": "BOOKS.md, 'Violence and civilisation' — Pinker ch.2: foragers "
                  "4–30% of deaths violent (the book's own figure).",
        "metric": "lagoon_violent_share", "test": "lte", "value": 0.30,
        "note": "An order of magnitude, and contested by Fry and Ferguson. "
                "Earlier engines produced 0.6–7.8%; this engine requires its own measurements.",
        "min_year": 30, "min_pop": 20, "min_deaths": 100,
    },
    {
        "id": "H-LAGOON-FAMINE",
        "world": "LAGOON",
        "statement": "In LAGOON, hunger is what kills: starvation is the "
                     "dominant cause of death.",
        "source": "DESIGN.md, 'Engine 2026.10.27.2' — famine dominates deaths; "
                  "Harari's agricultural revolution as a luxury trap.",
        "metric": "lagoon_dominant_cause", "test": "eq", "value": "starvation",
        "note": "If violence takes over, the world has become a war, not a world "
                "that fails to feed itself.",
        "min_year": 30, "min_pop": 20, "min_deaths": 100,
    },
    {
        "id": "H-LAGOON-BMI",
        "world": "LAGOON",
        "statement": "LAGOON's adults stay lean: their BMI sits between 18 and 26.",
        "source": "BOOKS.md, 'Minds and development' — a forager's appetite is "
                  "paid for in work; Harari, foraging and the lean body.",
        "metric": "lagoon_bmi", "test": "between", "value": [18.0, 26.0],
        "note": "The same brain in the same bodies: the difference is the world.",
        "min_year": 30, "min_pop": 20,
    },
    {
        "id": "H-LAGOON-PURPOSE",
        "world": "LAGOON",
        "statement": "LAGOON's adults are asked for something: purpose stays "
                     "at 0.5 or above.",
        "source": "BOOKS.md, 'Minds and development' — Frankl: purpose comes "
                  "from being asked something.",
        "metric": "lagoon_purpose", "test": "gte", "value": 0.50,
        "note": "Earlier engines produced purpose 0.8 against EDEN's 0.2; this is not a current-engine measurement.",
        "min_year": 30, "min_pop": 20,
    },
    {
        "id": "H-LAGOON-TECH",
        "world": "LAGOON",
        "statement": "LAGOON climbs the ladder: it reaches five technologies, "
                     "past fire, tools and fishing.",
        "source": "RESEARCH.md §4 — Diamond: food production, surplus, "
                  "specialists, states; Harari: the ladder out of the cognitive "
                  "revolution.",
        "metric": "lagoon_tech", "test": "gte", "value": 5.0,
        "note": "A world that stays a forager forever is a world where the "
                "ladder is broken, not a world at the bottom of one.",
        "min_year": 60, "min_pop": 10,
    },
    {
        "id": "H-LAGOON-DUNBAR",
        "world": "LAGOON",
        "statement": "A settlement without shared lore never grows past 150.",
        "source": "RESEARCH.md §3 — Harari, the gossip theory: groups without "
                  "shared fictions fission at about 150.",
        "metric": "lagoon_max_settlement", "test": "lte", "value": 150.0,
        "absent_tech": ["lore"],
        "note": "The model's own limit is 80 without lore, 220 with it. If the "
                "band outgrows the limit, the mechanic has broken.",
        "min_year": 30, "min_pop": 20,
    },
    {
        "id": "H-LAGOON-HUNGER",
        "world": "LAGOON",
        "statement": "LAGOON's adults are hungry most of the time, but not "
                     "starving: mean hunger stays at 20 or below.",
        "source": "BOOKS.md, 'Second pass' — a forager's life is spent "
                  "looking for food; the lean season is a season, not a famine.",
        "metric": "lagoon_hunger", "test": "lte", "value": 20.0,
        "note": "Above 40 is death. This is the distance between the two.",
        "min_year": 20, "min_pop": 20,
    },
    {
        "id": "H-LAGOON-EF",
        "world": "LAGOON",
        "statement": "LAGOON's mean self-control stays in a narrow band, 0.3 "
                     "to 0.7, whatever the culture does.",
        "source": "BOOKS.md, 'Two clocks' — genes move slowly, culture moves "
                  "within generations; neither is the other's clock.",
        "metric": "lagoon_ef_mean", "test": "between", "value": [0.30, 0.70],
        "note": "If the mean swings with culture, the two clocks have been "
                "confused in the model.",
        "min_year": 20, "min_pop": 20,
    },
    {
        "id": "H-LAGOON-CHILDREN",
        "world": "LAGOON",
        "statement": "LAGOON's last yearly births exceed five per hundred "
                     "adults alive now.",
        "source": "RESEARCH.md §3 — foragers reproduce slowly; a shrinking "
                  "population is a population that has lost its future.",
        "metric": "lagoon_births_per_100", "test": "gte", "value": 5.0,
        "note": "The denominator is today's adults, not the adults exposed during that year; this snapshot ratio is not a demographic birth rate.",
        "min_year": 20, "min_pop": 20,
    },
    {
        "id": "H-LAGOON-PAIRED",
        "world": "LAGOON",
        "statement": "Most of LAGOON's adults are paired: at least half.",
        "source": "BOOKS.md, 'Violence and civilisation' — Pinker ch.2–3: "
                  "unpaired young men are the dangerous ones; bonding is the "
                  "civilising mechanism.",
        "metric": "lagoon_paired", "test": "gte", "value": 0.50,
        "note": "The engine already doubles the homicide hazard for unpaired "
                "men aged 16–30, so this is the model's own assumption on trial.",
        "min_year": 20, "min_pop": 20,
    },
]


# ---------------------------------------------------------------- the story
# The corpus in one thread: what the shelf says happened to us, in the order
# it happened, and which hypothesis each part produced. This is the "hypothesis
# section" the reader asked for — the summary of the history of mankind that
# the books on the shelf agree on, and the point in the model where each
# piece of it is measured.
#
# Nothing here is a claim about people. It is a summary of what a particular
# set of books argues, and the tests below are what this model makes of it.

HISTORY = [
    {
        "t": "Before the story",
        "when": "the deep past",
        "claim": "Homo sapiens came out of a world of other hominins and was "
                 "not the strongest thing on the ground. What it had was "
                 "flexible cooperation in large numbers, and the tool that "
                 "made that possible was language about things that do not "
                 "exist: gods, ancestors, money, nations.",
        "source": "Harari, *Sapiens* chs. 1-5 and *Nexus* ch. 1 (RESEARCH.md §3); "
                  "Pinker, *The Blank Slate* ch. 19",
        "hypos": ["H-LAGOON-DUNBAR", "H-LAGOON-TECH"],
    },
    {
        "t": "The first fire",
        "when": "and the first dark",
        "claim": "Cooking changed what a body could be, and the fire changed "
                 "what a band could be. The night is when the fire makes a "
                 "group: people come in to it, they talk, and one of them "
                 "stays awake. The stories told there are the first lore.",
        "source": "Slingerland, *Drunk* ch. 3 (fire, cooking, the shared night); "
                  "Harari, *Nexus* ch. 2; the model's own night watch",
        "hypos": ["H-LAGOON-PURPOSE", "H-LAGOON-PAIRED"],
    },
    {
        "t": "The band",
        "when": "c. 50,000 years ago",
        "claim": "Human groups have a size that gossip alone cannot hold — "
                 "about a hundred and fifty. Past that, a band needs a story "
                 "it can all believe, and then it can be any size at all.",
        "source": "Harari, *Sapiens* ch. 1 (gossip and the ~150 threshold); "
                  "Dunbar via RESEARCH.md §3",
        "hypos": ["H-LAGOON-DUNBAR"],
    },
    {
        "t": "The exchange ring",
        "when": "the deep past, and still",
        "claim": "Observed in the field: a people who keep a long-distance "
                 "ring of gift exchange, and who believe the ring is "
                 "mythical and unprofitable even as they maintain it. "
                 "Obligation, not trade, is what holds it together.",
        "source": "Malinowski, *Argonauts of the Western Pacific* — the kula "
                  "and 'Magic and the Kula'",
        "hypos": ["H-LAGOON-DUNBAR", "H-LAGOON-PAIRED"],
    },
    {
        "t": "The tool, and the first kill",
        "when": "the first technology",
        "claim": "A species is domesticable only if it passes every test at "
                 "once, and very few do. The same filter applies to prey: a "
                 "hunter's gain is small until the weapon is right. And the "
                 "big cat is not only a terror — once it can be killed, it is "
                 "meat.",
        "source": "Diamond, *Guns, Germs, and Steel* (the Anna Karenina "
                  "filter); the model's own hunting of predators",
        "hypos": ["H-LAGOON-TECH", "H-LAGOON-VIOLENCE"],
    },
    {
        "t": "The first field",
        "when": "c. 12,000 years ago",
        "claim": "Farming raised the number of people and lowered the "
                 "quality of most of their lives: narrower food, harder "
                 "labour, new disease, and a one-way door — once the "
                 "population outgrows the foraging baseline, foraging cannot "
                 "feed it again.",
        "source": "Harari, *Sapiens* ch. 4 (history's biggest fraud, the "
                  "luxury trap); Diamond's surplus chain",
        "hypos": ["H-LAGOON-BMI", "H-LAGOON-CHILDREN"],
    },
    {
        "t": "The surplus and the specialists",
        "when": "after the field",
        "claim": "Storable surplus creates people who are not needed to hunt: "
                 "smiths, priests, scribes, soldiers. Every specialist is "
                 "another mouth to feed and another seat nobody empties.",
        "source": "Diamond, *Guns, Germs, and Steel* (food production → "
                  "surplus → specialists → writing → states); Bestor, "
                  "*Tsukiji* ch. 6 (seats are a fixed count)",
        "hypos": ["H-EDEN-POSTS", "H-LAGOON-TECH"],
    },
    {
        "t": "The gods and the covers",
        "when": "with the first city",
        "claim": "A society that cannot explain what happens to it explains "
                 "it with a story about somebody's will — a myth. Sacred and "
                 "profane separate; and a people who have just discovered "
                 "what a body is for begin to cover it.",
        "source": "Durkheim, *Elementary Forms* (collective effervescence, "
                  "the sacred); Harari, *Homo Deus* (the new gods); "
                  "Peterson on Genesis 3 (covering as the first cultural act)",
        "hypos": ["H-LAGOON-FAMINE", "H-LAGOON-PAIRED"],
    },
    {
        "t": "The stranger",
        "when": "the first crowds",
        "claim": "When the demands stop and nothing regulates anything, "
                 "people fall ill — not from hunger but from the emptiness. "
                 "Anomie is a disease of regulation, and it comes to those "
                 "who are competent and unasked-for.",
        "source": "Durkheim, *Suicide* (anomie); Frankl, *Man's Search for "
                  "Meaning* part 2 (the existential vacuum)",
        "hypos": ["H-EDEN-PURPOSE", "H-EDEN-WITHDRAWN", "H-EDEN-BMI"],
    },
    {
        "t": "The written word",
        "when": "c. 5,000 years ago",
        "claim": "Writing fuses strangers into a single mind that can hold "
                 "far more than any band, and it does so by carrying a "
                 "shared fiction further than speech can. The network, not "
                 "the village, is the unit that scales.",
        "source": "Harari, *Nexus* and *Homo Deus* (the cognitive fusion of "
                  "the modern era); the model's own lore and writing steps",
        "hypos": ["H-LAGOON-DUNBAR", "H-LAGOON-TECH"],
    },
    {
        "t": "The violence that went down",
        "when": "the long run",
        "claim": "Violence has fallen by orders of magnitude, and it fell "
                 "for reasons: more strangers to be watched, more people to "
                 "punish, and the state taking the killing over. The "
                 "forager's 4-30% violent share of deaths is the baseline "
                 "every later society is measured against.",
        "source": "Pinker, *The Better Angels of Our Nature* ch. 2 "
                  "(the numbers) and ch. 8 (revenge and the moralization gap)",
        "hypos": ["H-LAGOON-VIOLENCE", "H-LAGOON-FAMINE", "H-LAGOON-PAIRED"],
    },
    {
        "t": "The other and the war",
        "when": "the twentieth century",
        "claim": "Dehumanising the enemy is not a metaphor but a "
                 "mechanism: it widens the distance that makes killing "
                 "possible, and it feeds the hate that produces the next "
                 "atrocity. A band that cannot tell the difference between "
                 "an outsider and a monster will treat people the way the "
                 "model treats a predator.",
        "source": "Dower, *War without Mercy* (race hate and the "
                  "dehumanisation of the Other)",
        "hypos": ["H-LAGOON-VIOLENCE"],
    },
    {
        "t": "The feast",
        "when": "and the dark side of it",
        "claim": "Intoxication is a technology: it dissolves the ordinary "
                 "self and replaces it with a larger one, which is why "
                 "people drink together. The same mechanism carries risk, "
                 "aggression and loss of judgement — and it binds before it "
                 "binds well.",
        "source": "Slingerland, *Drunk* chs. 1, 3 and 5 (intoxication as "
                  "social technology; the dark side of Dionysus)",
        "hypos": ["H-LAGOON-VIOLENCE", "H-EDEN-WITHDRAWN"],
    },
    {
        "t": "The brain that did not change",
        "when": "and has not",
        "claim": "The hardware is old: a Stone-Age mind with modules for "
                 "gossip, status, bonding, and a very long time horizon. "
                 "Everything that has happened since has been a new "
                 "arrangement of the same parts. In a world that answers "
                 "every need and asks for nothing, that machine has nothing "
                 "to run on, and it stops.",
        "source": "Bloom, *Psych* (the architecture); Pinker, *The Blank "
                  "Slate*; Frankl (what the machine wants)",
        "hypos": ["H-EDEN-BMI", "H-EDEN-PURPOSE", "H-EDEN-WITHDRAWN",
                  "H-LAGOON-PURPOSE", "H-LAGOON-EF"],
    },
]


# ---------------------------------------------------------------- verdicts
# "supported" — the world agrees with the claim.
# "contradicted" — the world says otherwise, and keeps saying so.
# "undecided" — the world has not lived long enough, or not widely enough,
#               for the number to mean anything. This is never a failure.

SUPPORTED = "supported"
CONTRADICTED = "contradicted"
UNDECIDED = "undecided"


def _compare(test, value, threshold):
    if value is None:
        return UNDECIDED
    if test == "gte":
        return SUPPORTED if value >= threshold else CONTRADICTED
    if test == "lte":
        return SUPPORTED if value <= threshold else CONTRADICTED
    if test == "eq":
        return SUPPORTED if value == threshold else CONTRADICTED
    if test == "between":
        lo, hi = threshold
        return SUPPORTED if lo <= value <= hi else CONTRADICTED
    raise ValueError("unknown test: %r" % (test,))


def _ready(h, u):
    """A hypothesis is only worth testing once the world is old enough and
    big enough for the number to mean anything.

    "Big enough" is not the same as "populated enough": a share of deaths
    measured over a dozen deaths is noise, however many people are alive.
    So a hypothesis may also ask for a minimum number of deaths before it
    is allowed to contradict anything.
    """
    if any(tech in (u.get("tech") or []) for tech in h.get("absent_tech", [])):
        return False
    if h.get("min_year") and (u.get("day", 0) - u.get("founded_day", 0)) < h["min_year"] * DAYS_PER_YEAR:
        return False
    if h.get("min_pop") and len(_people(u)) < h["min_pop"]:
        return False
    if h.get("min_deaths") and _cod_total(u) < h["min_deaths"]:
        return False
    return True


def evaluate(world):
    """Measure every hypothesis against the live worlds. Read-only."""
    out = []
    for h in HYPOTHESES:
        u = world.get(h["world"].lower())
        if u is None:
            continue
        metric = METRICS.get(h["metric"])
        if metric is None:
            raise KeyError("unknown metric: %r" % (h["metric"],))
        value = metric(u)
        ready = _ready(h, u)
        verdict = _compare(h["test"], value, h["value"]) if ready else UNDECIDED
        out.append({
            "id": h["id"], "world": h["world"], "statement": h["statement"],
            "source": h["source"], "note": h["note"],
            "metric": h["metric"], "test": h["test"], "threshold": h["value"],
            "value": value, "verdict": verdict,
            "day": u.get("day", 0), "year": u.get("day", 0) // DAYS_PER_YEAR,
            "iteration": u.get("iteration", 1),
            "ready": ready, "engine": u.get("engine"),
        })
    return out


def record(world, results):
    """Write the verdicts into the world so they survive a restart."""
    store = world.setdefault("research", {})
    store.setdefault("h", {})
    store["tested"] = store.get("tested", 0) + 1
    store["last_day"] = (world.get("eden") or {}).get("day", 0)
    for r in results:
        h = store["h"].setdefault(r["id"], {
            "n": 0, "sup": 0, "con": 0, "und": 0, "hist": []})
        h["n"] += 1
        if r["verdict"] == SUPPORTED:
            h["sup"] += 1
        elif r["verdict"] == CONTRADICTED:
            h["con"] += 1
        else:
            h["und"] += 1
        h["last"] = [r["verdict"], r["value"], r["year"], r["iteration"]]
        h["hist"].append([r["year"], r["verdict"], r["value"],
                          r["iteration"], r.get("engine")])
        if len(h["hist"]) > VERDICT_HISTORY:
            h["hist"] = h["hist"][-VERDICT_HISTORY:]
    return store


def report(world):
    """The payload the viewer's research panel draws."""
    results = evaluate(world)
    store = world.get("research") or {}
    tally = store.get("h") or {}
    for r in results:
        t = tally.get(r["id"]) or {}
        r["tested"] = t.get("n", 0)
        r["supported"] = t.get("sup", 0)
        r["contradicted"] = t.get("con", 0)
        r["undecided"] = t.get("und", 0)
    # the engine that produced these numbers: the world's own stamp
    eng = (world.get("eden") or {}).get("engine") or \
          (world.get("lagoon") or {}).get("engine")
    return {
        "engine": eng,
        "record_scope": "Saved observations span iterations and engine versions; legacy rows without a version have unknown provenance.",
        "history": HISTORY,
        "tested": store.get("tested", 0),
        "cadence_days": CADENCE,
        "hypotheses": results,
        "counts": {
            "supported": sum(1 for r in results if r["verdict"] == SUPPORTED),
            "contradicted": sum(1 for r in results if r["verdict"] == CONTRADICTED),
            "undecided": sum(1 for r in results if r["verdict"] == UNDECIDED),
        },
    }
