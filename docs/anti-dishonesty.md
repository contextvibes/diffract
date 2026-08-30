# Anti-Dishonesty Mechanisms

Diffract assumes that reviewers — human and AI — will fail. Not out of
malice, but because of cognitive fatigue, confirmation bias, time pressure,
and social dynamics. The framework makes dishonesty structurally difficult
through 13 concrete mechanisms, each adapted from a high-stakes industry
where inspection failures have life-or-death consequences.

## What these mechanisms can and cannot detect

Every mechanism below is run **by the reviewer, about the reviewer, in the
reviewer's own output.** That is the shape of self-attestation, and it bounds
what the set can do. These are honesty aids for a reviewer that is trying to be
honest — they raise the cost of drifting into a false claim. They do not detect
an incompetent reviewer, and they do not detect an adversarial one.

The defect record is explicit about this, and every entry in it was caught from
outside the review, never by the review:

- A reviewer wrote the planted defect into its own cognitive-anchoring example
  and then reported the lens clean — 4 of 4 runs (mechanism 5).
- A reviewer raised a `Fix` at High confidence about a sentence that exists only
  in `PROMPT.md` and never in the artifact, and its own Context Fidelity check
  affirmed it (mechanism 9).
- Three runs stated Scorecard counts contradicting their own findings index,
  including two `Discard:Integrity` verdicts appearing in no row.

As of v0.4.0, four of the thirteen are no longer purely self-attested:

- **Mechanisms 1, 2 and 9** can be checked from outside by
  [`scripts/check_review.py`](../scripts/check_review.py) — lens coverage,
  anchoring form, count reconciliation against the findings index, and whether
  quoted text appears verbatim at the line it is cited to. It checks **form and
  fidelity, not judgment.** It can prove a quote is real; it cannot tell you the
  finding was worth raising, and it cannot tell you what the reviewer missed.
- **Mechanism 5** has a real seeded variant in [`calibration/`](../calibration/):
  defects planted in a frozen artifact and a reviewer scored against an answer
  key it has not seen. That measures recall directly instead of asking the
  reviewer whether it thinks it would have noticed.

The other nine remain self-attested. So does the decision to run the checker at
all: a reviewer that never runs it, or runs it and ignores the result, is
governed by nothing on this page.

## The Mechanisms

### 1. Evidence (Proof of Observation)

**Source:** Aviation maintenance — RFID scanning forces physical presence
at the inspection site before a task can be signed off.

**In Diffract:** Every lens must produce `file:line` evidence or an explicit
list of what was checked. A claim of "all clean" without evidence is invalid.

Invalid by enforcement, not only by instruction: `check_review.py` requires a
`Checked:` line on every lens, and — when the run's ⚖️ Integrity governor asks
for verbatim quotes — matches each quote against the cited artifact at the cited
line range.

### 2. Cognitive Anchoring (Shisa Kanko)

**Source:** Japanese railways and nuclear control rooms — operators must
physically point at each indicator and verbally call out its state. This
engages motor, visual, auditory, and verbal processing simultaneously,
breaking the "looking without seeing" failure mode.

**In Diffract:** When a lens produces no findings, the reviewer must describe
what a finding **would** look like.

```markdown
### 🎯 Variety
Checked: all switch/match statements on HTTP status codes
A finding would look like: a status code reaching the default branch
that should have explicit handling (e.g., 503 for retry logic).
No findings matching this pattern.
```

**"No findings" without cognitive anchoring is not allowed.** This is checkable
and now checked: `check_review.py` fails a review whose nothing-found lens omits
the anchoring line or its closing sentence.

What it demonstrates is narrower than it looks. Across 22 runs every
nothing-found lens carried its anchor — 48 of 48, with one reviewer going from 0
of 12 to 17 of 17 — and recall did not move. Many anchors are generic templates
reusable on any document. Anchoring is evidence that the reviewer engaged the
lens; it is not evidence that the artifact was read, and mechanism 5 records a
case where writing the anchor fixed the reviewer's error as the standard of
correctness. See issue #24.

### 3. Falsifiability

**Source:** Philosophy of science (Karl Popper) — a claim is only valid if
it can be disproven.

