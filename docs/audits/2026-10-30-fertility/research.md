# Fertility calibration evidence — 2026-10-30

Research only: no simulation/UI edits, medical advice or fitted parameters.
Recommendation: use the literature to choose a stated endpoint and exposure
structure; do not claim the existing per-part pregnancy roll is calibrated.

## Verified endpoints and coefficients

| Source | Quantity and units | What may be reused honestly |
| --- | --- | --- |
| Wilcox, Weinberg & Baird (1995) | Estimated pregnancy probability with intercourse on one day relative to estimated ovulation; urinary hCG around implantation | Six-day exposure support and endpoints0.10 at−5 /0.33 at0, as study-specific benchmarks; not directly observed fertilization |
| Li, Wilcox & Dunson (2015) §2.3 | Clinical pregnancy probability following a single act, indexed by ovulation-relative day | Exact vector below; not per quarter-day and not live-birth probability |
| Dunson et al. (1999) | Clinical pregnancy estimates corrected for ovulation-marker error | Peak before ovulation and measurement-error caution; not the same estimand as the 1995 hCG curve |

The primary 2015 article explicitly provides:

| Day relative to ovulation | −5 | −4 | −3 | −2 | −1 | 0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Single-act clinical-pregnancy probability | 0.04 | 0.13 | 0.08 | 0.29 | 0.27 | 0.08 |

It fixed outside-window pregnancy probability to zero after citing estimates
below 0.01. Zero here is an approximation. Its menstrual-calendar-day table
integrates uncertain ovulation and a behavior distribution; it must not be
applied as another multiplier on top of the ovulation-relative vector.
The 1995 hCG curve and this clinical vector must not be spliced or relabelled
as interchangeable fertilization estimates.
The selected 2015 vector peaks at reference day −2; the error-corrected 1999
analysis peaks at −1. They are not one interchangeable curve, and the chosen
model reference day is not an observed subday egg-release time.

## Selected .7 contract: an explicit best-exposure approximation

The implementation decision is daily binary exposure: a day with at least one
completed mutual mating contact is exposed once, regardless of quarter-parts
or number of partners. Actual father candidates remain recorded. After the
ovulation calendar day closes, make one clinical-pregnancy outcome trial with
`max(q[d])` across exposed days in bins −5…0, or zero without exposure. Modifiers
are bounded to 0…1: environmental or physiological factors cannot boost the
healthy-reference benchmark. Their strengths remain qualitative model choices.

Royston & Ferreira (1999) provide primary precedent for an approximate most-
fertile-intercourse-day model. This particular maximum of the 2015 marginal
vector is not a reproduction of their fitted algorithm. It is not a calibrated
joint probability or a proven conservative bound; contributions from other
days and dependence between exposures remain unknown. Choosing a father only
among actual partners from the best day, including any tie rule, is unfitted
bookkeeping and not a claim about sperm competition.

Intervals are sampled uniformly over integer days 24…35. This gives mean 29.5
and population SD `sqrt((12²−1)/12) ≈ 3.45` days by arithmetic, not fitting. Each
person starts at a sampled phase in her current interval with no invented
historical exposure. Cycle/phase renewal, ovulation placement and menstrual
semantics remain explicit simulation assumptions. There is no subday estimate
of ovulation: six calendar-day bins are not a strict 120-hour sperm clock.
Allocating an outcome at the end of model ovulation day does not imply clinical
recognition at that time.

The existing miscarriage probability 0.14 is retained only as an illustrative
later loss conditional on the clinical-endpoint pregnancy. Its scheduled
50…90 days after the model ovulation date are also illustrative. There is no
additional hCG-to-clinical/preclinical loss roll. Wilcox et al. (1988) separately
identified losses before recognition and total postimplantation losses; these
denominators cannot be used interchangeably or subtracted without conditioning.
They do not supply this model's 0.14 or its event-time distribution.

## Multiple acts and independence

The classical product-of-failures formulation assumes independent effects of
intercourse days; extensions add cycle viability and couple/cycle heterogeneity.
That independence is not a biological law. Sundaram, McLain & Buck Louis (2012)
explicitly discuss it and develop a model that relaxes it. Their methods also
show why an act-free cycle needs zero pregnancy opportunity.

If a viable-cycle formulation is chosen, write its interpretation explicitly:
`P(outcome | exposed days) = v × (1 − product(1 − r[d]))`, where `r[d]` is
conditional on viability and `v` is cycle viability. A published marginal
single-act probability `q[d]` is not automatically `r[d]`; inserting it there
and adding another viability multiplier changes its meaning. The sources do
not identify a unique lightweight dependence model for this simulation.

Daily diary variables describe whether intercourse occurred on a day. They do
not justify independent retries for every quarter-part, animation frame, or
multiple reports of the same completed encounter. As a numerical illustration
of the error, four independent trials of 0.29 yield about 0.746, not 0.29. This is
arithmetic, not an empirical estimate of repeated intercourse.

## What remains assumed

The selected structure does not fit the timing or frequency of actual
menstruation, anovulation, puberty, postpartum amenorrhoea or menopause. Initial
phase and renewal/reset rules need explicit state semantics; every founder
must not inherit fabricated prior intercourse. Retaining exposure days until
ovulation represents qualitative persistence, not tracked sperm viability.

