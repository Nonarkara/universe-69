# Read-only public snapshot audit

Configured URL: https://gist.githubusercontent.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/raw/snapshot.json
Gist commit: ccdd9c04750d0e35a6be55684a36d402f31d7318; raw blob URL: https://gist.githubusercontent.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/raw/4aedd1d9c3cd722d67f914b68b12f075575fc242/snapshot.json
Latest captured wall: 2026-11-02T18:50:52.390748+00:00; SHA256 c4637d15ec6cc30b7304b24e59c6be9b69d838af74532563f774d2e50e6c2ec5

## Recorded deaths across sampled gist history

Snapshot 2026-10-31T22:58:35Z; engine 2026.10.31.1
- EDEN iteration2: terminal engine2026.10.31.1, day125425 (global year348.4028), founded98367, iteration age75.1611years, wall2026-10-31T22:22:45.762870+00:00, peak16, gen1, dominant counterage, counts{"age": 16}.
  Engine history: [{"from": "2026.10.27.3", "to": "2026.10.28.1", "day": 58258, "part": 0}, {"from": "2026.10.28.1", "to": "2026.10.29.1", "day": 68144, "part": 3}, {"from": "2026.10.29.1", "to": "2026.10.30.7", "day": 78456, "part": 2}, {"from": "2026.10.30.7", "to": "2026.10.31.1", "day": 123104, "part": 3}]
- LAGOON iteration1: terminal engine2026.10.30.7, day120797 (global year335.5472), founded0, iteration age335.5472years, wall2026-10-31T19:17:41.014351+00:00, peak675, gen14, dominant counterstarvation, counts{"childbirth": 29, "starvation": 2041, "infant": 205, "age": 218, "predator": 57, "epidemic": 212, "accident": 48, "violence": 17, "dehydration": 39}.
  Engine history: [{"from": "2026.10.27.3", "to": "2026.10.28.1", "day": 58257, "part": 0}, {"from": "2026.10.28.1", "to": "2026.10.29.1", "day": 68143, "part": 3}, {"from": "2026.10.29.1", "to": "2026.10.30.7", "day": 78455, "part": 2}]
- EDEN iteration1: terminal engine2026.10.30.7, day87566 (global year243.2389), founded0, iteration age243.2389years, wall2026-10-30T23:46:22.733248+00:00, peak749, gen6, dominant counterinfant, counts{"plague": 31, "age": 603, "infant": 1102, "violence": 401}.
  Engine history: [{"from": "2026.10.27.3", "to": "2026.10.28.1", "day": 58258, "part": 0}, {"from": "2026.10.28.1", "to": "2026.10.29.1", "day": 68144, "part": 3}, {"from": "2026.10.29.1", "to": "2026.10.30.7", "day": 78456, "part": 2}]
Snapshot latest; engine 2026.11.01.1
- EDEN iteration2: terminal engine2026.11.01.1, day31080 (global year86.3333), founded0, iteration age86.3333years, wall2026-11-02T03:55:41.339185+00:00, peak20, gen2, dominant counterage, counts{"age": 20}.
  Engine history: [{"from": "2026.10.31.2", "to": "2026.11.01.1", "day": 17192, "part": 3}]

## Limits

