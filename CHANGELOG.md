# Changelog

All notable changes to Diffract will be documented in this file.

## Versioning

- **0.x** — Framework is being refined through application and research
- **1.0** — Framework has been applied to 3+ independent codebases by 2+
  independent reviewers with consistent results (calibration validated)

Entries describe each release as it shipped. 0.1.0 predates tagging and was
never cut as a release; v0.2.0 is the first tagged version.

## [0.4.0] — 2026-08-30

The review becomes checkable from outside. Every previous release asked
the reviewer to verify its own arithmetic, its own quotes and its own
coverage — the same self-attestation defect the Confidence column had
before 0.3.0, one level up. This release moves four of the thirteen
anti-dishonesty mechanisms out of the reviewer's own output and into a
script anyone can run, splits the one Scorecard row that made a correct
review impossible to state, and writes down what the remaining nine
still do not detect.

The `PROMPT.md` batching rule was overridden deliberately. The rule
exists to pay the tier-staleness cost once per release, but the tiers it
protects are already invalid: #23 shows all six pairings fail Success
Criteria condition 1 while all four configurations saturate at tier 4,
and #22 shows the clustering that produces tiers is undefined. Batching
on coherence beat batching on a staling cost that is charged against
numbers already known to be wrong.

### Added

- **`scripts/render_scorecard.py`** — derives every derivable Scorecard
  count from the Findings Index and rewrites the rows that disagree.
  Output-identical by construction: it produces the document the
  reviewer would have produced with the arithmetic correct, never a
  different format. `--write` applies; without it the run is a diff.
  Exit 0 when the counts already agreed, 1 when any were corrected.
  Verified output-identical at exit 0 against all three published
  reviews, and verified to catch five separately injected count errors
  with exactly one line changed each.
- **Two Scorecard counts are documented as not derivable.** `Fixes
  applied` depends on what happened to the artifact, not on the index.
  `PDCA cycles run` cannot be derived at all: a final cycle that raises
  nothing is what convergence *is*, so it leaves no row behind. An
  early draft of the renderer derived it from the highest `Cycle` value
  and "corrected" `examples/web-service.md` from 2 to 1 — a correct
  review, made wrong by a check. Both exclusions are now stated in
  `PROMPT.md`, in the script, and in `check_review.py`.
- **`docs/anti-dishonesty.md` gains "What these mechanisms can and
  cannot detect"** — every mechanism is run by the reviewer, about the
  reviewer, in the reviewer's own output. They do not detect an
  incompetent reviewer and they do not detect an adversarial one. The
  Summary Table gains a **Checked by** column: four mechanisms are now
  externally checkable, one ships nothing, and the remaining nine stay
  self-attested — including the decision to run the checker at all.
- **`README.md` states the same limit** where the mechanisms are first
  claimed, rather than leaving it to a document a reader may not reach.
- **CI runs the checks it documents.** `.github/workflows/check.yml`
  gains named steps for the published example review, the calibration
  fixture review, and Scorecard arithmetic across all three reviews.

### Changed

