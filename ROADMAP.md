# Roadmap

## Vision

Diffract's 9 lenses start as human/AI judgment. Over time, the deterministic
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
| 🎯 **Variety** | Partially | Exhaustive match warnings (compiler), coverage tools |
| 🔍 **Observability** | Partially | Lint rules for swallowed errors, missing log calls |
| ⚡ **Efficiency** | Partially | Profilers, benchmark suites, allocation trackers |

## Roadmap

### v0.2 — Agentic Skill + Deterministic Tools
- [x] Antigravity skill driver (clone, locate, execute the protocol)
- [x] Deterministic tool scripts (`scripts/discover.sh`, `subtract.sh`,
      `shield.sh`, `truth.sh`, `boundary.sh`)
- [ ] Execute calibration tests across 3+ AI models
- [ ] Add guidance for reviewing non-code artifacts (API specs, schemas)
- [ ] Add more example reviews (different languages, architectures)

### v0.3 — Multi-Tool Adapters + Output Formats
- [ ] Define a machine-readable output format for findings (JSON/SARIF)
- [ ] Claude Code adapter (`.claude/CLAUDE.md`)
- [ ] Cursor adapter (`.cursor/rules/diffract.md`)
- [ ] Map popular linters/scanners to lenses so existing tool output can be
      presented in Diffract format

### v0.4 — Calibration Automation
- [ ] Automated calibration via subagent (second reviewer with fresh context)
- [ ] IDE extension: highlight findings inline with lens icons
- [ ] Auto-generate PLAN from project context (language, CI config)

### v1.0 — Calibration Validated
- [ ] Framework applied to 3+ independent codebases (currently: 2)
- [ ] Calibration validated across 2+ independent reviewers
- [ ] Deterministic lenses produce identical results regardless of runner

## Design Principle

> **Three tiers: tools, agents, humans.**
>
> **Tools** run deterministic checks — dead code, security, duplication.
> They execute the same way every time.
>
> **AI agents** apply judgment — naming, boundaries, simplification.
> They reason, challenge, and collaborate. They are not tools.
>
> **Humans** set the Compass. They decide what matters, what to fix,
> and what to ship. Governors are always human-set.
