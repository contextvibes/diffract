# Research: Reviewer Tiering (RQ5)

## Research Question

Do the reviewer tiers defined in [calibration](../calibration.md) separate
reviewer configurations in practice, and does a tier-4 assignment predict
that two reviewers will pass The Test?

Both answers are no. The tier criteria saturated — four configurations whose
run-to-run dispersion differs by roughly 5x all measured tier 4 — while every
one of the six pairings between them failed Success Criteria condition 1.

## Method

Twelve independent reviews of one frozen artifact, three runs each by four
Claude models under a byte-identical prompt (only the output path differed).
Every run stopped at CHECK — no fixes. All twelve ran in one-shot mode and
all twelve carried the mandatory `[async — no PLAN confirmation]` tag.

**Frozen inputs:**

| Input | Fingerprint |
|-------|-------------|
| `README.md` @ `22926ec` (the artifact) | md5 `fbd1b0534cadf89fa1327cc2ec25a7a7`, 262 lines |
| `PROMPT.md` v0.2.1 @ `9cb9cf2` (the instrument) | md5 `dfee94aaf0f40d33c57b0a48531aa84a`, 272 lines |

**Pre-set governors** (identical in every run):

- 🧭 Compass: "Could a newcomer apply Diffract correctly using this file
  alone?"
- 🐍 Cobra: library/framework
- ⚖️ Integrity: line-number evidence per lens; cognitive anchoring required.

**Deviations from RQ3's protocol**, recorded before results were seen: both
files were pinned to out-of-repo copies rather than live repo paths, because
`docs/governors.md` had drifted since RQ3 and reusing RQ3's prompt verbatim
would have changed the artifact as well as the instrument; and the harness
required a `## FINDINGS INDEX` section that `PROMPT.md` v0.2.1 did not.

## Ground Truth

**GT1 — established before the runs.** `README.md:111` said "Apply 10
lenses"; the table at `:115–125` listed nine. 🔗 Provenance was absent from
the entire file, and positions 7–9 were shifted against `PROMPT.md:91–102`.
The defect is a self-contained contradiction fourteen lines wide: no outside
knowledge is needed to see it. `CHANGELOG.md` claims 0.2.0 fixed "Provenance
missing from the lens count" — it did so everywhere except the README, which
was the only markdown file in the repo with zero mentions of the lens.

**GT2 — surfaced by the runs; barred from scoring.** `README.md:39` linked
to `#contributing`; no such heading existed, though `CONTRIBUTING.md` shipped
in the repo, unlinked. Independently verifiable, but established *by the
reviews under test*, which [calibration](../calibration.md) excludes. It is
recorded here as design input, not as a measurement.

## Counting Is Not Defined by the Instrument, and It Showed

`PROMPT.md` v0.2.1 had no findings-index requirement and no definition of
what a "finding count" includes. Across twelve runs, three policies appeared:
everything not discarded; `Fix` verdicts only; and an index of some verdicts
but not others. The first dispersion table computed for this study compared
numbers produced under all three and was not meaningful.

Recomputed with one policy throughout — **claims raised**, which is every
finding that reached CHECK:

| Reviewer | Runs | Mean | Range | CV |
|---|---|---:|---:|---:|
| Haiku | 6, 22, 2 | 10.0 | 2–22 | ~1.0 |
| Sonnet | 5, 4, 9 | 6.0 | 4–9 | 0.44 |
| Fable | 12, 9, 10 | 10.3 | 9–12 | ~0.15 |
| Opus | 22, 18, 27 | 22.3 | 18–27 | 0.20 |

What survives the correction: **Haiku is 3–6x noisier than every other
configuration**, replicating its CV of 0.91 in RQ3 on a different artifact
and a different instrument version. What does not survive: any finer ranking
among the other three. An earlier reading of this data put Fable an order of
magnitude tighter than Haiku and clearly tighter than Opus; both gaps were
artifacts of mixed counting policies.

This is why `PROMPT.md` now specifies a `## FINDINGS INDEX` and defines
*raised* against *survived*.

## Tier Assignments

Scored on GT1 only, per the shipped criteria.

| Reviewer | Stable claims | GT1 recall | Tier |
|---|---:|---|---|
| Haiku | 4 | 2 of 3 | **4** |
| Sonnet | 3 | 3 of 3 | **4** |
| Fable | 8 | 3 of 3 | **4** |
| Opus | 13 | 3 of 3 | **4** |

All four pass. The criteria did not discriminate, and the reason is GT1's
difficulty, not the reviewers' similarity: any reviewer that read the section
found the contradiction. This was pre-registered as the study's main threat
to validity before results were seen.

GT2, which cannot be scored, does discriminate — raised in 0 of 3 Haiku runs,
2 of 3 Sonnet runs, and 3 of 3 for both Fable and Opus. That gradient is the
evidence that a recall test needs defects at graded difficulty rather than
one defect.

## Every Pairing Fails The Test

Stable claims compared claim-level, verdict ignored, per Success Criteria.