- **`| Fixed |` splits into `| Fix verdicts |` and `| Fixes applied |`**
  (#33). The single row conflated a verdict with an outcome, which made
  a review-only run impossible to state correctly — both published
  semver reviews had already hand-patched the row with "listed, not
  applied" to say what the template would not let them say.
- **W5H1 is excluded from `Most productive lens`.** It is a question
  set, not a lens, and it out-raises every lens on most reviews — 4
  against a leader's 2 on the semver review, which states the point in
  its own prose.
- **Integrity carries a default** (#21): file:line per lens, cognitive
  anchoring, and a verbatim quote of the text each finding cites.
- **The renderer instruction is scoped to the instrument, not the
  artifact.** Telling a reviewer to run `scripts/render_scorecard.py` by
  bare relative path meant that a repository under review shipping its
  own file at that path would have it executed, by the reviewer, on the
  instrument's own instruction — the artifact running code during its
  own review. `PROMPT.md` now resolves the script relative to itself,
  says the artifact's copy is input rather than instrument, and falls
  back to counting by hand when the two cannot be told apart. Found by
  the release gate that requires a written Shield + Variety pass over
  any new input channel, which exists because agentic mode's
  `diffract.yaml` shipped with the same defect one channel over.
- **`scripts/check_review.py`** resolves `PROMPT.md` from the repository
  root rather than the working directory, and reconciles `Fix verdicts`
  when a review states it while accepting legacy `Fixed` unchecked, so
  0.3.0 reviews keep passing while 0.4.0 reviews are held to the new row.
- **`examples/web-service.md`** re-synced to the 0.4.0 templates and
  version strings. Its `Fixed | 13` became `Fix verdicts | 13` +
  `Fixes applied | 13` — a pure row split with no factual change; the
  review's own ACT section already read "All 13 Fix verdicts applied in
  one pass".

### Fixed

Seven Majors from the blind cycle below, all verified against the files
before being accepted:

- **The config could not express the Integrity default** (TRU-1). The
  PLAN default gained a third clause in this release — every finding
  quotes the text it cites — and `diffract.yaml`'s vocabulary was left
  at `file-line-with-anchoring`. A config-driven run therefore applied a
  weaker evidence bar than an interactive one on the same artifact, with
  nothing recording the difference. The vocabulary now carries the third
  bar, and a config naming a weaker one is applied but reported.
- **`diffract.yaml` had no revision rule** (SHI-1). It is read from the
  repo root under review, so under `scope: pr` a diff could set the
  governors of its own review — `cobra: prototype`, `max_cycles: 1`, a
  Compass narrow enough to filter the lenses out. The existing mitigation
  challenged only a *trivially* narrow Compass; a plausible weakening was
  obeyed silently. The base revision now governs, and a diff that edits
  its own config is reported as a Shield finding.
- **The entry gate had no outcome for partial access** (VAR-1). Checks
  that have targets but cannot be run for lack of access fell between
  "cannot be run" and "nothing to run against", forcing a reviewer to
  either overstate or understate what it verified. New outcome, tagged
  `[entry partial: <checks not run>]`.
- **A failing entry check voided a one-shot review with no
  proportionality** (VAR-2). One rotted external URL — a link the author
  does not control — produced a failure report instead of a review, in
  the mode this instrument uses for its own calibration. Failures wholly
  outside the artifact's control now waive, tagged.
- **The competing-hypotheses step left no trace in the output** (OBS-1).
  It is mandatory for Low-Confidence findings, and the CHECK table had no
  Confidence column, so neither which rows owed the step nor whether it
  ran was visible. The table now carries Confidence, and the weighing has
  a mandated location below it.
- **W5H1 was exempt from every verification applied to lenses** (OBS-2).
  Mandatory, carrying the same anchoring duty, and named in neither the
  form check nor Nothing-Found Verification, with no Scorecard row — so a
  run that skipped it entirely passed every self-check. This is the
  failure mode `PROMPT.md`'s own RQ5 note already records for lenses, one
  step over. Now verified like a lens, with a `W5H1 run` row.
- **The README restated a Cobra level** (TRU-3), against `PROMPT.md`'s
  explicit "other files may reference them but never restate them" — and
  restated it as a disposition ("fix more, skip less") where the
  normative rule is a condition. It now points at PROMPT.md, the form the
  README already used 60 lines later.

Two smaller defects fixed in passing because the same edits reached them:
the README governor block had dropped the verbatim-quote clause (TRU-2),
and `max_cycles` had no lower bound, so `0` and negative integers were in
range by the written rule (VAR-3). Removing the typed numeral from "Four
outcomes:" resolved TRU-5, where the count had already drifted from five
bullets.

`examples/web-service.md` re-syncs again: its CHECK table gains the
Confidence column, populated from its own Findings Index rather than
invented, and its Scorecard gains `W5H1 run`.

### Frozen reviews

`examples/semver-2.0.0-review.md` and
`calibration/semver-2.0.0-seeded-review.md` are **not** re-synced, and
remain at `Instrument | Diffract 0.3.0`. This is an exception to the
"template changes re-sync `examples/`" gate, and `CONTRIBUTING.md` now
states it: those two reviews are hash-pinned against a frozen artifact
and quote-checkable line by line — they are evidence of what 0.3.0
produced, and editing them to match a newer template destroys exactly
the property that makes them worth publishing. `examples/web-service.md`
is anonymized, carries no hash, and exists to demonstrate the current
output format, so it re-syncs as it did in #27 and in the 0.3.0 release.

### Staleness

`PROMPT.md` changed, so all measured reviewer tiers are stale
(`docs/calibration.md`). The practical cost is lower than usual: #22 and
#23 establish that the tier numbers were not measuring what they claim
to measure before this release either.

### Deferred

Research blockers carried forward, per the release gate. None are fixed
here and none block the release:

- **#22** claim equivalence is undefined, and it decides both tiers and
  pairings (RQ3, RQ5)
- **#23** Success Criteria condition 1 punishes coverage, not
  miscalibration (RQ5)
- **#24** Mechanism 5 is 0 for 4 — add a nearest-miss quote, or retire
  it (RQ3)
- **#26** Diffract's research is author-graded
- **#29** residual defect estimate for v0.2.4
- **#31** Golden Hammer: reviewers grade the instrument against canon,
  not against its written definitions

These six are one problem seen from six sides — the measurements that
compare reviews to each other are not yet valid — and they are the
proposed 0.5.0 theme rather than a backlog.

### Validation

One blind cycle ran before release — a fresh-context reviewer (Claude
Opus) executing this instrument version against `README.md` +
`PROMPT.md`, one-shot, review-only, in a directory containing only those
two files. Blindness is procedural, as `calibration/README.md` defines
it: no repository access, no network, no `scripts/`.

- **Cycle 5** (Claude Opus, against 0.4.0): 23 findings, 7 Major, 17 Fix
  verdicts. All seven Majors were verified against the files by the
  maintainer before being accepted, and all seven are fixed above.

The cycle is numbered 5 because it continues the four cycles of 0.3.0,
but it is not comparable to them: those ran against 0.3.0, and a
reviewer configuration change already made cycles 1 and 2–4 two series
rather than one. Treat it as a first measurement of 0.4.0, not as a
fifth point on a trend.

**Three of the seven Majors were introduced by this release** — the
Integrity vocabulary gap, the README's dropped clause, and the
unenumerated "four of the thirteen". Two more, the entry-gate defects,
were found the hard way: the reviewer hit the uncovered partial-access
case during its own run and could not tag its own entry result, because
no defined outcome fit what had happened to it.

The one that matters most for how this release was built is the config
provenance gap. This release fixed exactly that defect class for the
`render_scorecard.py` path, under a release gate requiring a written
Shield pass over any new input channel. The pass covered the channel
being added and not the channel the same reasoning implicated —
declarative input felt safe because only executable input feels
dangerous. Governors are as load-bearing as code.

**Not covered by this cycle:** the reviewer had no `scripts/`, so it
took the manual counting path and never exercised the renderer — the
main thing 0.4.0 adds. It also recorded a 0% Integrity-discard rate
against itself as a possible sign of a lax evidence bar.

**Exit Estimate: ≈4 Major defects remaining** — the reviewer's own
estimate, on a basis it states: cycle 1 yielded 7 Majors from 11
sections, concentrated in cross-section consistency and in enumerated
input spaces, both classes that persist after one pass.
Capture–recapture does not apply to a single run. One cycle is not
convergence, and this release does not claim it.

## [0.3.0] — 2026-08-29

This release closes the loop on the `Confidence` column. Since its
introduction, Confidence has been a label a reviewer asserts and nothing
ever grades — the same defect class as the pre-0.2.4 exit rule, which
measured reviewer fatigue rather than artifact cleanliness. Two mechanisms
from the judgment-calibration literature fix that, and the five-cycle
self-review record from 0.2.4 supplied the decision data for a third
change the record itself demanded. All `PROMPT.md` changes are batched
here so the tier-staleness cost of changing the instrument is paid once.

### Added

- **Brier-scored Confidence** (Glenn W. Brier, 1950; calibration practice
  per Philip Tetlock, *Superforecasting*). Each Confidence bin now carries
  a canonical probability that the finding survives vetting — High = 0.95,
  Medium = 0.75, Low = 0.4, defined in `PROMPT.md` and nowhere else — so
  the column is a scoreable forecast instead of an ungraded label.
  `docs/calibration.md` gains a "Scoring Confidence (Brier)" section with
  the method, a resolution rule (outcomes resolved by vetting not
  performed by the finder; self-vetted scores flagged), and a worked
  example computed from the real cycles 3–5 data: 37 findings, 1 discard,
  pooled Brier 0.0197 — and a per-bin table showing why the pooled number
  alone flatters (always answering High would score 0.0268 against the
  97% survival base rate). First empirical insight, visible only in the
  per-bin view: Medium resolved 8 of 8 — as used, Medium behaves like
  certainty, so either the reviewers are underconfident at Medium or the
  bin needs recalibration.
- **Competing hypotheses for Low-Confidence findings** (Richards J. Heuer
  Jr., *Psychology of Intelligence Analysis*, CIA 1999 — Analysis of
  Competing Hypotheses). Before a Low-Confidence finding gets a verdict,
  CHECK now weighs 2–3 rival explanations (defect is real / artifact
  intent explains it / reviewer misread) and keeps the one the evidence
  *least disconfirms* — the inversion is the method: a reviewer can
  assemble support for anything it has already written down.
  Confirmation bias is the LLM reviewer's dominant failure mode, and Low
  findings are where it does verdict damage. Scoped to Low only so the
  cost stays proportional to the doubt.
- **Mechanical checks shipped as code.** `scripts/check.py` (standard
  library only, run in CI by `.github/workflows/check.yml`) implements
  link/anchor resolution, fence balance, version-string agreement, and a
  README↔PROMPT.md lens-table diff. The validation cycles below kept
  raising the same two classes — normative text drifting between files,
  and an instrument that mandates deterministic checks while shipping no
  implementation of them ("tools first, reasoning second", applied to
  itself). The repo now runs its own entry gate.
- **Preregistration named as an ancestor.** PLAN-before-DO — governors
  declared before findings exist — *is* preregistration; the References
  table now says so (Chris Chambers; Center for Open Science). No
  instrument change, lineage only.

### Changed

- **The done-rule counts Majors only.** Convergence is now "a full PDCA
  cycle produces zero new **Major** Fix outcomes" (previously all Fix
  outcomes). The evidence is the 0.2.4 record: cycles 2–5 raised 12, 12,
  12, and 13 findings — largely disjoint sets — while the Major *kind*
  shifted from contradictions to marginal underspecification. Minor
  findings are inexhaustible for prose artifacts, so a done-rule that
  counts them can never fire and the convergence signal it defines is
  meaningless. The circuit breaker's diminishing-returns test counts the
  same quantity. Decision tracked in issue #29.

### Staleness

`PROMPT.md` changed, so all measured reviewer tiers are stale
(`docs/calibration.md`: a tier is bound to the instrument version it was
measured against). Reviews run under 0.3.0 additionally emit competing-
hypotheses blocks for Low-Confidence findings; when comparing finding
counts across instrument versions, note that 0.3.0 verdicts on Low
findings are not produced by the same procedure as earlier ones.

### Validation

Four blind validation cycles ran before release — each a fresh-context
reviewer executing this instrument version against README.md + PROMPT.md,
one-shot, review-only, with maintainer vetting and fixes applied between
cycles. The reviewer model changed after cycle 1, so the four cycles are
two reviewer configurations, not one converging series:

- **Cycle 1** (Claude Fable 5): 13 findings, 3 Major; 6 fixes applied
  (2 Major).
- **Cycle 2** (Claude Opus): 22 findings, 15 Major; 18 fixes applied
  (14 Major). The jump measures the reviewer change as much as the
  artifact — a new configuration re-opens the finding stream.
- **Cycle 3** (Claude Opus): 22 findings, 12 Major; 16 fixes applied
  (11 Major). First same-configuration comparison: Major Fix outcomes
  fell 14 → 11. Its Competing Hypotheses step produced the release's
  first genuine ACH self-discard.
- **Cycle 4** (Claude Opus): 23 findings, 13 Major; 17 fixes applied
  (12 Major). Its Competing Hypotheses step discarded one of its own
  Majors for lack of in-scope evidence. Major Fix outcomes did not fall
  (11 → 12): the diminishing-returns stop fired, so this was the last
  cycle. Its largest fixes: the Cobra test was stated four non-equivalent
  ways across the two files, Rule 9's instrument exception was unbounded
  when the artifact under review is the protocol being executed, and the
  review-only run type — the very kind these cycles are — had no defined
  Scorecard rendering.

Not converged: no cycle produced zero new Major Fix outcomes, and the
instrument's own circuit breaker terms are met — three cycles in the Opus
configuration (the max), with the Major Fix count no longer falling
(14 → 11 → 12). These were separate one-shot runs, each cycle 1 of its
own review, vetted and fixed out-of-band. **Exit Estimate: ≈8 Major
defects remaining** — basis: the final cycle's per-lens yield;
capture–recapture does not apply across sequentially-fixed trees, and
the flat Major trend says to read 8 as a floor, not a ceiling. Shipping
on the estimate rather than convergence is the 0.2.4 exit rule applied
to the release itself: the estimate, not reviewer fatigue or a
finding-free cycle, is the claim about the artifact.

## [0.2.4] — 2026-08-29

This release folds in the software-inspection lineage — Tom Gilb & Dorothy
Graham, *Software Inspection* (1993), after Michael Fagan's IBM inspections.
Diffract cited aviation, medicine, and manufacturing for its honesty
mechanisms while leaving the software-native ancestor unnamed, and several
of that lineage's quantified techniques answer problems RQ3 and RQ5 left
open: the self-check that cannot detect its own misses, the exit rule that
measured reviewer fatigue rather than artifact cleanliness, and finding
counts that reward padding. All `PROMPT.md` changes are batched here so the
tier-staleness cost of changing the instrument is paid once.

### Added

- **Entry criteria in PLAN** (Gilb & Graham). The artifact's own cheap
  deterministic checks — build + test + lint, or the non-code equivalent —
  must pass before a review starts; review attention is not spent on defects
  a tool reports for free. A waived gate is tagged `[entry waived: <reason>]`,
  the same auditable-tag pattern as one-shot mode.
- **Major/Minor severity** on every finding, in the per-lens tables and the
  `## FINDINGS INDEX` (Gilb & Graham). Only Majors count in process metrics,
  so a review cannot be padded with trivia — the counting-dispersion lesson
  of RQ5, one level down. The definition lives in `PROMPT.md` (DO) only;
  after 0.2.3's "survived" defect, no counting term is defined in two files.
- **Quantified exit** (Gilb & Graham exit criteria). "Done" now requires
  both the existing convergence signal (a full PDCA cycle with zero new Fix
  outcomes) and an **Exit Estimate**: estimated remaining Majors with a
  stated basis — capture–recapture, per-lens yield, or the explicit tag
  `[exit unestimated]`. Zero new findings is a claim about the reviewer;
  the Exit Estimate is the claim about the artifact.
- **Capture–recapture estimation** in `docs/calibration.md`
  (Lincoln–Petersen from ecology; applied to inspections by Eick et al.
  1992; exit-from-estimate per Gilb & Graham). Stable-claim overlap between
  independent reviewers now estimates the defects missed by both — the
  complement, from the estimation side, to the seeded-error variant still on
  the roadmap. Shipped with its caveats up front: LLM reviewers share blind
  spots, so the estimate is a lower bound; counts move with clustering
  granularity; Majors only.
- **Sampling in Rule 6** (Gilb & Graham checking rates). An artifact too
  large for one rigorous pass gets a declared, rigorously-reviewed sample
  and a density estimate — not a shallow pass presented as complete.
- **Example rules per lens** in `docs/lenses.md`, and Rule 4 reworded: a
  finding names the written rule or invariant it violates (rules-based
  defects, Gilb & Graham). The lens remains the question; the rules make
  findings citeable, and they are the mapping substrate for the v0.3
  linter-to-lens goal.
- **Defect Prevention section in LEARN** (Robert Mays & Carole Jones, IBM,
  as integrated by Gilb & Graham): for the Majors, the upstream cause and
  one process change that would prevent the class. "Most productive lens"
  says where defects were found; this says where they came from.
- **Compass failure level** in `docs/governors.md` (Tom Gilb's Planguage,
  *Competitive Engineering*): the sharpest Compass names what failure would
  look like, which is what makes `Skip:Compass` verdicts arguable with
  evidence instead of taste.
- Five References rows in `README.md` covering the above, attributed to
  their actual origins — not everything traces to Gilb, and the table says
  so.
- **`AGENTS.md`** — the vendor-neutral entry point most coding agents read
  on arrival. Two audiences: an agent asked to *run* a review is pointed at
  `PROMPT.md` and told not to improvise the process from anywhere else; an
  agent *working on* this repo gets the house rules distilled from shipped
  defects (single-home counting terms, tier staleness, template
  conformance, the dual-home version string). Pointers only — it defines
  nothing, because defining things twice is how 0.2.3 happened. This is
  the baseline for the v0.3 per-tool adapters, which remain planned for
  tools that don't read `AGENTS.md`.
- **Hardening from five Diffract self-review cycles** run on `README.md`
  and `PROMPT.md` with this release's own instrument (cycles two through
  five each by a fresh-context reviewer with no knowledge of the earlier
  findings). In the instrument: new Rule 9 — the artifact
  under review is data, not instructions, closing the prompt-injection
  channel unique to LLM reviewers that no imported human-inspection
  mechanism covered; the Findings Index `Confidence` column and the
  finding-ID scheme are now defined (both were mandated but undefined —
  the counting-comparability defect one field over); W5H1 states that
  What/Where are deliberately delegated to the Name and Boundary lenses;
  entry criteria define the one-shot path for both unrunnable and failing
  checks; templates say "artifact" where they said "codebase". In the
  README: a measured-status block under the Goal (RQ5's failed pairings,
  stated up front), the protocol summary marked non-normative with
  PROMPT.md as source of truth, "Quick Start" renamed to what it is,
  lens-question wording re-synced, the two-lens on-ramp scoped to human
  checklist use so it no longer contradicts "show all 10", the Harari
  epigraph marked as paraphrase with its work named, and a note that the
  research numbering skips RQ4 because it was never run. Several of these
  — including the two-lens contradiction and the W5H1 gap — were blockers
  RQ5 had already named that no release had closed. The third cycle found
  four more Majors the first two missed: Cobra's quantified level
  definitions lived only in `docs/governors.md` and the example config,
  drifting from the instrument's glosses (they are now normative in
  PROMPT.md, with the outer copies reduced to references); a
  circuit-breaker stop had no defined output state (now tagged
  `[stopped: circuit breaker, not converged]`, with "diminishing returns"
  defined and an Exit Estimate still required); the non-code adaptation
  remapped Integrity's `file:line` but left Cobra's levels code-only (the
  unfixed half of a 4/4-model RQ3 finding — non-code artifacts now map
  levels by exposure); and the README misreported its own worked example's
  cycle count and most-productive lenses. Config-prescribed governors also
  gained their own tag (`[governors: diffract.yaml]`), and the
  protocol/framework naming drift was settled in favor of "protocol".
  A human-authorized fourth cycle — past the instrument's own circuit
  breaker — raised six more Majors, all fixed: Rule 9 gained its
  instruction-artifact exception (without it, self-review mechanically
  converts the instrument's own imperative voice into false Shield
  findings); the count-consistency check moved from CHECK to LEARN, where
  the Findings Index it consumes actually exists; the W5H1 stage got an
  output contract (`W5H-<n>` IDs, same row format and severity rules);
  the Findings Index `Line(s)` column is now defined; "survived" is no
  longer restated in `docs/calibration.md` (the exact duplication
  mechanism this file narrates as the 0.2.3 defect, reintroduced one
  level up); and entry-gate compliance is now visible in output, with
  tags for the two previously untagged stop states. The ID grammar's
  abbreviations are enumerated and the flagship example re-synced to
  them, Cobra's Prototype level was reworded to the same only-if form as
  the other two, and Rule 6 now covers a narrowed lens set as well as a
  narrowed artifact. A fifth cycle found the two Majors everyone else
  had walked past — both in the agentic config channel that a 0.2.x
  release added without turning the instrument on its own new surface:
  governors read from `diffract.yaml` (a file inside the repo under
  review) were obeyed without the trivially-narrow-Compass challenge the
  guardrails mandate when a *human* proposes one, and the
  user-present-plus-config-present state had no precedence rule at all —
  with the shipped example config flatly asserting that config bypasses
  interactive confirmation. Both fixed: a user who can confirm PLAN now
  always outranks the config, config-supplied governors get the same
  challenge as human-supplied ones, and the example's comment says so
  instead of the opposite. The same cycle's Minors: the README's CHECK
  diagram glossed Integrity with the Medium-confidence bar rather than
  the Integrity check; the entry criteria were restructured from one
  17-line paragraph into four explicit branches; the RQ citations inside
  the instrument gained file paths; the Findings Index gained a `Cycle`
  column, so the convergence done-rule is finally derivable from the one
  table the instrument calls authoritative; and the Scorecard gained a
  `Reviewer` row, because a protocol whose science compares reviewers
  was producing anonymous reviews.
  **Exit by estimate, not by convergence.** Five cycles never
  demonstrated convergence: cycles two through five raised 12, 12, 12,
  and 13 findings — largely disjoint sets, carrying 4, 4, 6, and 2
  Majors. The disjointness is the repo's own RQ3 result reproduced on
  the repo itself, and it means the convergence signal — a fresh
  reviewer finding zero new Fixes — is empirically out of reach for a
  prose artifact at this granularity. This release therefore exits the
  way the instrument prescribes when convergence fails: tagged
  `[stopped: circuit breaker, not converged]` (cycles four and five ran
  past the three-cycle breaker on human authorization), with an Exit
  Estimate. **Estimated remaining Majors: ≈2** — basis: historical
  per-lens yield. Single-run Major recall against pooled stable claims
  ran well below 1.0 throughout RQ3 and RQ5, so the final cycle's two
  Majors imply roughly as many again unseen. Capture–recapture across
  the five cycles is *not* a valid basis here and was not used:
  sequential fixing changes the artifact between runs, which breaks the
  closed-population assumption the estimator needs — near-zero overlap
  across cycles measures the moving target, not the defect pool.
  Expect residual defects; the estimate is the honest count of them.