**In Diffract:** Every finding must be grounded in an objective, measurable
criterion. "This variable is never read" is falsifiable (grep the codebase).
"This variable name feels wrong" is not falsifiable and should be discarded
unless the reviewer can explain **what** it should be called and **why**.

### 4. Calibration (Peer Review / Cross-Check)

**Source:** Metrology (measurement science) + Radiology (dual-reading) —
two independent radiologists read the same images. The final report only
proceeds when both findings are reconciled.

**In Diffract:** A different reviewer applying the same lenses to the same
code should reach the same conclusions. This is not aspirational — it's
testable.

**Calibration Test:** After a review is complete, a second reviewer
(human or AI at the same capability level) independently applies the same
lenses. Each reviewer completes at least 3 runs against a frozen artifact,
and the comparison is on **stable claims** — those recurring in a majority
of a reviewer's own runs. Calibrated requires both directions to be clear
*and* both reviewers to have produced stable claims; a reviewer whose
claims never recur has a failed run set, not a passing score. One run per
reviewer cannot separate a miscalibrated reviewer from noise
(see `calibration.md`).

### 5. Nothing-Found Verification (Blind Seeding)

**Source:** Three independent domains:
- **UXO clearance** — inert munitions secretly buried in grids before sweep
  teams arrive. If a team declares a grid "clear" but misses a planted seed,
  the entire grid is resurveyed.
- **Radiology** — slides with known abnormalities mixed into daily screening
  queues. If a pathologist misses one, thresholds are recalibrated.
- **Legal e-discovery** — pre-coded documents seeded into review pools. If
  reviewers miss them, the algorithm is retrained.

**In Diffract:** After a "nothing found" round, ask: *"If I deliberately
introduced a bug in this lens's domain, would my process have caught it?"*
If not, the process failed — not the code.

**Known limitation — this is not blind seeding.** In all three source
domains a *third party* plants a *real* defect and the reviewer is not told.
Diffract's version has none of the three: the reviewer imagines a
hypothetical bug, in a domain of its own choosing, and grades its own
process. The faculty that answers *"would I have caught it?"* is the faculty
that just missed it.

[RQ3](research/rq3-calibration-reproducibility.md) measured this. The frozen
artifact contained one verified misattribution — Bounded Rationality credited
to Kahneman rather than Herbert Simon. Every reviewer that caught it filed it
under 🔗 Provenance (4 Opus runs, Sonnet, Fable — 6 of 6), so the lens that
owned the defect is not in dispute. Across four Haiku runs it was never
raised, and the verification step never registered the miss:

- **Run 1** wrote the error into its own cognitive-anchoring example — *"A
  finding would look like: A claim about 'Bounded Rationality' with no
  indication that Kahneman is the originator"* — and then: *"No findings
  matching this pattern."* Anchoring made the miss more certain, not less. It
  fixed the false attribution as the standard of correctness.
- **Run 3** recorded the false claim as a verification result: *"'Kahneman'
  (line 11): Explicitly named; 'Bounded Rationality' is Kahneman's
  framework."*
- **Run 4** read line 11, judged it only for missing publication details,
  reported nothing on all ten lenses, then attested *"Lens 7 (Provenance):
  Would catch missing attribution. ✓"* and closed with *"Process is sound.
  All bugs would be caught if present."*

A reviewer holding a false belief imagines a seeded bug that its belief
system can detect. The mechanism therefore cannot fail its own audit: it
verifies that the reviewer *believes* it looked, not that looking would have
found anything. Read it as a self-attestation.

As shipped in `PROMPT.md`, this mechanism does not do what its source domains
do, and the "(Blind Seeding)" in its title describes the source, not the
implementation.

**A real seeded variant now exists alongside it.** [`calibration/`](../calibration/)
holds a frozen artifact with defects planted in it, an answer key the reviewer
never sees, and `scripts/score_seeds.py` to match findings against it — the UXO
grid, not the reviewer's opinion of the grid. The first run scored 4 of 4, with
the review of the *clean* copy of the same artifact scoring 0 of 4 as a negative
control.

Two things it does not fix. It is a **separate procedure**, not a repair of the
in-review question above: a reviewer working from `PROMPT.md` alone still grades
its own process. And one fixture at one difficulty is not a calibration curve —
`calibration/results.md` records what the run does not say.

