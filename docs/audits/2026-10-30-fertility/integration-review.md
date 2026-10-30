# Reproductive timing integration review

**Engine 2026.10.30.7: no unresolved causal blocker in the reviewed integration.** This is an implementation review, not a validation of human fertility or population outcomes. The reviewer authored `reproduction.py`; its pure tests are self-verification. Engine/minds integration and the integration tests were authored separately and reviewed here independently. Another reviewer owns the independent module/data verification.

## Reviewed behavior

- Both universes keep actual reciprocal same-instant contact capture before action reassignment. `reproductive_contacts` remains a separate social-bond operation; its current-father survival filter does not gate biological exposure ingestion.
- Each universe records the raw captured mate facts once per part after ordinary casualties; EDEN additionally removes plague casualties first. A dead mother cannot ingest or advance. A father who dies, withdraws, boards or changes bonds **after actual capture** remains represented by his detached exposure/trait record. No global male pool or current partner is needed at ovulation.
- Each living female is processed independently of reproductive discovery. The private phase/cycle clock exists while the world is still innocent, but innocence cannot invent an exposure. Only age-eligible living female identities advance cycles; existing gestations clear schedule/exposures without changing due date, saved hereditary values or actual pregnancy father.
- Exposure units are calendar days, not parts or persistent social tokens. Repeated same-father/day facts collapse; distinct actual fathers are bounded at four/day and six calendar bins. The same token on a later actual-contact day can record that distinct day. This deliberately coarse day policy is not a strict 120-hour sperm window or a count of validated intercourse events.
- Day O evaluation happens only after that night's contact frames were ingested, before `advance_part`. Each ovulation identity is persisted; repeating part calls or reloading cannot reopen the trial. No daily hazard or quarter-day multiplier remains. The maximum benchmark across actual exposed days is multiplied by a caller modifier capped 0..1; food/technology cannot exceed the healthy clinical reference.
- Phase initialization, cycle length, clinical pregnancy allocation and father selection use private deterministic streams. They consume no global ecology/behavior RNG. The engine applies its existing conditional recognized-loss/gestation fate once to a successful payload, using its ordinary world RNG; clinical allocation and later loss are explicitly different stages.
- Successful allocation copies actual father ID/traits to the pregnancy. Delivery preserves actual dad despite subsequent social-bond changes or death. Legacy due/fe/paternity fields are retained; migration adds `reproduction=None` without a random phase or invented exposures. Newborns/reseeds start without reproductive history.
- An integration retention edge was found and fixed by the engine author: EDEN previously skipped bulk record/prune on an empty-contact part, allowing inactive older women's expired records to persist. EDEN now calls the bulk operation once per part, symmetrically with LAGOON. The new whole-engine regression checks both worlds, empty contact, bounded history expiry and unchanged inactive cycle index.
- The renderer summary does not initialize or advance cycles. An actual 64-part engine probe followed by repeated summaries preserved the exact world JSON and global RNG; public facts matched after excluding only the wall-clock capture timestamp.

## Verification

Apple `/usr/bin/python3` (3.9):

```text
PYTHONPATH=tests /usr/bin/python3 -m unittest test_reproduction test_reproductive_contact test_death_cleanup test_encounters test_labor test_social_choices test_cycle_integration
Ran 89 tests in 0.497s — OK
```

The 20 pure module cases also pass on Python 3.14. The independently rerun integration set includes real encounter capture, father death after exposure, EDEN plague, no ambient exposure, dead-mother references, dayO/night ingestion, repeated parts, reload after failed evaluation, father inheritance, social/physical gates, labour, record pruning and pre-discovery cycles. Controlled coins/terrain are used where a deterministic gate test requires them. These cases are not a natural forecast; statistical benchmark checks, full-suite and bounded natural arc evidence are separate.

## Remaining assumptions and limits

The clinical single-exposed-day table, its endpoint and its source provenance are recorded in RESEARCH and this audit's research/controlled evidence. Using **MAX** over exposed days is an explicit most-fertile-exposure approximation, not a proven probability bound or fitted joint model. Uniform 24..35-day cycles and uniform initial phase are illustrative priors; population-level cycle variation is not claimed as within-person calibration. Father selection is uniform among actual records on the best benchmark day(s), not validated sperm competition.

Existing nutrition/age/nursing/environment multipliers, gestation/twins and recognized-loss assumptions remain simplified. Fresh phase after gestation plus the existing nursing multiplier is not a clinical postpartum-amenorrhea model. Calendar dates do not reveal ovulation hormone dynamics, subday timing or sperm viability. Captured reciprocal utility choices are not a validated account of human agency or consent. Voyage physiology still has its pre-existing suspension abstraction. None of these changes guarantee survival, civilization or an intended population curve.

This behavior change invalidates older trajectory figures as evidence for this release. Natural results must come from the separately frozen source arc; no coefficient was selected to force those results.

## Exact reviewed source SHA-256

| File | SHA-256 |
|---|---|
| `sim/animals.py` | `5622b0910d185da4e9c8b6f680ce87a1feada111fb5505b483bd3de563864577` |
| `sim/encounters.py` | `913e361567a682618c20f8a887eefc695eb77af6ad428591843080141eea4394` |
| `sim/engine.py` | `53415944ef4d5af155462f7af4217053319868a2f6e1abc4cfa952af16b8ee53` |
| `sim/historian.py` | `ad0728651b5f6b326fc02cc05ab2c112dfe34506e1ba1af81dacfa3541f30c69` |
| `sim/labor.py` | `3f05c805ba8d2e0e113e079709909a5f34f40a066dc3df6b3b587983cb36c1be` |
| `sim/learning.py` | `b83ddb2818f8e4675eaebc7f0f38526d08aa4ad06e595ef075f1464bad99a5ff` |
| `sim/minds.py` | `95965b717e4e72fa45a79b48c8b5a00904b416406ce0b6e905bcab882c481d0a` |
| `sim/needs.py` | `1d9f69de0b20b71710d529e91d52b2c6e339bc63f48c716f7b9f007e781db6a5` |
| `sim/reproduction.py` | `20c9c189cba51db418eaa000b3b6cd3b7b68c2f865436bbbb485fe182725e3cf` |
| `sim/research.py` | `a0afcd7055afa28777f4c8721a7d5b1fbd70c9c5bbae198f5eae03d4bdca54e4` |
| `sim/server.py` | `5e1bfe65ed3a37e8695c190bc8764fe98d6986108c877fead8c4bbf87cf44f4d` |
| `sim/skills.py` | `5588dad50dd1a925d30a08bb35907cc7cc6c6dc23ab31ca58597aa6eddd74555` |
