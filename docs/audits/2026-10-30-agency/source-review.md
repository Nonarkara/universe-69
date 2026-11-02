# Agency increment: final source review

**Engine 2026.10.30.8: no unresolved blocker within the reviewed changes.** The source matches all thirteen entries in the frozen model manifest. This is a causal implementation/choice review, not validation of human agency or a population outcome.

The reviewer authored the watch guard changes and rechecked their final readback/tests; root separately reviewed that component. The common mate policy and finished-stint normalization were authored by root and independently reviewed here. No production source was changed during this final review.

## Own decisions, not bookkeeping privileges

`needs.assign` now has one mate utility core for eligible adults. In free EDEN, the same world ennui factor applies regardless of the stored `p` biography pointer. The old unpaired-only purpose multiplier is absent. Purpose can still affect the competing post utility; it no longer changes bodily mating utility merely because a relationship pointer exists. Local eligibility, the recipient's own scoring, actual reciprocal completion and the reproductive exposure gate remain separate.

The retained `.7` diagnostic is unchanged. A separate `diagnostics/paired_choice_after.py` reuses the matched controlled bodies, candidates and RNG, copies actual local options from unchanged production `needs.assign`, and writes separate after JSON/log files. It asserts identical paired/unpaired options, tie-band inclusion and selected action, plus unchanged peer state. Only the starting reciprocal biography pointers differ.

| Matched condition | .7 paired / unpaired | .8 paired / unpaired |
|---|---|---|
|Purpose .3, intimacy .5, post|MATE / WORK|MATE / MATE, both utility 1.05, band .918|
|Purpose .6, intimacy .6, post|MATE / MATE|MATE / MATE, both utility 1.20|
|Purpose 1, intimacy .5, post|WORK / MATE|WORK / WORK, both mate utility 1.05|
|Purpose .6, intimacy .6, ennui .5, post|MATE / WORK|WORK / WORK, both mate utility .60|
|Purpose .3, intimacy .5, no post|MATE / MATE|MATE / MATE, both utility 1.05|

The fix does not make mating win every comparison: high-purpose work and world ennui still can win. No pregnancy trial or probability routine is called by this counterfactual, and no coefficient was chosen from resulting births. The controlled generation-two feasible-state proof establishes local pointer invariance, not how frequently these bodies occur naturally.

## Finished activity versus another body's continuing state

The scorer normalizes **only its own** prior action when its stint has ended (`ad<=0`) and its own target has actually been reached. BIRTH and WITHDRAW remain protected continuing states. It does not normalize an unfinished sleeper, an unreached sleep destination, another person's state, or incoming offers. The engine still decides when an actor enters the scorer; normalization is not a command to rescore every ongoing activity.

This removes a stale self-label veto after sleep, voluntary care, grooming or a fight without waking a still-sleeping candidate. Food, water, injury and rest remain competing needs. Visible invitations can reopen only the existing nonurgent activity classes; the recipient independently scores the choice. The readiness suite checks actual dawn wakeup and a completed midday nap, urgent food/rest, continued peer sleep, protected birth/withdrawal and completed care/social stints.

The behavioral upper-45 gate is removed for both initiating adults and candidates. The after probe now allows the former 46-year-old actor/candidate cases; source tests also cover older adults. This is distinct from the unchanged **female 16..45 clinical cycle gate**. Sexual interaction is not a promise of conception, and no child availability guard was removed.

## Watch and gathering do not commandeer explicit needs

Final source excludes A_TEND from guard selection along with the existing bodily/social exclusions. A raw learning/teaching goal also prevents background selection even when its observer label is inactive at night; its own need/learning processing remains responsible for ending it. This avoids turning an intended lesson into a night watch through a presentation-time eligibility difference.

Night gathering can change targets only for uncommitted IDLE/WALK/TALK without those meeting goals. It leaves SLEEP/REST/EAT/DRINK/BIRTH/TEND/FIGHT/RITE/MATE/GROOM and work targets alone. The eligible awake guard pool and actual idle convergence still work. Story increments still require arrived talk by a lit hearth with dry contact.

Separate `care_paths_after` artifacts rerun the original actual call sequence: a caregiver remains TEND when no eligible guard is available, and a different guard can staff watch without retargeting the caregiver or the mother prepared by `labor.prepare`. The old failure evidence remains separate. The new watch suite additionally verifies an actual `needs.assign`-chosen, arrived birth helper rather than only an injected care label.

This is not a rewrite of all watch decision-making: staffing among the remaining eligible camp adults remains the existing background routine. The change prevents the specified preemptions, not a claim that every action in the model has become fully autonomous.

Movement comments now identify tiles per active **part**, matching callers. The legacy-named `reproductive_contacts` docstring describes social-bond resolution, not a conception gate; raw retained exposures continue to survive a father's later death/departure.

## Verification and source boundary

Independently rerun on Apple Python 3.9:

```text
PYTHONPATH=tests /usr/bin/python3 -m unittest test_choice_readiness test_watch_agency test_reproduction test_reproductive_contact test_social_choices test_labor
Ran 81 tests in 0.371s — OK
```

Root's separately run full suite reports 502 passing cases. The watch changes had red-before/green-after tests; the final matched-body and care controls passed against the exact frozen sources. Both before and after scripts save source hashes and full detached actor/peer snapshots. No live data or natural arc was used in these local controls.

Clinical probability tables, private cycle RNG, calendar exposure bins, modifiers, age gate and pregnancy fate mechanisms were not changed; `sim/reproduction.py` retains its prior SHA below. Because behavior and the ordinary world RNG consumption change, natural trajectories still change. New three-seed bounded arcs are separate evidence and must all be reported, including decline/extinction; local choice reachability is not calibrated fertility, guaranteed survival or civilization.

## Exact frozen SHA-256

| File | SHA-256 |
|---|---|
| `sim/animals.py` | `5622b0910d185da4e9c8b6f680ce87a1feada111fb5505b483bd3de563864577` |
| `sim/encounters.py` | `913e361567a682618c20f8a887eefc695eb77af6ad428591843080141eea4394` |
| `sim/engine.py` | `bd4fa94d3c74d7a2dc3f2ab45eb44322adfff70fbc03ada593dce0fd08b293de` |
| `sim/historian.py` | `ad0728651b5f6b326fc02cc05ab2c112dfe34506e1ba1af81dacfa3541f30c69` |
| `sim/labor.py` | `3f05c805ba8d2e0e113e079709909a5f34f40a066dc3df6b3b587983cb36c1be` |
| `sim/learning.py` | `b83ddb2818f8e4675eaebc7f0f38526d08aa4ad06e595ef075f1464bad99a5ff` |
| `sim/minds.py` | `95965b717e4e72fa45a79b48c8b5a00904b416406ce0b6e905bcab882c481d0a` |
| `sim/needs.py` | `add77ab03aa1ccf000cf8b75b16e419adfba3cb22f49fae21c72c623e76adac2` |
| `sim/reproduction.py` | `20c9c189cba51db418eaa000b3b6cd3b7b68c2f865436bbbb485fe182725e3cf` |
| `sim/research.py` | `a0afcd7055afa28777f4c8721a7d5b1fbd70c9c5bbae198f5eae03d4bdca54e4` |
| `sim/server.py` | `5e1bfe65ed3a37e8695c190bc8764fe98d6986108c877fead8c4bbf87cf44f4d` |
| `sim/skills.py` | `5588dad50dd1a925d30a08bb35907cc7cc6c6dc23ab31ca58597aa6eddd74555` |
| `tools/lab.py` | `0df66f318210a7c106fc31a5874679feb2882c901551b743dddc20b8afb1e0f0` |