| Direction | Stable claims absent from all of the other's runs | Result |
|---|---|---|
| Sonnet → Haiku | none | pass |
| Haiku → Fable | none | pass |
| Haiku → Opus | none | pass |
| Sonnet → Opus | none | pass |
| Haiku → Sonnet | cognitive anchoring undefined | **fail** |
| Fable → Haiku | GT2, Cobra underspecified, W5H1 name | **fail** |
| Fable → Sonnet | cognitive anchoring undefined, W5H1 name | **fail** |
| Opus → Haiku | GT2, Cobra value space, "Quick Start" misnamed | **fail** |
| Opus → Sonnet | anchoring, "Quick Start" misnamed, "Start simple" contradiction, `file:line` vs non-code | **fail** |
| Opus → Fable | "Quick Start" misnamed | **fail** |

Condition 1 requires both directions clear, so **all six pairs fail.**

Three verified absences carry the result. No Sonnet run ever raises that
"cognitive anchoring" is used as a mandatory rule and never defined in the
artifact — though Sonnet performs anchoring correctly throughout. No Haiku
run raises GT2 or Cobra underspecification. No non-Opus run raises that
"Quick Start" is the longest section and contains no runnable step; one Haiku
run affirms the opposite.

The passing directions all point from claim-poor reviewers toward claim-rich
ones. A reviewer with three stable claims can hardly fail in its own
direction. Condition 2 blocks only the zero-claim case; a 3-versus-13
asymmetry passes it. At n=3 that is an observation to record, not yet grounds
to change the criteria.

**The framework issued two contradictory certifications from one dataset.**
All four configurations are "qualified as a calibration counterpart" and no
two of them are calibrated. Tier 4 gates entry to The Test; it does not
predict passing it. [calibration](../calibration.md) now says so.

## Cognitive Anchoring Is Widely Skipped, and Nothing Detects It

Rule 3 forbids claiming "no findings" without describing what a finding would
look like. Counting nothing-found lenses against anchoring lines present:

| Reviewer | r1 | r2 | r3 |
|---|---|---|---|
| Haiku | 5 lenses, **0 anchored** | 2, **0** | 12, **0** |
| Sonnet | 4 / 4 | 10 / 8 | 4 / 2 |
| Fable | 2 / 1 | 2 / 4 | 4 / 3 |
| Opus | 0 (none empty) | 3 / 1 | 0 (none empty) |

Haiku violated rule 3 on every nothing-found lens in all three runs. In every
one of those runs, Nothing-Found Verification then passed.

Haiku r3 is the sharpest case and the third recorded instance of mechanism 5
affirming the error it exists to catch. Its 📌 Truth lens read the defective
table and wrote *"10 lenses: Quick Start (115-125) as summary"* — affirming
the count that GT1 falsifies — then reported no findings. Its 🔗 Provenance
lens reported no findings with no anchoring. Nothing-Found Verification
concluded *"**Provenance:** If a citation were incomplete or wrong, it would
be detected. ✓"* and *"All checks pass."*

The failure was detectable from the run's own text: eight lenses said "no
findings" and the file contained zero anchoring lines. `PROMPT.md` now makes
that check the mechanism's first step — a lens missing its anchoring line has
not produced Output B and is re-run, not verified. This does not make
mechanism 5 sound; it makes one of its failure modes mechanically detectable.
Real seeded-error verification remains unbuilt and on the ROADMAP.

## Impact on Diffract

| Change | Evidence |
|---|---|
| Tier binds to the artifact, not just the instrument | Four configurations, one easy artifact, all tier 4 |
| Tier 4 is necessary, not sufficient, for The Test | All four tier 4; all six pairings fail |
| One ground-truth defect is an upper bound, not a measurement | GT1 saturated; GT2 discriminated |
| "Survives CHECK" defined as raised and not `Discard:Integrity` | Recall for one reviewer varied 0/3 to 2/3 by counting rule alone |
| `## FINDINGS INDEX` required, *raised* vs *survived* defined | Three counting policies across twelve runs |
| Nothing-Found Verification checks anchoring form first | Rule 3 violated in 3 of 3 runs by one reviewer, passed 3 of 3 times |
| Cluster map recorded in results | Stability counts were not independently re-derivable |
| README lens table, `#contributing` anchor, Provenance evidence format | GT1, GT2, and the format drift found while verifying them |

## Limitations

- **n=3 per configuration, one artifact, one Compass, one vendor.** Nothing
  here supports ranking models. "Haiku is unsuitable as a calibration
  counterpart on documentation artifacts" is supported by replication across
  two studies; any finer ordering is not.
- **The tier assignments in this document are already stale.** This release
  changed `PROMPT.md`, and a tier does not carry across instrument versions.
  They are published as a record of the method, not as usable measurements.
- **GT1 was too easy**, and this was known in advance. The study measured the
  criteria's ceiling rather than the reviewers' floor.
- **GT2 cannot be scored** and its recall gradient partly measures Compass
  policy rather than detection: Sonnet raised it twice and judged it
  `Skip:Compass` both times, having verified it against all headings.
- **Clustering is a human judgment.** Several pairwise cells flip between
  pass and fail under finer granularity. Coarse clustering was used, which
  favours passing; the result is that all six pairs fail under the reading
  most generous to them.
- **Harness contamination.** The instrument was renamed to
  `instrument-v0.2.1.md` in the run directory. Four runs mention the name;
  three only in scope lines. One produced a spurious finding — a Haiku run
  reported "PROMPT.md naming inconsistency" between the two names. It is
  excluded from every count here and changes no tier.
- **One run omitted the findings index** the harness required. That was a
  deviation from the experiment's instructions, not from the instrument,
  which had no such requirement at the time. It is the reason the requirement
  now exists.
