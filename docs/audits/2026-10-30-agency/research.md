# Independent agency and physical-units audit

Audited main `638eb48`, engine 2026.10.30.7, 2026-10-30. This is a read-only code/research audit; no model, renderer, parameters or trajectory were changed by this lane. It evaluates decision causes, not a desired survival result.

## Exact decision cause

`needs.assign` first finds a genuinely local available compatible mate. Both branches then use the same bodily score:

`(.3 + .3*want_company + 1.5*intimacy) * (1-.85*want_food) * (.4+.6*energy)`.

Only an **unbonded EDEN actor** receives an additional `(0.4+purpose)*max(.2,1-ennui)` multiplier. At purpose .5 and ennui .8 this is .18: the same body and available unrelated partner receive 18% of the bonded actor's utility. At purpose 1 and ennui 0 the multiplier is 1.4, so it is not always a penalty. The difference is determined by own bond status, rather than whether this actual proposed partner is the bond partner. EDEN compatibility permits nonbond partners; LAGOON separately excludes competing bonds.

This is an unsupported motivational asymmetry, not a demonstrated human effect or an access restriction. The narrow recommendation is to use a common personal desire score and preserve local perception, actual independent acceptance, urgent bodily exclusions, known-family exclusions and world-specific access rules. Removing the asymmetry would be an explicit model assumption/correction, not empirical proof that everyone has identical desire. Preserve the already separate fertility environmental hypotheses unless separately justified; do not increase weights until a population survives.

