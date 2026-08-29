# Changelog

All notable changes to Diffract will be documented in this file.

## Versioning

- **0.x** — Framework is being refined through application and research
- **1.0** — Framework has been applied to 3+ independent codebases by 2+
  independent reviewers with consistent results (calibration validated)

Entries describe each release as it shipped. 0.1.0 predates tagging and was
never cut as a release; v0.2.0 is the first tagged version.

## [0.2.3] — 2026-08-29

Two counting defects found by re-running RQ3 and RQ5 against 0.2.2 — 22 runs,
same artifacts, same allocation, only the instrument changed. The three
mechanisms 0.2.2 shipped held (22/22 lens sections present, 22/22 parseable
findings index, every nothing-found lens the extractor saw carrying its
anchoring line). These are the two things the runs showed it got wrong.

### Fixed

- **`PROMPT.md` and `docs/calibration.md` defined "survived" differently.**
  The instrument said a finding survived if its verdict was `Fix`;
  `docs/calibration.md` said raised and not `Discard:Integrity`, with a
  governor skip counting, because verdict disagreement between reviewers is
  expected while failing the evidence bar is not. On one re-run those two
  rules gave 2 and 12 for the same review. 0.2.2 shipped the findings index
  to stop reviews counting by different rules and then reintroduced the same
  defect one level up, in the paragraph defining the terms. The instrument now
  carries `docs/calibration.md`'s definition, and **fixed** is named
  separately for the verdict-`Fix` count that the Scorecard already reports.
  `Fix` is described as *passing* all three governors, so "survives" carries
  one meaning in the file rather than two.

- **A review's Scorecard could contradict its own findings index, and
  nothing checked.** Three of the 22 runs did: one reported 23 findings and 15
  `Fix` over a table holding 20 rows and 16; one reported 25 over 26; one
  reported two `Discard:Integrity` verdicts that appear in no row of its
  table. The index is now stated as authoritative, every count elsewhere in
  the review is derived by counting its rows, and the mechanical form check in
  Nothing-Found Verification confirms they agree before verifying anything —
  a review whose Scorecard contradicts its index is recounted, not verified.
  The index is built before the Scorecard, since the Scorecard restates it.

### Note on prior measurements

This release changes `PROMPT.md`, so every reviewer tier measured against
0.2.2 — including the 22 runs that found these two defects — is stale, by
the same rule 0.2.2 applied to its predecessors. The finding that all four
reviewers measured tier 4 while all six pairings between them failed Success
Criteria condition 1 is a property of the criteria, not of an instrument
version, and is not addressed here.

## [0.2.2] — 2026-08-29

### Added

- **RQ5 — reviewer tiering** (`docs/research/rq5-reviewer-tiering.md`): 12
  independent reviews of `README.md` @ `22926ec`, three runs each across four
  models, testing whether the tier scale shipped in 0.2.1 separates reviewer
  configurations. It does not. All four configurations measured tier 4, and
  all six pairings between them then failed Success Criteria condition 1 —
  the framework issued two contradictory certifications from one dataset.
- **`## FINDINGS INDEX` is now required**, with *raised* (has a row) and
  *survived* (verdict `Fix`) defined against each other. `PROMPT.md` defined
  neither, so the twelve RQ5 runs used three different counting policies and
  the study's dispersion metric had to be recomputed before it meant
  anything. Comparing runs is what calibration is for.
- **A Contributing section in the README.** The Table of Contents linked to
  `#contributing` and no such heading existed, while `CONTRIBUTING.md`
  shipped in the repo unlinked. Found by 8 of the 12 RQ5 runs.

### Changed

- **A reviewer tier now binds to the artifact**, not only to the model,
  version, settings and `PROMPT.md` version. RQ5 measured four
  configurations ranging from 3 to more than 11 stable claims each as
  identically tier 4, because the artifact carried one easy defect. Artifact
  difficulty was an uncontrolled variable in a definition that claimed to
  name all of them. A tier reported without its artifact means nothing.
- **Tier 4 is documented as necessary, not sufficient**, for The Test. It
  gates entry; RQ5 shows it does not predict passing.
- **One ground-truth defect is an upper bound, not a measurement.**
  `docs/calibration.md` said an artifact needs "at least one" independently
  verified defect. One self-contained defect saturates the recall criterion.
  Separating tiers needs several defects at graded difficulty — tracked on
  the ROADMAP, not claimed as shipped.
- **"Survives CHECK" is defined** as raised and not `Discard:Integrity`;
  governor skips count, since verdict disagreement is expected and failing
  the evidence bar is not. Undefined, it moved one reviewer's recall between
  0 of 3 and 2 of 3 on the same run set.
- **Nothing-Found Verification checks form before it checks judgment.**
  Its first step is now mechanical: a lens that reported no findings without
  an "A finding would look like:" line has not produced Output B, and is
  re-run rather than verified, and the same step confirms all ten lens
  sections are present. In RQ5 one reviewer anchored none of its twelve
  nothing-found lenses across three runs and the mechanism passed all three,
  once while its own Truth lens had affirmed the defect under test — the third
  recorded instance of mechanism 5 certifying an error it exists to catch. A
  separate run silently reviewed 9 of the 10 lenses, omitting 🔗 Provenance,
  and nothing detected it: every check the framework runs afterwards is scoped
  to lenses that *reported*, and a lens never run reports nothing. It does not make the
  mechanism sound; it makes one failure mode detectable from the review's own
  output. Seeded-error verification remains unbuilt.
- Recording Results now carries a cluster map, so reported stability counts
  are re-derivable by someone who did not do the clustering.

### Fixed

- **The README lens table listed 9 of 10 lenses.** 🔗 Provenance was absent
  and Variety/Observability/Efficiency were numbered 7/8/9 against
  `PROMPT.md`'s 8/9/10 — two lines below a heading reading "Apply 10 lenses".
  This is the defect 0.2.0 claims to have fixed: its entry reads "Provenance
  missing from the lens count, the ROADMAP automation table, and the worked
  example". It reached the other two and the README was the only markdown
  file in the repo with no mention of the lens at all. The 0.2.0 entry
  overclaimed; this is the correction.
- **`docs/lenses.md` documented a Provenance evidence format that the
  instrument does not define.** Nine lenses show the `### <icon> <Lens>` /
  `Checked:` / findings-table form of Output A; Provenance alone still showed
  a pre-0.2.0 `Before:/Finding:/Risk:` block. A reviewer following it for
  that lens produced output `PROMPT.md` never specifies.
- **RQ3 was never listed in the README's documentation table** after shipping
  in 0.2.0, alongside RQ1 and RQ2. Both it and RQ5 are now listed.

### Note on prior measurements

Every reviewer tier recorded in `docs/calibration.md` and the research
documents is **stale as of this release**, because this release changed
`PROMPT.md` and a tier does not carry across instrument versions. That is the
rule working as written, not an oversight. RQ3's and RQ5's assignments stand
as records of method, not as usable measurements.

## [0.2.1] — 2026-08-29

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
