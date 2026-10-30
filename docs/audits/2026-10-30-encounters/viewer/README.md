# Viewer evidence — engine 2026.10.30.6

Final mirrored HTML SHA-256:
`529d0594fae4248fcb915154bd2e26a2c584eecd1d3f4e92174251f1c7194a19`.
All final screenshots and response-hash reports use this source.

- [Full journey report](full/frozen-report.json): 268/268 phone, 242/242 tablet,
  242/242 desktop checks, including reading pages, controls, recovery and
  anatomy/motion diagnostics. Zero console, page or failed-request errors.
- [Focused report](focused/report.json): 441/441 checks across five cases and
  three widths; native focus, expanded facts, MORE, portraits and actual
  `matingSprite` participant IDs. Every initial snapshot already populates and
  content-fits its record. Empty focus footers are 54px at all three widths.
- [Fixture recipes and source hashes](fixtures/provenance.json): explicit
  controlled/synthetic setup through real engine APIs and summary packets.
  Cases cover bonded but unaccepted proposals, nonbonded EDEN contact, LAGOON
  contact, prebirth labour and immediate postpartum rest.
- [Found / Changed / Verified / Remaining](provenance.json), including chrome
  bounds and source/fixture hashes.
- [Independent final visual review](../independent-visual-review.md).

`before/` preserves the preceding viewer actually drawing phantom bonded
IDs [1,2] from the same unaccepted-proposal packet. The final draw probe emits
no pair there and draws the actual nonbonded IDs [1,4] in its positive case.
`before-record-init/` and `before-footer-fit/` retain the initial blank-footer
failure: 111→54px on phone and 130→54px on desktop, returning 57/76px to the
worlds. The cause was record initialization delayed until the eighth animation
frame; the final poll populates the record before the first visible snapshot.

These fixtures are not natural runs or validation of human reproductive rates,
clinical labour duration, willingness frequencies or independent social choice.
The one-day prebirth window remains an illustrative model interval. The
renderer keeps its 18-year adult visual gate independently of the model's age
threshold: younger or unknown-age actors use neutral poses even if a contact
record exists.

Verification scripts and compact inputs are retained beside their reports.
Browser/Node tooling is workbench-only; production remains standard-library.
