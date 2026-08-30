# Calibration results

One entry per scored run against a fixture in this directory. A run belongs
here only if it met the conditions in [`README.md`](README.md): the reviewer saw
only `PROMPT.md` and the seeded artifact, with no repository access, no git and
no network.

## 2026-08-30 — `semver-2.0.0-seeded.md`

Fixture sha256 `3f17407b3e34e16296ae9680284079f3ce96599b0bf2c35589ab808f7ace5bd6`

| | |
|---|---|
| Reviewer | claude-opus-5, Claude Code agent, blind single-run |
| Instrument | Diffract 0.3.0 |
| Compass | Adoption: where must a team implementing against this text make a call the text declines to make? |
| Cobra | library-framework |
| Integrity | `file:line` per lens, cognitive anchoring, verbatim quote block per finding |
| Findings raised | 24 (15 Major) |
| **Seeds found** | **4 of 4** |
| Form check | 24/24 quote blocks verbatim at cited lines |
| Review | [`semver-2.0.0-seeded-review.md`](semver-2.0.0-seeded-review.md) |

Identical governors to the published review in
[`examples/semver-2.0.0-review.md`](../examples/semver-2.0.0-review.md), which
reviews the unseeded text, so the two runs differ only in the artifact.

| Seed | Found as | Lens predicted | Lens that found it |
|------|----------|----------------|--------------------|
| S1 | `TRU-1` Major | 📌 Truth | 📌 Truth |
| S2 | `VAR-2` Major | 🛡️ Shield | 🎯 Variety |
| S3 | `SUB-1` Minor | 🎯 Variety | 🗑️ Subtract |
| S4 | `TRU-2` Major | 🧱 Boundary | 📌 Truth |

Each was confirmed by reading the finding, not by line overlap alone. S3 is the
notable one: the reviewer identified not only the duplicated grammar alternative
but what its duplication implies — "the tell that a distinct fourth alternative
was intended and is absent."

**Negative control.** The published review of the *unseeded* artifact scores
0 of 4 against this key. A review of the clean text hits no seeds, so a nonzero
score cannot come from the two documents sharing territory.

### What the run says about the fixture

**The predicted lens was wrong three times in four.** Seeds are found; which
lens finds them is not stable. `seeds.md` now records the lens as a prediction
and says explicitly that it is not part of the score.

**S1 was partly detectable as a formatting artifact.** The seeded sentence
borrowed the wrapped line below it without its continuation, leaving a dangling
line the reviewer called out as a tell. The seed could be spotted without
understanding the contradiction. Corrected after this run, so a future run
against S1 is not comparable with this one.

### What the run does not say

Four seeds is coarse. 4/4 distinguishes a reviewer that finds planted
contradictions from one that finds none; it does not separate a good reviewer
from an excellent one, and it says nothing about the far larger population of
defects nobody planted. One run cannot be calibrated against itself — this is a
single measurement, not a calibration curve.

All four seeds are internal contradictions, which is the class this instrument
should be best at. Recall on this fixture is not evidence of recall on defect
classes the fixture does not contain.
