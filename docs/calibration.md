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
  CHECK, in a majority of its runs. **Survives** means raised and not
  `Discard:Integrity`; a governor skip still counts, because verdict
  disagreement is expected (see Success Criteria) while failing the evidence
  bar is not. Without this rule the same run set yields different recall
  numbers depending on who counts.

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
four configurations whose run-to-run dispersion differed by roughly 5x all
cleared the same two-line contradiction, and all four measured tier 4. Read a
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
- Result: [calibrated / not calibrated — cycle again]
```
