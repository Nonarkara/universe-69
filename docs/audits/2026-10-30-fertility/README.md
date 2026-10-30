# Reproductive timing — engine 2026.10.30.7

The `.6` audit found actual meetings but an incorrectly timed conception
hazard. This increment replaces the old daily/part rate with genuine exposed
days, an individual cycle clock and one clinical-outcome allocation per cycle.
It changes future trajectories. It does not establish a realistic population,
validate the full human model or guarantee civilization.

## Causal change

- A completed mutual mate contact supplies an actual father/calendar-day
  record and detached hereditary values. Repeated parts with the same father
  on that day add no opportunity. The social token is not treated as an act
  counter. A continuing completed action on a new day may expose that day.
- At most four distinct fathers/day are retained across six calendar-day bins.
  No exposure is invented by a bond, a global male pool, migration or a query.
  A father's later death, departure or new relationship cannot erase earlier
  genuine exposure; a mother must still be alive to allocate a pregnancy.
- Each mature female has an individual deterministic phase and variable
  24–35-day interval prior. Her cycle stream is independent of actor order,
  observer queries, wall-clock pace and the main action RNG. Initial unknown
  phase is a fresh prior, not inferred menstrual or sexual history.
- The night closes the model ovulation day after that part's exposures are
  recorded. One evaluation marker and next schedule are saved before outcome
  sampling. Duplicate calls, parts and JSON reloads cannot reroll that cycle.
- Clinical pregnancy references for O−5..O are .04, .13, .08, .29, .27, .08.
  Several exposed days use the maximum applicable reference, scaled once by
  existing physiology/environment hypotheses with a modifier capped at 0–1.
  There is no division by four, independent product of marginal risks or
  above-reference food-surplus boost.
- Paternity is sampled uniformly among maximizing **records**, not necessarily
  unique fathers. A father represented on two tied days has two records. This
  is explicit bookkeeping, not a sperm-competition or paternity-inference model.
- Existing pregnancies, due dates, hereditary values and known/unknown father
  IDs are preserved. Newborn/reseeded/legacy reproductive state defaults to
  `None`. A private phase initializes lazily without inventing old exposure.

## Endpoint and model limits

The published vector concerns clinical pregnancy, not fertilization, early
hCG detection or live birth. Allocating its trajectory at O is operational
advance sampling, not same-day clinical recognition. The existing .14 later
recognized-loss hypothesis and O+50–90 loss timing remain unfitted; no extra
hCG-to-clinical early-loss coin is added. Birth remains due at O+270.

The maximum-day rule is an explicit most-fertile-exposure approximation, not
an estimated joint probability model or proven conservative bound. The cycle
interval is an illustrative uniform prior, not a fit to pooled app data or
within-woman variability. Calendar bins do not represent a strict 120-hour
sperm-survival window or measured subday ovulation. Nutrition, nursing, age,
illness and social multipliers remain hypotheses. Postpartum hormones,
anovulation, full physiology, perceived kinship, genetic load and clinical
outcome calibration remain incomplete. See [the primary-source review](research.md).

## Controlled verification

The independent [controlled runner](controlled/README.md) uses genuine mutual
`encounters.capture → record → advance` facts in explicit fixtures with forced
known reference days. Expected values are hardcoded from the primary source,
not read back from the implementation's constants.

| Exposure day | Reference | Allocations / 10,000 independent seeds |
| --- | ---: | ---: |
| O−5 | .04 | 396 |
| O−4 | .13 | 1,282 |
| O−3 | .08 | 767 |
| O−2 | .29 | 2,881 |
| O−1 | .27 | 2,653 |
| O | .08 | 767 |

Every rate is within 1.22 binomial standard errors of its configured reference.
No exposure and O−6 controls allocated zero pregnancies in 10,000 replicas each.
Repeated contact parts, repeated ingestion, modifier 5 versus 1, and JSON
roundtrip controls produced identical outcomes and cycle states for the paired
same seeds. Python 3.9.6 and 3.14.6 sequence digests match, beyond matching totals.
This verifies implementation/units against the selected configuration; it is
not clinical validation, natural mating frequency or a population calibration.

Independent source reviews: [module](module-review.md),
[integration and query purity](integration-review.md). All source is standard
library Python; the renderer and its mirrors retain the prior byte-identical
source. Natural checkpoint rendering is separately scoped under `viewer/`.

## Final tests and natural checkpoint

The final full suite passes **482/482 on Apple Python 3.9.6** in 449.039 seconds
(`full-suite-shipped-apple.log`). The prior 481-case full Python 3.14.6 suite
passes in 247.762 seconds; the extra final case pins the phone-header repair.
Pure-module, engine lifecycle/paternity, older-save, duplicate/reload, query
purity and private-RNG controls are retained alongside the independent reviews.

