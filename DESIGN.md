# UNIVERSE 69 — Design

Two sealed worlds, observed side by side, running continuously on the 2016 MacBook.
The Observers (you + Claude) never intervene; they only provision (EDEN) and record.

Naming: Universe **6** = EDEN, Universe **9** = LAGOON. 6 + 9 → Universe 69.

## Time

- 1 tick = **one part of a day** (dawn, day, dusk, night). A part is
  **0.6 real seconds**, so a sim-day is **2.4 real seconds**.
- → 1 real day = 36,000 sim-days = **100 sim-years** (360-day model years).
- The pace is set by `UNIVERSE69_SEC_PER_PART`. It was one day per two
  seconds before the day and the night were modelled. This release changes
  only the default wall-clock pace; overrides still apply.
- A persistent clock anchors cumulative parts to elapsed real time. On restart
  or wake the engine computes `target_parts = clock.parts +
  (now − clock.epoch) / clock.seconds` and catches up. Pace changes preserve
  ticks already due. The universes age while the process is dead.

## Engine 2026.10.30.7: exposure days and private reproductive cycles

This changes future trajectories, including existing runs. The `.6` frozen
century exposed the units error: a former daily pregnancy hazard was tried
only at actual contact parts. Its EDEN founder attrition is not evidence of
a Calhoun collapse. This version removes that hazard, rather than fitting it
to a desired population or restoring pregnancy without physical exposure.

| Finding / causal requirement | Mechanic | Qualification |
| --- | --- | --- |
| Li, Wilcox & Dunson (2015), clinical pregnancy benchmarks by intercourse day relative to ovulation | Single exposed-day reference probabilities for O−5 through O are .04, .13, .08, .29, .27, .08. Genuine captured mutual contact records an exposed calendar day and detached actual father/traits. Repeated parts with the same father/day add no extra fertility opportunity. | Clinical-pregnancy endpoint, not fertilization, early hCG pregnancy or live birth. Six calendar-day bins are not a strict 120-hour sperm-survival model. |
| Daily diary exposure differs from separate independent quarterly trials; Sundaram et al. (2012) | At most one clinical-outcome allocation after the ovulation day's night exposures have been recorded. Multiple exposed days use the maximum applicable single-day benchmark. | Explicit most-fertile-exposure approximation, related to the alternative discussed by Royston & Ferreira (1999). It is neither a fitted joint model nor a proven conservative bound. Marginal day probabilities are not multiplied as independent trials. |
| Cycles vary; Wilcox et al. (2000), Bull et al. (2019) | Each mature female has a private deterministic phase and independently sampled integer intervals of 24–35 model days. No action or observer query draws her reproductive RNG. | Uniform mean 29.5 days is an illustrative prior, not a fit to app users, within-person variability, hormones, menstruation or anovulation. The end-of-day boundary is operational, not a measured subday ovulation time. |
| Past physical exposure survives later social changes | Fathers are selected uniformly from the actual records on the best-scoring exposed day(s); later death, withdrawal, departure or a new bond cannot rewrite those records. Only a living mother's body can allocate a pregnancy. | This is model paternity bookkeeping, not a sperm-competition model or human knowledge of genetic paternity. Current male pools and current partner identity do not gate a retained exposure. |
| Physiology/environment can suppress a healthy reference | Existing age, BMI, nursing, food, crowding, illness and ennui hypotheses scale the cycle benchmark once. The combined modifier is bounded to 0–1. No store/farm bonus exceeds the healthy reference. | These modifiers remain illustrative and uncalibrated for prehistoric populations. Fertility is not divided by four and is not retried each part. |
| Clinical pregnancy and subsequent loss are distinct | A successful cycle allocates a pregnancy trajectory due O+270, with the existing .14 later recognized-loss hypothesis and O+50–90 loss timing. | No additional hCG-to-clinical loss roll is applied. Rate and timing are unfitted. Allocation at O is advance sampling of a trajectory, not clinical recognition at ovulation. |
| Old saves cannot supply unrecorded reproductive history | `reproduction` defaults to None. Lazy mature-female initialization draws a fresh phase prior, with empty exposures. Existing due dates, hereditary values and known/unknown pregnancy fathers are preserved. | The private stream is seeded by universe seed, iteration, person, cycle index and purpose; JSON persists the schedule/evaluation marker. Migration itself draws no RNG or historical exposure. |

The bounded history holds at most four distinct fathers per day across six
calendar days. The intended unit is **an exposed day**, not the social token,
an inferred number of intercourse acts or repeated geometrical observations.
A continuously completed mate action on a new day can mark that new day;
this is an explicit daily behavioral resolution, not a claim of measured
intercourse frequency. Same-day multipartner records do not raise cycle chance.

LAGOON bond formation remains separate and requires a surviving actual mutual
meeting. Biological exposure does not retroactively disappear if a father dies
after such a meeting. At pregnancy, old exposure/scheduling state clears;
after the pregnancy ends, a fresh phase prior resumes under the existing
nursing/body modifier. Postpartum cycle physiology is not fully modeled.
The 100-year-per-real-day clock, independent choices, island and renderer remain.
Population outcomes must be re-derived across the shipped code and seeds.

## Engine 2026.10.30.6: embodied reproductive contact

This changes future trajectories, including an already-running instrument.
The previous unconditional pregnancy hazard could select a remote, sleeping or
missing father. Earlier population arcs do not predict this version.

| Causal requirement / source | Mechanic | Qualification |
| --- | --- | --- |
| Reproduction requires actual reproductive exposure; Wilcox et al. (1995), RESEARCH | Pregnancy trials require a frozen simultaneous mutual mate encounter, captured before activity reassignment. Both participants must actually arrive at their own reciprocal same-session target, on adjacent connected dry ground. | Same-part attribution omits ovulation, sperm persistence and fertile windows. Completion is an operational event boundary, not a clinical act duration. |
| Each participant acts independently | A local invitation changes only its initiator. A recipient may reconsider a nonurgent task but scores their own food, water, energy, work and company needs. An invitation is not acceptance. | Existing grooming weights remain. Mating additionally reads a personal intimacy need. Single LAGOON adults can now score the same mate option as paired adults, because global automatic pairing is removed. Choices are a bounded utility model, not human consent or general cognition. |
| Bonds and actual parentage differ | LAGOON singles form a reciprocal bond only at actual mutual contact. EDEN encounters create no permanent bond. Successful conception stores actual father ID and detached hereditary values; children keep that father even if the social bond changes. | Known direct parents/shared parents are excluded from mate candidates; this is a rule over recorded relationships, not a population genetics model. Old pregnancies retain their old hereditary values with unknown father ID. |
| One interaction cannot fabricate repeated independent trials | Same-part records are limited to one trial per mother, after casualties. Reassignment after a real contact does not erase it; death, withdrawal or departure before resolution prevents a trial. | The old 1/180 and 1/240 daily coefficients are still divided by four, now conditional on actual contact. This changes effective fertility and is **not** a calibrated per-intercourse probability. No parameter is increased to guarantee survival. |
| Kin recognition / sexual aversion studied by Lieberman et al. (2007), RESEARCH | Recorded direct parents and shared parents exclude a mate candidate. | A categorical design approximation. The engine does not infer kinship from maternal association or co-residence, model genetic load, or claim a universal cultural rule. Perceived kinship remains future work. |
| Labour precedes delivery; WHO (2020), RESEARCH | One model day before an expected surviving delivery, the mother stops at her actual dry position in BIRTH. Nearby people independently score help; no helper is assigned by the mother. Delivery still occurs when due, with existing hazards. | One day is an illustrative visibility budget, not universal clinical labour duration. Actual qualified arrived healing help retains its existing benefit; a missing/refusing helper cannot postpone delivery. |
| The picture must distinguish an invitation from a completed encounter | Existing scene and person information use current reciprocal contact, separately from permanent partner identity. | No extra panel, observer intervention or claim of biologically validated movement is introduced. |

