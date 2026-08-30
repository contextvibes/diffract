# Diffract — A Review Protocol for Human-AI Collaboration

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.0-green.svg)](CHANGELOG.md)

> **AI is not a tool. It is an agent.**
> — paraphrasing [Yuval Noah Harari](https://en.wikipedia.org/wiki/Yuval_Noah_Harari),
> a central argument of *Nexus* (2024)
>
> A linter runs the same way every time. An AI agent reasons, interprets,
> and makes judgment calls — just like a human. And like any agent, it can
> be lazy, biased, or wrong.
>
> Diffract keeps both human and AI reviewers honest — structurally.

**Vision:** Every review reveals the truth about the artifact — regardless of
who reviews it.

**Mission:** Keep each other honest — structurally, not aspirationally.

**Goal:** Same artifact + same lenses + different reviewer = same findings.

**Measured status:** not yet achieved. In the latest tiering experiment
(August 2026, against the 0.2.x instrument), every reviewer pairing failed
the calibration criteria ([RQ5](docs/research/rq5-reviewer-tiering.md)). Diffract publishes its own
failures — the protocol exists to make them visible, not to hide them.

Diffract emerged from code review, but the lenses apply to anything that
can be reviewed: code, documentation, architecture, API designs, or processes.

**Value proposition (not measured):** A good senior reviewer already does
most of what Diffract does, intuitively. The claimed value is in the rest —
the lenses you'd skip, the proof you actually looked, and the calibration
test that catches what you missed. [No single component is original.](#references)
The value is in the combination.

## Table of Contents

- [Why Diffract?](#why-diffract)
- [How to Use](#how-to-use)
- [The Protocol at a Glance](#the-protocol-at-a-glance)
- [Documentation](#documentation)
- [How It Emerged](#how-it-emerged)
- [Acknowledgments](#acknowledgments)
- [Contributing](#contributing)
- [References](#references)
- [License](#license)

## Why Diffract?

The moment AI becomes an agent in your review process, you need the same
structural honesty mechanisms that aviation, nuclear, and medicine use for
their human inspectors:

- Evidence for every claim (not just "looks good")
- Separation of finding from vetting (the agent who finds doesn't decide)
- Testable findings (objective, not opinion)
- [Anti-manipulation mechanisms](docs/anti-dishonesty.md) borrowed from
  aviation, medicine, and other high-stakes industries

**What these mechanisms do not do.** They are aids for a reviewer that is trying
to be honest, not detectors of one that isn't. Most are executed by the reviewer,
about the reviewer, in the reviewer's own output — a reviewer that misreads the
artifact will certify a review of what it misread. Four of the thirteen are now
checkable from outside: `scripts/check_review.py` verifies a review's form,
its mandated output elements, and its quotes against the frozen artifact;
`scripts/render_scorecard.py` derives the Scorecard counts from the review's
own index instead of trusting them; `scripts/check.py` runs the entry gate
the review claims to have passed; and `calibration/` scores a reviewer
against defects it was not told about. The rest are
[self-attested](docs/anti-dishonesty.md#what-these-mechanisms-can-and-cannot-detect).

**Your most important role:** Don't just approve the PLAN and wait. Challenge
the agent during every phase. The most valuable findings in Diffract's own
development came from human interruptions, not from the lenses. The lenses
find what's wrong. You find what's missing.

## How to Use

### Manual (any LLM)

1. Open your preferred AI assistant (Claude, Gemini, ChatGPT, or any LLM)
2. Paste the contents of [`PROMPT.md`](PROMPT.md) into the chat
3. Paste the artifact you want to review (code, documentation, design)
4. The AI runs the deterministic entry checks it can (or tags the review
   `[entry waived: cannot run checks]`), then proposes governors (PLAN)
   and waits for your confirmation
5. Once confirmed, the AI runs all 10 lenses and produces findings

You can also use `PROMPT.md` as a checklist for human-only reviews.

### Agentic (any coding agent)

No skill package ships with this repo. To run Diffract inside a coding agent
— Claude Code, Antigravity, Cursor — point the agent at
[`PROMPT.md`](PROMPT.md) and ask it to follow the protocol. Agents that read
[`AGENTS.md`](AGENTS.md) on arrival are pointed there automatically.
Per-tool adapters are planned, not built; see [ROADMAP](ROADMAP.md).

**Start simple (human checklist use):** You don't need all 10 lenses to
review by hand — try 🗑️ Subtract and 🛡️ Shield on your next PR and declare
the narrowed lens set as partial coverage (PROMPT.md, Rule 6). An agent
executing PROMPT.md runs all 10 unless the user narrows the set; no
`diffract.yaml` key selects lenses.

## The Protocol at a Glance

[PROMPT.md](PROMPT.md) is the normative protocol. Everything this README
says about how a review runs — here and in *Why Diffract?* and *How to
Use* — summarizes it; where they disagree, PROMPT.md is right and the
README has a defect.

### 1. PLAN — Set your governors

**First, run the cheap deterministic checks** — build, test, and lint for
code; links, anchors, code fences, and version strings for prose. State
what you ran and what it returned at the top of the review: review
attention is the expensive resource and must not be spent finding what a
tool reports for free. PROMPT.md's PLAN section makes this a gate before
governors and defines the tags for waiving it.

Then, before any analysis, agree on scope, calibration, and evidence rules:

```
🧭 Compass: "Is this code ready for production?"
🐍 Cobra:   Production (level tests are normative in PROMPT.md, PLAN)
⚖️ Integrity: file:line evidence per lens. Cognitive anchoring required.
            Every finding quotes the text it cites.
```

**Cognitive anchoring** means: on any lens that reports nothing, write down
what a finding in that lens's domain *would* have looked like for this
artifact. It is the evidence that the lens was run rather than skipped —
borrowed from Shisa Kanko (see [References](#references)).

**PLAN is a checkpoint.** Propose governors, get agreement, then proceed.
No agreement = no analysis. Running async with nobody to agree? State the
governors, proceed, and tag the output `[async — no PLAN confirmation]`.

**Pick a Compass that fits your situation:**

| Compass | Best For |
|---------|----------|
| "Is this code ready for production?" | Pre-release |
| "Could a junior dev onboard from this in one day?" | Readability |
| "If the author left, could someone else maintain this?" | Bus factor |
| "Does this code respect the user's time and data?" | Ethics / UX |
| "Would this survive a 10x traffic spike at 3am?" | Resilience |
| "Are all ideas properly attributed?" | Intellectual honesty |

[More examples →](docs/governors.md)

### 2. DO — Apply 10 lenses + W5H1

Run each lens across the codebase. Collect ALL findings. **Do not fix yet.**

*Reproduced from PROMPT.md's normative lens list. If the two disagree,
PROMPT.md is right and this table is a defect.*

| # | Lens | Question |
|---|------|----------|
| 1 | 🗑️ **Subtract** | Can I remove this entirely? |
| 2 | ✂️ **Simplify** | Can this be simpler without losing capability? |
| 3 | 🏷️ **Name** | Does the name match the thing? |
| 4 | 📌 **Truth** | Is this knowledge in exactly one place? |
| 5 | 🧱 **Boundary** | Can an isolated change stay in one boundary? |
| 6 | 🛡️ **Shield** | Does it neutralize all inputs violating its invariants? |
| 7 | 🔗 **Provenance** | Can I verify the origin and integrity of every dependency? |
| 8 | 🎯 **Variety** | Does every possible input map to a defined output? |
| 9 | 🔍 **Observability** | Can I determine system state from outputs? |
| 10 | ⚡ **Efficiency** | Is resource use proportional to work required? |

Then ask [W5H1](docs/w5h1.md) to find what's **missing** — **Why**
(rationale), **Who** (ownership), **When** (expiry), and **How**
(tech-stack neutralization). What and Where are omitted deliberately:
they are covered by the 🏷️ Name and 🧱 Boundary lenses.

### 3. CHECK — Vet findings through governors

```
Finding
  → ⚖️ Integrity: "Did I look? Is it objective?"
    → No  → Discard:Integrity (fails the evidence bar — not established as real)
    → Yes →
      → 🧭 Compass: "Is this relevant to our goal?"
        → No  → Skip:Compass
        → Yes →
          → 🐍 Cobra: "Does the declared level say to skip?"
            (level tests are normative in PROMPT.md, PLAN)
            → Yes → Skip:Cobra
            → No  → Fix
```

Low-Confidence findings first weigh competing hypotheses — keep the one the
evidence *least disconfirms* — before any verdict (see `PROMPT.md`, CHECK).

### 4. LEARN — Fix, verify, retro

- Apply all fixes
- Verify (re-run the PLAN entry checks)
- Retro: scorecard, gap analysis, defect prevention
- If fixes were applied → cycle back to PLAN

**Done when a full cycle produces zero new Major Fix outcomes AND the
review states an Exit Estimate** — the estimated Major defects remaining,
with its basis (PROMPT.md's LEARN section is normative on the rule, its
tags, and why Minors do not gate exit).
In [our first application](examples/web-service.md), Diffract raised 15
findings across 2 PDCA cycles, with 🔍 Observability and 🛡️ Shield as the
most productive lenses (3 findings each). That artifact is anonymized, so its
findings cannot be independently checked. The
[SemVer 2.0.0 review](examples/semver-2.0.0-review.md) is the counterpart:
a public, hash-pinned artifact reviewed blind, where every quote and line
number can be verified against the original text.

## Documentation

| Document | Description |
|----------|-------------|
| [Governors](docs/governors.md) | Detailed governor specifications |
| [Lenses](docs/lenses.md) | Each lens with root principle, evidence format, and examples |
| [Anti-Dishonesty](docs/anti-dishonesty.md) | 13 structural mechanisms adapted from high-stakes industries |
| [W5H1](docs/w5h1.md) | Completeness scan for what's missing |
| [Review Prompt](PROMPT.md) | Self-contained instructions for running a Diffract review |
| [Agent Entry Point](AGENTS.md) | Where coding agents start: review runs → PROMPT.md, repo work → house rules |
| [Calibration](docs/calibration.md) | How to validate review consistency across reviewers |
| [Example Review](examples/web-service.md) | Full Diffract cycle on a web service; the repo's demonstration of Output B (nothing-found lenses) |
| [Example Review: SemVer 2.0.0](examples/semver-2.0.0-review.md) | Blind adoption review of a public, hash-pinned artifact; every quote machine-verified |
| [Review Artifacts](examples/artifacts/README.md) | Frozen third-party review targets: provenance, licenses, hashes, and the posture these reviews take |
| [Calibration Fixtures](calibration/README.md) | Public documents with known defects planted in them, for measuring what a reviewer actually finds |
| [Calibration Results](calibration/results.md) | Scored runs against those fixtures, and what each score does and does not show |
| [Research: First Principles](docs/research/rq1-first-principles.md) | DeepThink analysis validating the lens set |
| [Research: High-Stakes Review](docs/research/rq2-high-stakes-review.md) | Patterns from aviation, nuclear, medicine, law |
| [Research: Calibration Reproducibility](docs/research/rq3-calibration-reproducibility.md) | 10 reviews of one frozen artifact across 4 models |
| [Research: Reviewer Tiering](docs/research/rq5-reviewer-tiering.md) | 12 reviews testing whether reviewer tiers separate reviewers (numbering skips RQ4 — never run, not withheld) |
| [Roadmap](ROADMAP.md) | Future: multi-tool adapters, calibration automation, v1.0 criteria |

## How It Emerged

Diffract was developed through a collaboration between a human engineer
and AI assistants during a code review session in February 2026. The
protocol started as 8 review lenses, was challenged against independent
first-principles research (DeepThink), cross-validated against high-stakes
industry practices (DeepResearch), and refined through multiple PDCA
cycles — including applying the protocol to itself.

The process was itself an act of Diffract: the human set the Compass, the
AI applied the lenses, and both challenged each other's findings. The
anti-dishonesty mechanisms emerged from this dynamic — the need to keep
both human and AI reviewers honest was not theoretical but experienced
firsthand.

The name comes from optics: diffraction splits a wave into its component
parts. Diffract splits an artifact into its component concerns.

### The Compass in Practice

During development, 8 different compasses were applied to this repo — the
same artifact, same lenses, different intent — each producing unique findings:

| Compass | What It Found |
|---------|--------------|
| "Can someone use this from the repo alone?" | Missing "How to Use" section |
| "Can any LLM follow this equally well?" | Missing one-shot mode, no-tool fallback |
| "Would a newcomer feel welcomed?" | Academic jargon in README, no "Start simple" |
| "Is this original? Did we attribute sources?" | Harari unattributed, no bibliography |
| "Are all links and spelling correct?" | Terminology drift (falsifiable vs testable) |
| "Does it guide AI to use tools first?" | No per-lens tooling table |
| "Is it language-neutral?" | Go-specific tools in automation table |
| "Is every sentence clear and kind?" | "Refuse" → "Pause", added kindness rule |

The Compass is the most powerful lever in the protocol.

## Acknowledgments

This protocol was co-created by [Jasper Duizendstra](https://github.com/duizendstra)
and AI assistants during a collaborative code review session.

### AI Contribution

The following AI systems contributed to the development of Diffract:

- **Antigravity** (Google DeepMind) — Primary collaborator. Co-developed the
  protocol structure, applied lenses to real codebases, drafted documentation,
  and challenged findings across multiple PDCA cycles.
- **Google DeepThink** (Gemini 3.1 Pro) — Independent first-principles
  analysis (RQ1) that validated the lens set and identified two missing lenses
  (Variety, Efficiency).
- **Google DeepResearch** (Gemini 3.1 Pro) — External research (RQ2) that
  identified structural anti-manipulation mechanisms from aviation, nuclear,
  medicine, and legal industries.

### Human Contribution

All design decisions, research direction, governor calibration, and quality
standards were set by the human author. The Compass was always human-set.
The AI proposed; the human decided.

### Disclaimer

This project contains AI-generated content. While the human author reviewed
and approved all material, the documentation, examples, and structural design
were produced through human-AI collaboration. We believe in full transparency
about AI involvement in intellectual and creative work.

## Contributing

Proposals, calibration runs, and lens challenges are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md) for what a lens proposal must carry and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for conduct.

The most useful contribution is a calibration run: apply
[`PROMPT.md`](PROMPT.md) to an artifact of your own, record the results per
[docs/calibration.md](docs/calibration.md), and open an issue with them —
including the runs where the protocol failed you.

## References

No single component of Diffract is original. The value is in the combination.

| Component | Source |
|-----------|--------|
| "AI is not a tool, it is an agent" (paraphrase) | Yuval Noah Harari, *Nexus* (2024) |
| PDCA cycle | Walter Shewhart (origin); popularized by W. Edwards Deming, Toyota Production System |
| Inspection method: entry/exit criteria, checking rates, sampling, Major/Minor severity | Tom Gilb & Dorothy Graham, *Software Inspection* (1993); antecedent: Michael Fagan (IBM, 1976) |
| Capture–recapture defect estimation | Lincoln–Petersen (ecology); applied to software inspections by Eick et al. (1992); remaining-defect estimation per Gilb & Graham |
| Brier-scored confidence calibration | Glenn W. Brier (1950); judgment-calibration practice per Philip Tetlock, *Superforecasting* (2015) |
| Analysis of Competing Hypotheses (Low-Confidence vetting) | Richards J. Heuer Jr., *Psychology of Intelligence Analysis* (CIA, 1999) |
| Governors declared before findings exist (PLAN precedes DO) | Preregistration / registered reports (Chris Chambers; Center for Open Science) |
| Planguage — a goal names its failure level | Tom Gilb, *Competitive Engineering* (2005) |
| Evolutionary delivery (ancestor of the PDCA circuit breakers) | Tom Gilb, *Principles of Software Engineering Management* (1988) |
| Defect Prevention Process | Robert Mays & Carole Jones (IBM), as integrated by Gilb & Graham |
| Shisa Kanko (cognitive anchoring) | Japanese National Railways |
| Falsifiability | Karl Popper, *The Logic of Scientific Discovery* |
| Via Negativa | Nassim Nicholas Taleb, *Antifragile* |
| Requisite Variety | W. Ross Ashby, *An Introduction to Cybernetics* |
| Ubiquitous Language | Eric Evans, *Domain-Driven Design* |
| DRY | Andy Hunt & Dave Thomas, *The Pragmatic Programmer* |
| YAGNI | Kent Beck, Extreme Programming |
| Clean Architecture | Robert C. Martin |
| CRM / Challenge-Response | Aviation industry |
| Dual-reading / Calibration | Radiology |
| Blind seeding (adapted as a reviewer self-check, not implemented as seeding) | UXO clearance, Radiology, Legal e-discovery |
| "First, do no harm" | Hippocratic tradition |

## License

[MIT](LICENSE)
