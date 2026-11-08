"""Shared need rules with stable, modest personal sensitivity.

Three overlapping triangular memberships have knots (0, midpoint, 1)
and singleton outputs (0, .5, 1). Their normalized Sugeno output is the
piecewise linear response below. Midpoint .5 is exactly the identity curve.

The identity-derived midpoint in [.44, .56] is an illustrative, nonheritable
preference, not an empirical personality measure or a gene/need association.
Matched people in the two worlds share profiles through fseed. Iterations
have distinct profiles; neither world kind nor changing bodily state enters
the hash. No saved fields, RNG draws, hidden learning or outcome feedback.
Legacy dictionaries use the same seed/iteration defaults as engine migration.
"""
import hashlib
import json
from typing import Any, Dict


def midpoint(u: Dict[str, Any], p: Dict[str, Any], need: str) -> float:
    """Return the auditable personal deficit at which response equals .5."""
    identity = [u.get('fseed', u.get('seed', 69)), u.get('iteration', 1), p['id'], need]
    # Explicit separators/encoding avoid Python's process-randomized hash().
    digest = hashlib.sha256(json.dumps(identity, separators=(',', ':'), ensure_ascii=True).encode('ascii')).digest()
    unit = int.from_bytes(digest[:8], 'big') / float((1 << 64) - 1)
    return .44 + .12 * unit


def response(u: Dict[str, Any], p: Dict[str, Any], need: str, deficit: float) -> float:
    """Map a normalized bodily deficit continuously and monotonically to [0,1]."""
    x = max(0., min(1., deficit))
    m = midpoint(u, p, need)
    if x <= m:
        return .5 * x / m
    return .5 + .5 * (x - m) / (1. - m)


# A personal taste for a kind of day. Like the midpoints above, it is
# derived from identity alone — no RNG draw, no saved field, no outcome
# feedback — and it is fixed for life: the same person, in the same
# situation, leans the same way. It is what makes two fed, rested people
# in the same room choose differently: one leans to company, one to the
# work, one to the walk. The spread is chosen so an urgent body still
# dominates (hunger beats any taste) and a comfortable choice can tip.
TASTE_SPREAD = 0.14

TASTE_CATEGORIES = ("work", "company", "still", "roam", "care", "indulge", "quarrel")


def taste(u: Dict[str, Any], p: Dict[str, Any], category: str) -> float:
    """This person's stable lean toward a category of activity, in [-1, 1].

    Identity-hashed like the midpoints: auditable, deterministic, fixed
    for the person's life. A taste is a temperament reading, not a
    measured human parameter."""
    identity = [u.get('fseed', u.get('seed', 69)), u.get('iteration', 1),
                p['id'], 'taste', category]
    digest = hashlib.sha256(json.dumps(identity, separators=(',', ':'),
                                       ensure_ascii=True).encode('ascii')).digest()
    unit = int.from_bytes(digest[:8], 'big') / float((1 << 64) - 1)
    return 2.0 * unit - 1.0