The old mate utility was structurally unable to enter the 85% choice band for
EDEN roleholders: work or food always won. A separate personal `intimacy` need
now grows from zero by 1/7 per model day (divided across four parts) for adults,
capped at one. It adds 1.5 times that need to the old mate score, under the same
hunger/energy/ennui factors and both partners' availability. Actual completed
mutual contact alone resets it. Seven days and weight 1.5 are explicit
motivational hypotheses, not fitted libido, intercourse frequency or birth
rates; neither rejection nor a distant bond can satisfy it. Children start at
zero and do not accumulate adult desire. Work cannot permanently exclude this
option, and desire cannot force another body to accept.

Persistent additions `social`, `pregnancy_father`, `dad` and `groom_day` default
to `None`, and `intimacy` to zero, for new people and legacy saves. No historical intercourse or paternity is invented.
The 100-year-per-real-day clock, island resources and anatomy rig are unchanged.
The versioned encounter audit measures one bounded century: both worlds die
out, exposing the uncalibrated conception time basis. This is an unresolved
model limitation, not ecological validation or an inevitable human outcome.

## Engine 2026.10.30.5: purposeful instruction

This changes future trajectories. The `.4` seed-69 diagnostic ran only LAGOON
for 30 years, with identical traced/plain states and events. Its sole tool-maker
never completed a teaching conversation or tool work; fishing demonstrations
could not bypass learners' missing tool prerequisite. These are observations
of that code/seed, not a universal explanation of cultural loss.

| Research finding / causal requirement | Mechanic | Qualification |
| --- | --- | --- |
| Morgan et al. (2015): instruction can improve real task production; Caldwell & Millen (2009): learning routes depend on the task | A person who actually witnesses a skilled task can remember that person's demonstrated expertise and seek instruction. Seeing fishing does not reveal the teacher's entire skill inventory. | Purposeful seeking and its utility weights are model assumptions, not experimentally calibrated prehistoric behavior. |
| A method can depend on an unfamiliar prerequisite | At actual voluntary contact, a requested lesson can explain the first unaware prerequisite before the requested method. The fishing witness may learn tools first, then fishing on a later eligible day. | The finite prerequisite graph is predefined; this is bounded subgoal pursuit, not general planning or human intelligence. |
| Teachers and learners have their own needs | A visible request may reopen a teacher's nonurgent choice. Teaching competes with food/rest/work, never assigns another person's action, and cannot override birth, injury, thirst or sleep. Accepted TALK meetings retain their targets rather than being relocated into a social circle. | Active seeking starts at 12 in the shared decision helper; existing childhood branches still differ between worlds. Passive observation remains available from 3. No privileged EDEN teachers or inherited personal knowledge. |
| Location knowledge requires perception | Up to 12 detached expertise notes retain demonstrated method/day and last actually seen position/day. Only local awake sight updates positions. Pursuit uses that memory, never the global expert list or a remote current location. | Six-tile direct dry sight and four-tile contact are coarse operational geometry, not optical/acoustic models. Location freshness 30 days, pursuit 8 parts, failed-search retry 7 days are illustrative. Durable procedures do not expire with mentor locations. |
| Instruction takes attention but is not practice | Requested and incidental verbal instruction share at most 4 unique pupils per teacher/model day. Actual-work observation uses no verbal attention slot; every learner still receives at most one new procedure/day. Frozen facts prevent instant relay. | Exposure remains .25 and actual work supplies later practice. Repeated chat cannot fabricate work, resources or mastery. |
| The observer must distinguish intention and outcome | Existing person cards/captions show seeking/explaining. Successful requested exposure records `requested_instruction` provenance and one cultural event; logging cannot change the world. | Active goals and retained learned entries are point-in-time facts, not cumulative intelligence or a guarantee of cultural retention. |
| Old saves cannot contain unrecorded social history | Migration defaults mentor notes, goals, offers and attention budget to independent empty containers. Newborns and reseeded founders start empty. | Existing durable skills/provenance survive unchanged; no historical mentor is invented. |

Readiness uses current hunger below HUNGRY, thirst below 1, energy at least .4,
and injury at most .45; night and urgent roles stop purposeful seeking/offers. Incidental conversation
and actual-work observation keep their existing transfer rules. Seeking/offer
base scores .65/.8 compete in the existing needs loop. All such thresholds
are explicit model choices. A failed pursuit can remain a failure; the observer
does not replace a missing teacher, grant a prerequisite or boost invention odds.

## Engine 2026.10.30.4: personal procedures and local works

| Research finding / modeling choice | Mechanic | Qualification |
| --- | --- | --- |
| Morgan et al. (2015): instruction changes stone-knapping performance; Caldwell & Millen (2009): learning routes vary by task (RESEARCH, procedural transmission) | Historical discoveries no longer grant every person an ability. Inventors hold a procedure; nearby completed conversations and witnessed work expose one new procedure per person/day. Frozen contact facts prevent same-part teaching cascades. | A finite predefined skill ladder, not invented human knowledge or general intelligence. |
| Practical production differs from hearing a description | First exposure gives level .25; actual task use adds .1 at most once/day, capped at 1. Personal prerequisites must be mastered for qualification. Repeated conversation cannot supply practice. | Rates, prerequisites and competence thresholds are illustrative, not fitted experimental estimates. Failed genuine attempts may count as practice; pretending to work does not. |
| Knowledge can outlive stale resource reports | Procedures retain original teacher/origin and learning basis; they have no stock-report 90-day expiry or three-hop ceiling. | No modeled forgetting, misinformation about procedures, or richer pedagogy yet. |
| Physical supplies and works are not the builder's memory | Camp fires expire without tending; actual preservation work tags existing food; local completed granaries reduce rot even after a builder dies. Farm-origin food remains an inventory tag. | Food processing conserves food units. Construction materials, fuel and tools are still abstract, not a wood/ore economy. |
| Learning routes include observable products | Nearby lit fires, completed huts, prepared food, stores and records can expose their corresponding procedure, subject to personal prerequisites. | Seeing a product supplies awareness only; it does not grant mastery. |
| Historical saves never recorded individual learners | Only old-schema working-age survivors missing a skills field retain old capabilities as `legacy_global_capability`, with unknown dates, teachers and origins. They must actually use a procedure before teaching it. New people and new worlds start empty. | This is an explicit migration prior, not recovered history. Existing ecology and world history are preserved. |

Camp projects track person-work rather than unlocking on a world tag: grain
storage 40, livestock enclosure 30, record-keeping 10 person-days at full capacity.
These values are illustrative. Domestication remains a coarse handling/enclosure
abstraction: completion requires a real game animal at capture distance, removes
that animal from the wild population and records a local aggregate. It does not
establish the biological domesticability of deer or simulate selective breeding.
Metallurgy remains a historical procedure on the finite ladder, with no invented
ore, smelting, walls or industrial economy. Civilization beyond this ladder is
unimplemented; elapsed millennia alone cannot supply it.

Fire maintenance gains priority only when unlit or within one part of expiry;
a fully lit four-part fire must not monopolize all other camp crafts. This
choice schedules real work; it supplies no food, fuel or skill by assignment.
Watch duty respects sleep and urgent bodily needs. Sailing needs a completed
boat and a present qualified operator; historical builders learn completion
only while physically present and awake. Landfall creates no food or wildlife.

This engine version changes all subsequent trajectories. Re-derive results from
the exact shipped source hashes; prior century results remain historical.


## Engine 2026.10.30.3: knowledge passes through contact

**This changes future run trajectories.** Completed conversation/grooming can
pass one resource report to a listener per model day. Both worlds use the same
transfer-only phase; it does not add solitude bonuses, food, water, skill or
personal harvest experience. Primary human foraging experiments support social
information use with context-dependent benefits (King 2011; Deffner 2024;
RESEARCH.md). They do not calibrate these numerical choices.

