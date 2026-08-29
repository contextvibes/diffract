# Research: Calibration Reproducibility (RQ3)

## Research Question

> Diffract claims that same artifact + same lenses + different reviewer =
> same findings (docs/calibration.md), and Integrity's third sub-principle
> requires that "different reviewers should reach the same conclusion from
> the same evidence" (docs/governors.md).
>
> Does the claim hold in practice — and can the documented calibration
> protocol (two reviewers, one run each) detect it when it does not?

## Method

Ten independent reviews of one frozen artifact, executed by four Claude
models under a byte-identical prompt (only the output path differed).
Every run stopped at CHECK — no fixes — per docs/calibration.md. Counts
below are findings that **survived governor vetting** (each run's FINDINGS
INDEX).

**Frozen inputs** (verified unchanged across all 10 runs):

| Input | Fingerprint |
|-------|-------------|
| `docs/governors.md` @ `bd780e4` (the artifact) | md5 `63bf766c5b1ccc747491c6b595a4ba0b` |
| `PROMPT.md` @ `bd780e4` (the framework) | md5 `1af01c72503a75047d8b91ad1e600f90` |

**Pre-set governors** (identical in every run):

- 🧭 Compass: "Could a reviewer apply these three governors correctly
  without reading any other Diffract document?"
- 🐍 Cobra: library/framework
- ⚖️ Integrity: file:line evidence per lens; cognitive anchoring required

**Two experiments:**

1. **Cross-tier** — the documented protocol: four models
   (Haiku, Sonnet, Fable, Opus), one run each
2. **Within-tier** — the control the protocol lacks: Haiku ×4 and
   Opus ×4, identical runs

## Experiment 1 — Cross-Tier, One Run Each

| Reviewer | Surviving findings |
|----------|-------------------:|
| Haiku | 3 |
| Sonnet | 7 |
| Fable | 9 |
| Opus | 18 |

Read alone — and this is exactly what the documented protocol produces —
this is a clean monotonic tier effect: the strongest reviewer reports 6x
the findings of the weakest.

## Experiment 2 — Within-Tier, Four Identical Runs

| Reviewer | Findings per run | Mean | Range | CV |
|----------|------------------|-----:|------:|---:|
| Haiku | 3, 4, 1, 0 | 2.0 | 0–4 | 0.91 |
| Opus | 18, 14, 23, 15 | 17.5 | 14–23 | 0.23 |

CV = sample standard deviation / mean.

**Recurrence separates the tiers; raw counts do not.** Clustering
equivalent claims across each reviewer's four runs: at least nine Opus
claim clusters recur in 3 or more of 4 runs. No Haiku claim recurs in more
than 2 of 4 runs — zero Haiku claims meet the 3-of-4 bar.

