# Current engine boundary — 2026-11-04

Engine `2026.11.04.1` fixes EDEN's mate/groom search, which used the same
6-tile local radius as LAGOON's tight camps against a 48-tile pen whose nest
boxes are spread around all four walls by design. Audit trail:

**The symptom, in the instrument's own record.** Three consecutive live
EDEN postmortems on this run — iterations 2, 3 and 4, engine `2026.11.01.1`
— each read: peak 18-20 (barely above the 16 founders), generation stuck
at exactly 2, and cause of death `{'age': N}` for every single death, zero
infant or violence deaths. That is not Calhoun's sink; it is almost nobody
beyond the founders ever conceiving.

**The cause, found with `tools/lab.py`-style isolated runs, not a guess.**
`encounters.candidates(u, adam, people, 'mate')` returned `[]` for a founder
at the pen's centre against fifteen other adults, all individually
`available()`, because every one of them was more than 6 tiles away —
expected, once founders scatter to nest boxes around a 48-tile perimeter.
A 60-year isolated EDEN run under the old radius: peak 21, 13 conceptions,
generation stuck at 2 the entire run. The same run re-examined at year 60
showed the real reason generation never advanced past 2 *in that window*:
none of the 28 generation-2 children had yet turned 16 — but the historical
live postmortems ran 86-88 years, long past that, and still never produced
a generation 3. Small populations plus the search-radius bug compounded:
too few generation-2 children, from too few successful pairings, for enough
of them to find a non-sibling partner once they did come of age.

**The fix and its effect.** `encounters.social_sight(u)` returns the pen's
own size for EDEN (not the camp-tuned constant) and the unchanged local
radius for LAGOON. Same 90-year isolated run, same seed, after the fix:
peak 56 and generation 3 by year 90, growing continuously, zero
extinctions — where the old radius had already died by year ~87 in every
one of three independent reseeds. `tests/test_encounters.py::TestSocialSight`
pins both the widened EDEN radius and LAGOON's byte-identical-to-before one.

Engine `2026.11.03.2`'s own change (default to one 360-day model year per
real hour, 2.5 seconds per part) is unaffected by this fix — only EDEN's
candidate search changed; LAGOON and the clock mapping did not. The figures
below are version-specific historical trials, not runtime capacity
measurements or observations of a restarted instrument. Current graphics/clock
verification: [hourly audit](docs/audits/2026-11-03-hourly/README.md).

# STUDY — measurements from the running universes

**2026-11-12 the sink verdict — two 130-year arcs on the shipped engine
(`2026.11.12.5`-imported; EDEN-only, and `.12.6` is LAGOON-only, so the
figures stand for the shipped code). Seed 69, witness rng lineages 999 and
31337, chained checkpoints every 5 years.** The behavioral sink arrives as
Calhoun described it — and it no longer collapses the pen. The fuse ignites
on schedule (lineage 999: 0 feuds to Y30, 221 by Y50; the crowd era), the
withdrawn class follows it (16 at Y60 → 43 at Y75 → 82 at Y85, peaking at
95 of 280 — about a third of the pen — lineage 31337 the same at 99 of 248),
breeding slows late (births fall from 10–14 a year to 2–6), and the era's
deaths are age, infancy and violence (157 and 125 violent deaths across 130
years; starvation 4 and 2 — the pen is fed). What does not arrive is the
die-off: the pen peaks (280, 274) and **plateaus high** — 239 and 223 at
Y130, still two-thirds the peak, births and deaths near balance. Against
the `.12.2` re-derivation (pop 220, withdrawn 77 at Y120), the wider
individuality moved the ceiling up and the floor nowhere in sight: the
sink's *shape* is intact, its *depth* is gone. Two independent lineages
agree; the historical `.09.3` arc (164 at Y120) was one lineage's luck,
recorded as such.

**2026-11-12 the wild ring opens (live instrument, engine `2026.11.12.4`,
LAGOON Y507).** The plain lagoon finally fissioned on its own — Meera and
Parvati, two camps on the same land — and the gift ring opened *in the wild*:
`exchange_partners: 1`, thirty gift events in the record, the last reading
*"Sita brings the goods to Brahma — the exchange between the camps is kept."*
This retires the caveat recorded twice below (the ring had only been seen in
controlled two-camp witnesses). The sink-era contraction made it watchable in
a second way: the slate reads pop 37 under **183 huts** — homes persisting
across the die-off, which is exactly the domestic continuity the hearth pass
(`2026.11.12.4`) holds in place; the same record carries its first wild
keeping, *"Ganga keeps Krishna's hearth."*

**2026-11-12 the domestic test opens (live instrument, research layer on
shipped engine `2026.11.12.6`, LAGOON Y517).** The continuity the wild-ring
entry reached by eye is now a standing claim the panel tests at every
cadence — `H-LAGOON-ROOFS`: *in an old lagoon, more than half the finished
huts belong to no living pair.* The metric `lagoon_orphan_roofs` holds a
roof for the living while any of its owning pair survives (a widow keeps
her roof), and reads **0.974**: **150 of 154** finished roofs belong to the
dead, **11 finished roofs per living pair**. That is hut inheritance made
arithmetic — roofs are raised once, inherited after that, and never
demolished, so the camp's skyline belongs to its ancestors. A falling share
would be the engine quietly clearing the dead's houses, which the mechanic
does not do; the hypothesis is pinned structurally in
`tests/test_research.py`, and the story's thread gained its chapter, "The
hearth, and the first address." Read-only: moves no trajectory in either
world. Captured panel evidence archived at `docs/audits/2026-11-13-research/`,
where the claim shows as **SUPPORTED** with 43 test iterations on the live
instrument.

**2026-11-12 VR verified under headless WebGL (SwiftShader).** The headset
page — module graph, humans rig, instanced crowd with the gift bundles, held
items, the beside-you readout — loads and renders with **zero page errors and
zero console errors**. The table view renders both worlds at dusk
(`vr-table.png`); entering the lagoon puts the player inside a hut at night
among near bodies, and the readout names the person beside them:
*"beside you · Brahma, 35.6 · drinking · warm · close to #435"* — name, age,
activity, mood, and the named bond, read from the same detail rows the 2D
card draws (`vr-inside.png`). Physical-headset verification remains
outstanding (no hardware); everything short of it is now evidenced.
One honest negative beside it: the gift bundle on a carrier was verified
in the rig's code path and in the 2D viewer (contract field 14; the Y518
crossings), but no headless capture has caught a **walking carrier** up
close — the kula sends a party once a year and the window is the few days
the walk takes; repeated polling during the 2026-11-13 session found no
carrier in flight. The claim to verify remains: a bundle riding at the
hand of a near body, seen from inside.

**2026-11-14 the window was caught, the close evidence was not.** At the
Y561 boundary four carriers set out at once — ids 498/504 from Meera,
513/514 from Parvati, both camps qualifying — and the headless viewer
caught three departure frames with zero page errors. Two shortfalls, both
diagnosed: the beside-you readout never named a carrier (it named
Nakula, a sleeper) because the spawn stands 4.5–6.5 tiles from the camp
center while the readout radius is 4 tiles — the carriers passed outside
it at every sampled moment; and no departure frame shows an identifiable
bundle on a walking body (a white puff in one frame is ambiguous —
unverifiable, so not evidence). The return window never fired during the
75-minute watch. Next attempt stands the player at the camp center
itself, where the carriers begin and end their walk.

