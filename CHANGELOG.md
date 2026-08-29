# Changelog

All notable changes to Diffract will be documented in this file.

## Versioning

- **0.x** — Framework is being refined through application and research
- **1.0** — Framework has been applied to 3+ independent codebases by 2+
  independent reviewers with consistent results (calibration validated)

Entries describe each release as it shipped. 0.1.0 predates tagging and was
never cut as a release; v0.2.0 is the first tagged version.

## [0.2.0] — 2026-08-29

Framework grew from 9 to 10 lenses and from 8 to 13 anti-dishonesty
mechanisms. Deterministic tooling was tried and dropped — Diffract ships
prompt-only. The calibration protocol was rewritten after its own method was
found unable to detect the difference between a miscalibrated reviewer and
run-to-run noise.

### Added

- **🔗 Provenance lens** (10th) — dependency lineage, supply-chain and
  unvetted-code review
- **Anti-dishonesty mechanisms 9–13** — Context Fidelity
  (Anti-Confabulation), Chunked Attestation (Anti-Degradation), Tool
  Verification (Anti-Tool-Hallucination), Adversarial Decoupling
  (Cold-Start Calibration), Golden Hammer Neutralization (Domain Decoupling)
- **W5H1 "How — Golden Hammer Check"** — tech-stack choice as a distinct
  missing-information axis
- **RQ3 — calibration reproducibility** (`docs/research/`): 10 independent
  reviews of one frozen artifact across 4 models
- `examples/diffract.yaml` — example configuration

### Changed

- **Calibration protocol requires at least 3 independent runs per reviewer**
  and scores *stable claims* (recurring in a majority of a reviewer's runs)
  rather than raw overlap between two single runs. One run per reviewer
  cannot distinguish reviewer miscalibration from noise: on a frozen
  125-line artifact, one model produced 0–4 findings across four identical
  runs and another produced 14–23.
- Cobra levels quantified — prototype / production / library-framework each
  carry an explicit skip rule
- `PROMPT.md` Cobra template now offers all three Cobra levels; it
  previously omitted `library/framework`
- Calibration templates take a `[version]` placeholder instead of a
  hardcoded version string

### Removed

- **`scripts/`** (`discover.py`, `normalize.py`, `schema.json`) — no
  consumer, output format did not match the framework's evidence tables, and
  the lens-to-tool mapping had already drifted from `docs/lenses.md`.
  Diffract is prompt-only; tools are invoked directly.

### Fixed

- Bounded Rationality attributed to Kahneman; it is Herbert Simon's
- Provenance missing from the lens count, the ROADMAP automation table, and
  the worked example, despite `PROMPT.md` requiring all 10 lenses
- ROADMAP claimed five deterministic shell scripts as delivered; they never
  existed in any commit
- Cobra's `Calibration:` field was a stub; the Cobra Effect anecdote was
  asserted as history without a source; the Calibration Template silently
  dropped the Integrity default

## [0.1.0] — 2026-02-22

Initial release. 3 governors, 9 lenses, W5H1, PDCA cycle, 8 anti-dishonesty
mechanisms, review prompt, example, and research documentation.