| Causal requirement | Mechanic | Limits |
|---|---|---|
| Communication requires an actual encounter | Capture completed TALK/GROOM positions and knowledge before reassignment; resolve among surviving, non-withdrawn, non-aboard participants. Four-tile direct dry contact, including the movement corner rule | Not an acoustics/language model; under-three actors do not communicate reports |
| Retelling is not a fresh observation | Each note preserves original observer and seen_day; immediate sender, heard_day and a bounded path identify hearsay. Local observation replaces it with personal evidence | Modern experimental support is qualitative; literal map coordinates stand in for communicated location information |
| Rumour must not refresh or amplify itself | Freeze sender notes before delivery; one incoming report/listener/day, at most 3 hops, at most 90 days original age. Reject equal/older facts and return loops. Hearsay discounts expected stock by hop count | Limits and discount weights are illustrative. No deception, inferred trust or general theory of mind |
| Hearing is not harvesting | Received notes keep only the listener's own visits/gained counters. No stock lookup to verify distant reports. Stale reports cannot evict fresher notes at capacity | Actual-use outcomes remain audit data, not learned skills/action values |
| Both worlds perceive their actual resources | EDEN's provisioned hopper observation sites now exist and follow pen expansion; free provision and EDEN reset conditions remain unchanged | World-wide technology was still a separate abstraction in .3; superseded by .4 |

Source snapshots and contact positions prevent an instantaneous whole-chain
broadcast or fabricated meetings after fission relocation. Knowledge remains
bounded and JSON-safe; old .2 notes were locally observed and receive that
provenance on migration. Newborns/reseeded people inherit no personal claims.
The lab samples retained reported notes and path lengths read-only, not a
lifetime communication count. Postmortem/reseed wording now identifies model
policies without promising prevention or inevitable collapse. The default
100 years per real day is unchanged; all quantitative arcs must be re-derived.

## Engine 2026.10.30.2: personal resource experience

**This changes existing run trajectories.** The shared brain now chooses from
locally observed and remembered resources rather than consulting every reachable
patch's current stock. This is bounded stock/location learning, not general
cognition or learned harvesting skill. See RESEARCH.md, “Personal resource experience — primary human
evidence”, for the primary experimental evidence and its limits.

| Evidence / causal constraint | Implemented mechanic | Limits |
|---|---|---|
| Human food-location memory and sampled spatial rewards can guide later search (de Vries 2020; Wu 2018) | Each person records at most 24 nearby resource places, copying observed quantity, location, kind and model day. Physical use records actual source depletion, including food eaten on-site and water drunk before carrying | Six-tile connected-radius sight is illustrative, not occlusion/line-of-sight or a measured human range. Quantity observations are abstractions |
| A past success cannot reveal current distant stock | Planning ranks all known sites by remembered quantity and travel cost. Beyond sight, estimates drift toward uncertainty over a 30-day scale; a remembered empty patch can be checked after 7 days without changing its actual reserve | Capacity, prior 25% fullness, cost weights and decay/revisit times are model choices. Actual gained units are audit evidence, not a learned action-value or skill bonus |
| Resource encounters can guide subsequent local search (Hills 2013) | Hungry/thirsty people lacking known supplies scout nearby connected dry terrain. A 12-position trail contains actual visited positions, never intended destinations, and makes unfamiliar directions preferable | Local waypoint search is not general planning. It does not know unseen site coordinates or guarantee discovery/survival |
| Knowledge must come from perception or experience | Perception continues during travel/work. Party and farm targets use known places; away workers remember camp inventories rather than reading current distant stocks | In .2, technology and social knowledge remained shared abstractions; personal procedures supersede this in .4. Hunt initiation detects within 6 tiles; existing active animal pursuit retains its separate 12-tile approximation |
| Memories belong to the person who experienced them | New people and reseeded founders start with empty notes; migration supplies independent empty defaults without fabricating visits. JSON reload preserves subsequent choices | EDEN receives no inherited personal memory or new cross-iteration assistance; LAGOON's existing fixed lesson tags remain separate |

Two existing physical/behavioral contract bugs are corrected in this version:
`needs` supplies age in years, so its self-control adapter now converts to
`minds` day units; mature fight choices therefore change. Milk-food now needs
the same two-tile maternal proximity as milk-water, and both require connected
land. These are model contact distances, not clinical measures. Both worlds’
future trajectories can change; EDEN retains its provision/control conditions,
not its earlier buggy fights or remote nursing.

The century-per-real-day clock is unchanged. Older numerical arcs below are
historical unless re-derived for 2026.10.30.2. Fresh quantitative results and
source hashes belong in STUDY.md and the accompanying experience audit.

## Engine 2026.10.30.1: a tropical resource budget

**This changes existing run trajectories.** Older figures below are historical
unless explicitly re-derived for this version. New worlds use a Sri Lanka
coastal-ecology analogue: tropical forest, coastal fishing, freshwater catchments
and two monsoons (FAO, RESEARCH.md). It is neither an exact map nor a digital
twin: tiles have no surveyed physical scale. Existing saves retain their old
terrain geometry and seasonal regime (`terrain_version=1`); new worlds use 2.
Eight founding pairs remain unchanged.

| Evidence / causal constraint | Implemented mechanic | Limits |
|---|---|---|
| FAO: coastal lowlands, forest and seasonal monsoon rain support distinct resource habitats | New terrain has a forest mosaic; two rainy intervals replenish plants and freshwater differently from fishing | The locations and multipliers are illustrative, not measured Sri Lankan productivity |
| Food and water exist in physical places | Wild patches are generated from habitat cells once for the entire terrain. Camps share each patch's remaining stock; founding another camp does not create/refill patches. Fish require a dry bank directly adjoining water | One patch abstracts a habitat cell; yields are food units rather than calories or species inventories |
| Fresh water is a separate requirement from saltwater fishing | Inland `water` banks hold finite rain-fed reserves. `A_DRINK=22` visits a bank, drinks and carries up to 12 person-days home. Camp water evaporates 1% daily. Drinking depletes the source, carried supply or camp reserve actually used | Banks abstract catchments/seeps without changing terrain; no pathogen chemistry, containers or groundwater flow model |
| Human bodies need water; WHO confirms milk also supplies it (RESEARCH.md, “Milk supplies water as well as food”) | Thirst advances 0.25 per part, interrupts work to seek water, and can cause dehydration above 4 model days. A nursing mother pays the child's water cost through the same under-three nursing window as milk-food | Threshold and units are explicit hypotheses, not clinical predictions. EDEN retains unlimited provisioned water |
| An ocean gap requires a boat | Gathering, farm work, hunts, cat targets and nearby defenders require connected dry ground; walking does not cut diagonally over water | Perception reach remains tile distance; actual movement follows a dry path |
| A finite island cannot conjure replacement wildlife | Deer/cat births need living animals. Removed automatic low-stock herd/cat respawning. Plant/fish observer stocks mirror actual patches rather than an independent global renewable pool | Animal birth rates and grazing capacity remain simplified; there is no guarantee against prey/predator extinction |
| Old runs must resume without duplicate grants | Migration merges duplicate legacy patches using the minimum remaining stock, rejects dry inland fishing places, adds missing freshwater banks once, and defaults thirst/carry/camp water. Existing terrain is preserved | These repairs change future food availability; old trajectory forecasts no longer apply |
| Food-sensitive conception was already drafted | Retained 1/240 daily base, food-shortfall multiplier, 1.15 stored-food bonus and farming modifier | These coefficients are hypotheses; removed unsupported claims that these rates reproduce a universal forager growth target |

The clock defaults to `86400 / (100 * 360 * 4) = 0.6` seconds per part.
Changing pace preserves cumulative ticks already due with the existing clock
anchor; it does not replay the old world's calendar. This is a target pace,
not a measured throughput claim for the 2016 MacBook.

## The founders (engine 2026.10.29.1)

