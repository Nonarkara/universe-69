"""The people: who they are, and what a day does to their bodies and minds.

Standard library only, like the engine. Everything here is a mechanic from a
row of DESIGN.md, and every row cites where it came from (BOOKS.md,
RESEARCH.md). The organising idea is a mismatch: both universes are peopled
by the same Stone-Age brain. LAGOON is the world that brain was built for,
where hunger, status, belonging and purpose all have a natural outlet in
work. EDEN is a resort that answers every need except those last ones, and
the same brain reacts to it.

Person fields added here (all plain JSON, all defaulted in engine.migrate):
  ef   executive function / self-control, heritable genetic value (0..1)
  ag   aggressiveness, heritable genetic value (0..1); men express it higher
  pu   purpose: what the world asks of this person (0..1)
  bmi  body-mass index; what the day's eating and work did to the body
  sn   strength (0..1)
  inj  injury (0..1); heals with time
  gd   grudge (0..1) held against the person with id gk
  vg   vigilance: heritable threat sensitivity (0..1) — the watchful survive predators
  wk   withdrawn kind: 1 huddles on the floor, 2 a beautiful one, 3 retreats upstairs
  fe   the father's [ef, ag] carried from conception to birth
"""

import random

DAYS_PER_YEAR = 360
ADULT_AGE = 16 * DAYS_PER_YEAR
ELDER_AGE = 58 * DAYS_PER_YEAR

# Activity codes — shared verbatim with the renderer (tests/test_contract.py).
(A_IDLE, A_WALK, A_FORAGE, A_HUNT, A_FISH, A_FARM, A_BUILD, A_TALK,
 A_MATE, A_BIRTH, A_TEND, A_REST, A_EAT, A_WITHDRAW, A_FIGHT, A_PLAY,
 A_RITE, A_SLEEP, A_WORK, A_SCOUT, A_WATCH, A_GROOM, A_DRINK) = range(23)

WORK_ACTS = frozenset((A_FORAGE, A_HUNT, A_FISH, A_FARM, A_BUILD, A_WORK, A_SCOUT))

# Withdrawn kinds. Universe 25's withdrawn were not one crowd: dropout males
# pooled listless on the open floor, the beautiful ones only ate, slept and
# groomed, and lone females retreated to the upper nest boxes (RESEARCH.md
# [2][3]; Cabinet, Wiles 2011).
WK_HUDDLE, WK_BEAUTIFUL, WK_UPSTAIRS = 1, 2, 3

TRAIT_SD = 0.15            # founders' spread
MUTATION_SD = 0.06         # equilibrium sd ≈ 0.085 once mid-parent averaging bites
MALE_AG_SHIFT = 0.08       # ≈ half an sd: a distribution shift, never a rule (Pinker ch.18)

SYLLABLES = ["ka", "ra", "no", "ta", "mi", "lu", "se", "an", "ko", "ri",
             "ve", "sha", "on", "ba", "ni", "tu", "ma", "ilo", "ess", "ur"]

# The names a world gives its people.
#
# A name is a cultural invention, so the two worlds do not share a stock.
# EDEN is the older story: Adam and Eve, and the line after them. LAGOON
# is the other older story: Rahul and Siddhartha, and the line after
# them. The people themselves are the same — the founders of both worlds
# have the same bodies and the same tempers — but a world names its own.
#
# The founders are named from the head of the list; everyone born after
# them is named from the whole stock, so a name in the record always
# says which world the person belongs to.

NAMES = {
    "EDEN": {
        "m": ["Adam", "Cain", "Abel", "Seth", "Enosh", "Noah", "Lame", "Enoch",
              "Mica", "Jubal", "Tubal", "Peleg", "Reu", "Serug", "Terah", "Abram",
              "Isaac", "Jacob", "Judah", "Dan", "Zebulun", "Issachar", "Gad",
              "Joseph", "Benjamin", "Levi", "Judah", "Amos", "Obadiah"],
        "f": ["Eve", "Adah", "Zillah", "Miriam", "Ruth", "Sarah", "Rachel",
              "Leah", "Dinah", "Tamar", "Jael", "Deborah", "Naomi", "Hannah",
              "Rachel", "Dinah", "Phoebe", "Priscilla", "Lydia", "Mary",
              "Martha", "Mary", "Elizabeth", "Esther", "Judith", "Ruth",
              "Sarah", "Hephzibah", "Shiloh"],
    },
    "LAGOON": {
        "m": ["Rahul", "Siddhartha", "Ganesh", "Shiva", "Arjuna", "Krishna",
              "Indra", "Rama", "Vishnu", "Yama", "Brahma", "Hanuman", "Karna",
              "Nakula", "Sahadeva", "Duryodhana", "Bhishma", "Drona", "Asoka",
              "Chandraprabha", "Devadatta", "Maitreya", "Ananda", "Nirvana",
              "Ajita", "Nanda", "Mahakashyapa", "Sariputra", "Upananda",
              "Bodhisattva"],
        "f": ["Sita", "Parvati", "Ganga", "Tara", "Radha", "Lakshmi", "Maya",
              "Kali", "Ananda", "Savitri", "Meera", "Bhagavati", "Padma", "Durga",
              "Sati", "Ganga", "Indrani", "Rambha", "Menaka", "Apsara", "Kausalya",
              "Sumitra", "Kaikeyi", "Mandodari", "Sita", "Sundari", "Amrapali",
              "Vasudha", "Kishnadevi", "Kambala"],
    },
}


