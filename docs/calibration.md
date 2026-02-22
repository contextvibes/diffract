# Calibration

Calibration is how Diffract validates itself. The framework claims that
the same code + same lenses + different reviewer = same findings. This
claim must be testable.

## The Test

1. **Reviewer A** completes a full Diffract review (PDCA cycle)
2. **Reviewer B** — a different human or AI model — independently reviews
   the same artifact using the same PROMPT.md
3. Reviewer B does **not** see Reviewer A's findings
4. Compare findings:
   - **Overlap:** Both found the same issues → framework is calibrated
   - **A found, B missed:** B's process failed → investigate B's lens application
   - **B found, A missed:** A's process failed → review is incomplete, cycle again
   - **Disagreement:** Same issue, different verdict → governor calibration differs

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
to review. Use the same Compass. Compare findings.

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
Apply all 9 lenses + W5H1. Vet through governors. Provide retro.

At the end, rate each finding's calibration confidence (high/medium/low):
"Would a different reviewer reach the same conclusion?"
```

## Success Criteria

A review is calibrated when Reviewer B produces **zero new findings** that
Reviewer A missed. Disagreements on governor *verdicts* (fix vs skip) are
expected — Compass calibration is inherently subjective. But disagreements
on *findings* (whether something IS an issue) indicate a framework problem.

## Recording Results

Document calibration results in your retro:

```markdown
### Calibration Test
- Reviewer A: [name/model]
- Reviewer B: [name/model]
- Same Compass: [yes/no]
- Findings overlap: [X of Y]
- New findings by B: [count]
- Result: [calibrated / not calibrated — cycle again]
```
