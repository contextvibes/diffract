# Calibration

Calibration is how Diffract validates itself. The framework claims that
the same code + same lenses + different reviewer = same findings. This
claim must be testable.

## The Test

1. **Freeze the artifact** (git tag or checksum) — every run must see the
   exact same bytes
2. **Reviewer A** completes at least **3 independent runs** (same prompt,
   same Compass, identical instructions)
3. **Reviewer B** — a different human or AI model — completes the same
   number of independent runs of the same artifact using the same PROMPT.md
4. No run sees any other run's findings, and neither reviewer sees the
   other's
5. Within each reviewer, cluster equivalent claims across runs. A claim is
   **stable** for a reviewer when it recurs in a majority of that reviewer's
   runs
6. Compare **stable claims**, not single runs:
   - **Overlap:** Both reviewers' stable claims match → framework is calibrated
   - **Stable for A, absent in all of B's runs:** B's process failed →
     investigate B's lens application
   - **Stable for B, absent in all of A's runs:** A's process failed →
     review is incomplete, cycle again
   - **Same stable claim, different verdict:** governor calibration differs

**Why multiple runs:** one run per reviewer cannot distinguish "Reviewer B
is miscalibrated" from run-to-run noise. Measured on a frozen 125-line
artifact (`docs/governors.md` @ `bd780e4`): the same model, same prompt, and
same Compass produced 0–4 surviving findings across four runs of one
reviewer, and 14–23 across four runs of another. In the same experiment a
one-run comparison (3 vs 18) read as a reviewer effect — yet the low
reviewer's own range (0–4) could produce that split with no reviewer
difference at all. Raw overlap of a single pair measures noise; recurrence
across runs measures the reviewer. See
[RQ3](research/rq3-calibration-reproducibility.md) for the full experiment.

**Important:** Calibration tests stop at CHECK. Do not proceed to LEARN (fix).
Fixing changes the artifact, which invalidates the comparison. Both reviewers
must see the exact same artifact in the exact same state.

## When to Run

