# Diffract — A Review Protocol for Human-AI Collaboration

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](CHANGELOG.md)

> **AI is not a tool. It is an agent.**
> — [Yuval Noah Harari](https://en.wikipedia.org/wiki/Yuval_Noah_Harari)
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

Diffract emerged from code review, but the lenses apply to anything that
can be reviewed: code, documentation, architecture, API designs, or processes.

**Honest value proposition:** A good senior reviewer does 80% of what
Diffract does intuitively. The value is in the other 20% — the lenses
you'd skip, the proof you actually looked, and the calibration test that
catches what you missed. [No single component is original.](#references)
The value is in the combination.

## Table of Contents

- [Why Diffract?](#why-diffract)
- [How to Use](#how-to-use)
- [Quick Start](#quick-start)
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

**Your most important role:** Don't just approve the PLAN and wait. Challenge
the agent during every phase. The most valuable findings in Diffract's own
development came from human interruptions, not from the lenses. The lenses
find what's wrong. You find what's missing.

## How to Use

### Manual (any LLM)

1. Open your preferred AI assistant (Claude, Gemini, ChatGPT, or any LLM)
2. Paste the contents of [`PROMPT.md`](PROMPT.md) into the chat
3. Paste the artifact you want to review (code, documentation, design)
4. The AI will propose governors (PLAN) and wait for your confirmation
5. Once confirmed, the AI runs all 9 lenses and produces findings

You can also use `PROMPT.md` as a checklist for human-only reviews.

### Agentic (Antigravity)

Diffract ships as an [Antigravity](https://antigravity.google) skill. When
loaded, it transforms Antigravity into a structured Diffract review agent
with parallel lens execution and deterministic tool integration.

1. Clone: `git clone https://github.com/contextvibes/diffract.git`
2. Register the skill globally in `~/.gemini/config/skills.json`:
   ```json
   { "entries": [{ "path": "/path/to/diffract/.agents/skills" }] }
   ```
3. In any project (CLI, IDE, or Antigravity 2.0): *"Run a diffract review"*

### Programmatic (Python SDK)

```python
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

config = LocalAgentConfig(capabilities=CapabilitiesConfig())
async with Agent(config) as agent:
    response = await agent.chat("Run a diffract review on ./src")
    async for token in response:
        print(token, end="")
```

### Deterministic Scripts

The `scripts/` directory contains Python tool wrappers for deterministic
lenses. These work standalone — no AI required, no pip dependencies
(Python 3.8+ stdlib only):

```bash
# Discover available linters on your system
python3 scripts/discover.py              # JSON manifest
python3 scripts/discover.py --pretty     # human-readable
python3 scripts/discover.py --detail     # includes paths and versions

# Normalize tool output to the unified finding schema
deadcode ./... 2>&1 | python3 scripts/normalize.py --tool deadcode
semgrep scan --json . | python3 scripts/normalize.py --tool semgrep
bandit -r src/ 2>&1  | python3 scripts/normalize.py --tool bandit
```

The finding output format is defined in `scripts/schema.json`.

**Start simple:** You don't need to master all 9 lenses on day one. Try
🗑️ Subtract and 🛡️ Shield on your next PR. Add lenses as you get comfortable.

## Quick Start

### 1. PLAN — Set your governors

Before any analysis, agree on scope, calibration, and evidence rules:

```
🧭 Compass: "Is this code ready for production?"
🐍 Cobra:   Cautious — fix more, skip less.
⚖️ Integrity: file:line evidence per lens. Cognitive anchoring required.
```

**PLAN is a checkpoint.** Propose governors, get agreement, then proceed.
No agreement = no analysis.

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

### 2. DO — Apply 9 lenses + W5H1

Run each lens across the codebase. Collect ALL findings. **Do not fix yet.**

| # | Lens | Question |
|---|------|----------|
| 1 | 🗑️ **Subtract** | Can I remove this entirely? |
| 2 | ✂️ **Simplify** | Can this be simpler without losing capability? |
| 3 | 🏷️ **Name** | Does the name match the thing? |
| 4 | 📌 **Truth** | Is this knowledge in exactly one place? |
| 5 | 🧱 **Boundary** | Can an isolated change stay in one boundary? |
| 6 | 🛡️ **Shield** | Does it neutralize all inputs that violate its invariants? |
| 7 | 🎯 **Variety** | Does every possible input map to a defined output? |
| 8 | 🔍 **Observability** | Can I determine system state from its outputs? |
| 9 | ⚡ **Efficiency** | Is resource use proportional to the work required? |

Then ask [W5H1](docs/w5h1.md) to find what's **missing** — especially
**Why** (rationale), **Who** (ownership), and **When** (expiry).

### 3. CHECK — Vet findings through governors

```
Finding
  → ⚖️ Integrity: "Is this objective? Would another reviewer agree?"
    → No  → Discard (bikeshedding or bias)
    → Yes →
      → 🧭 Compass: "Is this relevant to our goal?"
        → No  → Skip (Compass)
        → Yes →
          → 🐍 Cobra: "Does fixing it cause a new problem?"
            → Yes → Skip (Cobra)
            → No  → Fix
```

### 4. LEARN — Fix, verify, retro

- Apply all fixes
- Verify (build + test + lint)
- Retro: what did the framework miss? Update it.
- If fixes were applied → cycle back to PLAN

**Done when a full cycle produces zero new Fix outcomes.**
In [our first application](examples/web-service.md), Diffract found 15 issues
across 3 PDCA cycles, with Observability and Subtract as the most productive lenses.

## Documentation

| Document | Description |
|----------|-------------|
| [Governors](docs/governors.md) | Detailed governor specifications |
| [Lenses](docs/lenses.md) | Each lens with root principle, evidence format, and examples |
| [Anti-Dishonesty](docs/anti-dishonesty.md) | 8 structural mechanisms adapted from high-stakes industries |
| [W5H1](docs/w5h1.md) | Completeness scan for what's missing |
| [Review Prompt](PROMPT.md) | Self-contained instructions for running a Diffract review |
| [Calibration](docs/calibration.md) | How to validate review consistency across reviewers |
| [Example Review](examples/web-service.md) | Full Diffract cycle on a web service |
| [Research: First Principles](docs/research/rq1-first-principles.md) | DeepThink analysis validating the lens set |
| [Research: High-Stakes Review](docs/research/rq2-high-stakes-review.md) | Patterns from aviation, nuclear, medicine, law |
| [Roadmap](ROADMAP.md) | Future: deterministic tooling, MCP integration, v1.0 criteria |

## How It Emerged

Diffract was developed through a collaboration between a human engineer
and AI assistants during a code review session in February 2026. The
framework started as 8 review lenses, was challenged against independent
first-principles research (DeepThink), cross-validated against high-stakes
industry practices (DeepResearch), and refined through multiple PDCA
cycles — including applying the framework to itself.

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

The Compass is the most powerful lever in the framework.

## Acknowledgments

This framework was co-created by [Jasper Duizendstra](https://github.com/duizendstra)
and AI assistants during a collaborative code review session.

### AI Contribution

The following AI systems contributed to the development of Diffract:

- **Antigravity** (Google DeepMind) — Primary collaborator. Co-developed the
  framework structure, applied lenses to real codebases, drafted documentation,
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

This framework contains AI-generated content. While the human author reviewed
and approved all material, the documentation, examples, and structural design
were produced through human-AI collaboration. We believe in full transparency
about AI involvement in intellectual and creative work.

## References

No single component of Diffract is original. The value is in the combination.

| Component | Source |
|-----------|--------|
| "AI is not a tool, it is an agent" | Yuval Noah Harari |
| PDCA cycle | W. Edwards Deming, Toyota Production System |
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
| Blind seeding | UXO clearance, Radiology, Legal e-discovery |
| "First, do no harm" | Hippocratic tradition |

## License

[MIT](LICENSE)
