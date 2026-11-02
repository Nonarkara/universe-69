# EDEN choice funnel: unmodified engine .7

This is a bounded diagnostic, not a survival target or a new population model.
Seeds 7, 25 and 69 each ran EDEN alone for 14,400 days (40 model years), using
`engine.genesis(seed)['eden']`, `engine.tick_eden`, and precisely the EDEN RNG
expression in `tick_world`. LAGOON was not advanced. No source, coefficient,
return value, random draw or actor decision was changed.

`trace_eden.py` wraps actual `needs.assign`, `encounters.offer/propose/capture`
and `reproduction.record/advance`. Each intercepted original is called exactly
once; additional candidate/availability queries only read dictionaries. Before
the long trace, each seed ran 120 days from identical deep-copied genesis
states with observation disabled/enabled. Full raw state dictionaries (including
private caches) and exact event sequences matched. Their SHA-256 values and all
before/after source hashes are in the compressed trace. All three processes
exited 0 at the declared horizon. The manifest verifies exact compressed and
uncompressed artifacts, and records the unchanged runner hash.

## Second-generation female funnel

These are decision opportunities and actual contact observations, not independent
people, population rates or probabilities. Action-blocked and hunger-blocked
counts can overlap. A candidate means locally visible and actually available
under the existing encounter guards at that decision.

| Seed | Own assignments | Prior-action guard blocks | Body available | Visible candidate | Mate chosen | Completed participant-parts | Father/day contacts | Evaluated cycles | Exposed cycles | Clinical allocations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 1685 | 1290 | 364 | 218 | 15 | 4 | 2 | 272 | 0 | 0 |
| 25 | 8793 | 8114 | 605 | 484 | 39 | 15 | 10 | 645 | 3 | 0 |
| 69 | 5363 | 5102 | 234 | 145 | 3 | 0 | 0 | 295 | 0 | 0 |

For seed 25 the sum of those three exposed-cycle probabilities is 0.5846;
zero outcomes is not by itself evidence of a broken fertility coin. Seed 69
has four second-generation women alive at year 40, but one is still a child.
Seven second-generation men and four women were observed born alive. These
cohort counts do not count immediate infant losses. Every actor's birth day,
known parents and individual funnel is retained, alongside annual living-sex
cohorts and the endpoint's physical state.

This already rules out a universal explanation of "no unrelated partner can be
found": seed 69's body-available second-generation women had unrelated adults
somewhere in the pen at all 234 decisions, and a compatible person in sight at
145. It does not prove a particular repair would improve survival.

## Source finding: stale sleep action at a fresh own decision

`needs.night` ends the night by setting `ad=0` and the target to the current
position when there is no resumable work, but leaves `a=A_SLEEP`. The same
part's engine then calls the actor's own `needs.assign`.
`_social_person -> encounters.candidates -> available(self)` excludes that
prior sleep action before mating can be scored. Eating and work remain options.
This conflates a person currently sleeping through another actor's invitation
with a person already being asked to make a fresh waking choice. The trace's
large action-guard counts require this distinction before interpreting them as
voluntary refusal, insufficient desire, incest avoidance or inability to travel.
A separate completed action-code detail trace confirms all 5,102 of seed 69's
second-generation female action blocks were `A_SLEEP` (not birth, care or fight).
It reproduces every original funnel count, exact endpoint people and equality
proof. Its distinct runner and artifacts are retained in `seed-69-action-detail`
and pinned in the manifest. No model correction is included in this diagnostic.

Incoming-offer decisions and actual capture failure reasons are separately
retained. For seed 69 second-generation women, two own assignments had an
incoming offer and both selected eating. Men had 48 mating choices, with 28
recorded capture attempts rejected because the peer was not reciprocal; travel
is separately counted. Failed attempt counts overlap paired actor observations
and must not be treated as unique failed sessions.

## Reproduction and limits

Run from the repository root:

```sh
PYTHONUNBUFFERED=1 python3 /absolute/path/to/trace_eden.py --seed 69
```

The retained runner writes scratch evidence under
`/Volumes/Data/agent-scratch/u69-agency`; change only the output directory if
needed. Run the other declared seeds with `--seed 7` and `--seed 25`.

The initial 120 days are included in decisions/contact counts; newborn identity
observations begin after that equality check. `incoming_offer_returned` counts
actual helper returns, potentially repeated for an invitation; the separate
`assign_with_incoming_offer` counter counts own decision opportunities. Global
partner checks are reviewer diagnostics only and never enter actor knowledge.
`available` alone lacks the chooser's upper reproductive-age limit; use the
explicit `reproductive_age_*` counters for adult body gating. For gen2 females
within these 40-year traces, all own assignments fall in that 16–45-year range.

These are local-workbench diagnostics. They are not full two-world century
runs, independent empirical observations, a calibrated human model, or evidence
that EDEN ought to survive. Original scratch states remain available to the
parent audit; no live MacBook state was accessed.