- Before publishing a review as final
- When adopting Diffract in a new team (establish baseline)
- After major framework updates (validate changes didn't break calibration)

## Smoke Test (before calibration)

Before running a full calibration test, the **original reviewer** re-reads
PROMPT.md and follows it literally — as if seeing it for the first time.

This is NOT calibration (same person = same biases). It catches a different
class of problems:

- **Ambiguous instructions** — if the author can't follow their own prompt,
  no one else can
- **Prior-knowledge dependencies** — if you need to use knowledge you have
  from building the artifact (not from the prompt text), the prompt is
  incomplete. Flag it.
- **Missing steps** — the prompt says "do X" but doesn't say how

The smoke test answers: *"Is this prompt self-contained?"*
Run the smoke test first. Fix any gaps. Then freeze and calibrate.

## How to Run (AI)

Copy PROMPT.md into a different AI model's context along with the artifact
to review. Use the same Compass. Repeat with an identical prompt until each
reviewer has at least 3 independent runs — a single run cannot be told apart
from noise (see The Test). Compare stable claims.

For large codebases, scope the review to a specific module or set of files.
Both reviewers must review the **same scope** — calibration requires
identical inputs.

**Important:** Both reviewers must see the exact same artifact. If the
artifact changes between Reviewer A and Reviewer B (e.g., during PDCA
cycles), freeze a snapshot (git tag, copy) before the calibration test.

### Template

```
Read the review framework below and follow it exactly.

This is a calibration test: a previous reviewer has already completed a full
review using the same framework. Your findings will be compared to theirs.
Keep reviews independent — don't share findings beforehand.

[PASTE PROMPT.md HERE]

---

Artifact to review:

[PASTE CODE / DOCS HERE]

---

Use this Compass: "[SAME COMPASS AS REVIEWER A]"
Do not wait for confirmation — proceed directly (async review).
Apply all 10 lenses + W5H1. Vet through governors. Provide retro.

At the end, rate each finding's calibration confidence (high/medium/low):
"Would a different reviewer reach the same conclusion?"
```

## Success Criteria

A review is calibrated when **both** conditions hold:

1. **Both directions clear.** No stable claim of either reviewer is absent
   from all of the other reviewer's runs. Check A against B *and* B against
   A — a one-directional check certifies a reviewer who found nothing.
2. **Both reviewers produced stable claims.** A reviewer whose own claims
   never recur across its own runs has not been shown to agree with anyone;
   it has been shown to be unreliable. Zero stable claims is a failed run
   set, not a passing score. Re-run, or replace the reviewer.

Disagreements on governor *verdicts* (fix vs skip) are expected — Compass
calibration is inherently subjective. But a *stable* disagreement on
findings (whether something IS an issue) indicates a framework problem. A
claim that appears in only one run of several is noise, not a calibration
failure — record it, but do not cycle on it.

**Why condition 2 exists.** The criterion shipped in v0.2.0 tested one
direction only: calibrated when B produced zero stable claims absent from
A's runs. Replay [RQ3](research/rq3-calibration-reproducibility.md) against
it. Reviewer B produced *zero stable claims at all* — nothing recurred in a
majority of its four runs — while nine of Reviewer A's stable claims were
absent from every single B run, including a verified factual error B never
raised once. The one-directional rule returns **calibrated**. Step 6 of The
Test, on the same page, returns **B's process failed**. A criterion that
contradicts its own comparison table, and that the weakest reviewer passes
by finding nothing, measures nothing.

## Estimating What Both Reviewers Missed

The Test measures *agreement*, and agreement cannot say how much both
reviewers missed — two reviewers sharing a blind spot agree perfectly (see
Reviewer Tiers, tier 3 on both sides). Capture–recapture turns the same
overlap data into an estimate of the total defect population. The method is
Lincoln–Petersen estimation from ecology, applied to software inspections by
Eick et al. (1992); driving the exit decision from an estimate of *remaining*
defects, rather than from the reviewer running dry, is the exit discipline of
Gilb & Graham, *Software Inspection* (1993).

With Reviewer A raising `n_A` stable claims, Reviewer B raising `n_B`, and
`m` of them shared:

```
estimated total    N̂ ≈ n_A × n_B / m
missed by both       ≈ N̂ − (n_A + n_B − m)
```

For small counts, prefer the Chapman correction, which is less biased when
`m` is in the single digits:

```
N̂ = ((n_A + 1)(n_B + 1) / (m + 1)) − 1
```

**Illustration** (numbers chosen for arithmetic, not measured — RQ5's
published tables record claims *absent from all* of the other reviewer's
runs, which is not the same quantity as stable-claim overlap, so `m` cannot
be recovered from them): with `n_A = 8` and `n_B = 11` stable Major claims
and `m = 6` shared, N̂ ≈ 14.7 — the pair together raised 13 distinct claims,
so roughly 2 Majors are estimated to have been missed by both. That number,
not zero-new-findings, is what the Exit Estimate in `PROMPT.md` (LEARN)
reports when calibration data exists.

**Caveats — each one biases the estimate, and each is checkable:**

1. **Independence is assumed and never holds between LLM reviewers.** The
   estimator assumes finding a defect in run A says nothing about finding it
   in run B. Models sharing training data share blind spots, which inflates
   `m` and drives N̂ *down*. Treat N̂ as a **lower bound** on the total, and
   prefer maximally different reviewer configurations (see Reviewer Tiers
   for what a configuration is).
2. **Counts depend on clustering granularity.** `n_A`, `n_B`, and `m` all
   move with how claims are clustered (RQ5 notes its stable-claim counts do
   exactly this). The cluster map in the recording template below is what
   makes an estimate auditable; an estimate without its cluster map is a
   number without an instrument.
3. **Estimate Majors only.** Severity is defined in `PROMPT.md` (DO) — that
   definition is authoritative and is not restated here. Without the
   severity split, minor-flooding dominates both `n` values and the estimate
   measures verbosity, not defects.
4. **Single-digit `m` has wild variance.** Read such an estimate as an
   order-of-magnitude signal, not a measurement.

Capture–recapture and the seeded-error variant on the
[ROADMAP](../ROADMAP.md) attack the same gap — RQ3's finding that the
self-check cannot detect its own misses — from opposite sides: estimation
says *how many* defects remain, ground truth says *which one* was missed.
Neither substitutes for the other.

## Scoring Confidence (Brier)

The Findings Index's `Confidence` column is a forecast: each bin carries a
canonical probability — normative in `PROMPT.md` (Findings Index section),
not restated here — that the finding **survives** vetting, with *survives*
as defined there: raised and not `Discard:Integrity`. That makes Confidence
scoreable. The **Brier score** (Glenn W. Brier, 1950; the judgment-calibration
practice of Philip Tetlock's forecasting work) is the mean squared error of
those forecasts:

```
BS = mean((p − outcome)²)     outcome: 1 = survived, 0 = discarded
```

0 is perfect; 0.25 is what always answering 50% earns; lower is better.

**Resolution rule.** An outcome counts as resolved when the vetting was not
performed by the finder — the counterpart reviewer in a calibration pair, or
maintainer vetting of a fresh-context run. Self-vetted outcomes are
scoreable but must be flagged as such: a reviewer grading its own forecasts
can inflate its score.

**Report the per-bin table, not just the score.** Discards are rare (1 in
37 findings across the v0.2.x self-review cycles), so the base rate is
heavily skewed and a single pooled number rewards answering High every
time. The per-bin resolution table is what exposes mis-calibration.

### Worked example — v0.2.x self-review, cycles 3–5

Three fresh-context reviewer runs against the instrument repository, all
outcomes resolved by maintainer vetting (not the finder — the resolution
rule above holds). 37 findings raised; 1 discarded.

| Confidence | canonical p | n | resolved true | rate | per-bin Brier |
|------------|-------------|---|---------------|------|---------------|
| High       | 0.95        | 28 | 28 | 1.00 | 0.0025 |
| Medium     | 0.75        | 8  | 8  | 1.00 | 0.0625 |
| Low        | 0.40        | 1  | 0  | 0.00 | 0.1600 |

The `canonical p` values are inputs copied from `PROMPT.md`, where they are
normative; this table does not define them. Pooled Brier: **0.0197**
(per cycle: 0.0125 / 0.0256 / 0.0210).

What the table says that the pooled score hides:

- **Medium resolved 8 of 8.** As used, Medium behaves like ~1.0, not 0.75 —
  the reviewers were underconfident at Medium, or the bin's probability
  needs recalibration. The Medium bin alone contributes more total error
  (0.50) than the other two bins combined.
- **The pooled score barely beats the degenerate strategy.** Answering High
  on all 37 findings would score 0.0268 against the actual 0.0197 — with a
  97% survival base rate, the pooled number can barely distinguish
  calibration from flattery. The per-bin table can.
- **Low has n = 1.** Its 0-of-1 resolution is directionally consistent with
  p = 0.4 and evidentially nearly worthless.

**Caveats:** n is small; the base rate is skewed (see above); and
resolution-by-vetting measures evidence quality, not ground truth — a wrong
finding that survives vetting still scores as a success. The frozen-tag
capture–recapture runs queued in
[issue #29](https://github.com/contextvibes/diffract/issues/29) will
provide stricter resolution when they exist.

## Reviewer Tiers

A **reviewer tier** is a measured property of a *reviewer configuration*, not
a vendor's product name. A configuration is the model, its version, its
settings, the version of `PROMPT.md` it ran, and the artifact it was measured
against (identity + checksum). Change any of the five and the tier must be
re-measured — a tier assigned against one instrument does not carry to the
next, and a tier assigned against one artifact does not carry to another.

A tier is a statement about a configuration *on an artifact*, never a
property of a model. Reported without its artifact, a tier number means
nothing.

Tiers are assigned from two criteria, both already defined on this page:

- **Stability** — the reviewer produces at least one stable claim across at
  least 3 of its own runs (Success Criteria, condition 2).
- **Ground-truth recall** — on an artifact containing an independently
  verified defect, the reviewer raises that defect *and* the claim survives
  CHECK, in a majority of its runs. **Survives** is defined in
  [PROMPT.md](../PROMPT.md)'s Findings Index section and is used here
  unchanged — deliberately not restated, because this file once defined it
  differently from PROMPT.md and the two disagreed by an order of magnitude
  on the same run set.

|  | Recall passes | Recall fails |
|---|---|---|
| **Stable** | **Tier 4** — qualified as a calibration counterpart | **Tier 3** — repeatable, and repeatably wrong: it misses the same defect every run |
| **Unstable** | **Tier 2** — sees the defect, cannot be relied on to see it again | **Tier 1** — output is noise; unusable on either side of a calibration pair |

Tier 4 is the only tier qualified to serve as Reviewer A or Reviewer B in
The Test. Tiers 2 and 3 each fail one criterion; which failure is worse has
not been measured, so the numbering between them is a slot label, not a
ranking.

**Tier 4 is necessary, not sufficient.** It gates entry to The Test; it does
not predict passing it. In [RQ5](research/rq5-reviewer-tiering.md) all four
configurations measured tier 4 on the same artifact, and every one of the six
pairings then failed Success Criteria condition 1. Qualifying two reviewers
does not mean they will agree.

**Why Success Criteria does not already cover this.** Those criteria measure
*agreement*, not correctness. Two stable reviewers that share a blind spot
agree with each other perfectly and are certified calibrated, while both miss
the same defect on every run — tier 3 on both sides. Ground-truth recall is
the axis that agreement cannot supply.

**What tiering requires.** Ground-truth recall needs an artifact carrying at
least one defect verified independently of the reviewers being tested. One
defect is a floor for *assigning* a tier, not for *trusting* one. A single
self-contained defect saturates: in [RQ5](research/rq5-reviewer-tiering.md)
four configurations ranging from 3 to more than 11 stable claims each — and
differing sharply in whether they followed the instrument at all — cleared the
same two-line contradiction, and all four measured tier 4. Read a
tier measured against one defect as an upper bound. Separating the tiers
needs several independently established defects at graded difficulty — the
reference artifact set on the [ROADMAP](../ROADMAP.md).
[RQ3](research/rq3-calibration-reproducibility.md) used a defect found after
the fact — sound, but not repeatable on demand, and a published ground truth
degrades as soon as reviewers can read it. A designed reference set is on the
[ROADMAP](../ROADMAP.md). Until one exists, tiers can only be assigned
against artifacts whose defects were established by some means other than the
review under test.

**Assignments measured so far:**
[RQ3](research/rq3-calibration-reproducibility.md) placed two reviewers and
left two unplaced, bound to `PROMPT.md` @ `bd780e4`.
[RQ5](research/rq5-reviewer-tiering.md) placed four at tier 4, bound to
`PROMPT.md` v0.2.1 @ `9cb9cf2` and to `README.md` @ `22926ec`. Both sets are
**stale**: this release changed `PROMPT.md` again. Every tier on this page
must be re-measured before it is relied on — which is the rule in the
definition above doing its job, not an oversight.

## Recording Results

Document calibration results in your retro:

```markdown
### Calibration Test
- Reviewer A: [name/model + version] — [N] runs — tier [1-4 / unplaced] on [artifact]
- Reviewer B: [name/model + version] — [N] runs — tier [1-4 / unplaced] on [artifact]
- Instrument: PROMPT.md [version] + checksum
- Ground-truth defect in artifact: [yes, verified by X / no — tiers not assignable]
- Same Compass: [yes/no]
- Governors: [agreed (human-confirmed) / declared (async, tagged)]
- Artifact frozen at: [tag/commit + checksum]
- Findings per run: A [n₁, n₂, …] / B [n₁, n₂, …]
- Stable claims (majority of runs): A [X] / B [Y]
- Cluster map: [cluster → the run-local finding IDs it groups, per reviewer]
- Stable-claim overlap: [count]
- Stable claims of A absent from all B runs: [count]
- Stable claims of B absent from all A runs: [count]
- Estimated total Majors (capture–recapture, Majors only): [N̂ / n/a — see
  Estimating What Both Reviewers Missed]
- Estimated missed by both: [count / n/a]
- Brier score (per-bin table attached): A [x] / B [y]
- Result: [calibrated / not calibrated — cycle again]
```
