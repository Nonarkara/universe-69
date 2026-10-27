"""Checks for the day-life, the farms, and the famine record. No dependencies.

    python3 sim/selftest.py
"""

import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine


def test_famine_line():
    assert engine.famine_line(["Nami"]) == "Nami starves in the lean season."
    line = engine.famine_line(["A", "B", "C", "D", "E"])
    assert line.startswith("5 starve")
    assert "and 2 others" in line
    assert "A" in line and "C" in line


def test_farms_stay_dry():
    u = engine.genesis_universe("LAGOON", 99)
    rng = random.Random(1)
    terr = engine.terrain_of(u)
    for _ in range(30):
        assert engine.place_farm(u, rng, u["settlements"][0])
    for x, y in u["farms"]:
        assert terr[y][x] != 2, (x, y)


def _close_pair(people):
    for i, a in enumerate(people):
        for b in people[i + 1:]:
            if abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) <= 2:
                return True
    return False


def test_a_day_has_work():
    world = engine.genesis(seed=69)
    ev = []
    for _ in range(80):
        engine.tick_world(world, ev)
    terr = engine.terrain_of(world["lagoon"])
    for key in ("eden", "lagoon"):
        people = world[key]["people"]
        assert people, key
        assert all(p.get("act") for p in people), key
        assert len({(p["x"], p["y"]) for p in people}) > 1, key
        assert _close_pair(people), key
    for p in world["lagoon"]["people"]:
        assert terr[p["y"]][p["x"]] != 2, (p["n"], p["x"], p["y"])
    acts = {p["act"] for p in world["eden"]["people"] + world["lagoon"]["people"]}
    assert acts & {"talk", "eat", "hunt", "play", "rest", "walk"}
    by_day = Counter(e[0] for e in ev if e[2] == "famine")
    assert all(n == 1 for n in by_day.values())
    snap = engine.summarize(world)
    person = snap["u"]["lagoon"]["people"][0]
    assert len(person) == 7  # x, y, class, sex, act, face, id
    assert "rounds" in snap["u"]["eden"]


def test_replay_does_not_double_a_famine_day():
    """The same (day, world, message) is one record, even if the day is replayed."""
    seen = set()
    written = []

    def log(evts):
        for day, uni, _kind, msg in evts:
            key = (day, uni, msg)
            if key in seen:
                continue
            seen.add(key)
            written.append(key)

    line = (100, "LAGOON", "famine", engine.famine_line(["Nami", "Raka"]))
    log([line])
    log([line])
    assert written == [(100, "LAGOON", line[3])]


if __name__ == "__main__":
    test_famine_line()
    test_farms_stay_dry()
    test_a_day_has_work()
    test_replay_does_not_double_a_famine_day()
    print("ok")