def make_name(rng, pool=None, index=None, sex=None):
    """A name from the world's own stock.

    With an index it is the name at that place in the list — used for the
    founders, so that EDEN begins with Adam and Eve and LAGOON with Rahul
    and Sita. Without one it is drawn at random from the stock.
    """
    if pool:
        names = pool[sex] if sex in ("m", "f") else pool["m"] + pool["f"]
        if index is not None:
            return names[index % len(names)]
        return names[rng.randrange(len(names))]
    n = rng.choice([2, 2, 3])
    return "".join(rng.choice(SYLLABLES) for _ in range(n)).capitalize()


def clamp01(x):
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def founders(fseed, iteration, pairs, pool=None):
    """The same people, for both universes.

    Both worlds start from the same founders: the same bodies, the same
    tempers, in the same order. The world is the only difference, which is
    what makes the comparison an experiment. What differs is the *name*
    each world gives them, because a name is a thing a world invents.

    EDEN begins with Adam and Eve; LAGOON begins with Rahul and Sita.
    Each world receives eight pairs, as on every reseed.
    """
    rng = random.Random(fseed * 1009 + iteration)
    out = []
    for i in range(pairs * 2):
        sex = "m" if i % 2 == 0 else "f"
        if pool:
            nm = make_name(rng, pool, index=i // 2, sex=sex)
        else:
            nm = make_name(rng)
        out.append({"n": nm, "s": sex,
                    "ef": clamp01(rng.gauss(0.5, TRAIT_SD)),
                    "ag": clamp01(rng.gauss(0.5, TRAIT_SD)),
                    "vg": clamp01(rng.gauss(0.5, TRAIT_SD))})
    return out


def new_mind(p, ef=0.5, ag=0.5):
    p.update({"ef": ef, "ag": ag, "vg": 0.5, "pu": 0.6, "bmi": 21.5, "sn": 0.55,
              "experience": {"sites": [], "trail": [], "heard_on": None, "mentors": []},
              "learning": None, "teaching": None, "teaching_day": None, "teaching_ids": [],
              "skills": {}, "skill_day": None, "craft": None, "craft_part": None, "stories": 0.0,
              "inj": 0.0, "gd": 0.0, "gk": 0, "wk": 0, "fe": None,
              "dad": None, "pregnancy_father": None, "social": None, "groom_day": None, "intimacy": 0.0})
    return p


def inherit(child, mother, rng):
    """Mid-parent plus a small mutation (Bloom; Pinker ch.19: about half the
    variance in a behavioural trait is genetic). Nothing regresses toward a
    fixed mean, so selection and drift can move a population over generations,
    slowly. The father's values were captured at conception."""
    fe = mother.get("fe") or [mother.get("ef", 0.5), mother.get("ag", 0.5), mother.get("vg", 0.5)]
    child["ef"] = clamp01((mother.get("ef", 0.5) + fe[0]) / 2 + rng.gauss(0, MUTATION_SD))
    child["ag"] = clamp01((mother.get("ag", 0.5) + fe[1]) / 2 + rng.gauss(0, MUTATION_SD))
    fvg = fe[2] if len(fe) > 2 else 0.5
    child["vg"] = clamp01((mother.get("vg", 0.5) + fvg) / 2 + rng.gauss(0, MUTATION_SD))
    child["bmi"] = 16.0
    child["sn"] = 0.1
    child["pu"] = 0.6


def aggression(p):
    """Expressed aggression: genes, sex, youth, and whether he has a mate."""
    a = p.get("ag", 0.5) + (MALE_AG_SHIFT if p["s"] == "m" else 0.0)
    return a


def self_control(p, age):
    """The prefrontal cortex matures last (Bloom; Pinker ch.3): expressed
    self-control ramps to full by about 22, so the young act on impulse."""
    return p.get("ef", 0.5) * min(1.0, 0.45 + age / (22 * DAYS_PER_YEAR) * 0.55)


def body_center(age):
    """The BMI a well-fed, active body settles at for its age."""
    return 16.0 + 6.0 * min(1.0, age / ADULT_AGE)


def tend_body(p, age, eden, shortfall, healing=False):
    """What one day did to the body.

    EDEN: a forager's appetite with food always in reach. The brain was built
    to eat whenever food appeared, because it seldom did; where nothing else
    is asked, eating is what is left to do (Frankl's vacuum). LAGOON: the body
    is paid for in work, and famine takes it back.
    """
    act = p.get("a", 0)
    center = body_center(age)
    if eden:
        intake = 0.6 + 0.8 * (1.0 - p.get("pu", 0.5))
        if act in (A_PLAY, A_FIGHT, A_RITE):
            intake -= 0.4
        p["bmi"] += 0.0035 * intake - 0.0004 * (p["bmi"] - center)
    elif shortfall > 0:
        p["bmi"] -= 0.06 * shortfall
    else:
        p["bmi"] += 0.004 * (center - p["bmi"])
    p["bmi"] = min(48.0, max(12.0, p["bmi"]))

    base = (0.62 if p["s"] == "m" else 0.48) * min(1.0, age / ADULT_AGE + 0.15)
    if age > 40 * DAYS_PER_YEAR:
        base -= (age - 40 * DAYS_PER_YEAR) / DAYS_PER_YEAR * 0.008
    if act in WORK_ACTS:
        target = base + 0.25
    elif eden and age >= ADULT_AGE:
        target = base - 0.15                 # nothing to lift, nowhere to walk to
    else:
        target = base
    if p["bmi"] < 15.5:
        target -= 0.2                         # wasting
    p["sn"] = clamp01(p["sn"] + 0.003 * (target - p["sn"]))

    if p.get("inj", 0) > 0:
        p["inj"] = max(0.0, p["inj"] - (0.02 if healing else 0.01))
    if p.get("gd", 0) > 0:
        p["gd"] = max(0.0, p["gd"] * (1 - 0.08 / DAYS_PER_YEAR) - 1e-5)


def tend_purpose(p, age, asked, paired, mothering, placed):
    """Purpose: what the world asks of this person (Frankl part 2; Homo Deus
    ch.2). It rises with dependents, work and a place of one's own, and decays
    when every need is met and nothing is asked. `asked` is the world's own
    demand: high in LAGOON, where everything must be earned; none in EDEN."""
    if age < ADULT_AGE:
        return
    t = 0.15 + asked
    if mothering:
        t += 0.3
    if paired:
        t += 0.12
    if placed:
        t += 0.1
    if p.get("a") in WORK_ACTS:
        t += 0.2
    p["pu"] = clamp01(p["pu"] + 0.01 * (min(1.0, t) - p["pu"]))


def hurt(p, amount):
    p["inj"] = clamp01(p.get("inj", 0.0) + amount)


def body_words(p, age):
    """What a viewer would see: plain words for the body's state."""
    b = p.get("bmi", 22.0)
    if age < ADULT_AGE:
        shape = ("starving" if b < 13.5 else "thin" if b < 15
                 else "plump" if b > body_center(age) + 4 else "")
    else:
        shape = ("starving" if b < 15 else "thin" if b < 18.5 else
                 "obese" if b >= 30 else "heavy" if b >= 25 else "")
    words = [w for w in (shape,
                         "strong" if p.get("sn", 0) > 0.72 and age >= ADULT_AGE else
                         "weak" if p.get("sn", 0) < 0.3 and age >= ADULT_AGE else "",
                         "badly hurt" if p.get("inj", 0) > 0.5 else
                         "hurt" if p.get("inj", 0) > 0.15 else "") if w]
    return ", ".join(words)


# ------------------------------------------------------------- reproduction
# Human reproductive biology, as calibration rather than citation from the
# owner's books: fecundability (chance of conceiving per cycle) peaks in the
# twenties and falls toward menopause near 50; very low body fat suppresses
# ovulation; breastfeeding on demand suppresses it for years, which is why
# forager births come about four years apart (Howell, Demography of the Dobe
# !Kung, 1979); roughly one in seven recognised pregnancies miscarries; about
# one birth in seventy is twins. The engine multiplies its own social rate by
# this factor, which is 1.0 for a healthy, non-nursing woman of 25.

LACTATION_DAYS = {"LAGOON": 3 * DAYS_PER_YEAR, "EDEN": int(1.5 * DAYS_PER_YEAR)}
MISCARRIAGE = 0.14
TWINS = 0.014


def fertility(p, age, day):
    """0..1: how fertile this woman's body is today."""
    y = age / DAYS_PER_YEAR
    if y < 16 or y >= 50:
        return 0.0
    f = 1.0 if y < 30 else max(0.0, 1.0 - (y - 30) * 0.045)
    b = p.get("bmi", 22.0)
    if b < 18.5:
        f *= max(0.0, (b - 15.0) / 3.5)      # too little fat to ovulate
    elif b > 35:
        f *= 0.7
    nurse_until = p.get("nurse", 0)
    if day < nurse_until:
        left = (nurse_until - day) / max(1, p.get("nurse_len", 1))
        f *= 0.05 + 0.6 * (1 - left) ** 2    # suppression wanes as weaning nears
    return f