**2026-11-13 the live pen's fifth life ends.** The instrument's own EDEN
line — the one that has been ticking through every engine since the
founders arrived — emptied at day 191942 (Y533): `extinct_day 191942`,
iteration 5, peak 201, generation 6 reached. The last census rows read two
alive at Y531–533; the save now reads pop 0. The Observers' law holds: 30
quiet years before a reseed, so the pen sits empty until day 202742
(Y563), when iteration 6 begins from the same seed lineage with the
postmortems and lessons carried over ("as they were: the same castaways,
at the ages they have"). The lagoon carries on beside the empty pen: pop
33, two camps, the standing exchange partnership. Note the contrast with
the witness verdict above: the two 130-year controlled lineages plateaued
high, while the live lineage — older engine history, different rolls — ran
the arc all the way down. The two kinds of evidence are not the same
thing, and the determinism study says so: the controlled lineages are
figures the shipped code re-derives; the live arc is the record of one
long run that crossed many engine boundaries, a lineage's anecdote and
nothing more. Now there are three lineages on the shelf, and they do not
agree — which is the finding.
**2026-11-14 iteration 6 begins.** The Observers' law held to the day:
the pen reseeded at day 202743 (Y563), one day past the thirty-year
quiet. Verified against the shipped code, 11/11: iteration 6, seed 503
(= 498 + 5), fseed 69 unchanged, the same sixteen founders at the ages
they have (18–42), founded_day the reseed day, four postmortems and
seventeen engine-history rows carried, phases back at strive,
extinct_day cleared, and the record line — "The Observers reseed the
pen. Iteration 6 begins under the same controlled conditions." One
asymmetry now on the shelf: EDEN's reseed drops the lessons list
(iteration 6 opens with lessons []), while LAGOON's reseed path carries
them — the lagoon still holds "preserve" and "cleanliness" from its own
dead. The pen forgets how to behave; the lagoon remembers. LAGOON itself
is untouched by the reseed: Y563, two camps, the standing exchange
partnership, H-LAGOON-ROOFS reading 0.982 (543x tested, 543x supported),
the Y562 kula completed with all four arrivals recorded — though the VR
close-up of a bundle on a walking carrier remains the open negative.
The VR page is now public as a frozen snapshot at vr.nonarkara.org (the
West World); the live instrument stays local, and no trajectory moved.
**2026-11-15 the West World is built; the domain awaits its DNS.** The
public viewing room is live at the repo `vr.nonarkara.org` (GitHub Pages,
built): the VR page and the 2D terrarium, byte-identical copies of the
shipped `web/` sources, both reading a frozen `snapshot.json` through the
same `config.js` `SNAPSHOT_URL` hook the live mirror uses. Verified in a
real headless browser against the pushed tree: the lagoon renders, the
beside-you readout names the nearest person, zero page errors. The
snapshot refreshed once (Y582: EDEN pop 33, LAGOON pop 18). The custom
domain is registered at GitHub and `nonarkara.github.io/vr.nonarkara.org`
already redirects to it — but `vr.nonarkara.org` itself still answers with
the old VR hub, because its DNS still points elsewhere (Cloudflare). The
flip is one record at the DNS provider: CNAME `vr.nonarkara.org` to
`nonarkara.github.io` (or A records 185.199.108.153-111.153), then GitHub
provisions the certificate. Until then the West World is visitable at the
github.io URL only. The Y562 exchange completed in the record (four
arrivals: Bhishma→Apsara, Chandraprabha→Rahul, Sita→Devadatta,
Duryodhana→Nirvana); the Y564 exchange completed too (Kaikeyi→Menaka/
Nirvana/Sariputra, Ganesh→Bhagavati, Bhagavati→Rahul). The VR close-up of
a bundle on a walking carrier remains the open negative; next window at
the Y565 boundary, day 203400.
**2026-11-15 the checkerboard dies; the snapshot's black lagoon dies with
it.** Two graphics defects, both found the same afternoon, both fixed in
the viewer only (no trajectory moved, no engine version taken). First:
the ground cache's grain painted each speckle as half a tile of solid ink
(`fillRect` at width 0.5 in a space where one unit is one tile), so every
sand and lawn field showed a regular checkerboard of grey squares — the
terrarium's oldest visual complaint, finally diagnosed as a units bug,
not a design. Speckles are now one to two cache pixels, drawn only where
a tile has enough pixels to read as texture (below that the screen-space
grain carries the surface). Second: the public snapshot page drew the
lagoon as a black field, because a snapshot carried no `/world` payload
and the mirror viewer reads `st.world.terrain` in snapshot mode; the
deployed snapshot now carries the world (245 KB total). Tree and palm
shadows stop drawing below ~3 device px a tile, where they merged into a
smear. Before/after pinned at `docs/audits/2026-11-15-graphics/`; style
and contract batteries green (95 OK) with the mirror in the same commit.
**2026-11-15 the deployed tree proves clean; the domain still serves the
old hub.** The exact files the Pages repo carries were checked headless:
`2d.html` renders the frozen snapshot with the checkerboard-free ground
and a fully painted lagoon (pinned as
`docs/audits/2026-11-15-graphics/westworld-2d-deployed.png`), zero page
errors. The flip itself has not landed: `vr.nonarkara.org` still answers
with the old hub ("VR · nonarkara", linking arena/games/league/life)
behind Cloudflare proxy addresses (104.21.x/172.67.x, `cf-cache-status:
HIT`), and our paths — `/snapshot.json`, `/vr.html`, `/2d.html` — return
404, so the origin is the old site regardless of cache. That pattern fits
a Cloudflare Pages project still holding the custom domain, in which case
a DNS record change alone would not detach it. Honest note while waiting:
the `events` tail carries no death events at all (zero across both worlds
over d209945–211399) — the census is the authority, and it shows LAGOON
Y587 pop 17→16 with deaths=1, births 0. The hearth watch: at d211331
"[heir] Bhagavati keeps Kaikeyi's hearth" — the hearth line again, the
roof still unseen.
**2026-11-15 the lattice dies — and the checkerboard's true root is
found.** The user looked again that evening and the ground still showed a
regular dot grid, and the ablation proved it: with `groundGrain` and the
screen grain both no-op'd in the live page, the lattice survived, so the
hunt went one level deeper — the ground cache itself was dumped as an
image, and it carried a perfect one-dot-per-tile lattice. The real root
cause was not the speckle size at all (that fix was real but partial):
`hash2` returns a number in **[0,1)**, and `groundGrain` had been
consuming it with integer shifts — `h>>>8`, `h%2` — which on a fraction
collapse to zero. Every speckle sat at exactly the tile corner and every
parity picked the dark ink: the original checkerboard was literally
"one half-tile dark square at every tile corner", and after the size fix
the same bug became "one dark dot at every tile corner". The offsets now
come from the hash float directly (two hash calls per speckle, small
exact inputs), and the cache dump after the fix shows an organic scatter
with no grid anywhere — pinned as `cache-lattice.png` (before) and
`cache-fixed.png` (after) beside the other evidence. Viewer only; no
trajectory moved; style and contract batteries green (95 OK) with the
mirror in the same commit.
**2026-11-15 the Y588 kula window: the readout chain closes, the bundle
stays unseen.** The boundary exchange fired at day 211680 exactly on
schedule; watch v2 burst 14 frames across gens 211680–211713. Two honest
notes on how the evidence landed. First, a mechanics correction to the
standing assumption: the gift events at d211680 show *sets out* and
*brings the goods* sharing one model day — at 10 s a model-day the walk
is compressed to minutes, not the several-real-minutes-each-way the
earlier watches assumed, so the capture window is the boundary tick
itself. Second, the live pairing failed on the script side (the beside
line was parsed as innerHTML and kept its age suffix), so the person
rows were resolved after the fact: /state at gen 211680 showed the four
outbound carriers by id — #554 Bhagavati, #557 Devadatta, #561 Ganesh,
#564 Kaikeyi, all gift field 1 — matching the gift events name for name,
and the readout named **Kaikeyi** beside the player at gen 211680→211682
and again at 211700→211701, **Ganesh** at 211695→211698. So the
player-relative signal and the engine's carrier list agree in the same
generations. What is still missing is the pixel: the frames show the camp
at dusk with held items (a staff and grey box) but no bundle identifiable
at the waist at that distance and light. Watch v3 is armed for Y589
(day 212040) with plain-text beside parsing, name→id resolution at
capture time, and a burst triggered only when the beside line names a
carrier — the frame, the readout and the carrier row will then be bound
by construction, not by reconstruction.
**2026-11-15 the Y589 window was missed; Y590 closed the binding by
ladder, not by luck.** The boundary exchanges fired on schedule at
d212040 (Y589: Ganesh sets out for Meera; Kaikeyi and Ganesh bring the
goods) and d212400 (Y590: same ring, Ganesh home to Nirvana, Kaikeyi
home to Mahakashyapa) — one model day, as at Y588. Honest accounting of
the instrumentation: watch v3 (plain-text beside parsing, live
name→id resolution) crashed 8 minutes before the Y589 boundary on a
missing generator-expression clause; the frame-level window was lost, and
the events are all we have for that year (Ganesh out, goods delivered —
the mechanism works; nobody was photographed). The v3 fix worked, but the
Y590 watch carried a second script bug one level deeper (a beside-name
read shadowed the browser handle and crashed the close at the end — after
the log was written), and the beside-carrier burst fired zero times
because the beside read preceded the screenshot by one poll. The year's
window was nonetheless captured through the watch's context path: at
d212400, with carriers within 8 tiles of a camp, the frame shows the camp
at dawn beside the fire and the readout in *that same frame* reads
"beside you · **Ganesh, 38.6** · foraging · feuding · at odds with #537,
gone" while the `/state` carrier list names **#561 Ganesh, gift=2
(homeward)** alongside #564 Kaikeyi — frame, readout, and carrier row
bound in one capture, pinned as `vr-gift4-ctx-000.png` (zoom:
`vr-gift4-ctx-000-zoom.png`). The bundle pixels remain unidentifiable at
that distance and light — three windows, three negatives — but the
proximity claim no longer rests on post-hoc reconstruction.
**2026-11-15 Y591: the live binding fires.** Watch v4 (browser/beside
names de-shadowed; clean close, zero page errors) armed for day 212745
and woke on the boundary: at **d212760** — exactly 360·591, the Y591
boundary, one tick before the events landed — the poll saw beside
"Ganesh" resolving to person row #561 (x=140, y=93, gift=2 homeward,
already at the camp edge), and the beside-carrier burst fired:
14 frames across d212760→212789. The events show the exchange in that
tick: Ganesh sets out for Meera; Ganesh brings the goods to Nirvana;
Kaikeyi brings the goods to Mahakashyapa. The arrival read four minutes
earlier already named Ganesh beside the player; the burst's frames 00
and 12 (pinned `vr-gift4-b1-00.png`, `vr-gift4-b1-12.png`) hold the
readout "beside you · Ganesh, 39.6" at d212762 (gift=2, hands at his
sides, at the fire) and d212787 (gift=0, delivered). So the trigger
works end-to-end — but **four windows, four negatives on the bundle
box**: the gift rides the waist only during the one-model-day walk,
and every capture to date has landed before or after it. Watch v5
therefore triggers on the outbound leg itself (any person with gift
field 1, present at the boundary tick) with a 0.2 s burst, beside or
not — armed for the Y592 boundary (day 213120).
**2026-11-15 Y592: the outbound trigger fired, and the window is
smaller than the camera.** At d213120 exactly the poll caught #561
Ganesh gift=1 at (139,103) and #564 Kaikeyi gift=1 at (145,91) — both
outbound — and the 50-frame 0.2 s burst began. Frame 0, shot within
half a second, already reads day 213121 with `out: []`: the gift==1
outbound state lasted less than one engine tick, shorter than any
poll, so the waist bundle was never in view — the walk is sub-tick.
The zoomed frames (`vr-gift5-o1-00-zoom.png`, `-01-zoom.png`) show the
carriers home by the fire, hands empty; the only warm masses near a
hand belong to a non-carrier at the fire and are not identifiable as
the bundle. Fifth negative, and the sharpest: the mechanism is proven
by the trigger log and the same-tick exchange events, not by pixels.
No viewer-side watch can catch a state that ends inside one tick; that
would need an engine- or page-side hook, outside the viewer-only
discipline, and it was not built.
**2026-11-16 the arc is reproducible.** Two independent processes —
`full_arc.py` run 1 (Y130 cap, 268 min) and run 2 (400-year cap, completed,
852 min) — both began from `engine.genesis(seed=69, attempt=1)`,
the first universe exactly as founded (EDEN seed 489, LAGOON 492, fseed
69). Run 2's checkpoint already covers years 1–130, and every one of the
260 common rows — both worlds × 130 years × 11 fields (day, pop, peak,
gen_max, phase, phases, births_y, deaths_y, bad_years, cod, census_len,
iterations) — matches run 1 with **zero mismatches**. Spot-checked: Y1
EDEN 16/16/1, Y50 EDEN 169/172/4, Y100 EDEN 229/243/6, Y130 EDEN 173/243/7,
Y130 LAGOON 31/57/7, all identical. The engine is deterministic across
processes, not merely within one; the witness arc is a real measurement,
not a single lucky draw. (Run 2's first 1.4 min were lost to a stale
`OUTDIR` reference in the checkpoint writer — fixed, verified, no data
lost; run 1's record is the untouched baseline.)

**2026-11-16 the deployed snapshot refreshed to Y607.** The West World's
frozen `snapshot.json` had been serving Y590 since the deploy; today it is
rebuilt from the live instrument's `/state` merged with `/world` (same
schema the mirror uses, 212 KB compact) and pushed to
`Nonarkara/vr.nonarkara.org` as `20de4bf`. The rebuilt snapshot reads d218798
— Y607 at the build: EDEN pop 83, LAGOON pop 17, engine `2026.11.12.6` —
checked headless on a scratch static server before push: `2d.html` and
`vr.html` both render with zero page errors (screenshots
`/tmp/u69w/deploy-2d-fresh.png`, `/tmp/u69w/deploy-vr-fresh.png`). What is
**not** verified: the deployed domain itself, because DNS has not flipped —
`vr.nonarkara.org` still resolves to the old Cloudflare hub (104.21.65.217 /
172.67.192.186), `nonarkara.github.io/vr.nonarkara.org/` 301s to it, and both
`snapshot.json` and the tree 404 behind it. The fresh snapshot is committed
and waiting; end-to-end verification remains blocked on the user-side DNS
record change, exactly as on 2026-11-15. The trees were re-audited
byte-for-byte after the push: every shipped `web/` file is identical to its
`docs/` counterpart (the mirror rule) and to its Pages copy, with
`web/index.html` shipped as `2d.html`; the only deploy-only files are the
landing page and ops files (`.nojekyll`, `CNAME`, `README.md`,
`build_landing.py`, `config.js`, `index.html`, `pages.json`,
`snapshot.json`), and the only `docs/`-only files are the gist-snapshot hook
`config.js`, `MANGA_PLAN.md`, and the `audits/` and `design-laws/` records.
The Pages README's refresh instructions were wrong in a way that would have
undone the 2026-11-15 fix — they wrote bare `/state` to `snapshot.json`,
which loses the `/world` payload and renders the lagoon black; the deployed
README now documents the `/state`+`/world` merge with a headless check of
both pages before push, plus a grey-cloud note for the DNS flip
(`044ce14`). The first 12-hour watcher window (attempts 481–625) elapsed
without a flip — 145 polls, every one `404` from the old hub, and the 404s
carry no `cf-cache-status`/`age`, so they are the origin speaking, not an
edge cache; the next window (626–770) is armed. Health check on the same day, engine untouched: the full
suite ran green — `test_style` 2 s, `test_contract` 14 s, `test_vr` 1 s,
`test_engine` 77 tests / 757 s, and the whole `unittest discover -s tests`
at 697 tests / 1085 s, `OK`.

