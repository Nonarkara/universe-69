# Encounter and labour evidence — 2026-10-30

Scope: source verification and qualitative model boundaries only. No clinical
advice, probability fitting, new fertile-window implementation or model edits.

## Verified primary sources

1. Wilcox AJ, Weinberg CR, Baird DD. “Timing of sexual intercourse in relation
   to ovulation. Effects on the probability of conception, survival of the
   pregnancy, and sex of the baby.” *N Engl J Med.* 1995;333(23):1517–1521.
   DOI [10.1056/NEJM199512073332301](https://www.nejm.org/doi/full/10.1056/NEJM199512073332301);
   [NLM abstract record, PMID 7477165](https://pubmed.ncbi.nlm.nih.gov/7477165/).
   Daily intercourse records and urinary hormones linked conception to a
   six-day interval ending at estimated ovulation in the analyzed cycles.
   Participants were healthy women planning pregnancy; this is not calibration
   for every age, nutritional state, social setting or population.
2. World Health Organization. *WHO labour care guide: user's manual.* Geneva:
   WHO; 2020. ISBN 978-92-4-001756-6. [Official catalogue](https://www.who.int/publications/b/56119).
   Annex 4 recommendations 5–6 distinguish stages before birth and variable
   latent duration. The same definitions are readable in the [official WHO
   intrapartum recommendation summary, page 2, nos. 5–6](https://cdn.who.int/media/docs/default-source/maternal-health/ipc.pdf?sfvrsn=dc30fc00_8).
   A fixed one-day early-labour state is not established by these sources.

## Recommended model constraints, before tuning

- Treat a completed reproductive encounter as an explicit causal exposure.
  A bond, intention, approach, proximity or elapsed quarter-day is insufficient.
  Completion is the model's operational boundary, not an empirically required
  duration of intercourse. Even completion does not mean fertilization occurred.
- If an encounter creates the model pregnancy, persist that encounter's actual
  partner as its genetic-father record. Do not silently substitute the current
  social partner at conception or birth. Unknown legacy attribution stays
  unknown. This is a provenance invariant, not a human paternity inference.
- Keep the gate separate from the conditional probability. Existing per-part
  coefficients were not validated by these papers. Applying them only at
  encounters changes effective fertility, even if their numeric values remain.
- Explicitly disclose omitted sperm survival, ovulation, fertile timing,
  competing encounters and delayed fertilization. The observed study window
  is a source fact, not a new model rule. Without those mechanisms, attribution
  to a single successful encounter is intentionally simplified.
- Expose a represented labour state before the birth event. One model day
  offers an illustrative observable interval at the four-part timestep;
  it must not be presented as a clinical duration, diagnostic threshold,
  validated distribution or new survival benefit.

## Retrieval and limits

Applied `/Users/axiom/.agents/skills/agent-reach/SKILL.md` search/web routes.
`agent-reach doctor --json` failed because its Python module is missing;
`mcporter` reported no configured Exa server. Direct primary-source web search
was the fallback. Jina reached the official WHO catalogue; the NEJM full-page
request returned a security challenge, and WHO IRIS PDF retrieval returned 403.
The NEJM publisher's indexed text and NLM abstract supplied the bibliographic
and study checks; the accessible official WHO recommendation PDF supplied the
labour definitions. No third-party summary was used as evidence.

The WHO document is dated 2020 in its catalogue/copyright; another WHO web
landing page is posted 20 August 2021. Neither posting date changes the document's
citation year. These sources support qualitative causal ordering, not exact
simulation timesteps, encounter frequencies, conception coefficients,
parentage algorithms or a fit to prehistoric demography. No claim of human
validation follows from a controlled model demonstration.

Follow-up source boundary: Lieberman, Tooby & Cosmides (2007),
[*The architecture of human kin detection*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3581061/),
doi:10.1038/nature05510, was checked in the primary full text. It motivates
investigating perceived kinship. The current categorical recorded-family filter
is explicitly an approximation; it does not implement the paper's cue system
or establish universal human mating behavior. See the added DESIGN row.