- Current packet EDEN iteration3/pop15, LAGOON iteration2/pop5: neither currently extinct. Latest terminal observed death is new EDEN iteration2 at day31080.
- Calendar/state discontinuity between Oct31 (globalday126320) and Nov1 (day23625). EDEN iteration2 appears in both with different peak/end chronology. IDs alone cannot identify a unique lineage. No remote live-state repair or service access performed.
- Old iteration1 records absent from latest observations, but remain in versioned gist snapshots. Empty observations was not proof no older deaths existed.
- Dominant cause is the maximum cumulative death counter; it neither identifies the final death nor diagnoses why replacement stopped. Old EDEN infant count1102 is not evidence every death was an infant death; LAGOON starvation2041 is not proof a unique sufficient cause.
- Mixed engine histories and missing seed/source revision make cross-version causal claims unsupported. Global calendar year differs from iteration age, especially reseeds.
- Daily sampled7historical revisions out of941; this is not a complete event reconstruction. Latest56event buffer and observations are partial public projections, not raw live state or every postmortem.
- research.history is literature/story shelf, not empirical chronology. recorded is empty in sampled current packets, so no book-of-run artifact is available from this gist. No other service or unpublished files consulted.
- Test invocation began on a559b63; parent changed model sources while it ran. Treat terminal results as a mixed-source check, not a frozen baseline. Final frozen suite is parent-owned.

## Fetch scope and local dates

Fetched on **2026-11-03 Asia/Bangkok**. Latest packet wall is **2026-11-02 18:50:52 UTC /2026-11-03 01:50:52 Bangkok**. This is the last observed public packet, not confirmation of the live instrument now. No live database, service changes or instrument postmortem-file access occurred. UTC timestamps above are authoritative recorded event walls; Bangkok is UTC+07:00.

| Recorded event | UTC | Asia/Bangkok |
|---|---|---|
| EDEN iteration1 extinction |2026-10-30 23:46:22|2026-10-31 06:46:22|
| LAGOON iteration1 extinction |2026-10-31 19:17:41|2026-11-01 02:17:41|
| Earlier EDEN iteration2 extinction |2026-10-31 22:22:45|2026-11-01 05:22:45|
| Later reused EDEN iteration2 extinction |2026-11-02 03:55:41|2026-11-02 10:55:41|

## Retained primary public records

Byte hashes and deterministic gzip hashes are in [manifest.json](manifest.json). Files decompress to retrieved UTF-8 packet bytes; JSON is not reformatted. Terrain is already included. The941-entry commits index is retained separately as `commits.json.gz`.

- [Gist revision 1d66af6fae87e78beb527e3ed206a464c0e80bd9](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/1d66af6fae87e78beb527e3ed206a464c0e80bd9) → `history-1d66af6fae87e78beb527e3ed206a464c0e80bd9.json.gz`.
- [Gist revision 259035a00683ed74efe310477a6d8418da8edcb3](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/259035a00683ed74efe310477a6d8418da8edcb3) → `history-259035a00683ed74efe310477a6d8418da8edcb3.json.gz`.
- [Gist revision 276305697d59d7f5d54d61ef44021713f67a2287](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/276305697d59d7f5d54d61ef44021713f67a2287) → `history-276305697d59d7f5d54d61ef44021713f67a2287.json.gz`.
- [Gist revision 3243645c7d73800d6e54c6d48197781db807d85b](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/3243645c7d73800d6e54c6d48197781db807d85b) → `history-3243645c7d73800d6e54c6d48197781db807d85b.json.gz`.
- [Gist revision 3358f6eb8ff8f4ea9532545285ac6e3f06df78eb](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/3358f6eb8ff8f4ea9532545285ac6e3f06df78eb) → `history-3358f6eb8ff8f4ea9532545285ac6e3f06df78eb.json.gz`.
- [Gist revision b45d07152204b8b07b2c201846a8b678f5ea1043](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/b45d07152204b8b07b2c201846a8b678f5ea1043) → `history-b45d07152204b8b07b2c201846a8b678f5ea1043.json.gz`.
- [Gist revision fd45231b39c1c97dfaece865a3a67a7480f5c2fa](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/fd45231b39c1c97dfaece865a3a67a7480f5c2fa) → `history-fd45231b39c1c97dfaece865a3a67a7480f5c2fa.json.gz`.
- [Latest observed gist commit](https://gist.github.com/Nonarkara/4f22e527b4daf39c97d88e1fc1d37b6e/ccdd9c04750d0e35a6be55684a36d402f31d7318) → `snapshot.json.gz`.
