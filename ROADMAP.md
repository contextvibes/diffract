# Roadmap

## Vision

Diffract's 10 lenses start as human/AI judgment. Over time, the deterministic
parts should be offloaded to tools — freeing the reviewer to focus on what
only judgment can assess.

## Automation Potential

| Lens | Deterministic? | Tool Opportunity |
|------|---------------|-----------------|
| 🗑️ **Subtract** | Partially | Dead code detectors (`deadcode`, `vulture`, `ts-prune`) |
| ✂️ **Simplify** | No | Requires judgment — what is "unnecessary" complexity? |
| 🏷️ **Name** | No | Requires domain understanding |
| 📌 **Truth** | Partially | Duplication detectors (`jscpd`, `flay`, `simian`) |
| 🧱 **Boundary** | Partially | Dependency graph analyzers, import cycle detectors |
| 🛡️ **Shield** | Mostly | Security scanners (`gosec`, `bandit`, `semgrep`) |
| 🔗 **Provenance** | Mostly | Advisory scanners (`npm audit`, `osv-scanner`), lockfile diff, SBOM generators |
| 🎯 **Variety** | Partially | Exhaustive match warnings (compiler), coverage tools |
| 🔍 **Observability** | Partially | Lint rules for swallowed errors, missing log calls |
| ⚡ **Efficiency** | Partially | Profilers, benchmark suites, allocation trackers |

## Roadmap

### v0.2 — Prompt-Only + Calibration
- Antigravity skill driver — **never shipped.** No `.agents/` directory has
  existed in any commit. Diffract is driven by pointing an agent at
  `PROMPT.md`; per-tool adapters are tracked under v0.3.
- Deterministic tool scripts — **dropped.** Diffract ships prompt-only. The
  lens-to-tool mapping lives in `docs/lenses.md` ("Automation: Tools First");
  tools are invoked directly rather than through wrappers.
- [x] Execute calibration tests across 3+ AI models — see
      [RQ3](docs/research/rq3-calibration-reproducibility.md) (4 models,
      10 runs, one frozen artifact)
- [ ] Add guidance for reviewing non-code artifacts (API specs, schemas)
- [ ] Add more example reviews (different languages, architectures)

### v0.3 — Confidence Calibration + Multi-Tool Adapters
- [x] Vendor-neutral adapter: `AGENTS.md` (shipped in 0.2.4) — the
      convention file most coding agents read on arrival; points review
      runs at `PROMPT.md` and contributors at the house rules
- [x] Brier-scored Confidence (shipped in 0.3.0) — canonical bin
      probabilities in `PROMPT.md`, scoring method + worked example from
      real self-review data in `docs/calibration.md`
- [x] ACH-style vetting for Low-Confidence findings (shipped in 0.3.0) —
      competing hypotheses weighed before the verdict, per Heuer
- [x] Majors-only done-rule (shipped in 0.3.0) — five self-review cycles
      showed Minor findings are inexhaustible for prose artifacts; see
      issue #29
- [x] CI gate, first slice (shipped in 0.3.0): `scripts/check.py` runs
      link/anchor resolution, fence balance, version-string agreement, and
      the README↔PROMPT.md lens-table diff in
      `.github/workflows/check.yml` — recommended by the 0.3.0 validation
      cycles after the drift class recurred
- [ ] CI gate, remaining slice: mechanical README↔PROMPT.md spec diff for
      verdict glosses, the done-rule, and tag strings
- [ ] Define a machine-readable output format for findings (JSON/SARIF)
- [ ] Claude Code adapter (`.claude/CLAUDE.md`) — for setups where
      `CLAUDE.md` shadows `AGENTS.md`
- [ ] Cursor adapter (`.cursor/rules/diffract.md`)
- [ ] Map popular linters/scanners to lenses so existing tool output can be
      presented in Diffract format — the per-lens example rules in
      `docs/lenses.md` are the mapping substrate: linters are rule engines,
      so each tool check maps to the lens whose rule it enforces

### v0.4 — Calibration Automation
- [ ] Automated calibration via subagent (second reviewer with fresh context)
- [ ] Executable partitioning spec for mechanism 10 — needs an operational
      trigger, a precedence rule over boundary kinds, fresh-context hand-off,
      and a deduplication procedure at CHECK. A draft was rejected in review
      on all four counts
- [ ] Reference artifact set carrying independently verified defects at
      **graded difficulty** — required to assign reviewer tiers on demand
      (`docs/calibration.md`) and to populate tiers 2 and 3, which RQ3
      defined but left empty. RQ5 showed a single easy defect saturates the
      recall criterion: four configurations ranging from 3 to more than 11
      stable claims each all measured tier 4 against one two-line
      contradiction
- [ ] Seeded-error variant of Nothing-Found Verification — a real defect
      planted by a third party, per RQ2's blind-seeding designs. RQ3 showed
      the current self-check cannot detect its own misses. Complemented
      since 0.2.4 by capture–recapture estimation in `docs/calibration.md`
      (Lincoln–Petersen; Eick et al.; Gilb & Graham), which attacks the same
      gap from the other side: estimation says *how many* defects remain,
      seeding says *which one* was missed
- [ ] IDE extension: highlight findings inline with lens icons
- [ ] Auto-generate PLAN from project context (language, CI config)

### v1.0 — Calibration Validated
- [ ] Framework applied to 3+ independent codebases (currently: 2)
- [ ] Calibration validated across 2+ independent reviewers
- [ ] Deterministic lenses produce identical results regardless of runner

## Design Principle

> **Three kinds of reviewer: tools, agents, humans.**
>
> **Tools** run deterministic checks — dead code, security, duplication.
> They execute the same way every time.
>
> **AI agents** apply judgment — naming, boundaries, simplification.
> They reason, challenge, and collaborate. They are not tools.
>
> **Humans** set the Compass. They decide what matters, what to fix,
> and what to ship. Governors are always human-set.
