# Changelog

All notable changes to Diffract will be documented in this file.

## Versioning

- **0.x** — Framework is being refined through application and research
- **1.0** — Framework has been applied to 3+ independent codebases by 2+
  independent reviewers with consistent results (calibration validated)

Entries describe each release as it shipped. 0.1.0 predates tagging and was
never cut as a release; v0.2.0 is the first tagged version.

## [Unreleased]

### Added

- **Evidence against Nothing-Found Verification (mechanism 5).** RQ3's run
  transcripts are now written up in `docs/anti-dishonesty.md` and
  `docs/research/`. The mechanism is named for blind seeding but implements
  none of its three properties — no third party, no real defect, no blindness
  — and in the only test it has, it passed on all four reviews that missed a
  verified misattribution. Two of those affirmed the error while performing
  the verification; one wrote the error into its own cognitive-anchoring
  example and then found nothing matching it. `PROMPT.md` now tells reviewers
  a ✓ is self-attestation, the mechanism table no longer claims it prevents
  false negatives, README no longer lists blind seeding as a component, and
  ROADMAP tracks the seeded-error variant as unbuilt.

- **Verdict vocabulary.** CHECK verdicts are now one of four values —
  `Fix`, `Skip:Compass`, `Skip:Cobra`, `Discard:Integrity` — instead of
  free-text "Fix / Skip (reason)". Every rejection names the governor that
  made it, so the Scorecard's per-governor counts are derivable from the
  review's own output. RQ3 found the framework's reproducibility claim
  unverifiable precisely because that attribution was not recorded.

### Changed

- **One-shot mode is the documented solo path.** `PROMPT.md` already
  permitted stating governors and proceeding when no human is available to
  agree, while Rule 1, `docs/governors.md`, and the README all said "no
  agreement = no analysis". The three now defer to one-shot mode, and its
  `[async — no PLAN confirmation]` tag is mandatory rather than a note.
  Calibration records which mode a review ran in.

### Fixed

- README documented three installation paths; two could not work. The
  Antigravity skill registration pointed at `.agents/skills`, a directory
  that has never existed in any commit, and the Python SDK snippet depended
  on that same registration. Both removed; the agentic section now says what
  actually ships.
- README advertised "deterministic tool integration" after 0.2.0 removed
  `scripts/` and declared Diffract prompt-only — the README contradicted its
  own release notes.
- ROADMAP listed the Antigravity skill driver as delivered. It never
  existed. This is the same defect 0.2.0 fixed for the shell scripts, one
  line above it on the same checklist; the audit missed it.
- The calibration success criterion shipped in 0.2.0 was one-directional
  and could be satisfied by silence: a reviewer producing zero stable
  claims passed vacuously, contradicting step 6 of The Test on the same
  page. In RQ3 the weakest reviewer would have been certified calibrated
  while missing all nine of the other reviewer's stable clusters. The
  criterion is now bidirectional and requires stable claims from both
  reviewers; Recording Results tracks both directions.
- `PROMPT.md` and `docs/anti-dishonesty.md` (Mechanism 4) still carried the
  pre-0.2.1 calibration criterion — one reviewer, one run, "zero new
  findings" — after `docs/calibration.md` was corrected. `PROMPT.md` is the
  self-contained file reviewers paste, so the correction reached no one
  until now.
- `PROMPT.md` referenced `SKILL.md` (never existed in any commit) and
  `.diffract.yaml` (the shipped example is `examples/diffract.yaml`, no
  leading dot), and linked to the pre-rename repository URL.
- Rule 6 required declaring partial coverage only when the artifact was too
  large to fit in one pass. `examples/diffract.yaml` ships `scope: pr` as the
  default and `PROMPT.md` directs agents to read it, so the common agentic
  run reviewed changed files only and triggered no disclosure obligation at
  all. Rule 6 now covers scope narrowed by config or by the user, and the
  config comment states that setting the key is not the disclosure.
- "Cold-Start Calibration" named two different procedures: writing 2-3
  domain invariants before reading code (`PROMPT.md`, rule 8 — the one that
  ships) and completing a seeded-bug challenge (`docs/anti-dishonesty.md`,
  mechanism 12.2 — which nothing generates). The second is now the
  **Calibration Challenge**, marked as an unshipped RQ2 design.
- Nothing-Found Verification asked whether a seeded bug in *each* lens's
  domain would have been caught, then required "at least one example" — one
  example satisfied the letter and tested one domain out of ten. It now
  requires an example per lens that reported no findings, matching
  mechanism 5, which was always scoped to a single lens's nothing-found
  round.

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
