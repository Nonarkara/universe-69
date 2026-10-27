# The owner's books → candidate mechanics

Study notes, October 2026, from the owner's shelf. Each row is a
**candidate** for `DESIGN.md`: nothing here is in the engine until it is
built, tested in `tools/lab.py`, and moved into the design table.
Parameter values are design choices to calibrate unless a row says the book
gives the number. All text is paraphrase.

Reading depth was targeted (tables of contents, then the relevant chapters
by search), not cover to cover. The Durkheim volume is mostly secondary
commentary. The Homo Deus copy is the German edition, so check numbers
against the English edition before quoting them.

## Minds and development: Bloom *Psych*, Pinker *Blank Slate*, Frankl

| Finding | Mechanic | World | Caveat |
|---|---|---|---|
| Behavioural traits are ~40–50% heritable. Shared family environment adds near 0; the rest is unique experience (Bloom; Pinker ch.19) | Per-person traits in [0,1]: `ef` (executive function / self-control), `agg`, `sociab`, `risk`. At birth: regressed mid-parent + noise | both | Heritability is not a constant. It is lower in poor environments, and twin-study assumptions are contested |
| Children are socialised mostly by peers, not parenting style (Pinker ch.19, after Harris) | Culture norms drift toward the mean of same-age peers in the tribe, ~0.1/yr. Severe early neglect is still a floor penalty | both | Contested |
| The prefrontal cortex matures last. Damage to it leaves intelligence intact but planning broken (Bloom; Pinker ch.3) | `ef` is expressed ramping with age to ~22, with a risk dip at 13–20. If an impulse check fails, the person takes the nearest immediate reward | both | The age-22 figure comes from general neuroscience, not these books |
| Childhood hunger costs adult capability (Bloom, Flynn discussion) | If mean hunger before age 12 exceeds 0.5, competence drops by up to 0.15 | LAGOON | |
| Average sex differences are small to moderate and overlapping (Pinker ch.18; Bloom) | Sex-shifted trait *distributions*, never rules. Young-male status drive falls with pairing and fatherhood | both | Within-sex variance exceeds between-sex variance |
| Existential vacuum and "Sunday neurosis": when the demands stop, emptiness shows as boredom, aggression and addiction (Frankl, part 2) | `purpose`: rises with tasks, dependents and roles, decays when needs are met with nothing asked. Below 0.3 for 60 days: restless, apathetic, compulsive | **EDEN** | Clinical observation, not a trial |
| People who lost a future died sooner, and a broken hope was followed by deaths (Frankl, part 1) | `hope`: a failed time-bound hope multiplies frailty ×1.5–2 for 14 days | LAGOON | Anecdotal |
| Isolated populations lose technology (Pinker ch.3–4, citing Diamond on Tasmania) | Techniques have carriers. If fewer than 2–3 carriers or no learners remain, the technique is lost | both | The Tasmania case is debated |

**Two clocks.** Genes move slowly: at 2–8 founding pairs, drift and founder
luck dominate, and selection moves an `ef` mean only ~0.05–0.1 sd per
generation even when strong. Culture moves within 1–3 generations, both up
and down. A society "does something different" mainly because the cultural
ratchet turns. The tail of high-`ef` people, who have time and contact,
supplies the inventions. Report the two separately, so nobody mistakes
cultural change for a bigger brain. EDEN's twist: with nothing to solve,
purpose collapses first in its most capable people, and no ratchet forms.

## Violence and civilisation: Pinker *Better Angels*, Freud *Civilization and Its Discontents*