**2026-11-17 the live record at Y617, and the snapshot refreshed to meet
it.** Read at d222301 (engine `2026.11.12.6`): EDEN, iteration 6 on the
stored counter, climbs to 123 — its stored peak — gen 4, `exploit` since
d564 of the iteration, nobody homeless, `box_free` 101 of 224 slots,
`box_vacant` 6; LAGOON, iteration 3, holds 17 across two camps (Meera,
197 huts, store 854.1; Parvati, 27 huts, store 1311.5), 8 technologies
through agriculture, dry season, food 94.4 days after the Y617 storm
"destroys most of the stores" (d222120), lessons [preserve, cleanliness].
The `phase` field now reads `agriculture` while `phases` still logs only
[0, strive]. The event tail (last 500, all since d218798) still carries no
death events; it does carry the kula alive in the live lineage: nine gift
events on exactly the two annual exchange days (d221760 = Y616, d222120 =
Y617, both day % 360 == 0), every one completed — "the exchange between
the camps is kept" — Bhagavati→Parvati and Ganesh→Meera via
Brahma→Duryodhana→Ganesh at Y616, Ganesh→Meera via Tara and
Duryodhana→Tara at Y617; and Mahakashyapa keeps Bhagavati's hearth
(d222004, Y616). Stored cod reads LAGOON {dehydration 306, violence 112,
infant 85, age 78, accident 38, starvation 30, childbirth 17, feud 2},
EDEN {age 13, infant 21, starvation 2, violence 1} — the field's
accumulation window is still unpinned (§5), so cite as stored, not as a
rate. The deployed snapshot was refreshed to this day (d222301, 218 KB
compact, `2c359ca`) and headless-verified before push: `2d.html` and
`vr.html` render the Y617 record, zero page errors. The domain still waits on the
DNS flip; the watcher's window 626–770 elapsed all-404 (the old hub, not
the cache), and window 771–915 is armed (`/tmp/u69w/watcher-771-915.log`).




**Chronicle — The Iterations.** The visitor-facing iteration history is now wired into the viewer as *The Iterations* book, registered under `READER_DOCS` in `web/index.html`. The book records every engine boundary, every observed behaviour, and every agreed-on or disagreed-upon figure, from the first two-seed life to year 617. Its chapters cover: how the worlds were made and why there are two; the first uncontrolled run (EDEN peaked at 749 Y79, sank to 47 at Y175, behavioural sink arrived in year 45; LAGOON's island wrote its culture in years of plenty and starved in year 173); the three silent-pen iterations (2–4) where EDEN's mate-search radius of 6 tiles against 48-tile pen geometry produced peak 18‑20, generation stuck at 2, and the entire world was almost never conceiving — the fix (`social_sight()`) gave EDEN its own size and left LAGOON identical; iteration 5 emptied at day 191942 (Y533) and reseeded iteration 6 at day 202743 (Y563) seed 503=498+5; iteration 6 climbs to 123 at Y617 with exploit since d564, 101 free/6 vacant; LAGOON's third life at Y617 holds 17 in two camps (Meera 197 huts, Parvati 27), agriculture, dry season, 94.4 food-days after the storm that destroyed most stores (d222120), lessons [preserve, cleanliness]. The kula's walk runs through the live lineage: at Y588–Y592 five carriers set out, four honest negatives were recorded across five watch windows, and at Y616–Y617 nine gift events completed across the two exchange days — each exchange kept between camps, Bhagavati→Parvati and Ganesh→Meera via the named chain of carriers, and Mahakashyapa kept Bhagavati's hearth. The witness arc (260 rows, 130 years, zero mismatches) confirms that the same seed produces the same history; EDEN never goes extinct in 400 years (stored peak 243 at year-row 242, generation 16, final population 187 riding its own cycle with lessons preserve and retain; LAGOON's own peak 79 at year 172). The honest ledger records what is open: census is the authority, event log is a sampler, cause-of-death tables are cumulative and unpinned (cite as stored), and the West World exists as a frozen snapshot (`snapshot.json` read via `window.SNAPSHOT_URL="snapshot.json"`). This book is registered as `archive/history.json` and read from the `?` veil sheet button labelled THE ITERATIONS.

**2026-11-17 EDEN's lodgings get volume, and the dome's sky gets a night.**
Viewer-only repaint in the cached painter and the per-frame night pass — no
engine change, no trajectory moved, nothing quoted from the drawing. The
resort's condos and capsule hotels are drawn as volumes under the same
top-left light the rest of the world uses: a CABANA roof plane with a
sunlit top sliver and a fascia shadow, a shaded front face with a lit west
edge and a deeper east jamb, and a contact shadow at the base; the night
windows in `edenNight` moved to that face's own coordinates, so day and
night paint the same building. §6 item 3 in GRAPHICS.md — the absent
exterior night-sky artwork — is closed for the dome: the horizon band the
daylight painter paints with clouds becomes a deterministic star field and
a small moon at dusk and night. Evidence captured from the live interface
through a read-only proxy to the instrument (390/1024/1440, night and day
parts, island-rung and clips; each file's clock label read back and
matching), in `docs/audits/2026-11-17-realism/` — including the honest
negatives: the display light cycles four times per model year so a DAY
clock can sit under a dark display phase (the lit windows are the night
painter doing designed work), the 1440 frames were taken at dsf 1 because
a dsf-2 shot straddles the 2.5-second part clock, and §6 items 1 and 6
remain open. Batteries green: `test_style` 75, `test_contract` 20,
`test_vr` 36.