Social choices remain independent agents' decisions, not assignments by the
observer. The literature's association between intercourse and ovulation does
not establish that inhabitants know their ovulation date. A cycle clock or
clinical benchmark supplies no desire, willingness, partner, age/BMI curve,
nursing effect or environmental coefficient. Without a matching endpoint,
exposure denominator and joint-outcome fit, no population calibration claim
follows. No model tuning or century run was done in this research lane.

## Variability and generalization

Wilcox et al. (2000) found substantial cycle timing variation; among 69 cycles of
length 28, only 10% had ovulation exactly 14 days before the next menses. That
observation does not supply a complete cycle-length generator.
Dunson, Colombo & Baird (2002) analyzed 782 healthy natural-family-planning couples
and 5860 cycles using basal temperature. Reported age-group differences do not
establish a linear year-by-year multiplier or cover undernourished founders,
postpartum amenorrhoea, adolescents, infertility or every mating system.
Ovulation measurement error and selected healthy cohorts limit all transfers.

## Cycle length descriptives, not a fitted generator

Bull et al. (2019), publisher Table 1, report 612,613 detected-ovulatory app
cycles: mean ± SD cycle length 29.3 ± 5.2 days, follicular length 16.9 ± 5.3 days,
luteal length 12.4 ± 2.4 days. Only 13% were exactly 28 days. The pooled SD is not
per-person jitter; their per-user variability summary is 2.6 ± 2.5 days. Sampling
was from app users aged 18…45 and excluded cycles without detected ovulation.
The selected uniform 24…35 rule is a bounded illustrative clock that permits
variation; it is not fitted to these pooled values and omits tail/ovulatory
failure behavior. A bounded interval and mean alone do not validate a
follicular/luteal phase generator.

## Primary-source provenance

- Wilcox AJ, Weinberg CR, Baird DD. 1995. *Timing of sexual intercourse in
  relation to ovulation. Effects on the probability of conception, survival of
  the pregnancy, and sex of the baby.* NEJM 333(23):1517–1521.
  [DOI 10.1056/NEJM199512073332301](https://www.nejm.org/doi/full/10.1056/NEJM199512073332301),
  [NLM abstract](https://pubmed.ncbi.nlm.nih.gov/7477165/).
- Dunson DB, Baird DD, Wilcox AJ, Weinberg CR. 1999. *Day-specific probabilities
  of clinical pregnancy based on two studies with imperfect measures of
  ovulation.* Human Reproduction 14(7):1835–1839.
  [DOI 10.1093/humrep/14.7.1835 / NLM](https://pubmed.ncbi.nlm.nih.gov/10402400/).
- Dunson DB, Colombo B, Baird DD. 2002. *Changes with age in the level and
  duration of fertility in the menstrual cycle.* Human Reproduction 17(5):1399–1403.
  [DOI 10.1093/humrep/17.5.1399 / author institutional record](https://scholars.duke.edu/publication/769710).
  Abstract verified; no unavailable full-text coefficient table was claimed.
- Wilcox AJ, Dunson D, Baird DD. 2000. *The timing of the “fertile window” in the
  menstrual cycle: day specific estimates from a prospective study.*
  BMJ 321:1259–1262. [DOI 10.1136/bmj.321.7271.1259 / full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC27529/).
- Li D, Wilcox AJ, Dunson DB. 2015. *Benchmark pregnancy rates and the assessment
  of post-coital contraceptives: an update.* Contraception 91(4):344–349.
  [DOI 10.1016/j.contraception. 2015.01.002 / full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4374046/).
  §2.3 supplies the exact six coefficients; its Table 3 has a different time axis.
- Sundaram R, McLain AC, Buck Louis GM.2012 (online 2011). *A survival analysis
  approach to modeling human fecundity.* Biostatistics 13(1):4–17.
  [DOI 10.1093/biostatistics/kxr015 / primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3276273/).

Agent-reach skill and search routing were read. Exa returned “Unknown MCP
server 'exa'”; the reported doctor module failure was already known. Direct
primary web search/read was the fallback. NEJM's direct full page returned 403;
its primary publisher/NLM indexed abstract was verified. OUP full-text routes
were unavailable for the 2002 article, so the author's Duke record was used for
its abstract and citation. PMC full text supplied the 2015 coefficients and
2000 cycle-variability evidence; primary indexed methods text supplied the 2012
independence discussion. No blog or fertility calculator supplied coefficients.

Additional primary citations for the selected contract:

- Royston P, Ferreira A. 1999. *A new approach to modeling daily probabilities
  of conception.* Biometrics 55(4):1005–1013.
  [DOI 10.1111/j.0006-341x. 1999.01005.x / NLM abstract](https://pubmed.ncbi.nlm.nih.gov/11315041/).
- Bull JR, Rowland SP, Berglund Scherwitzl E, Scherwitzl R, Gemzell Danielsson K,
  Harper J. 2019. *Real-world menstrual cycle characteristics of more than
  600,000 menstrual cycles.* npj Digital Medicine 2:83.
  [DOI 10.1038/s41746-019-0152-7 / publisher](https://www.nature.com/articles/s41746-019-0152-7).
- Wilcox AJ et al. 1988. *Incidence of early loss of pregnancy.*
  NEJM 319(4):189–194. [DOI 10.1056/NEJM198807283190401 / NLM](https://pubmed.ncbi.nlm.nih.gov/3393170/).

The skill-mandated update check was attempted; `agent-reach check-update`
also failed with the missing `agent_reach` module. No update status is claimed.