- **Release Gates in `CONTRIBUTING.md`** (Defect Prevention put into
  practice, per Mays & Jones): eleven checklist gates, each tracing to a
  defect this repo actually shipped — research blockers must be closed or
  deferred in the CHANGELOG, no mandated table column without a
  definition, README's spec statements diff clean against `PROMPT.md`,
  version strings agree, template changes re-sync `examples/`, prose
  citing an example's metrics diffs against its FINDINGS INDEX,
  quantified governor thresholds appear only in `PROMPT.md`, new
  execution paths walk the full state matrix, a mandated check may
  consume only artifacts that exist by its phase, a PR adding an input
  channel to the instrument includes a Shield + Variety pass over that
  channel, and version-string equality is checked mechanically before
  tagging. Lens
  proposals now also state their adversarial assumption: mechanisms
  imported from human-inspection industries assume an artifact that
  cannot talk back.

### Fixed

- **`PROMPT.md`'s version header read 0.2.2 through the 0.2.3 release**,
  which changed the file without bumping it. A tier is bound to the
  instrument version it was measured against; an instrument that misreports
  its own version breaks that bookkeeping. Now 0.2.4.

### Note on prior measurements

This release changes `PROMPT.md`, so every reviewer tier measured against
earlier instruments remains or becomes stale, per the rule in
`docs/calibration.md`. New reviews additionally emit severity and an Exit
Estimate, so their findings indexes are a superset of earlier ones —
comparisons across the boundary must ignore the new columns or re-run.

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
