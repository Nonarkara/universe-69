"""Personal procedural knowledge; history alone never grants a new skill.

Callers establish physical invention, instruction and actual work. This module
records their consequences without reading a world, moving resources or using
randomness. Knowledge persists; it does not expire like resource-stock notes.
The explicit migration prior preserves previously global capabilities without
claiming that an old save recorded personal training or demonstrations.
"""

from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


TECH_LADDER: List[Tuple[str, Optional[str], float, int]] = [
    ("fire", None, 0.50, 2),
    ("stone_tools", None, 0.40, 2),
    ("fishing", "stone_tools", 0.35, 6),
    ("predator_hunt", "fishing", 0.08, 25),
    ("shelter", "fire", 0.35, 6),
    ("preservation", "fire", 0.20, 12),
    ("lore", "shelter", 0.15, 40),
    ("agriculture", "preservation", 0.10, 90),
    ("domestication", "agriculture", 0.12, 120),
    ("granary", "agriculture", 0.20, 120),
    ("seacraft", "fishing", 0.08, 140),
    ("healing", "lore", 0.10, 150),
    ("metallurgy", "granary", 0.06, 250),
    ("writing", "lore", 0.05, 400),
]

_PREREQUISITES = {name: parent for name, parent, _chance, _pop in TECH_LADDER}
_LEGACY_BASIS = "legacy_global_capability"
_LEGACY_MIN_AGE = 12 * 360  # the engine's 360-day calendar


def _entry(p: Mapping[str, Any], tech: str) -> Mapping[str, Any]:
    return (p.get("skills") or {}).get(tech) or {}


def level(p: Mapping[str, Any], tech: str) -> float:
    """Read a bounded recorded level without creating or changing state."""
    if tech not in _PREREQUISITES:
        return 0.0
    return min(1.0, max(0.0, float(_entry(p, tech).get("level", 0.0))))


def knows(p: Mapping[str, Any], tech: str) -> bool:
    """Awareness requires awareness of every prerequisite in the chain."""
    if level(p, tech) <= 0.0:
        return False
    parent = _PREREQUISITES[tech]
    return parent is None or knows(p, parent)


def qualified(p: Mapping[str, Any], tech: str) -> bool:
    """Operational competence requires fully competent prerequisites too."""
    if level(p, tech) < 1.0:
        return False
    parent = _PREREQUISITES[tech]
    return parent is None or qualified(p, parent)


def _new_entry(
    value: float,
    day: Optional[int],
    teacher: Optional[int],
    origin: Optional[int],
    basis: str,
) -> Dict[str, Any]:
    return {
        "level": value,
        "learned_day": day,
        "teacher": teacher,
        "origin": origin,
        "basis": basis,
        "practice_day": None,
        "uses": 0,
    }


def expose(
    p: Dict[str, Any],
    tech: str,
    day: int,
    teacher: Optional[int] = None,
    basis: str = "instruction",
    origin: Optional[int] = None,
) -> bool:
    """Record first instruction as awareness, never repeated-chatter mastery."""
    if tech not in _PREREQUISITES or level(p, tech) > 0.0:
        return False
    parent = _PREREQUISITES[tech]
    if parent is not None and not knows(p, parent):
        return False
    p.setdefault("skills", {})[tech] = _new_entry(.25, day, teacher, origin, basis)
    return True


def invent(p: Dict[str, Any], tech: str, day: int) -> bool:
    """A verified invention grants competence to its eligible inventor only."""
    if tech not in _PREREQUISITES or level(p, tech) >= 1.0:
        return False
    parent = _PREREQUISITES[tech]
    if parent is not None and not qualified(p, parent):
        return False
    previous = _entry(p, tech)
    entry = _new_entry(1.0, day, None, p.get("id"), "invention")
    # Earlier actual work remains factual; invention cannot reopen today's
    # practice allowance or erase a person's already recorded use.
    entry["practice_day"] = previous.get("practice_day")
    entry["uses"] = previous.get("uses", 0)
    p.setdefault("skills", {})[tech] = entry
    return True


def practice(p: Dict[str, Any], tech: str, day: int, worked: bool = True) -> bool:
    """Record one verified daily use, including real use at full competence.

    Prerequisite practice is recorded separately by the action integration;
    calling this function does not fabricate work on the ancestor skills.
    """
    if not worked or not knows(p, tech):
        return False
    entry = p["skills"][tech]
    if entry.get("practice_day") == day:
        return False
    entry["level"] = min(1.0, level(p, tech) + .1)
    entry["practice_day"] = day
    entry["uses"] = entry.get("uses", 0) + 1
    return True


def can_teach(p: Mapping[str, Any], tech: str) -> bool:
    """A legacy capability prior needs real-use evidence before teaching."""
    if not qualified(p, tech):
        return False
    entry = _entry(p, tech)
    return entry.get("basis") != _LEGACY_BASIS or entry.get("uses", 0) > 0


def migrate_person(
    p: Dict[str, Any], history: Iterable[str], day: int, legacy: bool
) -> None:
    """Initialize only absent fields, preserving the explicit old-rule prior.

    Older rules gave historical techniques to everyone of working age. Keep
    that capability as a labelled migration assumption, with unknown training
    day, teacher and origin. It is not evidence of a demonstration, and it
    cannot teach until a subsequent verified use. New people start empty.
    """
    if "skills" in p:
        return
    p["skills"] = {}
    if not legacy or day - p.get("b", day) < _LEGACY_MIN_AGE:
        return
    for tech in history:
        if tech in _PREREQUISITES:
            p["skills"][tech] = _new_entry(1.0, None, None, None, _LEGACY_BASIS)
