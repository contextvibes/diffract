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

A review is calibrated when Reviewer B produces **zero stable claims** that
appear in none of Reviewer A's runs. Disagreements on governor *verdicts*
(fix vs skip) are expected — Compass calibration is inherently subjective.
But a *stable* disagreement on findings (whether something IS an issue)
indicates a framework problem. A claim that appears in only one run of
several is noise, not a calibration failure — record it, but do not cycle
on it.

## Recording Results

Document calibration results in your retro:

```markdown
### Calibration Test
- Reviewer A: [name/model] — [N] runs
- Reviewer B: [name/model] — [N] runs
- Same Compass: [yes/no]
- Artifact frozen at: [tag/commit + checksum]
- Findings per run: A [n₁, n₂, …] / B [n₁, n₂, …]
- Stable claims (majority of runs): A [X] / B [Y]
- Stable-claim overlap: [count]
- Stable claims unique to B: [count]
- Result: [calibrated / not calibrated — cycle again]
```