| Finding | Mechanic | World | Caveat |
|---|---|---|---|
| Violent share of deaths: foragers ~14% (4–30%), horticulturalists ~25%, early states ~5% (Pinker ch.2, book's numbers) | Calibration target and a reported metric: % of deaths violent, and homicides per 100k per year, over rolling 50-year windows | both | Disputed by Fry and Ferguson; treat as order of magnitude |
| A third party (Leviathan) replaces feud. Violence fell 10–50× (ch.2–3) | Tribe `arbiter` = legitimacy × capacity. It grows past ~150 members when an elder holds prestige, cuts retaliation, and punishes killers. When the arbiter is lost, violence relapses (Enga) | LAGOON | Legitimacy matters, not just force |
| Revenge deters only if credible, and each side counts its own harm as larger (ch.8, moralization gap) | Kin of a victim carry a `grudge`, decaying ~8%/yr and inherited at half strength. Harm received counts 1.5× | both | |
| Revenge has a dimmer: kinship, valuable ties, shared threat (ch.8) | Grudges decay ×2 across a marriage or trade tie, and during a shared crisis | both | |
| Too many young unmated men (ch.2, ch.10) | Male aggression at 15–30 ×(1+2·unmated). Pairing halves it. Elders damp it | both; EDEN's status-starved males | Correlational |
| Gentle commerce: trade makes a partner worth more alive (ch.3) | Inter-tribe `trade_tie` cuts raid odds by up to 80% | LAGOON | Contested |
| Narcissism of small differences (Freud §V) | Feuds peak between near neighbours and sister tribes after a split | LAGOON | |
| Conscience as an internalised garrison; guilt as the price (Freud §VII–VIII) | `guilt` after harming one's own: less aggression, less happiness | both | Speculative; Pinker rejects the "hydraulic" drive, so model triggers, not a reservoir |
| Happiness traded for security (Freud §III) | Wellbeing = security + freedom − guilt − unmet status. EDEN is maximal security, and its discontent appears as boredom and status contests | **EDEN** | Theory, not a measurement |

## The historical ladder: Diamond *Guns, Germs, and Steel*, Harari *Nexus* and *Homo Deus*

Social-organisation ladder (Diamond ch.14), with hysteresis so a stage
does not flicker:

1. **Band**, under ~50. Informal leaders, no stores, no specialists.
2. **Tribe**, ~50–300. Everyone knows everyone. A big-man, reciprocity.
3. **Chiefdom**, ~300 up to tens of thousands. Hereditary chief, tribute
   and redistribution, priests, 1–2 levels of officials.
4. **State**, 50,000+. Many levels, ledgers, law. Not reachable on these
   maps.

| Finding | Mechanic | World | Caveat |
|---|---|---|---|
| Past a few hundred people, strangers' conflicts force a chief, or the group blows apart (D. ch.14) | `stranger_ratio`, and fission pressure past ~300 without a chief | both | |
| Stored food feeds specialists (D. ch.4, 14) | Specialists come from days of stored food beyond 90. Toolmaker → priest → scribe → soldier → smith. Drought hits them first | LAGOON | Ratios are invented |
| Kleptocracy is tolerated if the elite redistributes, keeps the peace and has an ideology (D. ch.14) | `tribute_rate`, `elite_share` and `legitimacy`. Rising grievance leads a rival lineage to revolt | LAGOON | Easy to over-trigger |
| Mergers come only from threat or conquest (D. ch.14) | No peaceful merging by default | LAGOON | |
| Writing began as accounting (D. ch.12; Nexus ch.3) | `writing` needs a scribe plus a granary or tribute stream. It yields a ledger, not literature | LAGOON | |
| Stories scale cooperation without a chief (Nexus ch.2) | Tribes sharing a founder story are allied. A schism splits the story | both | |
| Networks that claim infallibility cannot self-correct (Nexus ch.4) | `correctability`: a bad belief persists longer under a divine chief. Witch-panic events | both | Keep to one counter |
| Satisfaction tracks expectation, not conditions (Homo Deus ch.2) | EDEN `expectation` adapts to comfort, so satisfaction drifts to 0 (generalises the existing ennui) | **EDEN** | |
| Money and credit are trust fictions (Homo Deus; Nexus) | Credit only after a ledger. A default destroys trust | LAGOON | |

## Religion and cohesion: Durkheim, Peterson's *Genesis* lectures, Warburton

| Finding | Mechanic | World | Caveat |
|---|---|---|---|
| The sacred is set apart and binds a moral community (Durkheim, *Elementary Forms*) | Each tribe sets apart a totem (a species it depends on) or a place (a spring or a grave), taken from a salient event | both | Call it a totem, not a god |
| Collective effervescence renews the sacred (Durkheim) | A rite fires *emergently* when ≥60% of members gather at the site with food. It raises cohesion, lowers anomie and boosts pairing. Skipped rites decay cohesion | both; rare in EDEN | Must be a threshold, not a holiday |
| Suicide's axes, integration and regulation, give four types (Durkheim, *Suicide*) | Per-person `integration` and `regulation`. Low regulation means anomie: wants outrun means, pairing stops, withdrawal. Shown as withdrawal, never as a method | **EDEN** (the beautiful ones) | Parameters are calibration |
| Rising dynamic density forces the division of labour, or struggle (Durkheim, *Division of Labour*) | LAGOON density leads to roles. In EDEN, density rises with no roles, a crowded role-less mass: the key contrast | both | |
| The fall as self-consciousness: covering oneself is the first cultural act (Peterson on Genesis 2–3) | Per-person `selfaware` rises with age and being seen by non-kin. Crossing it, the person covers and ornaments | both | Peterson reads it as psychological, not sexual |
| Cain and Abel: envy over a favoured offering, the first murder (Peterson) | Sibling envy when tribe opinion ranks one sibling below another. Rare fratricide, then exile, and the exile founds a tribe | both | Fires only from state, never scheduled |
| Babel: an over-centralised system scatters (Peterson) | A single enclave at cap scatters into factions, and the lore variant diverges | EDEN | Label the source honestly |

## Economy and captivity: Bestor *Tsukiji*, Smith *Spares* (fiction), the Universe 25 article

| Finding | Mechanic | World | Caveat |
|---|---|---|---|
| Animals learn to crowd where they eat with company (U25 article) | Per-person `site_pref`, so the buffet clumps while the beach stays empty | **EDEN** | Rodent result |
| More rooms in other Calhoun runs prevented the pathology (U25 article) | Cabanas as nooks, an Observer-side pen setting in `sweep.py` | EDEN | |
| Auction at dawn after the boats return, through intermediaries (Bestor ch.4–5) | A market day once fish surplus exists: lots go to the highest need × freshness bid | LAGOON | Needs surplus first |
| Trust between one trader and one supplier, built over years (Bestor ch.5) | `trust` edges between people: fair trades build them, cheating breaks them, and above 0.5 the pair deals privately | LAGOON | |
| Perishability drives timing (Bestor ch.3, 8) | Fish freshness decays faster in the hot season. Smoking or drying freezes decay at a loss | LAGOON | Rates are placeholders |
| Apprentices branch off carrying the master's name (Bestor ch.6–7) | Apprenticeship builds skill, and graduation founds a branch household | LAGOON, late | |
| *Fiction:* children raised fed but unspoken-to never acquire language; the young learn, the old barely do (*Spares*) | `language` grows only from adults talking nearby, with a critical window before ~8 | EDEN | Label as fiction |

## Second pass: survival, drives, routines (October 2026)

Three readers swept every book again by building a keyword index over the
whole text (hunger, forage, share, fear, predator, play, curiosity, tool,
self-control, sleep, groom, boat, voyage, routine, role, festival …) and
reading each dense cluster. Still not cover to cover; each reader recorded
which files were indexed fully and which sampled.

| Finding | Mechanic | Caveat |
|---|---|---|
| Choice between now and later is hyperbolic; the frontal cortex wins when it is the more active (Pinker *Better Angels* ch.9) | Delayed-reward actions weighted by expressed self-control | Curve shape only; no numbers |
| Hunger raises risk-taking; a fed animal will not risk the lion (Harari *Homo Deus*) | Hunger lifts foraging and hunting weights | An example, not a measurement |
| Starving prisoners thought of nothing but food; sex and culture fell away (Frankl) | Under hunger, sex, curiosity and talk lose weight | Camp, not island |
| Chimp communities forage in parties of 1–15 (Pinker ch.2) | Work trips join a party already out | Analogy |
| Infanticide was triage in most societies; nursing lasts 2–4 years (Pinker ch.7); births ~4 years apart nomadic, ~2 settled (Diamond ch.4) | Nursing suppresses fertility; shorter once farming | Infanticide not modelled |
| Carrying density by subsistence; colonists wiped out naive prey (Diamond ch.2) | Island capacity ~95; the mainland arrives untouched | |
| Outriggers and sails made Austronesian crossings possible; drift and scouting came first (Diamond ch.17) | Boat built at the shore over 400 person-days, then a visible crossing | Scouting voyages not yet modelled |
| Tsukiji's seats are a fixed count, refilled only on a holder's exit (Bestor ch.6) | EDEN posts: fixed, filled once | Japanese labour market |
| Routine is built from meals, sleep and recurring contacts; a bedroom needs a purpose elsewhere (Peterson) | Every EDEN activity has a place | Self-help lecture |
| Boredom is a cost of minds with nothing asked of them (Durkheim, via commentary) | Purpose drains in EDEN | Commentary, not Durkheim's text |
| *Fiction (Spares):* captives fed on a timer, never spoken to, collapse to eat–wander–sleep | The placeless in EDEN wander; their days have no shape | Fiction |