### 6. Challenge-Response

**Source:** Aviation Crew Resource Management (CRM) — the monitoring pilot
reads the challenge ("Landing Gear"), the flying pilot must physically verify
and verbally respond ("Down and Green"). This creates mutual verification
that nullifies single-person dominance.

Also related: the **Sterile Cockpit Rule** — below 10,000 feet, all
non-essential conversation is banned to protect cognitive bandwidth during
critical phases.

**In Diffract:** In panel reviews, the monitoring panel must actively
challenge each lens's conclusions. Not "I agree" — but "I see your evidence;
I challenge on X." Passive agreement is not allowed.

### 7. Finder/Decider Separation

**Source:** Aviation — Required Inspection Items (RII). The mechanic who
performs a repair is legally barred from signing off on the inspection. An
independent inspector, reporting to a separate management chain, must
validate the work.

**In Diffract:** Lenses find issues. Governors decide whether to fix them.
The reviewer who identifies a finding does not unilaterally decide its
disposition — the governors (Compass, Cobra) make that determination.

### 8. Retro

**Source:** Continuous improvement (Deming, Toyota Production System)

**In Diffract:** After every review cycle, ask:
- What did the framework miss?
- Were we honest?
- Should the framework itself be updated?

The framework evolves through its own PDCA cycle.

### 9. Context Fidelity (Anti-Confabulation)

**Source:** Pharmaceutical manufacturing — Certificate of Analysis (CoA)

Every batch of medication ships with a CoA proving the specific batch was
tested. The certificate is tied to the batch, not a template.

**In Diffract:** After DO, verify that every finding citing file:line actually
contains what you claim. If you cannot re-read (no tool access), flag the
finding as `[unverified]`.

**Known limitation — self-verification has failed this test.** A reviewer raised
a `Fix` at High confidence about the sentence *"This file is self-contained"*,
which appears nowhere in the artifact and only in `PROMPT.md` itself. Its own
Context Fidelity check then affirmed the fabrication. The faculty that re-reads
is the faculty that misread. Checking a quote against the artifact is mechanical
work and now runs mechanically: `check_review.py` verifies that quoted text
appears verbatim at the line it is cited to. See issue #21.

**Prevents:** Tool hallucination, stale context, confabulated evidence — when
the quote check is run. Unrun, it prevents none of them.

### 10. Chunked Attestation (Anti-Degradation)

**Source:** Aviation — Crew Duty Time Limits

Pilots are legally required to stop after a certain number of hours. The
mechanism isn't "try harder" — it's "stop and hand off."

**In Diffract:** If the artifact exceeds your working capacity, partition it.
Each partition gets its own DO phase. State partition boundaries in PLAN.
Findings from partition boundaries (cross-file issues) get a dedicated pass.

**No executable form ships.** `PROMPT.md` does not mention partitioning, so
the procedure above cannot be followed by a reviewer working from the
self-contained prompt. A specification was drafted and rejected in review:
"working capacity" has no operational definition, the boundary kinds have no
precedence rule, and the isolation requirement is unfollowable for a reviewer
in a single context — the mode this mechanism exists for. The mechanism's own
source is "stop and **hand off**", which implies a fresh context per
partition; specifying that is tracked on the ROADMAP. Until then, treat this
as source material, not as an instruction you can execute.

**Prevents:** Nothing, as shipped. Model degradation at long contexts and
diminishing thoroughness are what a partitioning procedure would address.

### 11. Tool Verification (Anti-Tool-Hallucination)

**Source:** Legal — Chain of Custody

Physical evidence must have an unbroken documented chain from collection to
courtroom.

**In Diffract:** When citing tool output as evidence, include the command run
and a representative snippet of raw output. If tool execution cannot be
independently verified, flag findings as `[tool-unverified]`.

**Prevents:** Hallucinated tool output, fabricated scan results.

### 12. Adversarial Decoupling (Blind Review)

**Source:** Double-Blind Clinical Trials (Medicine) + Independent Red Teaming (Cybersecurity)