Both universes receive **eight pairs** with the same sexes, bodies and
heritable temperaments, generated from one shared founder seed. Every reseed
also sends eight pairs. Their display names use separate world-specific pools;
name choices do not consume the founder trait RNG. Existing saved people
retain their names and population. Both worlds begin innocent; the first
successful birth records the discovery of naming.

## Minds and bodies: one Stone-Age brain, two worlds

The organising idea is a mismatch. LAGOON is the world the human brain was
built for: hunger, status, belonging and purpose all find an outlet in
work. EDEN is a resort that answers every need except those. Sources are in
`BOOKS.md` (the owner's books) and `RESEARCH.md`; parameter values are
calibration, checked with `tools/lab.py`.

| Finding | Mechanic | Where |
|---|---|---|
| Behavioural traits ~half heritable (Bloom; Pinker *Blank Slate* ch.19) | `ef` (self-control) and `ag` (aggression) per person: mid-parent + mutation. Men express `ag` +0.08 (a distribution shift, never a rule) | `minds.inherit` |
| The prefrontal cortex matures last (Bloom; Pinker ch.3) | Expressed self-control ramps to full by ~22 | `minds.self_control` |
| Purpose comes from being asked something (Frankl; *Homo Deus* ch.2) | `pu` drifts toward what the world asks: LAGOON asks 0.35 plus work, EDEN asks nothing; dependents, a partner, a place add to it | `minds.tend_purpose` |
| A forager's appetite in abundance | EDEN intake rises as purpose falls → BMI climbs toward obesity; idle muscle wastes. LAGOON BMI is paid for in work and lost to famine | `minds.tend_body` |
| Anomie: nothing regulated, nothing asked (Durkheim, *Suicide*) | A competent EDEN adult with purpose < 0.25 may withdraw for good; self-control is the brake | `tick_eden` |
| Universe 25's withdrawn were three kinds (RESEARCH.md [2][3]) | Placeless losers pool listless in the middle of the floor and are attacked there; the beautiful ones (born into the sink) groom alone in a corner; lone women retreat to the top row of cabanas. All feed at the hopper nobody else uses, and never join a circle, a couple or a fight | `withdraw`, `withdrawn_home` |
| Revenge, the moralization gap (Pinker *Better Angels* ch.8) | A killing gives the victim's kin a grudge (decays ~8%/yr); revenge when restraint fails | `lagoon_violence` |
| Young unpaired men kill (Pinker ch.2, ch.10) | LAGOON homicide hazard for men 16–30, ×2 unpaired, × temper × (1.2 − self-control) | `lagoon_violence` |
| Leviathan: a third party with standing (Pinker ch.2–3) | Band 0.1, tribe 0.35, chiefdom 0.65 arbiter (+0.15 with writing): damps violence, exiles or executes killers | `organise` |
| Band → tribe → chiefdom (Diamond ch.14) | At 50 and (with a granary) 300 people, with hysteresis | `organise` |
| Collective effervescence (Durkheim, *Elementary Forms*) | With lore, each settlement dances at midsummer for its totem; cohesion +0.5, decays 0.25/yr; a hungry year skips it | `hold_rites` |
| Covering as the first cultural act (Peterson on Genesis 3) | After innocence ends, modesty rises (LAGOON to 0.85; EDEN to 0.5 as the pen fills); the renderer covers that share of adults | `modesty` |
| Invention needs planners with company (Pinker ch.3; Diamond ch.13) | Tech discovery × (0.5 + 2 × share of adults with `ef` > 0.6); the discoverer is the most self-controlled of a few | `tick_lagoon` |
| Two clocks | Mean and tail of `ef` recorded yearly in `mind`, apart from tech and arts | `record_mind` |

Historical earlier-engine measurements (version not consistently recorded;
stale for 2026.10.30.1; `tools/lab.py`, seeds 69/7/123/5, 150 years):
LAGOON's violent share of deaths runs 0.6–7.8%, lowest where a chiefdom
formed (Pinker's forager range is 4–30%; famine dominates deaths here).
After 80 years from seed 69 the EDEN adults average BMI ≈ 32 with purpose
≈ 0.2, against LAGOON's ≈ 22 and ≈ 0.8.

## Engine 2026.10.27.2, second pass: routines, biology, boats, fire

Sources: `BOOKS.md` (second reading pass, sweeping every book by keyword
index — still not cover to cover), `RESEARCH.md`. Values are calibration.

| Finding | Mechanic |
|---|---|
| Calhoun: the scarce thing was socially meaningful roles (RESEARCH.md §1); Bestor ch.6: seats are a fixed count, refilled only on a holder's death | EDEN **posts** (bar staff, lifeguards, keepers) — a fixed list, filled once, vacated only by death or withdrawal. A post holder works shifts at their post |
| Every activity has a place | EDEN: sleep in one's **condo** (households) or **capsule hotel** (singles); the placeless sleep on **mats in the open hall**, jjimjilbang style; eat at the bars, talk on the boardwalks, lounge on the south beach. Aimless walking only for the placeless — the symptom |
| Calhoun's restless males; "pansexual" mounting (RESEARCH.md §1) | Placeless men in the sink roam the floor and press sex on whoever is near |
| More rooms held pathology off (Calhoun's later universes, RESEARCH.md [4][5]) | When crowding nears the sink, the **resort expands** 8 tiles on every side, with new lodgings and posts; at most twice (48 → 64 → 80). From seed 69 the sink begins in year 83 (about year 42 without expansion) and the death phase in year 103 |
| Primates bond by grooming; humans by gossip (Harari; Dunbar) | **Grooming** pairs in both worlds: kin and partners at LAGOON's hearths, anyone near in EDEN |
| Reproductive biology (Howell 1979 for forager spacing; Diamond ch.4 for settled spacing) | Fertility by age (0 before 16, falls after 30, 0 at 50), suppressed by low body fat and by nursing (3 years in LAGOON, 2 once farming, 1.5 in EDEN); 14% of conceptions miscarry; 1.4% of births are twins |
| Human birth needs help (the obstetric dilemma) | In LAGOON a mother or another woman kneels with the labouring woman. In EDEN she delivers alone, as Calhoun's mothers did |
| Drives and the prefrontal cortex (Bloom; Pinker *Better Angels* ch.9 on discounting) | LAGOON choices weigh hunger, fatigue, injury, care, company, sex and curiosity; delayed-reward actions (building, farming, the boat) are weighted by expressed self-control, immediate ones (eating the store) against it |
| Fire and the watch | With fire, one adult a day sits watch for each camp (the most vigilant take most turns); a watched camp halves predation, fire cuts it 30% |
| Vigilance is selected (Bloom on innate fears) | Heritable `vg` lowers predation risk; recorded in `mind` beside self-control |
| Stories make lore; lore explains with will (Harari, *Nexus* ch.2; Durkheim) | Talk at the fire accumulates stories; shared lore is discovered sooner the more there are. With lore, each new kind of disaster leaves a **myth** that explains it |
| Crowding puts people in boats (Diamond, Austronesian expansion) | When the island holds more than ~0.85 × 95, the camp builds a **boat** at its west beach (400 person-days, visible); a party of young adults, partners and children **sails across the strait** over days, lands, and leaves the boat on the far beach. The mainland is untouched land: fresh groves and naive game |
| Seasons | LAGOON has four (spring, summer, autumn, winter) with droughts, storms and ice-age winters; EDEN is always spring |

Historical measurements recorded for 2026.10.27.2 (seeds 69, 7, 123, 5, 11, 42, 300, 8; 150
years): LAGOON died out at least once in 3 of 8 runs, against 6 of 8 on
the previous engine; peaks ran 39–406, highest where a boat landed. LAGOON time budget after year 60 (seed 69): foraging 24%, walking
20%, minding children 13%, play 13%, sleep 8%, talk 7%, sex 3.5%,
grooming 3%.

## Engine 2026.10.27.3, the merge: one record a day

This engine is the merge of two lines of work — the routines/biology/boats
pass above and the record-keeping pass from the other branch. Both are kept.
Three model changes, none of them a new mechanism:

| Change | Why | What it does to the numbers |
|---|---|---|
| Famine is **one line a day**, not one line per death | A lean season is one event. Ten deaths in a day are one sentence, not ten | The event log's famine lines change wording and count. Cause-of-death totals do not |
| A fall is a separate cause, `accident`, from old age | The two were collapsed into one bucket, so a world of young people dying of falls reported as "age" | `cod` gains an `accident` bucket. Any figure that summed `cod` across causes changes; re-derive it |
| Farm fields are dug only on **dry land** | Water is not a field | LAGOON's farm tiles move off the shoreline. Farm count is unchanged; farm *positions* are not |

The engine also records its own version in every postmortem, so a published
figure can be traced to the code that produced it.

**Rolls are preserved.** The old per-death famine coin flip is still drawn
and discarded, so every later random draw in the day lands in the same
place it did before. The trajectories differ only where the three changes
above change an outcome.

**Figures that changed.** Any number derived from the 2026.10.27.2 engine
is not reproducible from this one. The 150-year seeds (69, 7, 123, 5, 11,
42, 300, 8) quoted above were re-derived on 2026.10.27.2 and have **not**
been re-derived on 2026.10.27.3 — treat them as stale until
`tools/lab.py` re-runs them.

## Engine 2026.10.28.1: the day has four parts

**The tick is a part of a day, not a day.** Dawn, day, dusk, night; the day's
counter turns when the night ends. Everything that happens in a world happens
inside one of those parts. This changes the trajectory of the live run — the
run is over a century old — so the engine version moves and every figure
derived from 2026.10.27.3 is stale until it is re-derived.

The unfinished 2026.10.27.4 draft advanced daily hazards, food and bodies four
times per calendar day. The audited engine keeps daily mortality, physiology
and purpose to one update; apportions fertility, hazards, harvest, stock
regrowth, hunger and story accumulation across four parts; and preserves
daily storage horizons. These corrections change trajectories again. Prior
engine figures remain historical, not measurements of this version.

The pace follows: a part is 3 real seconds, so a day is 12 and a sim-year
(360 days) is 72 minutes. The old rate was one day per two seconds, so the
year now goes by about six times more slowly in real time. That is the price
of a day and a night being watchable; a cycle that passes in two seconds is
not a cycle. `UNIVERSE69_SEC_PER_PART` sets the pace.

**Movement is now four steps a day, not one.** A part is a quarter of a day,
and people walk when they are awake. The world's tiles are therefore a
quarter-day of travel each. This is a calibration shift, not a design one:
it changes how far a foraging party goes in a day.

| Finding | Mechanic | Where |
|---|---|---|
| Fire makes a group; the night around it is where a band becomes a society (Slingerland *Drunk* ch.3; Harari *Nexus* ch.2) | At night a band converges on the camp fire, and the talk there is where stories are told | `keep_watch` |
| A group that watches one another's backs is safer than one that does not (Slingerland *Drunk* ch.4) | One adult per camp stands watch each night, and the turn goes round the watchable ones — the most vigilant take the most turns | `keep_watch` |
| A watch is paid for (model calibration) | The watcher gains 0.5 hunger for a night on watch, against recovery of 1 hunger per fed day. The unfinished draft added 6 nightly and would starve a fed watch rotation | `keep_watch` |
| The dark is bolder (model calibration, not a measured coefficient) | Predation risk is 1.8× at night; a camp with a watcher on roughly halves it | `tick_lagoon` |
| Tools change the food web (Diamond’s technology/ecology framing; predator hunting is a model choice, not his domestication filter) | New step on the ladder: `predator_hunt`, needing fishing and 25 people. With it, hunters bring down a big cat, the carcass feeds the band (with surplus stored when preservation exists) and the predator population falls | `tick_lagoon`, `TECH_LADDER` |
| A resort that never closes is not the same as a world with no nights (Calhoun: the pen's geometry, not its hours) | EDEN at night: the adults go to their own beds, the placeless sleep on the mats, children stay with their mothers. The food stays free and the posts stay filled — night is not a new pathology | `tick_eden` |


**Resuming the instrument.** Migration retains its calendar and anchors the new
clock at the last completed old-rate day. Any unsimulated wall time after that
anchor is caught up at the new part rate; completed days are never replayed.
Both empty worlds continue through the reseed wait, and reseeding preserves
cumulative ticks. Pace changes preserve pending ticks and survive restarts.
Every resumed universe records the old/new engine and transition day/part;
postmortems carry that history. Pre-reseed dates with no recorded founding date
remain historical absolute dates; new iterations record their founding day.

**Observation only.** Research tests use the current iteration's age, with
verdicts on each 30-day calendar boundary even during server catch-up. They
read the universes and write only the separate research record. Their numeric
thresholds are model checks inspired by the books; agreement cannot validate
a historical or human claim. Fresh predator meat is consumed or transferred
into storage once, with only the uneaten remainder retained to spoil.

## Engine 2026.10.28.2: every rate in the model is in days

**The law.** Every quantity in this model is denominated in days: an
activity's remaining time, a band's daily food need, the chance a woman
conceives in a day, the stories told around a fire in a day. When the tick
became a quarter of a day, every one of those had to be converted, because
a rate that is tried four times a day is four times the rate it claims to
be.

**What went wrong when it was missed.** The first four-part day (2026.10.28.1)
converted the food yields and the hunger, but not the *activity durations*,
the *conception rate* or the *stories*. So LAGOON's adults changed jobs four
times a day, the women conceived four times as often, and the band was full
of children it could not feed: it starved to death in its ninth year. The
arc recorded in `docs/audits/2026-10-28/` does not reproduce on that engine
and should not be quoted.

**The fix.** `engine.days(n)` converts a duration in days into ticks, in one
place, and every duration in the model goes through it. Rates that are tried
per part are divided by `PARTS_PER_DAY` where they are drawn. The engine
version moves to **2026.10.28.2**.

**The reference.** The pre-day engine (2026.10.27.3) was run for 166 years
from genesis on seed 69 as the calibration: LAGOON survived with eleven
technologies and a peak of 221, and EDEN reached its death phase with a peak
of 1,738. The four-part engine now gives the same shape of arc. Any figure
from 2026.10.28.1 is stale, and so is every figure from before it.

**The guard.** `tests/test_engine.py` pins two things that this bug would
have broken: the lagoon is still a lagoon in the fifteenth year, and a
person keeps the same job for the length of a day.

## Engine 2026.10.28.3: needs, places, one mind (the handoff's milestone N)

The activity labels used to be theatre: LAGOON's food came from a headcount
formula, EDEN's collapse from a phase script, and the two worlds had two
different assigners. This engine retires that layer. **It changes the
trajectory of any run started under an earlier engine; the live run should
be reseeded, and no figure from an earlier engine carries over.**

| Finding | Mechanic | Where |
|---|---|---|
| Foragers eat what somebody gathered (Lee & DeVore, *Man the Hunter*) | Food is in **sites** on the map (berry groves, shallows, game, tilled fields). A worker at a site eats there and carries a day's load home; a camp eats only from its own **store**. No food arrives because there are adults. If everybody sleeps, the store stays empty and the band starves (`tests/test_needs.py`, A1) | `needs.fulfil`, `needs.eat`, `needs.deposit` |
| Hunger, energy and company are a person's own | Personal meters `hun`, `ene`, `sol`. Eating lowers the eater's hunger and empties the pantry it came from (A2). An infant is fed by its mother, and the mother pays 0.6 of it in her own hunger | `needs.meters`, `needs.eat` |
| A body deprived of food weakens (illustrative model calibration, not a validated human starvation timescale) | Hunger 0→40 (death) at ~1.4/day for a working adult: about four weeks with nothing at all, longer with scraps | `needs.HUNGER_MAX`, `HUNGER_PER_DAY` |
| Foragers anticipate: they go out because the larder is low, not only when their own belly is | `want_food` is the larger of this belly's hunger and the camp's shortfall against four days' food | `needs.assign`, `larder_short` |
| Food does not keep without the craft to keep it | Raw food rots 4%/day; actually prepared units 0.8%; a built local granary 0.2%. The inherited "preserve" habit retains its separate 0.8% raw-food prior | `needs.keep_stores` |
| A field gives food only if it is worked (Diamond ch.6) | Tilled fields are sites that grow only when tended in the last 30 days, a quarter as fast in winter, a third in drought | `needs.ensure_sites`, `regrow_sites` |
| Night is slept (A3) | At night everyone not on watch, in labour, nursing, withdrawn or on the way to dinner sleeps where they are — at the hearth, or out at the patch. At dawn everybody decides again. Sleep restores energy | `needs.night` |
| One mind, two conditions (A5) | Both worlds' adults decide with `needs.assign`. The worlds differ only in `needs.CONDITIONS` (same keys): EDEN's food is provisioned, its mating free of bonds, its posts the only work; LAGOON must work to eat, works in parties, mates in bonds | `needs.CONDITIONS` |
| Crowding wears company instead of mending it (Calhoun 1962) | Past eight faces within five paces, company stops restoring `sol` and drains it. A fed, purposeless adult whose `sol` falls below 0.25 withdraws | `needs.meters`, `needs.assign` |
| Violence needs a crowd and a grievance (Pinker, *Better Angels* ch.9; Calhoun's placeless males) | EDEN fights are chosen in `needs.assign` from local crowding × temper × placelessness (men ×1, women ×0.15). A violent death is a fight's wounds reaching 1.0. There is no phase-gated death roll | `needs.assign`, `tick_eden` |
| Rearing decides a pup's fate (Calhoun 1962, 1973) | Abandonment and social incompetence at birth are read from the mother's nest crowding, purpose, wounds and own competence (`rearing`), not from a phase label | `rearing` |
| Phases describe; they do not decide | EDEN's phase names stay as a reading of the census, but the death phase can reverse if births come back | `tick_eden` |
| Walking round water | Blocked walkers follow a breadth-first land distance field (a cache, never state), so nobody strands on the far side of the inner lagoon | `land_field`, `step_toward` |
| Eight pairs (owner's decision, 2026-10-28) | Both worlds start with the same eight pairs, as every reseed already did | `FOUNDER_PAIRS` |

**Animals have places (handoff A4, owner's brief 2026-10-28: "we are God
creating the ecosystem that won't kill the population instantly if the
population could naturally learn how to fight back").** `sim/animals.py`.

| Finding | Mechanic | Where |
|---|---|---|
| Big cats kill people mostly when prey fails them, and mostly people alone (Packer et al. 2005, *Nature*; Treves & Naughton-Treves 1999) | Every deer and cat has a position. A cat looks for deer after eight days without a meal; only after 16 days without a kill does it look at people, and then only at someone with fewer than three adults within three paces, outside a lit or watched camp. Children and the night make prey easier; vigilance (`vg`) harder | `animals.tick`, `_choose_person` |
| People fight back | An attacked adult with stone tools kills the cat 25% of the time (5% unarmed), +20% per adult defender, +10% with the "vigilance" lesson; otherwise the victim is taken (adult 55%, child 85%, halved if armed) or mauled | `_attack` |
| The hunt follows the herd (Hadza: big kills are rare per hunter — Hawkes et al. 1991) | Hunters with stone tools track the nearest deer; deer bolt from people within four paces; a strike succeeds 5% + 5% per partner (max 30%) per part; the carcass is carried home as a shared load. Hunts last a day or two, and a hungry hunter gives up to eat | `animals.tick`, `needs.assign` |
| Predator hunting | With `predator_hunt`, three armed hunters within four paces of a cat may kill it (25% per part); the cat is meat | `animals.tick` |
| Herds and cats live on the land | Deer have aggregate annual growth 0.6 at low density toward 0.08 per tile of grass or wood; cat reproduction is limited toward one per 120 deer and starve after 45 days unfed. An empty island is recolonised: a small herd, or a single cat, arrives a few times a year (model calibration — the Observers' one act of design) | `animals._daily` |

| Shelter is built, pair by pair | With `shelter` known, each bonded pair raises its own hut at the camp: ten person-days of work (`needs.HUT_WORK`), scaled by body capacity. A finished hut is where the pair sleeps, and a cat does not take someone asleep under their own roof. Huts and their progress go to the viewer (`huts`) | `needs.hut_of`, `animals._sheltered` |
| The drama is recorded where it happened | Each deer killed, cat hunted, cat fought off, person mauled or taken is kept for three days as an encounter with its place (`encounters`), for the documentary camera | `animals._seen` |

All numbers in this table are model calibration, not measured coefficients.
The viewer draws exactly the animals in the summary (`animals`), where
they are; it invents none.

**Changed figures.** Conception in `try_conceive` was divided by the
parts of the day twice; it is now divided once, so conception per part is
four times what engine 2026.10.28.2 used. Together with eight founding
pairs, every trajectory differs from earlier engines; STUDY.md's
2026.10.28.3 baseline is the first figure from this model.

The day-counter fatigue is gone from LAGOON's assigner and the old
phase-gated scripts are gone from EDEN. **Not yet done:** LAGOON's homicide
model (`lagoon_violence`) is still a per-person hazard, unchanged.

## Engine 2026.10.29.1 — audit of needs, wildlife, naming and restart boundaries

**This changes the live run's trajectory.** Earlier engine numbers, including
2026.10.28.4, are historical. No old population is silently reset by migration;
only an explicit authorized `--genesis` starts new worlds. Eight pairs **per
world** remain the current owner decision; the unfinished reduction to four
pairs per world was removed.

| Finding or contract | Audited mechanic | Where |
|---|---|---|
| The shared founders are the experimental control | World-specific indexed names consume no trait draws; newborn names use the child's sex. Legacy names survive; older established worlds migrate as already named | `minds.founders`, `make_name`, `migrate` |
| Food must be earned and conserved | Existing pooled stores migrate once into camps by their resident headcounts. Food remains in sites, loads or stores until eaten, spoiled or lost with its carrier; death never teleports a remote load home. The world's total is synchronized after work, meals and spoilage | `migrate`, `tick_lagoon`, `needs` |
| A field has to be worked; fish have their own season | A new farm starts unworked, including during the first month. Fish and plant regrowth use their respective seasonal factors. A hunter cannot harvest an unrelated berry site merely by reaching it | `needs.regrow_sites`, `fulfil` |
| Need-driven withdrawal must be a reachable choice | In EDEN a fed adult with purpose <0.25 and solitude <0.25 can prioritize withdrawal above seeking company. The draft's maximum withdrawal score was always beaten by company. Purpose is now a required condition, matching the intended mechanic | `needs.assign` |
| The carried picture has to match its source | A load records plants, fish, field harvest, deer, cat or mixed; only a recorded animal carcass uses the carcass rendering flag. Large berry baskets and legacy unknown loads remain generic loads | `needs.carry_food`, `animals`, `summarize` |
| Death releases a claim and a bond, whatever its cause | One shared removal path handles ordinary, plague, epidemic and feud deaths; it frees occupied rooms/posts and unpairs survivors. Migration repairs old ghost occupancy, dead role holders and one-way pairs from actual living claims, preserving valid zero keys | `remove_dead`, `migrate` |
| Dead people cannot supply new opportunities | Mating pools refresh after plague; annual discovery/culture uses surviving population and adults after epidemic. Revenge cannot kill a staged casualty twice. Withdrawal and exile detach both sides of a bond | `tick_eden`, `tick_lagoon`, `lagoon_violence`, `withdraw` |
| Population stock must match its flows | An infant born and lost in the same part counts one birth and one death; a miscarriage counts neither. Census births minus deaths no longer subtracts these infants twice from population change | birth branches, `record_census` |
| Each casualty and carcass is counted once | A person already taken by one cat cannot feed another, eat or die again in a later fight that part. Passengers aboard a boat are not terrestrial hunters. Deer reproduction uses its aggregate annual rate once | `animals.tick`, `_daily`, `tick_lagoon` |
| Per-day rates convert once | Hunger has four quarter-day updates; a completed day's body/purpose update remains daily; story accumulation divides by the four parts once rather than twice | `needs.meters`, `keep_watch` |
| A runtime data override isolates the whole run | History books use the configured data directory, current-iteration event bounds, and in-memory postmortems when disk copies are absent. Living worlds create no book directory | `historian.compile_book`, `server` |
| An explicit restart must not mix iterations from different runs | State, events, postmortems and history books move together into a unique archive directory; runtime web configuration remains in place. Iteration 1 artifacts from an old run cannot suppress a new postmortem | `historian.archive_run`, `server --genesis` |

The numeric needs/ecology parameters are illustrative calibration, not measured
human or animal coefficients. Tests pin these causal contracts with controlled
fixtures; they do not require a particular century's population, extinction or
psychological outcome. One separately recorded bounded arc reports what this
engine actually did. Birth-helper staging in the viewer is visual inference
unless the snapshot actually records an `A_TEND` actor; there is no explicit
persistent helper-to-mother link in the model.

## Universe 6 — EDEN (after Calhoun's Universe 25)

A 48×48 sealed pen. Food hoppers and water are always full. Climate is perfect.
No predators and no provisioning work. Eight founding pairs; mating-borne
sickness remains a modeled risk.

The only scarce resource is **social space** (Calhoun's actual variable):

| Research finding (Universe 25)            | Mechanic                                                    |
|-------------------------------------------|-------------------------------------------------------------|
| Phase A "strive" → B "exploit"             | Normal pairing + conception while crowding < 35% of nominal capacity (900) |
| Phase C "stagnation", behavioral sink      | Above 35% of the pen's capacity: conception scales down. (Universe 25's stagnation began near 620 of 3,840, about 16%; 35% is this pen's design, not Calhoun's number.) Violence comes from crowded fights, not the phase |
| Maternal neglect                           | Abandonment read from the mother's nest crowding and state (`rearing`) |
| "Beautiful ones"                           | Children reared in a crowded nest can be *socially incompetent*; on adulthood they withdraw and never pair |
| Phase D "death"                            | Named when yearly deaths > births for 3 years; incompetence is fixed at birth, so recovery is hard — but the label reverses if births return, because whether it can is the test |
| Extinction (the mice: 122 left on 22 June 1972, about day 1,444; probably extinct in 1973) | Pen empties; event logged |
| LD&R "Ice Age" cyclicality                 | 30 sim-years after extinction the Observers reseed the pen; `iteration += 1` |

## Universe 9 — LAGOON (Blue Lagoon / first Sapiens world)

A 160×160 world: coastal forest, grassland, a saltwater lagoon and beaches.
Food patches deplete when harvested and replenish seasonally; animals live,
breed, hunt and die at actual locations. Inland freshwater is separate.
Eight founding pairs with world-specific names. Nothing is given; everything is earned.

| Research finding                           | Mechanic                                                    |
|--------------------------------------------|-------------------------------------------------------------|
| Foraging economics                          | People gather from actual patches; fishing/farming require personal procedures and yield scales with practice, season and remaining stock; hunger can kill |
| Predation, accidents, childbirth mortality  | Daily hazard rates; children more vulnerable; personal tool competence affects defense, present qualified care affects healing/childbirth |
| Seasons + disasters                         | 360-day year with monsoons, storms and droughts; legacy saved terrain keeps its old winter regime |
| Blue Lagoon innocence                       | The founders don't know how life begins; a discovery event in the first years unlocks reproduction |
| Sapiens: cognitive revolution / Dunbar 150  | Local enacted rites/cohesion raise the social limit; an overfull settlement splits or feuds, rather than benefiting from a distant lore discovery |
| Sapiens: agriculture = "luxury trap"        | Personally worked fields raise food supply; sufficient local farm-origin food affects nursing and fertility; labor remains necessary |
| GG&S: domestication → germs                 | Existing local handled livestock exposes present people to an illustrative epidemic (15–35% of the exposed group)    |
| GG&S: surplus → specialists → tech          | Tech ladder: fire → stone tools → fishing → shelter → preservation → shared lore → agriculture → domestication → granary → healing lore → metallurgy → writing. Historical finite ladder; personal qualified prerequisites gate inventors, discovery odds scale with population and need |
| Expansion                                   | Overfull settlements fission; new bands found new settlements — the map fills as the camera zooms out |

## Sex, boredom, and disease (EDEN)

Mating in EDEN is free and pedestrian — no pair-bonds, no cost — until it
isn't: (1) **ennui** — hedonic adaptation slowly dulls fertility in a world
where pleasure costs nothing; (2) **STD outbreaks** — free mating at density
carries one price; outbreaks cut fertility, kill some adults, and leave the
next generation *wary* (a ~20-year cultural-memory fertility dampener that
fades when that generation ages out — "the pen forgets"). All logged.
LAGOON keeps pair-bonds (widows re-pair); there, only famine suppresses
fertility.

## Growth and its limits

The uncommitted fertility draft reduced the base conception chance from 1/200
to 1/240 per woman-day, scaled it with hunger, and reduced the stored-food bonus.
This release preserves those explicit hypotheses while adding physical shared
food and water budgets. Neither fishing nor storage alone is agriculture; a
forager growth target cannot be inferred from one seed or assigned to a decade
because a technology appeared. The old draft's before/after growth figures were
not reproduced for 2026.10.30.1 and are removed. See STUDY.md for the bounded
shipped-code result, including failure or extinction if that is what occurs.

## Names (engine 2026.10.30.1)

A name is a cultural invention, so the two worlds do not share a stock.

| World | The first names | Where the rest come from |
|---|---|---|
| EDEN | Adam and Eve, then Cain, Adah, Abel, Zillah, Seth, Miriam | The line after them: Enosh, Noah, Lame, Enoch; Ruth, Sarah, Rachel, Leah |
| LAGOON | Rahul and Sita, then Siddhartha, Parvati, Ganesh, Ganga, Shiva, Tara | Arjuna, Krishna, Indra, Rama; Radha, Lakshmi, Maya, Kali |

The founders of the two worlds are **the same people** — the same bodies,
the same tempers, in the same order. Only the names differ, because a name
is a thing a world invents and EDEN did not invent the ones LAGOON uses.

**A world has no names at the beginning.** `u["named"]` is false until the
first child is born, and then it is true, with an event: *the first child
is named, and after this everyone has a name.* A language is a thing you
invent later; before that, the names in the record are the observer's
bookkeeping, and the people themselves have not got round to it.

Everyone born after the founders is named from the same stock, so a name in
the record always says which world the person belongs to.

## Death, postmortems, and lessons (the Edge-of-Tomorrow loop)

Every death is tallied by cause. When a universe dies, a **postmortem** is
recorded (data/postmortems/): peak, generations, technologies, cause-of-death
table, dominant cause, and a model preventability flag. That flag is a policy
assumption, not evidence of preventability.

- **LAGOON learns.** Reseeded founders inherit lessons mapped from past
  dominant causes — starvation → *preserve* (storage habit and faster
  preservation/fishing; no food gift), predators → *vigilance* (−40% predation, faster
  tools), epidemic → *cleanliness* (half outbreak odds), feud → *unity*
  (faster shared lore). Survivors of a near-wipe (one cause killing >20% in a
  year) imprint the same lesson without going extinct — instinct passed on
  with no written language, the way fear of snakes is.
- **EDEN cannot learn.** Each reseed restarts under identical controlled
  conditions. The absence of inherited assistance is experimental policy,
  not proof that any particular collapse was inevitable. That asymmetry is
  the experiment.

Each fall also produces an independent observer volume and durable index in
`data/history-books/`, even while the other universe lives. The RUNS reader
separates cumulative recorded facts from candidate lessons and unknowns.
Historical founding dates and engine versions remain unknown when absent;
current-run values are never substituted for earlier iterations. Explicit
`--genesis` archives these records with the old world. This observer layer
does not alter the engine or the worlds.

## Bands and tribes

Everyone starts together — bonding is survival. Past the cooperation ceiling
(~80 without shared lore, more with it), settlements fission into *named
tribes*: peacefully after lore exists, as a deadly feud before it.

## Rendering (web/index.html)

- **Full resolution, one palette, one screen** (owner, 2026-10-28; the
  8-bit lock is retired). The worlds are painted at device resolution —
  smooth coasts and wood edges over the model's grid, forms lit from the top
  left — cached per view and zoom step so a 2016 MacBook keeps up. One
  palette, TERRARIUM, on `:root`; the canvas reads it. The page never
  scrolls: the record, the research, help and the BOOK are read in pages.
  Reading order: the worlds, the instrument strip, the record, the chrome.
- Two canvas panels, always on the first screen together: side by side on a
  wide screen, stacked under ~700 px with each heading collapsed to one line
  (tap a heading to open it).
- **The BOOK** (`book/book.json`, schema in GRAPHICS.md) opens over the
  console as a reading page: table of contents, chapters, figures with
  caption, credit and licence, set in a serif at a 66-character measure,
  paginated. The RESEARCH dialog opens on "From Universe 25 to here"
  (`book/origin.json`) before the hypotheses.
- **The camera** is a documentary eye on a three-rung ladder — island, camp,
  hearth (~6, 18, 48 CSS px of adult height). The establishing shot is the
  camp rung on the densest cluster of people; EDEN's eye stays inside the
  pen. Close shots (a birth, a fight, a hunting party, or where most people
  are) use the hearth rung; a shot far from the last one is a cut, not a
  glide. The viewer may take the camera, follow a person, jump between rungs
  with 1/2/3, or **walk in** (arrows/WASD, `I`, or WALK): a person-height
  camera that introduces everyone nearby by name, activity and body.
- **People** (owner's brief, 2026-10-27) are life-drawing sketches with a
  skeleton under them. The pose solver says where hands and feet go; an
  anatomy rig (pelvis, spine, chest, neck, head, clavicles,
  shoulders/elbows/wrists, hips/knees/ankles) with proportions by age and sex
  solves each limb as two bones of fixed length. Proportion follows the
  anthropometric canon: 4 heads at birth, ~5 at two or three, ~6 at six, ~7
  at twelve, 7.5–8 adult; men's shoulders outgrow their hips, women's hips
  are about their shoulders' width, women stand ~7% shorter. The skin is
  painted around the bones: capsule limbs with muscle bellies, a torso from
  shoulders to waist to hips, hands, feet, a skull with a jaw, a hair
  silhouette. Standing is a straight-legged stance with a little
  contrapposto; the trunk is a ribcage and a pelvis joined at a visible
  waist, lit from the top left in two tones of the person's skin; at camp
  size a figure is a silhouette (head, shoulders, arms apart, two legs),
  under ~10 px an upright mark. Garments follow the modesty share: resort
  wear in EDEN, a hide wrap in LAGOON, fur in a hard winter. The body is the record — width from BMI, muscle or a stoop
  from strength, bone-thin limbs and ribs in famine, a stoop and hollow
  cheeks when hungry, a belly for obesity or pregnancy, a bandage and limp
  for injury. Adults are drawn as bodies are; children never get genital
  detail. Far away a figure is a body's mass, never a stick.
- **Light** is painted after the people: at night a figure is as dark as its
  ground, and the fire lights the ones in its circle.
- **Food places**, when the summary carries `sites` ({x, y, k, f}): berries on
  a bush, fish in the shallows, game tracks, standing rows in a field, a
  hopper's level — each as full as `f` says.
- **The instrument strip** under the worlds: eight gauges — population (log,
  against founding doublings, Universe 25 laid under it), births−deaths per
  100 adults, yearlings / prior births (legacy capped proxy), breeders and the withdrawn share, claimants
  per place, the sink, food in store, violent deaths per 100k — each with
  EDEN above LAGOON on one scale and a reference tick where the literature
  gives one (Calhoun 1962/1973; Gurven & Kaplan 2007; Pinker 2011). Colour
  marks only a reading outside its band. A click opens the sources, which
  say these are model readings, not findings. Each world's heading is one
  line; the rest of its facts open on a click.
- **The worlds at work.** LAGOON's huts are the record's (`u.huts`), drawn in
  construction stages; encounters with deer and big cats (`u.encounters`)
  are drawn where they happened and are what the camera looks for first; a
  load or a carcass, hunger, an infant in the arms, a birth with a helper,
  the watch with a spear and the couple on a mat are all drawn from the rig.
  EDEN reads as a Truman-Show resort island: painted sea, beach, lawn, pool,
  loungers, the dome's edge, bars with stools.
- **Labels** only for the person you chose and, at most two at a time, a birth
  or a fight.
- EDEN is dressed as the Truman Show's resort: beach floor, buffet bars for
  hoppers, striped cabanas for nest boxes, a horizon painted on the dome
  wall, and the real sea just outside it.
- Bottom record: the shared event log (discoveries, disasters, phases, deaths
  of note, extinctions, reseedings); a line that repeats is shown once, ×N.

## Processes

- `sim/server.py` — engine + HTTP on **localhost:6969** (serves UI, `/state`,
  `/world`, `/events`). Saves `data/state.json` every minute and on shutdown.
- LaunchAgent `com.universe69.sim` keeps it alive 24/7 (KeepAlive + RunAtLoad).
  When the lid is closed the Mac sleeps; on wake the engine fast-forwards.
- Uploader thread pushes a snapshot to the web mirror every ~2 minutes.
- Web mirror: static viewer on Vercel at **universe.nonarkara.org** reading the
  pushed snapshot.
- Chronicle: `tools/chronicle.py` writes a mechanical daily digest to
  `data/chronicle/`; a scheduled Claude job writes the narrative chronicle.

## Honest limitations

- Humans modeled with human demography (20-year generations, single births),
  so EDEN's arc takes sim-centuries — days of real time, not hours.
- Both universes are stochastic; a founding pair can die out early. That is a
  valid result (it happened to real founder populations); reseeding is logged,
  never hidden.
- This is a model of *dynamics from the literature*, not a claim about people.
- Determinism holds per `(seed, day, part)` **within one engine version**. Editing
  `sim/engine.py` changes every number derived from the previous version, and
  the live run's history becomes irreproducible from that point on. Re-derive
  figures from the shipped code; never quote one from an old log.
- The renderer reads a flat, positional payload from `engine.summarize()` with
  no type protection. `tests/test_contract.py` pins that contract from both
  sides so a rename fails the suite instead of the browser.

## Verifying the model

`tools/lab.py` runs a bounded arc locally and prints a verdict. Runtime
depends on population and hardware; a century can take minutes:

- did EDEN's pen actually empty (and therefore write a postmortem and reseed),
- did LAGOON survive, and which technologies and lessons it reached.

The verdict, not the eye, is the acceptance test for a change to the engine.
Run it before and after any model change, and treat a change in the verdict as
a change in the experiment.


### Observer limitation: the legacy `infant_survival` column

For compatibility, `gauges()` and the positional census retain the field name
`infant_survival`. Its actual formula is
`min(1, current people aged >=360 and <720 days / births in the latest annual census)`,
rounded to three decimals, or `None` if that census has no births. The numerator
is a rolling age window and the denominator is an annual period; they are not
the same birth cohort. The cap can also hide ratios above one. It is labelled
**YEARLINGS / PRIOR BIRTHS** in the viewer and must not be described as a true
infant-survival rate or compared with an empirical survival threshold. No cohort
tracking or trajectory change was introduced for this observer-label correction.