The natural year-10 seed-69 checkpoint is rendered at 390×844, 1024×768 and
1440×900, with real pointer selection, native keyboard focus, MORE and expanded
headings. No body, person position or proposal is synthesized. Independent
review accepts all 12 screenshots and 119 checks. The phone selected activity
repeated in header/card/caption and wrapped an orphan SLEEPING line; the header
now keeps the name and preserves full activity in the other existing regions.
This recovers 18.84375px of scene height (heading 46.59375→27.75px; total chrome
22.55%→20.32%) without new panels, clipping or smaller type.

This is a saved workbench checkpoint, not the live instrument. Its exact raw
summary omits narrative history and the static basemap: history is not invented
or asserted empty, and the terrain adapter is separately derived from the same
frozen seed/version. The broader `.6` browser journey remains historical
coverage; current natural checks are scoped to these states. See
[viewer evidence and qualifications](viewer/README.md).

## Predeclared natural experiments

Seeds 7, 25 and 69 each run 36,000 model days using the standard bounded lab.
No parameters are adjusted to select survivors. Read-only wrappers count
father/day records, evaluated/exposed cycles, allocated clinical trajectories
and newborn records observed at the birth part. These are distinct from
intercourse sessions, live-birth totals or surviving descendants. Exact sources
are hashed before and after each run. Elapsed times include concurrent checks
and are not MacBook throughput measurements.

All three runs completed the full horizon with source hashes unchanged. Seed 69
took 777.677s, seed 25 1,224.738s and seed 7 1,331.135s under concurrent load.
Seed 69 and 25 exit status 0 was observed. The seed-7 worker hit a model-capacity
error after launching its process; its original tool handle could not be
recovered. The final arc, state and last-written provenance were present, no
traceback appeared and the process was gone. Its OS exit status is left unknown
in the manifest rather than fabricated. No run was restarted or shortened.
The live instrument/state were not used.

| Seed | World | Peak | End population | Max maternal generation | Age-eligible F/M | Children F/M |
| --- | --- | ---: | ---: | ---: | --- | --- |
| 7 | EDEN | 22 | 0 | 2 | 0/0 | 0/0 |
| 7 | LAGOON | 55 | 30 | 6 | 7/4 | 6/6 |
| 25 | EDEN | 25 | 1 | 2 | 0/0 | 0/0 |
| 25 | LAGOON | 51 | 29 | 6 | 4/8 | 9/4 |
| 69 | EDEN | 27 | 1 | 2 | 0/0 | 0/0 |
| 69 | LAGOON | 28 | 5 | 3 | 0/0 | 0/0 |

Age eligibility uses the shipped 16–45 model gate, not a clinical fertility
assessment or proof of viable mating. Generation is the existing maternal
counter. EDEN seed 7 emptied on day 35,619; no case reseeded within the century.
The surviving EDEN women are about 88.41 (seed 25) and 82.97 (seed 69) model
years old. LAGOON 69 contains only men, aged 52.56–76.56. Those positive
headcounts are not viable breeding populations. Seeds 7 and 25 retain younger
cohorts and children; their survival beyond this horizon is unproven.

| Seed | World | Exposed cycles | Clinical allocations | Birth-part newborn records | Known father IDs in those records |
| --- | --- | ---: | ---: | ---: | ---: |
| 7 | EDEN | 54 | 7 | 7 | 7 |
| 7 | LAGOON | 2,869 | 185 | 139 | 139 |
| 25 | EDEN | 81 | 10 | 9 | 9 |
| 25 | LAGOON | 2,149 | 136 | 99 | 99 |
| 69 | EDEN | 78 | 10 | 11 | 11 |
| 69 | LAGOON | 733 | 53 | 34 | 34 |

Clinical allocations are trajectories, including later recognized loss.
Birth-part records exclude children lost before a person record is created;
twins can produce more than one record from one allocation. These are not
intercourse counts, total live births or endpoint survivors. Paternity counts
verify retained model provenance, not human inference of genetic paternity.

LAGOON seed 7 recorded lore as well as fire, tools, fishing, shelter,
preservation and predator hunting. Seeds 25/69 recorded the latter six methods.
These are historical discoveries, not claims that all living people know them.
No run demonstrated agriculture, metallurgy, writing or a great civilization.

All EDEN model death counters are age deaths and all three cases stop at
generation two. This does not establish a Calhoun crowding-collapse mechanism.
LAGOON counters include substantial dehydration, violence and infant losses;
these are model bookkeeping, not independently identified human causes.
The next causal audit should examine offspring mating opportunities, the
proposal→acceptance→contact funnel, age/sex cohort composition, work/rest/travel
budgets and physical water access. Do not raise the published clinical
benchmark to manufacture population replacement.

Exact endpoint classifications and qualifications are in `demography.json`,
with the executed read-only reader. Compressed arcs/logs, source-bound
provenance and terminal-status qualifications are under `arcs/`.
The full digital-human/civilization goal remains in progress.