Murray & Milhausen (2012), *Sexual desire and relationship duration in young men and women*, surveyed 170 university students aged 18–25. Duration related differently to reported desire by sex. This cross-sectional, partnered sample cannot establish lower bodily desire in all singles or the EDEN purpose/ennui multiplier. [Primary abstract/DOI](https://pubmed.ncbi.nlm.nih.gov/22268980/), doi:10.1080/0092623X.2011.569637. Only the abstract was available for this audit; no unreported coefficients were extracted.

## Actual units and scheduling

| Mechanism | Executed units | Interpretation / limitation |
|---|---|---|
| Calendar | Four parts/day | Each part spans six model hours; wall-clock speed does not alter the simulated interval. |
| Movement | `step_toward` up to 3 EDEN /6 LAGOON tile steps **each part**, thus up to12/24 per uninterrupted day | Source comments say per day incorrectly. Diagonal steps can cover sqrt(2) coordinate units; obstacles change paths. No surveyed metres/tile: no defensible km/day or walking-speed claim. |
| Visibility/contact | Sight radius6 tiles; contact squared distance≤2, dry route and completed reciprocal targets | Topological proximity abstraction, not metre-calibrated interpersonal distance. |
| Social stints | `_duration(8/7/21)` raw1–2 ticks after arrival, i.e.6–12 model hours | The comment “an hour” is false. These are coarse occupancy/decision bins, not measured intercourse duration. Travel precedes countdown. |
| Work stints | Hunting1–2days; foraging/fishing7–15; farm5–12; build4–9, converted by `days()` | Commitment lengths, interrupted/paused by other machinery; not continuous labour hours. Harvest fulfillment is additionally gated once/person/day. |
| Contact completion | Same-instant reciprocal actual actions and arrived targets, after movement | An endpoint fact does not imply six hours continuously together. Daily exposure is binary downstream; repeated parts do not independently multiply conception trials. |
| Intimacy | Refill1/(7×4) per part from age16; reset0 on completed contact | Seven-day linear urgency and weight1.5 are explicitly illustrative, not libido/frequency calibration. |
| Energy | Work−.055/day; travel−.012/day while off target; social−.008/day; sleep+.2/part; rest+.08/part | Dimensionless meters. Travel cost is based on pre-movement target mismatch, not physical distance. Work cost follows action, including transit. One sleep part restores ~3.64 work-days of this meter, not a measured sleep physiology result. |
| Night | Forced sleep for most nonurgent actions at part3; own position/home target; sleep duration2ticks; dawn restores paused work | `A_MATE` is exempt even for pending noncontact proposals; this can occupy the night without completed contact. Sleep scheduling is not governed solely by energy utility. |
| Labour | Due within0–1calendar day, mother at own dry location; cleared by delivery/resolution | Explicit illustrative visibility interval, not a clinical labour-duration fit. Delivery dates remain separate. |

`ad` decreases only on arrival. A distant goal can therefore occupy more than the nominal stint duration, and an unavailable offer can occupy decision time before contact. Urgent checks and night rules must be evaluated separately from the utility formula. The existing independence protocol is valuable; reducing a coarse meeting bin must not become assigning the other person's action or inventing remote contact.

## Sleep evidence and recommendation limits

Yetish et al. (2015), *Natural Sleep and Its Seasonal Variations in Three Pre-industrial Societies*, Current Biology25:2862–2868, doi:10.1016/j.cub.2015.09.046, measured three populations. Average sleep duration was5.7–7.1h, while onset-to-offset periods were6.9–8.5h. Timing varied with season and temperature; dusk was not a universal sleep onset. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC4720388/), [primary abstract](https://pubmed.ncbi.nlm.nih.gov/26480842/).

This supports a daily sleep need and contextual timing, not one universal prehistoric schedule, an automatic6h block, or the current energy constants. No sleep coefficient is fitted here. The smallest next step is to name units honestly and test decisions/interruptions within the existing clock. Subpart action time or a surveyed world scale would require a separate explicit design; do not silently reinterpret tiles as metres or contacts as six-hour acts.

## Retrieval and reproducibility

Read existing RESEARCH/DESIGN before recommendations. Applied agent-reach search routing: `agent-reach doctor --json` failed with `ModuleNotFoundError: agent_reach`; documented Exa command failed `Unknown MCP server exa`. Used direct primary PubMed abstracts via web fallback. The linked PMC full text presented a browser challenge; numerical sleep facts here are verified in the primary PubMed abstract, not claimed from a retrieved full text. `agent-reach check-update` failed with the same module error. No discussion sites, clinical advice, outcome tuning, long simulation or generated coefficients were used.

Audited source SHA256 (pre-change inputs; root may subsequently implement separately):

- `sim/needs.py`: `1d9f69de0b20b71710d529e91d52b2c6e339bc63f48c716f7b9f007e781db6a5`
- `sim/engine.py`: `53415944ef4d5af155462f7af4217053319868a2f6e1abc4cfa952af16b8ee53`
- `sim/encounters.py`: `913e361567a682618c20f8a887eefc695eb77af6ad428591843080141eea4394`
- `sim/labor.py`: `3f05c805ba8d2e0e113e079709909a5f34f40a066dc3df6b3b587983cb36c1be`

## Adult interaction versus reproductive age (.8 implementation boundary)

Lindau et al. (2007), *A Study of Sexuality and Health among Older Adults in
the United States*, NEJM357:762–774, doi:10.1056/NEJMoa067423, studied 3,005
adults aged57–85 and observed continuing sexual activity in each age group.
[Primary abstract](https://pubmed.ncbi.nlm.nih.gov/17715410/). Root verified the
primary record after the research worker's model-capacity failure. This supports
removing a universal behavioral zero at45, not a prehistoric frequency schedule,
constant older-adult libido, consent assumption, or fertility curve. The separate
female16–45 clinical cycle gate remains unchanged. Male reproductive aging,
menopause and age-dependent preference are still incomplete.

The final implementation also fixes finished self-action readiness and protects
care/explicit meetings from background watch/gather preemption. Those are
execution/agency corrections, not coefficients inferred from the papers above.
The final source hashes belong in `source-review.md`; hashes in this research
note identify the actual older inputs and are intentionally not rewritten.