In medicine, double-blind trials prevent both the administrator and recipient from knowing who receives the active drug, neutralizing placebo-by-proxy and observer bias. In cybersecurity, red teams operate without prior relationship to the engineering group to prevent professional or emotional captivity.

**In Diffract:**
1. **Source-Attribution Blindness:** Code reviews must be performed without knowing whether the code was human-written or AI-generated. All code is scrubbed of attribution (author names, AI generator signatures, or prior chat history) before the review begins.
2. **Calibration Challenge:** Before reviewing the target code, the reviewer completes a brief code snippet carrying a seeded critical bug in the same domain, forcing a mental "cold start" that resets the cognitive baseline to actively expect errors. This is **not** the Cold-Start Calibration in `PROMPT.md` — that one has the reviewer write 2-3 domain invariants before reading code (rule 8), ships, and is required. This one is a research-derived design from RQ2: no challenge set exists, and nothing generates one.
3. **Friction-Enforced Critique:** If a review results in zero rejections or accepts a sequence of suggestions without critique, a mandatory "Devil's Advocate" phase is triggered. The reviewer is required to explicitly document at least one architectural trade-off or sub-optimal decision in the accepted code.

**Prevents:** Algorithmic Stockholm Syndrome (Cognitive Captivity), automation bias, sycophantic validation, and cognitive complacency.

### 13. Golden Hammer Neutralization (Domain Decoupling)

**Source:** Systems biology and thermodynamics — cellular organelles (like mitochondria) are specialized structures optimized for specific cellular environments, but they must follow universal thermodynamic principles (minimizing waste heat/entropy, maximizing metabolic throughput). No biological entity builds complex internal structures unless there is an absolute selective advantage (subtraction by natural selection).

**In Diffract:** Reviewers (especially AI) must justify architectural recommendations and criticisms using universal, non-language-specific systems principles (such as energy minimization, Shannon entropy, Conway's Law, or evolutionary subtraction) rather than tech-stack jargon (e.g., "Go DDD," "React best practices," "Clean Architecture template").

If a reviewer suggests adding a wrapper, interface, abstraction, or helper, they must answer:
1. *What thermodynamic/informational entropy is reduced by this addition?*
2. *How does the energy cost of maintaining this abstraction compare to the raw cost of the duplication or simple direct implementation?*

Any finding based purely on "best practice" dogmatism without a universal systems-level justification must be discarded.

**Prevents:** Tech Stack Bias (Golden Hammer effect), over-abstraction, framework dogmatism, AI training-set gravity.

---

## Summary Table

| # | Mechanism | Source Industry | What It Prevents | Checked by |
|---|-----------|----------------|-----------------|-----------|
| 1 | Evidence | Aviation (RFID) | Claims without observation | External — `check_review.py` |
| 2 | Cognitive Anchoring | Railways (shisa kanko) | Looking without seeing | External — `check_review.py` |
| 3 | Falsifiability | Philosophy (Popper) | Opinion disguised as fact | Self-attested |
| 4 | Calibration | Metrology + Radiology (dual-reading) | Reviewer-dependent outcomes | Self-attested |
| 5 | Nothing-Found Verification | UXO / Radiology / Law | Unexamined "nothing found" claims — **not** false negatives; see the limitation under mechanism 5 | External — `calibration/` |
| 6 | Challenge-Response | Aviation (CRM) | Passive agreement | Self-attested |
| 7 | Finder/Decider Separation | Aviation (RII) | Conflict of interest | Self-attested |
| 8 | Retro | Manufacturing (Deming) | Framework stagnation | Self-attested |
| 9 | Context Fidelity | Pharma (CoA) | Tool hallucination, confabulated evidence | External — `check_review.py` |
| 10 | Chunked Attestation | Aviation (duty limits) | Nothing — no executable form ships; see mechanism 10 | Nothing ships |
| 11 | Tool Verification | Legal (chain of custody) | Hallucinated tool output | Self-attested |
| 12 | Adversarial Decoupling | Medicine (Double-Blind) + Cyber (Red Team) | Algorithmic Stockholm Syndrome (Cognitive Captivity) | Self-attested |
| 13 | Golden Hammer Neutralization | Systems Biology + Thermodynamics | Tech Stack Bias, over-abstraction, framework dogmatism | Self-attested |