**Detection of the one verified factual error** in the artifact (Bounded
Rationality attributed to Kahneman instead of Simon, frozen artifact
line 11 — fixed in PR #6):

| Reviewer | Raised | Survived CHECK |
|----------|--------|----------------|
| Haiku | 0 of 4 runs | 0 of 4 |
| Sonnet | 1 of 1 | 1 of 1 |
| Fable | 1 of 1 | 1 of 1 |
| Opus | 4 of 4 | 3 of 4 (one run Compass-skipped it) |

Haiku run 4 returned **zero findings** on a document containing that
verified factual error — after running Nothing-Found Verification
(mechanism 5, see RQ2) and concluding its process was sound. The
mechanism verifies that the reviewer *believes* it looked; it does not
verify that looking would have found anything.

## The Reproducibility Claim Is Falsified

The claim fails at a level stricter than it is stated. The framework
requires different reviewers to reach the same conclusion from the same
evidence. These runs show the **same** reviewer — same model, same
evidence, byte-identical prompt — reaching different conclusions: Haiku
ranged from "artifact is sound, zero findings" to four findings across
identical runs, and no two of the ten runs produced the same finding set.

## The Methodological Finding

The documented protocol — two reviewers, one run each — **cannot
distinguish "Reviewer B is miscalibrated" from run-to-run noise**, because
with n=1 per reviewer there is no estimate of either reviewer's own
variance.

This is not theoretical. Experiment 1 ran exactly the documented protocol,
produced the 3-vs-18 split, and supported a "6x tier effect" conclusion.
Experiment 2 then showed that Haiku alone spans 0–4 across identical runs
— a range that could have produced the low side of that split with no tier
difference at all. The protocol as documented would have let the wrong
conclusion stand.

The signal that does survive noise is **recurrence**: 9+ stable Opus
clusters against 0 stable Haiku clusters is a far sharper separation than
18 findings against 3. docs/calibration.md has been updated accordingly:
minimum 3 runs per reviewer, claims scored on recurrence across runs, and
single-pair overlap dropped as the success criterion.

## High-Recurrence Findings (design input)

Clusters recurring in ≥3 of 4 Opus runs. Line numbers refer to the frozen
artifact (`bd780e4`).

| Claim cluster (docs/governors.md) | Opus runs (of 4) |
|-----------------------------------|-----------------:|
| Cobra levels and the `file:line` rule are stated in code-only terms; non-code artifacts have no defined mapping (:71–79, :103) — found by all four tiers | 4 |
| No verdict vocabulary and no precedence/combination rule when the three governors disagree (:3–4) | 4 |
| "Must be explicitly agreed upon by all reviewers" (:6–7) has no solo, async, or automated path — a rule all 10 runs violated by construction | 4 |
| Integrity "Prevents: manipulation" (:99) names no mechanism against an adversary | 4 |
| Load-bearing terms undefined in-file: "lenses", "PLAN phase", "cognitive anchoring", "Ascension" | 4 |
| Nothing requires recording which governor rejected which finding, so the reproducibility claim (:111–112) is unmeasurable from a review's own output | 4 |
| "Calibration" carries 3–5 distinct meanings in one file | 4 |
| Prototype states a *sufficient* skip condition while Production and Library/Framework state *necessary* ones, so the levels are not parallel rules (:73–77) | 3 |
| ">30 minutes to fix" (:73) is reviewer-dependent — exactly the non-falsifiable criterion Integrity forbids (:109–112) | 3 |
| Bounded Rationality attributed to Kahneman, not Simon (:11) | 4 raised, 3 survived |

## Impact on Diffract

| Experiment finding | Diffract change |
|--------------------|-----------------|
| Kahneman misattribution, Cobra template drift, duplicated version string | Fixed in PR #6 |
| Calibration Template silently drops the Integrity default (:103 vs :124) | Template now points at the default |
| Integrity's Questions and Sub-Principles are the same three ideas, unmarked | The 1:1 correspondence is now stated |
| Cobra Effect anecdote asserted as history with no source | Now labeled a widely told but undocumented illustration |
| Cobra's Calibration field was a stub ("Context-dependent.") | Now directs the reviewer to the levels block |
| One run per reviewer cannot separate reviewer effect from noise | docs/calibration.md: ≥3 runs per reviewer, recurrence scoring |
| Nothing-Found Verification passed on a zero-finding run that missed a real error | Open — mechanism 5 needs a seeded-error variant (see RQ2, blind seeding) |
| Verdict vocabulary, governor precedence, solo/async path, per-finding vet record | Open — design questions, not one-line fixes |

## Limitations

- **Small sample:** n=4 runs per tier, two tiers, one artifact, one
  prompt, one Compass. The statistics describe this experiment, not the
  models in general.
- **One vendor:** all four reviewers are Claude-family models
  (Haiku, Sonnet, Fable, Opus). Cross-vendor reproducibility is untested.
- **One artifact type:** a 125-line prose document. Code artifacts, where
  more lenses are deterministic, may show less variance.
- **Sonnet and Fable ran once each**, so their within-tier variance is
  unmeasured; only Haiku and Opus have repeat data.
- **Claim clustering is judgment.** Deciding that two differently worded
  findings are "the same claim" is exactly the kind of unfalsifiable step
  the framework warns against; the cluster counts above carry that caveat.
- **One naturally occurring error**, not a seeded set, anchors the
  detection table — a single-item probe, unlike RQ2's blind-seeding
  designs.
