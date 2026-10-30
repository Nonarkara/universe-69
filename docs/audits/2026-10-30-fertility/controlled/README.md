# Controlled exposure-unit verification

**Mechanism verification only.** This is not population calibration, clinical
validation, natural intercourse behavior or a model of directly observed
fertilization. The output is an allocated clinical-endpoint payload; no
gestation, birth or century arc is simulated.

## Results

Each lag uses 10,000 replicas with distinct `u.seed` values. The expected vector
is hardcoded from [Li, Wilcox & Dunson (2015), §2.3](https://pmc.ncbi.nlm.nih.gov/articles/PMC4374046/),
not read from production constants. Probabilities are per single exposed-day
benchmark; they are not per quarter-part. The same seed range is paired across
lags, so the rows are not independent of each other.

| Exposure day | Expected | Allocations / 10,000 | Proportion | Binomial SE at expected | z |
| --- | ---: | ---: | ---: | ---: | ---: |
| O-5 | 0.04 | 396 | 0.0396 | 0.00196 | -0.20 |
| O-4 | 0.13 | 1282 | 0.1282 | 0.00336 | -0.54 |
| O-3 | 0.08 | 767 | 0.0767 | 0.00271 | -1.22 |
| O-2 | 0.29 | 2881 | 0.2881 | 0.00454 | -0.42 |
| O-1 | 0.27 | 2653 | 0.2653 | 0.00444 | -1.06 |
| O+0 | 0.08 | 767 | 0.0767 | 0.00271 | -1.22 |

All deviations are below 1.22 binomial SE. The runner uses a broad six-SE
failure threshold to catch implementation mismatches; this does not test
uncertainty in the published coefficients or their generalizability.

Per lag, all 10,000 paired controls give identical allocation payloads **and**
cycle states for:

- Twelve duplicate current-part captures/ingestions across the same four-part
  calendar day, using the same father. No extra probability or second trial.
- JSON save/reload after recording the exposure and before ovulation resolution.
- Passing modifier 5 instead of 1: the healthy-reference cap prevents a boost.

No-contact and actual O−6 exposure controls each allocate 0/10,000. This is the
configured coarse-window rule, not proof of biological sterility outside it.
An EDEN preflight rejects separated and travelling contact and accepts arrived
mutual contact through the actual capture function; water/path geometry and
full-engine physiological modifiers are separate integration-test concerns.

## Procedure and provenance

Fixtures use healthy 25-year-old adults, explicit reciprocal proposals at an
actual shared position, known synthetic ovulation day 100 and one father. Every
exposure is returned by `encounters.capture`, ingested by `reproduction.record`,
and resolved by `reproduction.advance`. No ambient/forged frame or probability
constant is substituted. Only the calendar fixture and controlled contact/body
setup are specified; social choice is not being validated.

Python 3.14.6 and Apple Python 3.9.6 produce identical counts, control outcomes
and SHA-256 digests of every per-lag allocation/cycle-state sequence. No
per-replica states are retained. Both runs have unchanged before/after source
hashes and no failures.

- [Runner](run.py), [Python 3.14 results](results.json), [exact output](run.log).
- [Python 3.9 results](results-python39.json), [exact output](run-python39.log).
- [Research definitions and limitations](../research.md).

The executed dependency modules are `reproduction.py`, `encounters.py` and
`minds.py`. The results additionally record every simulation source hash,
including `engine.py`, as contextual provenance; the full engine is not
imported or exercised by this module-level experiment. This distinguishes
JSON state persistence here from the complete engine migration/save integration.

```sh
python3 docs/audits/2026-10-30-fertility/controlled/run.py --replicas 10000
/usr/bin/python3 docs/audits/2026-10-30-fertility/controlled/run.py --replicas 10000 --out docs/audits/2026-10-30-fertility/controlled/results-python39.json
```

Runner SHA-256: `b12dd134ad49ba92e634084c541072a4a4e216243ff52d85d349e6f6ef2453f5`.

Elapsed time: 13.88s on Python 3.14; 27.45s on Python 3.9.