**2026-11-17 the world's own geometry hides whoever stands behind it.**
Viewer-only repaint — no engine change, no trajectory moved. LAGOON's huts
and EDEN's lodgings left the baked ground layer and are painted per-frame
in the people's own back-to-front order (a painter's-algorithm merge in
`render()`, y-keyed beside the people), closing §6 item 6: a person behind
a roofline is lost to it; a person in front still stands over it. Trees,
the buffet bars and the camp assets remain baked and are not occluders yet
(§6 item 6a, scoped out on purpose), and item 1 — crowd interpenetration
at extreme density — is untouched. The live record moves faster than a
camera can aim (a followed actor crossed two tiles between setting the
camera and the shutter), so the witness frames come from the deployed
frozen snapshot: actors 592/597 (on the hut tile) and 599 (key 90.0, before
the hut's key 90.05) are absent from the behind-ordering frame, while
595/579/589 (keys 90.81–91.1) paint over the same hut's base — both halves
read off the frame and off the page's sort keys, recorded in
`docs/audits/2026-11-17-occlusion/`. The EDEN facade's clip in the same
frame is sub-pixel (its still people stand at x=21 against an edge at
21.06); said plainly rather than staged. Batteries green: `test_style` 75,
`test_contract` 20, `test_vr` 36.

**2026-11-11 re-derivation — the long fuse under the shipped engine
(`2026.11.12.2`, same witness rng lineage as the first 120-year arc).**
Feuds 1,947, peaces 1,924, live bonds 4 at Y120; final population 220 (peak
221) against the `.09.3` arc's 164, withdrawn 77 against 57, violence deaths
147 against 104. The fuse's shape is unchanged — onset at the crowd era
(~Y32), the one-for-one count, the thin residue of grudges still burning —
but the wider individuality band and the temperament strengths moved the
century's demography: the sink no longer draws the pen down as far. Quoted
from the shipped code, as the honesty rules require; the earlier `.09.3`
figures above remain version-specific history.

**2026-11-11 controlled run — the gift (engine `2026.11.11.1`).** The 80-year
plain witness never founded a second camp (a camp fissions only past its
social limit — 80 people without lore — which this lagoon never reached), so
a controlled run founded a second camp exactly as the engine's own fission
does (same-land dry ground, 40% of the people move) and then left the worlds
alone: **69 gifts in 60 years** between the two camps, a standing partnership
by Y10 and held to the end, ~1 gift per year whenever both camps can pay
(the rate follows the stores). The record names the pairs: *Parvati carries
goods to Indra · Siddhartha to Ganga · Shiva to Maya · Arjuna to Krishna*.
The plain seed-69 arc (1 camp all 80 years) is recorded beside it as the
honest negative.

**2026-11-11 re-derivation — the gift, walked (engine `2026.11.12.3`, same
controlled setup).** 81 parties set out across the lagoon in 60 years (162
named landings — a pair carries each gift), a standing partnership by Y10 and
held; the pace is roughly one party a year early and slows as the two camps'
population falls to 10 by Y60. Against `.11.1`'s 69 ledger-gifts, the walked
exchange moves about a third more often, because the pair that carries it is
also the pair the record names. The plain seed-69 arc (1 camp all 80 years)
remains the honest negative beside it.

**2026-11-12 re-derivation — the gift under the hearth (engine
`2026.11.12.4`, same controlled setup, fresh lineage).** 87 parties set out
in 60 years (174 named landings), the standing partnership again from Y10 and
held, and the hearth pass itself visible in the arc's record: **6 keepings**
(*"X keeps Y's hearth"*) as deaths left children behind. Against `.12.3`'s
81/162 the cadence is ~7% higher — different household placements feeding
the same yearly rule — but the shape is unchanged: one party a year early,
slowing as the camps thin (pop 14 at Y60), one partnership pair throughout.
Measured on the shipped engine, as the honesty rules require. Re-derived
again on `2026.11.12.6` (the roof passes with the hearth), fresh lineage:
**identical** — 87 parties, 174 landings, partnership from Y10, 6 keepings.
The roof pass never touched this arc's gift cadence; recorded as the honest
negative it is.

**2026-11-10 replication — the long fuse, three seeds (engine `2026.11.09.3`,
witness rng lineages, EDEN-only, 60 years each).** Seed 7: 476 feuds, 475
peaces (Y60 pop 209, violence 11). Seed 25: 423/421 (pop 196, violence 25).
Seed 123: 469/466 (pop 220, violence 24). The one-for-one shape and the
crowd-era onset (~Y30–40) replicate off seed 69's 120-year arc; the residual
of 1–4 is feuds ended by death or still burning. `.10.1`'s inheritance
change is LAGOON-side only, so these EDEN arcs describe the shipped engine's
EDEN behavior unchanged.

**2026-11-10 witness run — the long fuse (engine `2026.11.09.3`).** A bounded
EDEN-only witness arc, seed 69, 120 model years (172,800 parts) on the
workbench, the world's own continuity but a witness RNG lineage — not the live
instrument's history and not quotable as such. The record: feuds named 1,572,
peaces named 1,551, live feud-bonds at Y120 = 3; violence deaths 104, withdrawn
57, population 16 → peak 221 (Y90) → 164 (Y120); cod {age 120, infant 271,
violence 104}. Grudges begin at Y28 (crowd era), resolve within about a year,
and the two counters track each other from then on: 19/19 by Y30, 1,422/1,402
by Y100. The residual difference is feuds ended by death or still burning. An
earlier witness under `2026.11.09.1` named 711 feuds and **0** peaces, which is
how the misplaced quarrel-close was found; the 30-year seed-69 arc now reads
7/7. Reproduction: the harness is chained-by-checkpoint (world parts + RNG
state every five years) so an interrupted run resumes rather than repeats.

**2026-11-03 boundary.** Engine `2026.11.03.1` adds bounded individual fuzzy
need sensitivity and repairs fresh-choice readiness, partner-dependent desire
and care preemption. It changes future trajectories. All prior numbers remain
version-specific history. The public death audit preserves the observed clock/
lineage discontinuity rather than combining reused iteration IDs. New tests and
bounded results belong in `docs/audits/2026-11-03/`; that release used 100 model
years per real day (superseded by the clock boundary above). No instrument restart is claimed.

## Current frozen centuries — 2026.11.03.1

Declared seeds 7/25/69, each 36,000 days, complete exit0: EDEN populations 250/198/239
(peaks255/229/240), maximum maternal generations6/6/7; LAGOON 26/64/21
(peaks102/64/35), generation 6 in all three. No extinction/reseed, and no agriculture or
writing in this horizon. LAGOON7's decline from 102 to 26 matters; headcount is not
viability. Standard arcs omit full final worlds/LAGOON age-sex cohorts, so those
are unverified. Exact sources, results, limitations and reproduction commands:
`docs/audits/2026-11-03/arcs/`. No isolated fuzzy-effect or human forecast claim.

## Historical version boundaries

**Earlier version boundary (upstream report, not re-derived in this audit).**
The following `.11.01.1` comparison has no retained raw arcs and is historical
source commentary, not evidence for `.11.03.1`. Engine `2026.11.01.1` changes LAGOON's
"quarrel" violence: the trigger now scales with the camp's real hunger
shortfall (up to 3x when starving, a flat rate before), and victim selection
among same-camp candidates weights a partnered man 3x over an unpartnered
one when the aggressor has no partner (DESIGN.md, "the quarrel has a
cause"). EDEN is untouched — it never calls `lagoon_violence` — and a
seed-69, 60,000-day (166-year) arc confirms EDEN's trajectory is bit-for-bit
identical before and after. LAGOON's RNG stream diverges from the first
quarrel roll onward, as it must (house rule #4); it does not diverge into a
different regime: violence's death share was 0.215 before this change and
0.185 after, both inside the ≤30% calibration target `BOOKS.md` draws from
Pinker ch.2. Nothing else observed — technology count, hunger, self-control,
pairing rate, EDEN's extinction day and peak — moved outside the range
already seen run to run on this seed. Full before/after arcs are not
preserved as files (no `--json` run was kept); re-derive with
`tools/lab.py --days 60000 --seed 69` against this commit and its parent
if the comparison needs to be repeated.

**Earlier version boundary.** Engine `2026.10.30.7` replaces per-part contact
hazards with genuine exposed days, individual variable cycles and one
clinical-outcome allocation per cycle. Actual exposure history, not current
partner survival, supplies the model father. Existing pregnancies are preserved.
The published single-day benchmark, maximum-day aggregation and phase prior
are explicit assumptions; no population fit is claimed. All `.6` arcs below
remain historical. Current source-bound evidence belongs in
`docs/audits/2026-10-30-fertility/`. The 100-year-per-real-day clock is unchanged.

**Earlier version boundary.** Engine `2026.10.30.6` requires actual mutual
reproductive contact, independent local social choices and persistent actual
paternity. It exposes labour before delivery. This changes both worlds' future
trajectories; the earlier unconditional fertility figures are historical.
The old coefficients now apply only at contact and are not calibrated per-act
rates. Final measurements belong in `docs/audits/2026-10-30-encounters/`.
The 100-year-per-real-day clock is unchanged.

**Earlier version boundary.** Engine `2026.10.30.5` adds purposeful, physically
grounded requests for instruction, prerequisite assessment at contact and finite
verbal attention. It changes future trajectories; all earlier arcs remain
historical. Final `.5` measurements belong in the instruction audit and must
match its exact source hashes. The 100-year-per-real-day clock is unchanged.

**Earlier version boundary.** Engine `2026.10.30.4` replaces universal
capabilities with person-held procedures and actual practice, and ties camp
benefits to local works. It changes future trajectories. Old-schema working-age
survivors keep labelled legacy capabilities; their training history is unknown.
See `docs/audits/2026-10-30-skills/` for final evidence. Prior results below
remain versioned historical observations.

**Earlier version boundary.** Engine `2026.10.30.3` adds actual-contact
resource reports, preserving original age/provenance without granting supplies
or personal harvest experience. All older arcs are historical until re-derived.

**Earlier boundary.** Engine `2026.10.30.2` changes resource choices
through local perception, personal stock/location memory and exploration.
It also corrects fight-scoring age units and requires physical maternal
proximity/connected land for nursing; both worlds can change trajectory.
Results for `2026.10.30.1` below remain historical, not forecasts for this
new trajectory. The 100-year-per-real-day target clock is unchanged.

**Earlier boundary.** Engine `2026.10.30.1` changes food/water availability,
wildlife replenishment, conception and the default clock. All earlier results
below are historical; none is evidence for the new trajectory. The model is a
Sri Lanka coastal-ecology analogue, not an exact island map, physical-scale
survey, demographic prediction or guaranteed civilizational ladder.

## Reproductive cycles — 2026.10.30.7

Frozen, predeclared seeds 7/25/69 each ran 36,000 model days. LAGOON 7 and 25
reached maternal generation 6 and ended with 30/29 people, including younger
cohorts and children. LAGOON 69 ended with five men aged 52.56–76.56, not a
viable breeding population. EDEN 7 emptied on day 35,619; EDEN 25/69 retained
one elderly woman each. All EDEN cases stopped at generation 2 with only age
losses; these observations do not demonstrate a Calhoun crowding mechanism.

Actual exposure timing and pregnancy provenance now work across generations,
but biological/social/ecological calibration and great civilizations remain
unverified. No coefficient was adjusted to select survivors. The primary
benchmark is clinical pregnancy; maximum-day aggregation and the phase prior
remain explicit assumptions. Exact sources, controlled/cross-runtime checks,
natural checkpoint geometry, raw results and terminal-status qualifications
are in `docs/audits/2026-10-30-fertility/`.

## Actual reproductive contact — 2026.10.30.6

Final seed 69, 36,000 model days, unchanged hashed sources, Python 3.14.6:
EDEN emptied on day 28,555 (year 79.32), peak 16, generation 1; LAGOON emptied
on day 35,630 (year 98.97), peak 17, generation 2. Neither reseeded within the
century because the 30-year quiet interval had not elapsed. EDEN recorded only
founder age deaths; this is not evidence of a Calhoun crowding collapse.
The old unconditional fertility coefficients are now contact-conditional and
uncalibrated; these results expose the remaining conception time-basis problem.
They do not establish ecological inviability or inevitable human extinction.
Exact data, contact counts, source hashes, diagnostic and independent review:
`docs/audits/2026-10-30-encounters/`. The larger goal remains in progress.

## Purposeful instruction — 2026.10.30.5

Final seed 69, 36,000 model days took 974.7s on the workbench with Python 3.14.6.
Exact input/output hashes, logs and independent review are retained under
`docs/audits/2026-10-30-instruction/`. This includes a one-second late-run stack
sample; elapsed time is not an isolated CPU benchmark or measured MacBook rate.

| World at year 100 | Population | Peak | Highest generation | Camps | Extinctions / reseeds |
| --- | ---: | ---: | ---: | ---: | --- |
| EDEN | 456 | 525 | 6 | — | 0 / 0 |
| LAGOON | 82 | 84 | 6 | 2 | 0 / 0 |

All 101 common sampled EDEN rows match `.4`; the terminal year is duplicated by
the lab's final append. Both worlds remain in iteration 1. LAGOON retains six
historical discoveries. At year 100, tools have 57 aware/46 qualified holders;
fishing 57/39; fire 70/33; preservation 70/33; shelter 70/28; predator hunting 1/1.
The camps have two lit fires, 284.0 total food and 78.04 prepared units inside
that total. No agriculture, lore, granary, livestock, seacraft or writing arose.

The natural arc records exactly four requested instruction exposures:

| Model day | Teacher → learner | Actually explained | Requested goal |
| ---: | --- | --- | --- |
| 3245 | Kali → Ganesh | Stone tools | Fishing |
| 4151 | Kali → Rama | Stone tools | Fishing |
| 16585 | Ganesh → Kaikeyi | Stone tools | Fishing |
| 27926 | Arjuna → Meera | Stone tools | Fishing |

These are foundational awareness exposures, not mastery, actual catches or four
direct fishing lessons. Maximum annually sampled retained requested-tool entries
is 2; at the endpoint it is 0. Other instruction/observation and actual practice
carry later skill transmission. Retained teacher-linked counts do not count
lifelong lessons or unique historical learners. The four actual recorded events
are distinct from those point-in-time fields.

The earlier `.4` outcome was 12 surviving LAGOON people with lost tools/fishing.
The `.5` choices differ, including random draw paths, attention rules and social
opportunities. This one-seed contrast does not isolate a population benefit or
validate the coefficients. Neither great civilization nor millennia are proven.
Conception's missing encounter gate is an explicit remaining causal defect,
recorded in the instruction audit; these are toy-model results, not human forecasts.

All 396 tests pass on Apple Python 3.9.6. Controlled pre-delivery seeking/teaching
states pass 61 visual/interaction checks at 390, 1024 and 1440 px after repairing a
19px tablet header expansion. That fixture proves intentions; the separate
unit continuation proves delivered instruction and subsequent real harvesting.

## Personal procedures and local works — 2026.10.30.4

Fresh seed 69, 36,000 model days (100 years), from the final source hashes in
`docs/audits/2026-10-30-skills/bake-inputs.json`, took 529.1s on the workbench
with Python 3.14.6. It does not measure throughput on the 2016 MacBook.

| World at year 100 | Population | Peak | Highest generation | Iteration | Extinctions / reseeds |
| --- | ---: | ---: | ---: | ---: | --- |
| EDEN | 456 | 525 | 6 | 1 | 0 / 0 |
| LAGOON | 12 | 22 | 5 | 1 | 0 / 0 |

Every common sampled EDEN column in all 101 rows matches the shipped `.3`
control. The last year 100 sample is duplicated by the lab's final-row append;
these are not 101 independent annual observations.

LAGOON retained five **historical discoveries**, but no living tool-making or
fishing holders at the endpoint. Of 12 living people, fire had 11 aware/9
qualified holders, preservation 11/9, shelter 11/3. The camp had one lit fire
and 173.19 prepared food units (173.2 total food rounded). Prepared food tags
existing inventory; it is not an additional food stock. No agriculture,
local granary, livestock or writing emerged. The controlled positive-rendering
fixture exercises grain-store construction, fire tending and writing work only;
it does not demonstrate natural cultural achievement, agriculture or livestock.
Endpoint teacher-linked entries were zero for surviving procedures; artifact
learning and practical use must not be described as observed verbal teaching.
Annual procedure maxima are in `procedure-samples.json`, not cumulative counts.

The completed pre-release run with the faulty fire-priority predicate died on
day 35330. That defect always ranked a fully lit four-part fire as needing
maintenance before every other craft. The independent pure-choice regression,
not the desired demographic outcome, justified changing the threshold to one
remaining part. The superseded arc and hashes remain separately retained;
`priority-change-proof.json` verifies the single model predicate difference.
Changed choices also change subsequent random draw paths: this one-seed
comparison does not establish a general survival benefit or real-world rate.

The final full suite passes 358 tests on Apple Python 3.9.6. Rendered natural
and explicitly controlled fixtures pass at 390, 1024 and 1440 px, with independent
MSH review and native keyboard focus. The finite ladder and illustrative
coefficients remain limitations; neither great civilization nor millennia of
survival has been established. The broader digital-human goal stays in progress.

## Contact-based knowledge — 2026.10.30.3

Final frozen-source seed 69 experiment: 36,000 model days (100 years), eight
founding pairs/world, Python 3.14.6, 691.7 seconds on the workbench. Raw arc,
compressed exact console bytes, source hashes and checks are retained under
`docs/audits/2026-10-30-social/`.

| World | Year 100 population / peak | Generation | Retained reports / people holding them | Recorded outcome |
|---|---:|---:|---:|---|
| EDEN | 456 / 525 | 6 | 20 / 17 | 239 withdrawn; no extinction/reseed |
| LAGOON | 34 / 38 | 5 | 0 / 0 |Six technologies, one camp, preserve lesson; no extinction/reseed |

Retained reports appear in 87 of 100 distinct annual EDEN observation years,
reaching 3 hops and
at most 99 stored reports in a sample. LAGOON retains reports in samples for
years 52, 90 and 91 (at most 2 reports, 1 hop), but none at year 100. These are
point-in-time memories, not cumulative conversations. Direct observation can
replace a report, so zero retained reports does not prove no communication.
Integration tests prove actual contact transfer in both worlds; controlled
LAGOON cases prove a received report changes the later resource destination
without granting supplies or harvest experience. The raw arc repeats its
identical year-100 terminal row; distinct-year counts exclude that duplicate.

All existing sampled EDEN columns (apart from new knowledge fields) match the
prior version. This is sampled demographic/control evidence, not a claim about
unrecorded state or other seeds. LAGOON's choices/population change; no human
benefit or isolated intelligence gain is inferred. The registry reports
12 supported / 1 contradicted / 4 undecided (H-EDEN-POSTS is contradicted).
No natural human-universe fall occurred in this century; forced lifecycle
checks cover reset/provenance rules. All 285 tests pass on Apple Python 3.9.6.

The default 100 model years/real day remains a target, not measured MacBook
throughput. Current tech knowledge is still world-shared, and the ladder ends
at writing. Source changes alter future trajectories; this is not a complete
digital-human model or a guarantee of civilization.

## Personal resource experience — 2026.10.30.2

Seed 69, 36,000 model days (100 years), eight founding pairs in each world,
from the final source hashes in `docs/audits/2026-10-30-experience/bake-inputs.json`:

| World | Year 100 population | Peak | Highest generation | Recorded outcome |
|---|---:|---:|---:|---|
| EDEN | 456 | 525 | 6 | 239 withdrawn; phase exploit; no extinction/reseed |
| LAGOON | 36 | 36 | 6 | Six technologies, one camp, preserve lesson; no extinction/reseed |

LAGOON reached fire, shelter, preservation, stone tools, fishing and predator
hunting. Lore, agriculture, seacraft and writing were not reached in this arc.
The predefined registry reported 12 supported, 1 contradicted and 4 undecided;
the contradicted claim was complete EDEN post occupancy, not a software test.
Registry support is not scientific validation. No human-universe fall occurred;
forced lifecycle tests cover fresh founders and the separate inherited-tag rule.

The run took 604.9 seconds on the workbench using Python 3.14.6. This is not
2016 MacBook throughput. All 268 tests pass on Apple Python 3.9.6; 22 new causal
cases cover local knowledge, outcomes, exploration, reload, maturation and
nursing. The initial 120-day canonical EDEN comparison matches the previous
release; later EDEN changes are expected from the maturation/nursing fixes.

Population and generation figures have changed from the prior release because
this version alters information, choices and physical/age contracts. The prior
source/provenance remains a separate historical audit. This combined
comparison does not isolate memory's population effect and is not a claim
about historical human growth. Reproduce with:

```sh
python3 tools/lab.py --days 36000 --every 360 --json /your/scratch/arc.json
python3 -m unittest discover -s tests
```

## Audit release 2026.10.30.1

Eight founding pairs per world; four parts per day; default 0.6 seconds per
part = 100 model years per real day. This is a configured pace, not a measured
speed for the 2016 MacBook. Existing saves retain their terrain/season version
and resume with a clock anchor that preserves ticks already due. Engine edits
change their future trajectories.

Food patches now belong to habitat locations rather than camps. Freshwater
banks, fetching, carried water, camp reserves and thirst make drinking distinct
from fishing in saltwater. Both resources deplete and replenish once per shared
place. Dry paths gate resources and animal encounters. Wildlife cannot respawn
from nothing. The retained food-sensitive fertility coefficients are hypotheses,
not a fit to a universal forager growth target.

The first audit arc was superseded after a causal nursing-channel bug: milk
supplied food until age three but supplied water only until six months. The
corrected model credits milk-water through the same nursing window, charging
the mother; no yield, mortality threshold or growth coefficient was tuned.
Private site/child cache keys were also made JSON-safe without changing their
lookup order or trajectory.

The final frozen-source, seed-69 measurement covers **36,000 full days =
144,000 parts = 100 model years**:

```sh
python3 tools/lab.py --days 36000 --seed 69 --every 1800 --quiet --json arc.json
```

| World | Day 3,000 population | Day 36,000 population | Peak | Generations reached | Iteration | Observed outcome |
|---|---:|---:|---:|---:|---:|---|
| EDEN | 34 | 614 | 619 | 6 | 1 | 229 withdrawn; phase label `exploit`; no extinction |
| LAGOON | 25 | 25 | 48 | 5 | 1 | Six technologies; one tribe; no extinction or greater-shore crossing |

Neither universe produced a postmortem or reseeded. **EDEN collapse remains
unobserved.** LAGOON reached fire, stone tools, shelter, fishing, predator
hunting and preservation. It did not discover lore, agriculture, domestication,
granaries, seacraft, healing, metallurgy or writing, and carried no inherited
lessons. Its final camp held 81.5 food units and 42.3 drinking units. Across the
whole terrain, including the unvisited mainland, 593 abstract deer and 0 big
cats remained; wildlife is not automatically replaced after extinction.

The recorded cause-of-death buckets were:

| Cause bucket | EDEN | LAGOON |
|---|---:|---:|
| Immediate infant loss at delivery | 893 | 12 |
| Starvation | 330 | 2 |
| Dehydration | 0 | 61 |
| Violence | 228 | 11 |
| Age | 69 | 16 |
| Accident | 0 | 7 |
| Childbirth | 0 | 2 |

The infant bucket counts immediate birth losses; infants who die later enter
their actual cause bucket. It is not a true infant-survival statistic.
Dehydration dominated LAGOON's recorded deaths, so the registry's starvation-
dominance hypothesis was **contradicted**. This is an outcome of this model's
water demand, access, transport and decision rules, not an estimate of Sri
Lankan mortality or carrying capacity. Resource units, travel reach and
thresholds remain illustrative hypotheses.

The registry returned 14 supported, 1 contradicted and 2 undecided checks; the
two unknown values are EDEN's absent sink-year/sink-gap phase dates. These
checks are not empirical validation. One seed and century do not validate a
millennium, founder genetics, or a guaranteed civilization timeline. The
technology ladder currently stops at writing.

**Validation and provenance.** All 231 tests passed on Apple Python 3.9.6
(547.846s); 22 new resource cases also passed independent review. Raw day-3,000
and day-36,000 saves were checked without migration: identities, reciprocal
bonds, clocks, claims, role holders, food/water bounds, unique shared sites,
shore adjacency, animal IDs and every adjacent annual census stock-flow all
passed. Ready-to-serve fixture events include the server's canonical year.
The final arc's captured source hashes still matched the frozen code after
completion. The raw saves, observer payloads, source hashes, logs and a clearly
superseded first arc are retained in the release audit.

Workbench arc runtime with Python 3.14.6: **1,146.888s** (about 19m7s), with
**42.8 MiB peak RSS**. This includes checkpoint observation and is not a
MacBook throughput guarantee. This audit did not inspect, reset or restart the
live instrument. The legacy yearlings/prior-births observer limitation below
also applies to this version.

## Historical audit release 2026.10.29.1

This engine changes the trajectory of an already running world. All historical tables
below belong to their named earlier engines and are **stale for this release**.
The needs/ecology fixes, world-specific names, and restored eight pairs per
world are documented in DESIGN.md. Migration preserves an existing population
and its food; an explicit restart archives the old run's state, events,
postmortems and books together.

A fresh seed-69 arc was re-derived from the reviewed engine for **60,000 full
simulated days (240,000 parts; 166 complete years plus 240 days)**:

```sh
python3 tools/lab.py --days 60000 --seed 69 --every 1800 --quiet
```

| World | Population at day 36,000 | Population at day 60,000 | Peak | Iteration | Recorded outcome |
|---|---:|---:|---:|---:|---|
| EDEN | 614 | 711 | 723 | 1 | 359 withdrawn; phase label remains `exploit`; no extinction |
| LAGOON | 231 | 435 | 439 | 1 | 13 technologies, three tribes, greater shore reached; no extinction |

Neither world reseeded or produced a postmortem. **EDEN collapse remains
unobserved**; withdrawal alone does not prove a future extinction. LAGOON
carried `preserve` and `cleanliness` and had not discovered writing. This is
one seed and horizon; no parameter was tuned to force an expected ending.

The registry returned 14 supported checks and three undecided: missing EDEN
sink-year/sink-gap phase dates and the inapplicable no-lore Dunbar check. This
is not validation: absent phase dates remain unknown in the registry even
beyond its proposed date range; withdrawal can precede a density phase label.

Raw day-3,000/36,000/60,000 saves passed identity, bond, room, role, store and
clock checks without migration; every adjacent census balanced population
change = births − deaths. Raw evidence is retained in the release audit.

Workbench runtime: **1,345.4 seconds**; a late memory sample was **41.4 MiB
RSS**, not a measured peak or a MacBook benchmark. The live instrument was
not inspected or changed.

**Observer limitation.** The legacy `infant_survival` field is only the capped
ratio of current people aged 360–719 days to births in the latest annual census
(`min(1, yearlings / latest births)`, three decimals; missing if no births).
Its cohorts do not match. It is not true infant survival and supports no
comparison to a clinical or forager survival threshold; the viewer labels it
YEARLINGS / PRIOR BIRTHS. The serialized column remains for compatibility.

## Authorized MacBook restart — executed (superseded)

The owner authorized a fresh start on the instrument. After the MacBook
pulls engine **2026.10.30.1**, the planned restart begins with eight pairs
in each world. **This workbench audit has not reset or restarted the live
MacBook.** Its actual current population and uptime were not inspected.

The explicit reset preserves the prior run in a unique archive directory;
state, events, postmortems and history books move together. Runtime mirror
configuration remains in place. Earlier trajectories are historical and
are not presented as results from this model. Planned MacBook procedure:

```sh
launchctl unload ~/Library/LaunchAgents/com.universe69.sim.plist
python3 sim/server.py --genesis   # once up, Ctrl-C saves the fresh state
launchctl load ~/Library/LaunchAgents/com.universe69.sim.plist
```

The first run's record is kept in the viewer (help card → ABOUT → *The First Run*).

That restart did happen — the public packet now carries attempt EDEN4
(seeded day 84263) — and the instrument has adopted every engine through
**2026.11.01.1** (`d02775f`).

## Adoption pending on the instrument — 2026.11.01.1 → 2026.11.03.2 (recorded 2026-11-04)

The public packet (gist mirror, 2026-11-04, fresh upload) reports the
instrument on **engine 2026.11.01.1** at the old pace (0.6 s/part, 100
years per real day): **EDEN4** holds 5 people in phase *exploit* (peak 19 —
a failed micro-attempt on its way to the empty pen), **LAGOON** holds 27
at year 294 in *predator_hunt* through repeated droughts. On the old
engine EDEN4 will auto-reseed under the same conditions.

The repository is at **2026.11.03.2** and the instrument has not adopted:

- `edaa698` — personal fuzzy needs, truthful terrarium views (2026.11.03.1)
- `523e7b5` — one model year per real hour, human-scale graphics (2026.11.03.2)
- `1fa5c79`, `52a5d61` — the skinned CC0 humans in the headset viewer
  (renderer only; no trajectory change)
- `2a979f8` — the crowd-test audit and docs

**Pre-flight (2026-11-04):** the full unittest suite — 631 cases, including
every engine-behaviour and migration path these two versions touch — is
green on the workbench for the first time since the last two engine bumps
(earlier sessions had run only partial modules). The viewer modules (153)
and the crowd test at 169 people, 59.9 fps (`docs/audits/2026-11-04-crowd/`)
are also green.

**The workbench cannot reach the instrument.** No SSH path exists or is
recorded here; every engine adoption so far was done by the owner pulling
on that machine. The remaining step is therefore on the 2016 MacBook:

```sh
cd "/Users/admin/repos/Universe 69"
git pull
launchctl kickstart -k "gui/$(id -u)/com.universe69.sim"
```

`KeepAlive` restarts the server; SIGTERM saves the state first;
`engine.migrate()` carries the 2026.11.01.1 state forward — **the same
world continues under the new rules**, its `engine_history` recording the
jump. That is a trajectory change to a 296-year-old run, made deliberately.
A fresh start instead (`python3 sim/server.py --genesis` once, after the
pull, then let the agent restart it) begins the new phase from eight pairs
with LAGOON carrying the dead attempts' lessons — the choice is the
owner's. Either way the published viewer on GitHub Pages is already the
new one and reads the same mirror.

### Adoption executed — 2026-11-04 (from the public packet)

The owner ran the update on the instrument. The mirror now reports
**engine 2026.11.03.2** at the new default clock (**1 year per real
hour**, 2.5 s/part). The day number **continued** (117070, Y325) — the
year-320 worlds were carried across by `engine.migrate()`, not restarted;
no `--genesis` was run.

- **EDEN4 emptied at Y325** — peak 19, the last person died at the cusp,
  under the old rules. It will reseed as **EDEN5, the first reseed ever
  processed under the new engine** (innocence roll, founding births
  anchored at the founding day, EDEN amenities).
- **LAGOON3 continues** — 36 people at Y325 in *predator_hunt*, growing
  through the drought years; it carries the dead attempts' lessons.

All figures re-derived from the public mirror packet, not private state.
The reseed is visible in the mirror on its next upload. This is the start
of the run's new phase: one world rerunning Calhoun's conditions under the
new mechanisms, one world earning everything, both on the hour-per-year
clock, observed and never helped.

## Historical engine 2026.10.28.4 — eight pairs, real needs, animals with places (re-derived 2026-10-28)

Both worlds start from the same eight pairs. Food is gathered, carried and
eaten by persons; EDEN and LAGOON decide with one function (DESIGN.md).
Every earlier figure in this file is from an engine whose food was a
headcount formula and whose EDEN collapse was a phase script — none of them
carries over. Re-derived with:

```sh
python3 tools/lab.py --days 36000 --seed 69 --every 1800   # and seeds 123, 5
```

| Seed | EDEN y20 | y40 | y60 | y80 | y100 | withdrawn at y100 | LAGOON y20 | y40 | y60 | y80 | y100 | LAGOON peak | tech |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 69 | 78 | 207 | 419 | 650 | 683 | 277 | 46 | 95 | 101 | 164 | 288 | 322 | 12 |
| 123 | 82 | 194 | 386 | 632 | 741 | 299 | 34 | 58 | 88 | 169 | 320 | 348 | 13 |
| 5 | 70 | 156 | 361 | 584 | 739 | 264 | 32 | 62 | 108 | 181 | 222 | 275 | 12 |

What the three seeds agree on, in the first century:

- **EDEN expands and hollows.** Growth is steady (~5%/yr early) and
  flattens after year 80. From year ~50 the withdrawn rise from a handful
  to ~36–40% of the pen, and competent breeding men fall to 4–14. By year
  30 there are already ~2 competent adults per post: Calhoun's role
  saturation. Withdrawal comes from crowding wearing company down at the
  beds and bars, and incompetence from being reared in a crowded nest — the
  sink appears at ~20–30% of the pen's capacity, before the `stagnate`
  label (35%) ever fires. Calhoun's own stagnation began near 16%. No seed
  collapsed within 100 years: whether this pen dies, and when, is the next
  arc to run (`--days 60000`).
- **LAGOON lives, alongside its animals.** No extinction in any seed.
  Bands grow to 222–320 by year 100 (peaks 275–348), split into two or
  three tribes and reach 12–13 technologies; famines still cut them back
  (seed 5 fell from 263 to 181 in the decade before year 80).
  Deer hold at roughly 420–590 and big cats at 0–4, recolonising
  when they die out (animals.py). Predation is real but bounded: in 50-year
  traces (taken before hunters learned to track the nearer cat) it took 0–12 people, mostly before fire and stone tools, and
  people killed 2–4 of the cats that came for them.
- **Calibration flags:** LAGOON's growth (~3%/yr over the century) is above
  the ≤1%/yr the forager literature gives (Howell; Marlowe), so fertility
  or child survival is too generous.

## Historical baseline — 2026.10.28.1

Re-derived from the shipped engine, seed 69, for 60,000 full simulated days
(240,000 parts; calendar year 166):

```sh
python3 tools/lab.py --seed 69 --days 60000 --every 3600 --quiet
```

| World | Final population | Peak | Iteration | Outcome |
|---|---:|---:|---:|---|
| EDEN | 926 | 1,802 | 1 | Death phase; no extinction or reseed yet |
| LAGOON | 463 | 470 | 2 | Survived after one extinction; 13 technologies, two tribes, greater shore reached |

EDEN's sink began in year 86 and its death phase in year 104. This run does
**not** establish when EDEN will empty. LAGOON carried two lessons at the end.
These are model outcomes, not measurements of human societies.

The raw observer report returned 15 supported checks and two contradictions.
One was a reporting defect: the Dunbar check says *without shared lore*, yet
it judged a terminal society that already had lore. The read-only research
layer was corrected after the trajectory run; the engine was unchanged.
Re-evaluating applicability from the terminal technology list yields
**15 supported, one contradicted, one undecided**. The remaining contradiction
is EDEN's posts: 89.7% held against the implementation's 99% threshold. It
remains reported; the model was not tuned to turn it into a pass.

The raw arc/log and the separate observer correction are retained with the
release audit evidence. Earlier studies below are historical and stale.

---

Earlier-study engine state at the time of writing: seed 69, `DAYS_PER_YEAR = 360`,
`ADULT_AGE = 16 years`, `GESTATION = 270 days`.

---

## 1. Could two pairs of young people reach 2,000 in a hundred years?

**Yes — demographically, easily. And in EDEN they never do, which is the
finding.**

The table below is **from the retired `tools/sweep.py` harness and was not
re-run under the current engine** — the current deterministic arc (Y1–Y400)
no longer even approaches 1,000, peaking at 242 (year-row; 243 stored) with
generation max 16, so treat the "pen as built" speeds as historical. This
experiment was run twice: once with the pen as built, and once with the
pathology removed so that only the demography remained.

```sh
python3 tools/sweep.py --study default  # retired harness; figures historical
```

| population first reached | pen as built | pathology removed |
|---|---|---|
| 50   | year 23 | year 23 |
| 100  | year 30 | year 30 |
| 200  | year 39 | year 39 |
| 500  | year 56 | year 50 |
| 1000 | never | year 58 |
| 2000 | never | **year 67** |
| 3000 | never | year 74 |

Peak population: **243** stored / **242** on a yearly row (pen as built,
year 93, measured arc Y1–Y400, two deterministic processes) against **4000+**
(pathology removed, still climbing when the run was stopped — from the retired
`sweep.py` harness; not re-run under the current engine).

The demographic engine is not slow. A woman conceives with probability
1/180 per day and carries for 270 days, so each woman bears roughly a child
every 450 days — from 16 to 45, that is about 23 children. With a 16-year
maturation the population roughly doubles every two years once the second
generation starts breeding, and two pairs reach 2,000 in **67 years**.

So the ceiling in EDEN is not human fertility. It is the pen.

**And the pen's size is the whole answer.** The table above uses the pen as
built: capacity 900, 32 nest boxes. Run the same seed in a pen of Calhoun's
proportions — capacity 3,840, 256 boxes of 15 — and **2,000 people are
reached in year 75**, the population peaks at 2,866, and it holds there for
roughly 150 years before the same collapse arrives. These figures are from the
retired sweep harness, never re-derived on the current engine; the current
deterministic arc peaked at 242 (year-row) and never approached 2,000. The
answer to "could they
populate 2,000?" is therefore *yes*, and it was the pen, not the biology, that
was saying no.

## 2. The pen has two capacities, and they disagree

The UI now prints both, because the disagreement is the mechanism:

> **PEN: 32 NEST BOXES · 224 PLACES · CAP 900**

`EDEN_CAP = 900` is the pen's nominal capacity. The pen actually has 32 nest
boxes of 7 places each — **224 socially meaningful places**. At the measured
peak of **243 people** that is **1.08 times as many people as there are places
to have a territory** — slightly crowded, but the sink never deepens to
Calhoun's 3.4× ratio because the engine's fertility/crowding feedback stabilises
a limit cycle instead of driving extinction.

Calhoun's Universe 25 had 256 boxes and about 15 mice per box — 3,840
nominal places, and a peak near 2,200. The ratio of peak to nominal was
about 0.57. This pen peaks at 0.84 of its declared capacity, and 3.36 of its
real one.

**Which number is right is a research question, not a detail.** That is why
the pen's architecture is now a parameter rather than a constant:

```sh
python3 tools/sweep.py --study calhoun     # Universe 25 as Calhoun built it
python3 tools/sweep.py --study boxes       # vary the number of nest boxes
python3 tools/sweep.py --study crowding    # vary where the sink begins
```

### The pen's architecture barely matters

Five pens, each run to extinction and reseeding, seed 69:

| pen | peak | peak year | extinction | reseed |
|---|---|---|---|---|
| Universe 25 as built (256 boxes × 15, cap 3840) | 2866 | 92 | 279 | 309 |
| same boxes, sink at 35% | 2914 | 100 | 250 | 280 |
| same boxes, sink at 10% | 2912 | 101 | 284 | 314 |
| 256 boxes of 8 (2048 places) | 2920 | 100 | 288 | 318 |
| 128 boxes of 15 (1920 places) | 2933 | 101 | 294 | 324 |

**Every pen collapses on the same schedule.** Halve the nest boxes, shrink
each box, or move the crowding threshold from 10% to 35%, and the peak stays
within 2% of 2,900 and the extinction within 40 years of the others.

Two things follow.

First, **the model reproduces Calhoun's shape.** His Universe 25 peaked near
2,200 around day 560 and was functionally extinct by day ~1,600. This pen, in
his proportions, peaks at 2,866 in year 92 and empties in year 279 — the same
arc, stretched to human generations.

Second — and this is the uncomfortable part — **this model does not support
the critique recorded in RESEARCH.md.** Ramsden and Adams argue the outcome
tracked the *architecture*: that the design funnelled animals into contact,
and that outcomes were design-dependent rather than an iron law of crowding.
In this model the architecture is close to irrelevant. What drives the
collapse is the fertility-versus-crowding feedback, and the sink threshold
merely sets when it starts. If the critique is right, then the mechanisms
that make *architecture* matter — the funnel, the territory, the crowding of
the roles — are under-modelled here. The box system currently records who
holds a place; it does not yet make *where* the places are shape the
behaviour.

## 3. The arc of Universe 6, measured from two independent runs

Two deterministic engine processes, both seeded from `engine.genesis(seed=69,
attempt=1)`, reproduce each other exactly — and together tell the true arc.

**Determinism witness.** Run 1 (Y130 cap) and run 2 (400-year cap) both began
from the same genesis and were cross-checked row-by-row across 260 common rows
(both worlds × 130 years × 11 fields). Every field matches with **zero
mismatches** — pop, peak, gen_max, phase, phases, births_y, deaths_y,
bad_years, cod, census_len, iterations. The witness arc is a reproducible
property of the engine, not a lucky draw. (Run 2's first 1.4 min were lost to
a stale `OUTDIR` reference in the checkpoint writer; fixed, verified, no data
lost; run 1's record is the untouched baseline.)

**EDEN.** Across 400 years EDEN never goes extinct — it oscillates in pop
(peaks 240+ mid-century, troughs ~150) while the `phase` label stays
`exploit` after the initial Y1 strive→exploit flip (399 of 400 rows read
`exploit`; the label reads the crowd, not the pop). Stored peak 243 (year-row
max 242 at Y93). Gen_max = 16. Final population at Y400 is 187. Terminal
cause-of-death cod: `{infant: 729, age: 698, violence: 340, starvation: 3,
plague: 1}`. Sampling: Y105 births=1, deaths=8; Y250 births=3, deaths=4;
Y400 births=5, deaths=5. Event counts: project 96,622 / bond 9,066 /
feud 8,563 / peace 8,497 / omen 2,342 / violence 57 / disease 3 / discovery 2
/ ennui 2 / generation 3 / phase 1. Zero `gift` events in the arc (kula fires
only in the live run's LAGOON lineage).

**LAGOON.** Across 400 years LAGOON never goes extinct. Stored peak 79 (year-
row max 78 at Y172). Gen_max = 15. Phase: strive only. Final population 27.
Terminal cause-of-death cod: `{dehydration: 307, violence: 79, infant: 81,
accident: 38, age: 54, starvation: 25, childbirth: 7, predator: 6}`. Lessons
learned: `vigilance` (Y1 predator took 3) and `preserve` (Y174 starvation took
5). Event counts: project 32,976 / omen 2,196 / bond 470 / heir 108 /
violence 63 / feud 170 / disaster 29 / lesson 2.

**Retired harness table.** The table below — peak 752 @ Y78, extinct Y234,
cod `{infant 952, age 571, violence 384, plague 24}` — came from the
retired `tools/lab.py` harness and does not reflect the current engine's
deterministic behaviour. It is retired here; the 400-year arc supersedes it
wholesale, not by update but by replacement.

| fact | EDEN | LAGOON |
|---|---|---|
| stored peak | 243 (Y93) | 79 (year-row 78 @ Y172) |
| peak year-row | 242 @ Y93 | 78 @ Y172 |
| gen_max | 16 | 15 |
| final Y400 pop | 187 | 27 |
| final cod | `{infant: 729, age: 698, violence: 340, starvation: 3, plague: 1}` | `{dehydration: 307, violence: 79, infant: 81, accident: 38, age: 54, starvation: 25, childbirth: 7, predator: 6}` |
| phase cycle | Y1 strive → exploit, then constant `exploit` | strive always |
| lessons | — | `vigilance`, `preserve` |

| | Y105 | Y250 | Y400 |
|---|---|---|---|
| EDEN births | 1 | 3 | 5 |
| EDEN deaths | 8 | 4 | 5 |
| LAGOON births | 2 | 2 | 0 |
| LAGOON deaths | 1 | 0 | 0 |

| EDEN events | count | LAGOON events | count |
|---|---|---|---|
| project | 96,622 | project | 32,976 |
| bond | 9,066 | omen | 2,196 |
| feud | 8,563 | bond | 470 |
| peace | 8,497 | heir | 108 |
| omen | 2,342 | violence | 63 |
| violence | 57 | feud | 170 |
| disease | 3 | disaster | 29 |
| discovery | 2 | lesson | 2 |
| ennui | 2 | | |
| generation | 3 | | |
| phase | 1 | | |
| **EDEN total** | **125,158** | **LAGOON total** | **36,014** |

(Both worlds combined: 161,172 events. Zero `gift` events anywhere in the
arc — the kula fires only in the live run's LAGOON lineage, never in a
fresh genesis lineage.)

**Summary.** EDEN lives and oscillates — it does not die. LAGOON rides its
own predator-driven cycle. The 400-year cap reveals a stable limit cycle,
not extinction. The arc watch ends at Y400 alive; the engine is
deterministic across processes; the old table is retired.

## 4. The two universes diverge, and the reason is worth knowing

**The determinism question is settled.** Two independent engine processes —
`full_arc.py` run 1 (Y130 cap) and run 2 (400-year cap) — both began from
`engine.genesis(seed=69, attempt=1)` and were cross-checked across 260 common
rows: both worlds × 130 years × 11 fields. Every field matches with **zero
mismatches**. Determinism holds across processes, not merely within one. The
fresh-vs-live table below was measured under the *previous* engine version,
when it still failed; it is retained as a record of that failure and of what
fixed it.

| | EDEN | LAGOON |
|---|---|---|
| live run (day 41,149) | 485 people, year 114 | **251 people**, year 114 |
| fresh run, same engine | 480 people, year 113 | **22 people**, year 113 |

EDEN tracks closely. LAGOON does not: the fresh run stalls at 22 people with
seven technologies, while the live run reached 251 and crossed to the
continent.

The cause is that determinism holds only *within one engine version*. The
live run has been ticking through many engine rewrites and restarts since it
began; each change re-rolls the trajectory from that day on. The claim in
`DESIGN.md` — "deterministic per seed+day" — is true within a version and
false across the history of a long run.

What this costs: **no figure derived from the live run can be re-derived
later.** The fix is to version the engine and record its version in the state
and in every postmortem, so a published number can always be traced to the
code that produced it. Until that exists, treat any number taken from the
live history as a record of *that run*, not a property of the model.

## 5. What is deliberately not claimed

- These are measurements of a **model** built from the literature in
  `RESEARCH.md`, not of people.
- The numbers above come from **one seed**. The pen's design sweep exists
  because a single run is an anecdote about a single run.
- The cumulative EDEN cause-of-death counts (§3: infant 729, age 698,
  violence 340, starvation 3, plague 1) accumulate over the whole 400-year
  window and describe *how* the living died across it, not a single die-off.
  The measured arc produced no EDEN postmortem because EDEN never emptied.
- **A place emptied by death is never taken again** by the people who were
  already displaced. The viewer shows this directly: amber nest boxes are
  held, green ones are vacant, and the status line reads *"61 without
  territory · 85 places vacant, never refilled"*. That is the model's
  reading of Calhoun's "death squared" — the social death precedes the
  physical one — and it is why the boxes can be a third empty while a fifth
  of the pen has nowhere to go.
