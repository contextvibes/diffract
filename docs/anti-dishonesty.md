# Anti-Dishonesty Mechanisms

Diffract assumes that reviewers — human and AI — will fail. Not out of
malice, but because of cognitive fatigue, confirmation bias, time pressure,
and social dynamics. The framework makes dishonesty structurally difficult
through 11 concrete mechanisms, each adapted from a high-stakes industry
where inspection failures have life-or-death consequences.

## The Mechanisms

### 1. Evidence (Proof of Observation)

**Source:** Aviation maintenance — RFID scanning forces physical presence
at the inspection site before a task can be signed off.

**In Diffract:** Every lens must produce `file:line` evidence or an explicit
list of what was checked. A claim of "all clean" without evidence is invalid.

### 2. Cognitive Anchoring (Shisa Kanko)

**Source:** Japanese railways and nuclear control rooms — operators must
physically point at each indicator and verbally call out its state. This
engages motor, visual, auditory, and verbal processing simultaneously,
breaking the "looking without seeing" failure mode.

**In Diffract:** When a lens produces no findings, the reviewer must describe
what a finding **would** look like. This proves they understand the lens and
actually examined the code, not just waved at it.

```markdown
### 🎯 Variety
Checked: all switch/match statements on HTTP status codes
A finding would look like: a status code reaching the default branch
that should have explicit handling (e.g., 503 for retry logic).
No findings matching this pattern.
```

**"No findings" without cognitive anchoring is not allowed.**

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
lenses. If they produce zero new findings, the review is calibrated. If
they find issues the first reviewer missed, the review is incomplete.

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

**Prevents:** Tool hallucination, stale context, confabulated evidence.

### 10. Chunked Attestation (Anti-Degradation)

**Source:** Aviation — Crew Duty Time Limits

Pilots are legally required to stop after a certain number of hours. The
mechanism isn't "try harder" — it's "stop and hand off."

**In Diffract:** If the artifact exceeds your working capacity, partition it.
Each partition gets its own DO phase. State partition boundaries in PLAN.
Findings from partition boundaries (cross-file issues) get a dedicated pass.

**Prevents:** Model degradation at long contexts, diminishing thoroughness.

### 11. Tool Verification (Anti-Tool-Hallucination)

**Source:** Legal — Chain of Custody

Physical evidence must have an unbroken documented chain from collection to
courtroom.

**In Diffract:** When citing tool output as evidence, include the command run
and a representative snippet of raw output. If tool execution cannot be
independently verified, flag findings as `[tool-unverified]`.

**Prevents:** Hallucinated tool output, fabricated scan results.

---

## Summary Table

| # | Mechanism | Source Industry | What It Prevents |
|---|-----------|----------------|-----------------|
| 1 | Evidence | Aviation (RFID) | Claims without observation |
| 2 | Cognitive Anchoring | Railways (shisa kanko) | Looking without seeing |
| 3 | Falsifiability | Philosophy (Popper) | Opinion disguised as fact |
| 4 | Calibration | Metrology + Radiology (dual-reading) | Reviewer-dependent outcomes |
| 5 | Nothing-Found Verification | UXO / Radiology / Law | False negatives |
| 6 | Challenge-Response | Aviation (CRM) | Passive agreement |
| 7 | Finder/Decider Separation | Aviation (RII) | Conflict of interest |
| 8 | Retro | Manufacturing (Deming) | Framework stagnation |
| 9 | Context Fidelity | Pharma (CoA) | Tool hallucination, confabulated evidence |
| 10 | Chunked Attestation | Aviation (duty limits) | Degradation at long contexts |
| 11 | Tool Verification | Legal (chain of custody) | Hallucinated tool output |
