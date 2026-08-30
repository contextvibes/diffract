# Diffract Review — Semantic Versioning 2.0.0

> **This is an adoption review, not an assessment of the specification.**
> Diffract versions itself with Semantic Versioning. We follow this standard;
> we are not grading it. Every finding below marks a place where a team
> implementing against the text must make a call the text declines to make for
> them — not a defect, not a correction, and not a request that anything
> change. Nothing here has been or will be filed upstream. See
> [`examples/artifacts/README.md`](artifacts/README.md) for the artifact's
> provenance, license and hash.
>
> The review was produced blind: the reviewing agent saw only `PROMPT.md` and
> the artifact, with no repository access, no network and no sight of any
> prior review. Its form is machine-verified — every quote below is checked
> character-for-character against the cited lines by
> [`scripts/check_review.py`](../scripts/check_review.py).

`[async — no PLAN confirmation]`
`[fixes listed, not applied — convergence untested]`

---

## PLAN

### Entry criteria — deterministic checks

Review attention was not spent on anything a tool reports for free. The
artifact is prose + code fences; there is no build, test, or lint target. Each
applicable check is named below with its individual result.

| Check | Applicable | Result |
|-------|-----------|--------|
| Build | No — prose artifact, nothing to compile | n/a |
| Test | No — no test target in the artifact set | n/a |
| Lint | No — no configured linter for this artifact | n/a |
| Code fences balance | Yes | **Pass** — 6 fence markers at lines 149, 211, 345, 347, 356, 358; three matched pairs, none unterminated |
| In-document anchors resolve | Yes | **Pass** — vacuously: `grep` for `](#…)` returns zero in-document anchor links, so there are none to break |
| External links resolve | Yes | **Not run — no network access.** Six external references exist (lines 56, 343, 354, 364, 368, 373). None was dereferenced. Recorded in Gap Analysis. |
| Version strings agree across the artifact set | Yes | **Pass** — the artifact set is one file. Its only self-identifying version is the title `Semantic Versioning 2.0.0` (line 1); no second self-version string exists to disagree with it. The 40+ other `X.Y.Z` strings are illustrative examples, not declarations. |
| Whitespace hygiene | Yes | **Pass with one note** — one trailing space, line 144. No tab characters. Cosmetic; not raised as a finding (it changes no rendered output and is invisible to an adopting team). |

**Gate outcome:** this is PROMPT.md's fifth PLAN case — some checks ran, others
had nothing to run against, and one (external link resolution) could not be run
in this environment. The gate **passes on the checks that ran**. This is not an
entry waiver, and no `[entry waived: …]` tag is carried; the unrun link check is
recorded in the Gap Analysis instead of guessed at.

### Governors

```
Diffract: 0.3.0
🧭 Compass: We are adopting Semantic Versioning 2.0.0 for a Go library this
            quarter. Working only from this text, where will the team be left
            guessing — where must we make a call the specification declines to
            make for us?
🐍 Cobra:   library-framework
⚖️ Integrity: file:line per lens; cognitive anchoring required; every finding
            carries a verbatim quote block
```

These governors were prescribed verbatim by the orchestrating caller. No human
was available at the PLAN checkpoint to agree to them, and no `diffract.yaml`
was read (this run is scoped to a two-file directory). The run therefore carries
`[async — no PLAN confirmation]`.

**Governor challenge (Guardrails duty).** The Compass is narrow by design but is
not trivially narrow: it selects for *undecided decision points*, which is a
large and load-bearing class in a specification, and it does not filter the
review down to nothing — every one of the ten lenses returned at least one
finding under it. It does, however, exclude two classes I would otherwise raise:
editorial defects in the text (the line-144 trailing space; the `1.` repeated
ordered-list markers) and quality judgments about the specification as a
document. Those are `Skip:Compass` by construction and are named in the Gap
Analysis rather than being silently dropped.

**Cobra reading for this run.** `library-framework` asks: *will downstream
consumers have to change what they built on this?* Two distinct "downstreams"
exist here and conflating them would corrupt every verdict, so I fix the reading
now: (a) the world's projects that already built processes on the published text
of SemVer 2.0.0, and (b) the consumers of *our* Go library. Under this Compass
the remediation for a finding is a decision our team records in its own release
policy — **not an edit to `semver-2.0.0.md`**. Downstream (a) is therefore
untouched by nearly every finding, and Cobra does not skip on its account. Where
the remediation would instead change the contract our library publishes to
downstream (b), Cobra bites; that happens once, at EFF-1.

**Interaction-style note.** Rule 9 applies. The artifact is a specification
written in the imperative voice (RFC 2119 keywords, line 54-56). That voice is
its content, not an address to this reviewer; its MUSTs govern software that
adopts it, not this run. Nothing in the artifact attempted to alter this run's
governors, scope, severity, or output, so no Shield finding under Rule 9 was
raised.

---

## DO

### Cold-Start Calibration

Before reading the specification's rules, the invariants a version-numbering
scheme must satisfy for a dependency ecosystem to work at all:

1. **Determinism.** The next version number must be a function of the change
   set alone. Two maintainers of the same library, applying the rules to the
   same diff, must arrive at the same number. Any rule that admits maintainer
   discretion converts the version number from a fact into an opinion, and
   downstream constraint solvers cannot reason about opinions.
2. **Totality of ordering.** Every syntactically valid identifier must have a
   defined precedence relation to every other one. A resolver that encounters an
   undefined comparison has no correct behavior available to it.
3. **Immutability and unique denotation.** One released identifier denotes
   exactly one artifact, permanently. If an identifier can be re-pointed, every
   cached resolution downstream becomes unsound.

These three are what I held the text against. Invariant 1 is where the artifact
leaves the most decisions open; invariant 3 is where it is strongest and where
the residual gap is procedural rather than definitional.

---

### 🗑️ Subtract — Can I remove this entirely?

Checked: every construct the specification defines, asking which our Go library
could decline to use, and whether the text tells us what happens if we do —
build metadata (lines 104-110), pre-release versions (lines 93-102), the 0.y.z
phase (lines 70-71), and the FAQ's non-normative guidance (lines 246-358).

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| SUB-1 | semver-2.0.0.md | Build metadata is defined as fully optional and explicitly excluded from precedence, but the text states no purpose for it and places no obligation on either producers or consumers. The team must decide unilaterally whether to emit it, and — because the spec says two versions differing only in build metadata "have the same precedence" — what our library's own parser should do when it *receives* one: accept, strip, or reject. Nothing in the text makes any of the three wrong. | 104-110 | Minor | High |

Evidence:
- SUB-1 — examples/artifacts/semver-2.0.0.md:104-110
  > 1. Build metadata MAY be denoted by appending a plus sign and a series of dot
  > separated identifiers immediately following the patch or pre-release version.
  > Identifiers MUST comprise only ASCII alphanumerics and hyphens [0-9A-Za-z-].
  > Identifiers MUST NOT be empty. Build metadata MUST be ignored when determining
  > version precedence. Thus two versions that differ only in the build metadata,
  > have the same precedence. Examples: 1.0.0-alpha+001, 1.0.0+20130313144700,
  > 1.0.0-beta+exp.sha.5114f85, 1.0.0+21AF26D3\-\-\-\-117B344092BD.

Rule/invariant violated: cold-start invariant 2 in its weak form — the ordering
is total, but "equal precedence, different string" leaves the *selection* rule
between two equally-ranked candidates undefined, and the text assigns the
decision to no one.

---

### ✂️ Simplify — Can this be simpler without losing capability?

Checked: the three increment rules (lines 77-91) clause by clause, counting the
distinct obligations bundled into each and separating MUST from MAY.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| SIM-1 | semver-2.0.0.md | Rule 7 bundles four obligations of three different strengths into one paragraph, and one of them — "It MAY be incremented if substantial new functionality or improvements are introduced within the private code" — supplies no threshold for "substantial" and no criterion for exercising the MAY. Two maintainers on our team will classify the same internal refactor differently and both will be compliant. The team must write down the threshold itself, or accept that the minor digit stops being a function of the change set. | 83-85 | Major | High |

Evidence:
- SIM-1 — examples/artifacts/semver-2.0.0.md:83-85
  > incremented if any public API functionality is marked as deprecated. It MAY be
  > incremented if substantial new functionality or improvements are introduced
  > within the private code. It MAY include patch level changes. Patch version

Rule/invariant violated: cold-start invariant 1 (determinism). A permissive MAY
whose trigger word is unquantified makes the next version a maintainer opinion.

---

### 🏷️ Name — Does the name match the thing?

Checked: every identifier the specification lets an adopter mint — pre-release
identifiers (lines 93-102), build identifiers (lines 104-110) — against what the
name is required to communicate, plus the precedence examples (lines 144-145).

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| NAM-1 | semver-2.0.0.md | Pre-release identifiers are constrained in character set and in ordering, but carry no required meaning: the spec's own examples include `1.0.0-x.7.z.92` and `1.0.0-0.3.7`, names that describe nothing about the release. The familiar `alpha < beta < rc` ordering shown at lines 144-145 holds only because those words happen to sort that way in ASCII — the spec never blesses that vocabulary. Our team must invent its own pre-release vocabulary and verify by hand that it sorts in the intended order; choosing one that does not (e.g. `rc` before `beta` alphabetically is false, but `pre` after `rc` is a real trap) is silently non-compliant with the team's own intent while remaining fully valid SemVer. | 101-102 | Major | High |

Evidence:
- NAM-1 — examples/artifacts/semver-2.0.0.md:101-102
  > normal version. Examples: 1.0.0-alpha, 1.0.0-alpha.1, 1.0.0-0.3.7,
  > 1.0.0-x.7.z.92, 1.0.0-x-y-z.\-\-.

Rule/invariant violated: the artifact's own stated goal that "version numbers
and the way they change convey meaning" (lines 47-49) — the pre-release segment
is exempted from that goal without saying so.

---

### 📌 Truth — Is this knowledge in exactly one place?

Checked: the increment rules, which are stated three times — Summary (lines
7-12), Introduction (lines 42-45), and normative section 6-8 (lines 77-91) —
compared clause by clause; plus the numeric-advancement rule at line 65 against
the reset clauses at lines 86 and 90-91.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| TRU-1 | semver-2.0.0.md | "Each element MUST increase numerically" appears to conflict with the MUST-reset clauses at lines 86 and 90-91, under which minor and patch elements decrease to 0. A reader must decide which reading governs. | 62-65 | Minor | Low |
| TRU-2 | semver-2.0.0.md | The minor-increment rule is stated twice with different scope. The Introduction says "backward compatible API additions/changes increment the minor version"; normative rule 7 (lines 81-82) says minor MUST be incremented only "if new, backward compatible functionality is introduced". A backward-compatible *change* that adds no functionality — relaxing a parameter type, widening an accepted input, tightening a returned error's specificity — is a minor bump under the Introduction and a patch under rule 7. The team must decide which of the two co-resident statements binds it, and that decision recurs on a large fraction of real Go pull requests. | 42-45 | Major | Medium |

Evidence:
- TRU-1 — examples/artifacts/semver-2.0.0.md:62-65
  > 1. A normal version number MUST take the form X.Y.Z where X, Y, and Z are
  > non-negative integers, and MUST NOT contain leading zeroes. X is the
  > major version, Y is the minor version, and Z is the patch version.
  > Each element MUST increase numerically. For instance: 1.9.0 -> 1.10.0 -> 1.11.0.

- TRU-2 — examples/artifacts/semver-2.0.0.md:42-45
  > number. Consider a version format of X.Y.Z (Major.Minor.Patch). Bug fixes not
  > affecting the API increment the patch version, backward compatible API
  > additions/changes increment the minor version, and backward incompatible API
  > changes increment the major version.

Rule/invariant violated (TRU-2): single-source-of-truth. The same rule is
written in two places at two different scopes and neither is marked as the
subordinate restatement.

---

### 🧱 Boundary — Can an isolated change stay in one boundary?

Checked: the definition of the boundary the whole scheme is built on — the
public API (lines 58-60, 73-75) — and every place the spec tells an adopter how
to determine whether a change crosses it.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| BOU-1 | semver-2.0.0.md | The specification requires a public API to be declared and requires it to be "precise and comprehensive", but never supplies a criterion for what belongs inside the boundary. Every increment rule (lines 77-91) is expressed in terms of this undefined boundary, so the team must define it for our Go library construct by construct before any of those rules can be applied: whether adding a field to an exported struct breaks unkeyed literals, whether adding a method to an exported interface breaks external implementers, whether an exported error's message text is API, whether struct field ordering or `//go:build`-gated symbols count. The spec makes none of these calls, and each one changes which digit we bump. | 58-60 | Major | High |

Evidence:
- BOU-1 — examples/artifacts/semver-2.0.0.md:58-60
  > 1. Software using Semantic Versioning MUST declare a public API. This API
  > could be declared in the code itself or exist strictly in documentation.
  > However it is done, it SHOULD be precise and comprehensive.

Rule/invariant violated: cold-start invariant 1. A rule stated over an undefined
set is not a function; the determinism of every downstream rule inherits the
looseness of this one.

---

### 🛡️ Shield — Does it neutralize all inputs violating its invariants?

Checked: the artifact's three validation surfaces — the prose constraints (lines
93-110), the BNF grammar (lines 149-211), and the two regular expressions (lines
346 and 357) — asking which one an implementer is to treat as authoritative when
rejecting malformed input.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| SHI-1 | semver-2.0.0.md | The artifact ships three overlapping definitions of "valid version string" — prose MUSTs, a normative-looking BNF grammar at lines 149-211, and two regexes at lines 346 and 357 offered under a heading that calls them merely "suggested" — and never states which one governs, nor asserts that they agree. The team must pick one to implement our parser against, and must decide what our library does with a string that one surface accepts and another rejects. Choosing the regex means our accept-set is defined by a copied-in expression whose equivalence to the grammar we would have to prove ourselves; choosing the grammar means our validator differs from the ecosystem's most-copied artifact. | 337 | Major | Medium |

Evidence:
- SHI-1 — examples/artifacts/semver-2.0.0.md:337
  > ### Is there a suggested regular expression (RegEx) to check a SemVer string?

Rule/invariant violated: a specification's accept-set must have exactly one
definition. Three co-resident definitions with no stated precedence order push
the reconciliation onto every implementer independently.

---

### 🔗 Provenance — Can I verify the origin and integrity of every dependency?

Checked: every external reference the artifact makes (lines 56, 343, 354, 364,
368, 373), and the artifact's own self-identification (line 1), asking what an
adopting team can pin and cite.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| PRO-1 | semver-2.0.0.md | The adoption instruction directs the team to "Link to this website from your README", but no URL for "this website" appears anywhere in the artifact. Working only from this text, the team must decide what URL to publish as the authority its release policy is bound to — and a README pointing at the wrong or a mirrored copy silently changes which rules the project claims to follow. | 242-244 | Minor | High |
| PRO-2 | semver-2.0.0.md | The artifact identifies itself only by the version string in its title. It carries no date, revision, or content hash, and the adoption procedure is "declare that you are doing so" — so there is no mechanism by which our project can record *which text* of SemVer 2.0.0 it adopted. If the published document is later edited without a version bump, our declaration silently re-points at a different set of rules. The team must decide whether to vendor a pinned copy or accept an unpinnable dependency. | 1 | Minor | High |

Evidence:
- PRO-1 — examples/artifacts/semver-2.0.0.md:242-244
  > Versioning is to declare that you are doing so and then follow the rules. Link
  > to this website from your README so others know the rules and can benefit from
  > them.

- PRO-2 — examples/artifacts/semver-2.0.0.md:1
  > Semantic Versioning 2.0.0

Rule/invariant violated: a normative dependency must be identifiable to a fixed
revision. The version number in the title is the only identifier, and by the
document's own rule 3 (lines 67-68) an unchanged identifier implies unchanged
contents — a rule the specification imposes on its adopters but does not visibly
bind itself with.

---

### 🎯 Variety — Does every possible input map to a defined output?

Checked: the increment rules' guard conditions (`x > 0` at lines 77 and 81,
`X > 0` at line 88) against the full space of (current version, change kind)
inputs; and the definition of "bug fix" (lines 78-79) against the definition of
"backward incompatible" (lines 88-89) for changes that are both.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| VAR-1 | semver-2.0.0.md | Rules 6, 7 and 8 are all guarded on a major version above zero, and rule 4 says only that "Anything MAY change at any time" during 0.y.z. There is therefore no normative mapping from any change kind to any increment while the library is pre-1.0 — the entire initial-development phase is unspecified. The FAQ's "increment the minor version for each subsequent release" (lines 251-252) is advice, not a MUST, and does not distinguish breaking from non-breaking. Our team must author its own 0.y.z increment policy from scratch, and must decide what our published version numbers mean to consumers during exactly the period when the API is least stable. | 70-71 | Major | High |
| VAR-2 | semver-2.0.0.md | A change that both fixes incorrect behavior and breaks a consumer who depended on that behavior satisfies rule 6's definition of a bug fix (MUST patch) and rule 8's definition of a backward incompatible change (MUST major) simultaneously. Two MUSTs map one input to two outputs, and the specification's only treatment of the collision — "Use your best judgment" at line 306 — declines to resolve it. In Go this is the common case for a bug fix, not the exotic one. The team must define the tie-break rule itself. | 77-79 | Major | High |

Evidence:
- VAR-1 — examples/artifacts/semver-2.0.0.md:70-71
  > 1. Major version zero (0.y.z) is for initial development. Anything MAY change
  > at any time. The public API SHOULD NOT be considered stable.

- VAR-2 — examples/artifacts/semver-2.0.0.md:77-79
  > 1. Patch version Z (x.y.Z | x > 0) MUST be incremented if only backward
  > compatible bug fixes are introduced. A bug fix is defined as an internal
  > change that fixes incorrect behavior.

Rule/invariant violated: cold-start invariant 1 (determinism) in both cases —
VAR-1 by leaving a region of the input space unmapped, VAR-2 by mapping one
input to two conflicting defined outputs.

---

### 🔍 Observability — Can I determine system state from outputs?

Checked: what a consumer of our library can infer about a release from the
version number alone, given the permissive MAY clauses at lines 83-85 and 89 and
the deprecation obligation at line 83.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| OBS-1 | semver-2.0.0.md | A version increment is not a sufficient statement of what changed, and the specification requires no supplementary signal. A major bump "MAY also include minor and patch level changes", so it does not disclose whether the API also grew; a minor bump may be new API, a private-code improvement, or a deprecation-only release (line 83) — all three are indistinguishable from the number. The team must decide what additional machine- or human-readable signal we publish (changelog format, deprecation markers, migration notes) and commit to it, because the version number alone cannot tell a consumer whether an upgrade requires action. | 88-89 | Major | High |

Evidence:
- OBS-1 — examples/artifacts/semver-2.0.0.md:88-89
  > 1. Major version X (X.y.z | X > 0) MUST be incremented if any backward
  > incompatible changes are introduced to the public API. It MAY also include minor

Rule/invariant violated: the artifact's stated purpose that version numbers
"convey meaning about the underlying code and what has been modified" (lines
47-49). The MAY-inclusion clauses make the number a lower bound on what changed,
not a description of it, and no compensating signal is specified.

---

### ⚡ Efficiency — Is resource use proportional to work required?

Checked: the bounds the specification places on inputs a conforming parser must
accept — string length (lines 323-327), pre-release identifier count (lines
141-142), and numeric identifier magnitude (lines 62-64, 184-186).

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| EFF-1 | semver-2.0.0.md | The specification sets no bound on version-string length, on the number of dot-separated pre-release identifiers, or on the magnitude of a numeric identifier — the grammar at lines 184-186 admits arbitrarily long digit strings, which overflow a fixed-width integer parse. "Use good judgment" and "255 character version string is probably an overkill" are advice with no number in them. Our parser must therefore choose its own limits, and the team must decide them: what length we cap at, and whether we parse major/minor/patch into `uint64` (rejecting spec-valid input) or into a big integer. | 325-327 | Minor | High |

Evidence:
- EFF-1 — examples/artifacts/semver-2.0.0.md:325-327
  > No, but use good judgment. A 255 character version string is probably an overkill,
  > for example. Also, specific systems may impose their own limits on the size of
  > the string.

Rule/invariant violated: a parser's resource use must be bounded by a stated
input bound. With no bound stated, cost is bounded only by whatever the caller
supplies.

---

### ❓ W5H1 — What's missing?

Checked: the artifact for missing rationale (Why), missing ownership (Who),
missing expiry/timeouts/edge cases (When), and golden-hammer technology choices
(How), after all ten lenses.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| W5H-1 | semver-2.0.0.md | **Who.** The artifact names an original author and a feedback channel, but names no current owner, maintainer, or body empowered to settle an interpretation dispute. An adopting team that reads two clauses as conflicting has no authority to appeal to and no stated turnaround for getting an answer. | 367-368 | Minor | High |
| W5H-2 | semver-2.0.0.md | **When.** The deprecation window is unspecified. Rule 7 makes marking something deprecated a MUST-minor event (line 83), but the only statement of how long a deprecated symbol must survive before removal is the FAQ's "there should be at least one minor release" — a SHOULD-strength floor of one release, with no calendar time and no upper bound. The team must decide our actual deprecation window (how many releases, how many months, whether an unadopted deprecation blocks the major bump), because "one minor release" can mean a week. | 319-321 | Major | High |
| W5H-3 | semver-2.0.0.md | **Why.** Rule 3 forbids modifying a released version's contents and gives no rationale, which leaves its scope undecidable at exactly the moment it matters: it does not say whether *withdrawing* a release — unpublishing, retracting, marking a version unusable — counts as a modification. The FAQ's remedy for a bad release is to ship a corrective patch and "document the offending version" (lines 285-292), which neither permits nor forbids retraction. The team must decide our policy for a release that must not be consumed, before we need it. | 67-68 | Major | High |
| W5H-4 | semver-2.0.0.md | **How (tech-stack neutralization).** The FAQ steers implementers toward a single 200-character regular expression, advertised as compatible with Go, and points at a third-party interactive site for it — while the same document already contains a complete BNF grammar (lines 149-211) that a hand-written recursive parser implements in a few dozen lines of standard-library Go with better error messages and no dependency on a copied opaque expression. The regex is the golden hammer here, not the simpler option. The team must decide which to build against; the artifact presents the regex as the convenient default without comparing the two. | 349-352 | Minor | Medium |

Evidence:
- W5H-1 — examples/artifacts/semver-2.0.0.md:367-368
  > If you'd like to leave feedback, please [open an issue on
  > GitHub](https://github.com/semver/semver/issues).

- W5H-2 — examples/artifacts/semver-2.0.0.md:319-321
  > in place. Before you completely remove the functionality in a new major release
  > there should be at least one minor release that contains the deprecation so
  > that users can smoothly transition to the new API.

- W5H-3 — examples/artifacts/semver-2.0.0.md:67-68
  > 1. Once a versioned package has been released, the contents of that version
  > MUST NOT be modified. Any modifications MUST be released as a new version.

- W5H-4 — examples/artifacts/semver-2.0.0.md:349-352
  > And one with numbered capture groups instead (so cg1 = major, cg2 = minor,
  > cg3 = patch, cg4 = prerelease and cg5 = buildmetadata) that is compatible
  > with ECMA Script (JavaScript), PCRE (Perl Compatible Regular Expressions,
  > i.e. Perl, PHP and R), Python and Go.

---

## CHECK

### Competing Hypotheses — TRU-1 (Low Confidence)

TRU-1 is the run's only Low-Confidence finding and receives the competing-
hypotheses step before its verdict.

*Observation:* line 65 says "Each element MUST increase numerically", while
lines 86 and 90-91 require minor and patch elements to be reset to 0 — a
decrease.

- **H1 — the defect is real.** Two MUSTs contradict; an adopting team must
  choose a reading, and a tool author implementing line 65 literally would
  reject a compliant `1.9.0 → 2.0.0` transition.
- **H2 — the artifact's intent explains the observation.** Line 65's own
  worked example is `1.9.0 -> 1.10.0 -> 1.11.0`: a sequence about a *single*
  element advancing, and specifically about it advancing numerically rather than
  lexically (9 → 10, not 9 → 91). Read that way the sentence constrains how one
  element advances within its own run, and says nothing about sibling elements
  at a bump — leaving the reset MUSTs uncontradicted.
- **H3 — the reviewer misread.** Line 65 could be read as scoped to the
  immediately preceding sentence about form and leading zeroes.

*Discriminating evidence:* the worked example on line 65 itself. It shows a
minor element going 9 → 10 → 11 while major stays 1 and patch stays 0 — an
example that is only informative under H2's reading, and that under H1's reading
would be a strange choice (it demonstrates nothing about a contradiction it
allegedly creates). Additionally, the reset rules at lines 86 and 90-91 are
stated explicitly, at MUST strength, and later in document order — a reader
reaching them is not left guessing. H1 is the hypothesis this evidence most
disconfirms; H2 survives least disconfirmed.

*Consequence:* the claim "the team must decide how to read this" is not
established. Verdict follows the surviving hypothesis: `Discard:Integrity`. The
finding stays in the index as raised-and-discarded, per PROMPT.md's counting
rule.

### Verdict table

| Finding | ⚖️ Integrity | 🧭 Compass | 🐍 Cobra | Verdict |
|---------|-------------|-----------|---------|---------|
| SUB-1: build metadata optional with no stated purpose or consumer obligation | Looked at lines 104-110; quoted verbatim; claim is about what the text omits, not about taste | Yes — "emit it or not, accept it or not" is a call we must make | Recording a build-metadata policy changes nothing for consumers of our library or of the spec | `Fix` |
| SIM-1: "substantial" private-code improvement has no threshold | Looked at lines 81-86; quoted; the missing quantifier is textual, not inferred | Yes — decides a real minor-vs-patch call on our own PRs | Writing our threshold down breaks no published contract | `Fix` |
| NAM-1: pre-release identifiers carry no required meaning or blessed vocabulary | Looked at lines 93-102 and 144-145; quoted the spec's own meaningless examples | Yes — we must choose a pre-release vocabulary before our first RC | Choosing our own vocabulary is internal | `Fix` |
| TRU-1: "each element MUST increase" vs the reset MUSTs | Competing hypotheses run above; H2 survives; not established as a place the team is left guessing | not reached | not reached | `Discard:Integrity` |
| TRU-2: Introduction's "additions/changes" is broader than rule 7's "new functionality" | Looked at lines 42-45 against 81-82; both quoted; the scope difference is on the page | Yes — governs a large class of Go PRs (widened inputs, relaxed types) | Deciding which restatement binds us is our policy, not a spec edit | `Fix` |
| BOU-1: "public API" required but never delimited | Looked at lines 58-60 and 73-75; quoted; no criterion appears anywhere in the text | Yes — this is the single largest call we must make, and every increment rule depends on it | Defining our own API surface is precisely what the spec instructs us to do; no contract broken | `Fix` |
| SHI-1: three validation surfaces, no stated precedence | Looked at lines 93-110, 149-211, 337-357; quoted the "suggested" framing | Yes — we must pick what our parser implements | Picking one for our implementation does not change what others built on the spec | `Fix` |
| PRO-1: "this website" has no URL in the artifact | Looked at lines 241-244; quoted; verified by grep that "website" occurs once and no URL accompanies it | Yes — we must decide what our README cites as the binding authority | Internal decision | `Fix` |
| PRO-2: artifact carries no date, revision, or hash to pin | Looked at line 1 and searched for any other self-identifier; none exists | Yes — vendor-a-copy vs. link-and-trust is a call we must make | Vendoring a copy for our own records affects no downstream | `Fix` |
| VAR-1: no increment rule applies below 1.0.0 | Looked at the guards on lines 77, 81, 88 and at rule 4; quoted | Yes — our library starts pre-1.0 this quarter; this is the first policy we need | Authoring a 0.y.z policy breaks nothing | `Fix` |
| VAR-2: a breaking bug fix satisfies two conflicting MUSTs | Looked at lines 77-79 against 88-89 and at the FAQ's "best judgment" punt; quoted | Yes — recurs on real bug fixes | Our tie-break rule is internal | `Fix` |
| OBS-1: the number does not disclose what changed | Looked at lines 83-85 and 89; quoted; the MAY-inclusion clauses are explicit | Yes — we must decide our changelog/deprecation signal | Adding our own changelog convention breaks nothing | `Fix` |
| EFF-1: no bound on string length, identifier count, or numeric magnitude | Looked at lines 141-142, 184-186, 323-327; quoted | Yes — our parser needs limits | **Bites.** Capping length or parsing into `uint64` makes our library reject strings the spec declares valid, breaking the contract our parser publishes to its consumers. The Cobra question — "will downstream consumers have to change what they built on this?" — answers yes for any cap tight enough to matter | `Skip:Cobra` |
| W5H-1: no named owner or interpretation authority | Looked at lines 360-368; quoted; no maintainer or governance statement exists | **Fails.** The Compass asks where *this text* forces our team to make a call. The spec's stewardship is a property of the document's governance, not a decision our release policy must record; we would resolve ambiguity internally regardless of who maintains the spec | not reached | `Skip:Compass` |
| W5H-2: deprecation window unspecified beyond "at least one minor release" | Looked at lines 313-321; quoted; the FAQ's floor is SHOULD-strength and countless in calendar time | Yes — we must set the window before our first deprecation | Setting our own window is internal | `Fix` |
| W5H-3: immutability rule silent on retraction | Looked at lines 67-68 and 285-292; quoted; neither permits nor forbids withdrawal | Yes — we must have a retraction policy before we need one | Our retraction policy is internal | `Fix` |
| W5H-4: regex presented as the default over the document's own grammar | Looked at lines 149-211 against 337-357; quoted the compatibility pitch | Yes — build-vs-copy is a call we make | Choosing a hand-written parser breaks nothing | `Fix` |

### Scope and Nothing-Found Verification

**Form check.** All ten lenses in the declared scope have a section, in
normative order, plus W5H1. Scope was not narrowed. **No lens produced Output
B** — every lens returned at least one finding under this Compass — so the
"A finding would look like:" verification has nothing to verify; that check is
vacuous for this run, not skipped. Per-section finding counts are: Subtract 1,
Simplify 1, Name 1, Truth 2, Boundary 1, Shield 1, Provenance 2, Variety 2,
Observability 1, Efficiency 1, W5H1 4 — total 17, matching the Findings Index
row count.

**Seeded-bug self-check.** For each lens: *if I deliberately introduced a bug in
this lens's domain, would my process have caught it?* Each example names a
defect different from that lens's DO-time finding.

| Lens | Seeded defect (different from this lens's finding) | Caught? |
|------|---------------------------------------------------|---------|
| 🗑️ Subtract | A duplicated FAQ entry answering the same question twice with different answers | Yes — I read the FAQ headings end to end (lines 249-357) and would have seen the repeat |
| ✂️ Simplify | Rule 11's precedence sub-clauses restated redundantly in both prose and grammar | Yes — I read lines 112-145 against 149-211 clause by clause while working SHI-1 |
| 🏷️ Name | The grammar naming a non-terminal `<version core>` in one place and `<core version>` in another | Yes — I read all 63 grammar lines; a non-terminal mismatch is visible on inspection |
| 📌 Truth | The Summary at lines 9-12 stating a different increment rule than rule 8 | Yes — I diffed all three restatements of the increment rules, which is how TRU-2 surfaced |
| 🧱 Boundary | A precedence rule placed inside the pre-release section instead of section 11 | Yes — I traced which section owns each rule while mapping the public-API boundary |
| 🛡️ Shield | The prose forbidding leading zeroes in build identifiers while the grammar at lines 176-177 admits `<digits>` | Yes — I compared prose constraints against the grammar productions and specifically checked this pair; they agree as written |
| 🔗 Provenance | An `https://` link with a typo'd host that no longer resolves | **Partially — no.** Link *presence* I checked by grep; link *resolution* I could not run without network. A dead-but-well-formed URL would pass this run. Recorded in Gap Analysis |
| 🎯 Variety | Rule 11.2 defining comparison for major/minor/patch but omitting the case where one version has a pre-release and the other does not | Yes — that case is covered at lines 124-127 and I enumerated the comparison cases to check it |
| 🔍 Observability | A rule requiring a changelog but never saying where it is published | Yes — I searched the text for any required supplementary signal; there is none, which is OBS-1's basis |
| ⚡ Efficiency | A precedence rule requiring comparison of pre-release identifiers right-to-left, forcing a full scan before any decision | Yes — I read lines 129-142 and the left-to-right requirement at line 131 is explicit |
| ❓ W5H1 | A missing license statement | Yes — the License section at lines 370-373 was read; its absence would have been visible |

One lens — 🔗 Provenance — returns a qualified "no" on this self-check. Per
PROMPT.md the process failed there rather than the artifact, and the correct
response is to re-run the lens. Re-running it without network access cannot
produce a different result, so the gap is carried into the Gap Analysis as an
unrun check rather than closed. PROMPT.md also warns that a ✓ in this table is a
prompt to look again, not evidence of cleanliness; RQ3 records four reviews
passing this step while missing a verified factual error.

### Stockholm & Hammer Audit

**Stockholm.** The strongest pull in this artifact is its FAQ, which answers
several of the hardest questions with "Use your best judgment" (line 306) and
"use good judgment" (line 325). Read sympathetically, those are an author's
honest acknowledgment that the cases are irreducible. I declined to adopt that
framing: under this Compass, an author's acknowledged discretion is exactly a
call the team must make, and VAR-2 and EFF-1 are raised on that basis rather
than being waved through as reasonable humility. Conversely, I did *not* let the
adversarial stance manufacture findings: the artifact's prose, grammar, and
regexes agree everywhere I compared them, and I say so above rather than
inventing a contradiction.

**Golden Hammer.** The suggested regex (lines 346, 357) is the artifact's one
piece of over-engineering-by-default, and W5H-4 challenges it directly rather
than accepting it because a regex is the familiar way to validate a string. I
also checked myself in the other direction: the BNF grammar at lines 149-211 is
not over-engineering — a 63-line grammar for a format with four regions is
proportionate, and I did not raise it as complexity for its own sake.

---

## LEARN

`[fixes listed, not applied — convergence untested]`

This is a review-only run commissioned by an orchestrating caller. No fixes were
applied, and none of the fixes below is an edit to `semver-2.0.0.md`: under this
Compass and the `library-framework` Cobra level, the remediation for every
finding is a decision our adopting team records in **its own** release policy.
Editing a published specification that thousands of projects have built
processes on is precisely what Cobra exists to prevent, and would not answer the
Compass's question in any case.

**Remediation target:** a new `RELEASING.md` in the Go library's repository. Each
entry below states the decision to record; the bracketed text is the recommended
default, which the team may overrule.

| ID | Decision to record in `RELEASING.md` |
|----|--------------------------------------|
| SUB-1 | Whether we emit build metadata, and what our parser does on receiving it. [Do not emit. Parse and preserve, ignore for ordering, never reject.] |
| SIM-1 | The threshold at which a private-code improvement earns a minor bump. [Never — private-code changes are patch unless they change documented behavior. This makes the minor digit mean "public API grew or something was deprecated", full stop.] |
| NAM-1 | The pre-release vocabulary and its verified ASCII ordering. [`alpha` < `beta` < `rc`, numbered; add nothing to the set without re-verifying the sort.] |
| TRU-2 | Whether a backward-compatible change that adds no functionality is minor or patch. [Patch — follow normative rule 7, not the Introduction's broader phrasing.] |
| BOU-1 | The enumerated definition of our public API surface, construct by construct: exported identifiers, struct fields and their unkeyed-literal exposure, interface method sets, error values vs. error strings, build-tagged symbols, and anything reachable via embedding. [Write this before the first release; it is the precondition for every other rule.] |
| SHI-1 | Which validation surface our parser implements. [The BNF grammar at lines 149-211, with the regex used only as a cross-check in tests.] |
| PRO-1 | The URL our README cites as the binding authority. |
| PRO-2 | Whether we vendor a pinned copy of the spec text alongside `RELEASING.md`. [Vendor it; the artifact offers no revision identifier to pin instead.] |
| VAR-1 | Our 0.y.z increment policy — specifically what a breaking change does to the version while below 1.0.0. [Breaking → minor; non-breaking → patch. Say so publicly, because the spec does not.] |
| VAR-2 | The tie-break when a change is both a bug fix and breaking. [Major, unless the behavior being removed was never documented as part of the public API defined under BOU-1.] |
| OBS-1 | The supplementary signal we publish per release. [A changelog with Added/Changed/Deprecated/Removed/Fixed sections, plus `Deprecated:` doc comments; the version number is a lower bound on what changed, not a description.] |
| W5H-2 | Our deprecation window. [At least two minor releases and 90 days before removal in a major.] |
| W5H-3 | Our policy for a release that must not be consumed. [Never modify or delete a published tag; publish a corrective release and a retraction notice in the changelog.] |
| W5H-4 | Parser implementation approach. [Hand-written recursive-descent over the BNF; no regex dependency.] |
| EFF-1 | *(`Skip:Cobra` — no fix.)* Recorded as a deliberate non-decision: our parser imposes no length or identifier-count cap, and parses numeric identifiers into a width wide enough that rejection is not observable. Revisit only if a denial-of-service path appears. |
| W5H-1 | *(`Skip:Compass` — no fix.)* Out of this review's goal. |
| TRU-1 | *(`Discard:Integrity` — no fix.)* Not established. |

### Verify — re-run of the PLAN entry checks

Re-run after LEARN, per PROMPT.md step 2. No fixes were applied to the artifact,
so the artifact is byte-identical to the one that entered the review; the checks
are re-reported rather than re-derived:

| Check | Result |
|-------|--------|
| Code fences balance | Pass — 6 markers, 3 pairs |
| In-document anchors resolve | Pass (vacuous — none exist) |
| External links resolve | Not run — no network access |
| Version strings agree | Pass — single self-version at line 1 |
| Whitespace hygiene | Pass with note (trailing space, line 144) |
| Build / test / lint | n/a — no target |

### Scorecard

| Metric | Value |
|--------|-------|
| Reviewer | claude-opus-5, Claude Code agent, blind single-run configuration |
| Artifact | `examples/artifacts/semver-2.0.0.md` — Semantic Versioning 2.0.0, 373 lines, reviewed in full |
| Instrument | Diffract 0.3.0 |
| Governors | 🧭 Adopting SemVer 2.0.0 for a Go library: where must the team make a call the specification declines to make? · 🐍 Library/Framework · ⚖️ file:line per lens, cognitive anchoring required, verbatim quote block per finding |
| Entry checks | Code fences balance: pass · In-document anchors: pass (none exist) · External links: not run (no network) · Version strings agree: pass · Whitespace hygiene: pass with note (line 144) · Build/test/lint: n/a (no target). Gate passed on the checks that ran; no waiver tag |
| Findings raised | 17 |
| Major findings raised | 10 |
| Fixed | 14 (verdict `Fix`; listed, not applied) |
| Cobra-skipped | 1 |
| Compass-skipped | 1 |
| Integrity-discarded | 1 |
| PDCA cycles run | 1 — converged: not testable (review-only) |
| Lenses run | 10 of 10 — none omitted; scope not narrowed |
| Most productive lens | 🎯 Variety (2 findings, both Major) — tied on raw count with 📌 Truth and 🔗 Provenance (2 each), but leading on Majors. W5H1 raised 4, more than any lens, but is not a lens |
| Estimated remaining Majors | 5 — basis: per-lens yield. 10 Majors across 11 sections in one cycle (0.91/section). PROMPT.md records that v0.2.x prose self-reviews produced 12-13 largely *disjoint* findings across four consecutive cycles, i.e. first-pass detection on prose artifacts is well under half; applying that to this run's 10 Majors gives roughly 5 more that a second independent pass would surface. This is a weak basis: no second cycle was run, so no decay is observable, and capture–recapture is unavailable with a single run (m undefined) |
| Calibration | not tested — a single run cannot be calibrated |
| Tags | `[async — no PLAN confirmation]` · `[fixes listed, not applied — convergence untested]` |

### Gap Analysis

| Gap | Reason | Recommendation |
|-----|--------|---------------|
| External link resolution (6 references: lines 56, 343, 354, 364, 368, 373) | No network access in this environment. PROMPT.md's entry criteria require every link to resolve; this check was not run and was not guessed at | Re-run a link checker against these six URLs before relying on any of them. PRO-1 and PRO-2 are consequences of what the *text* omits and stand regardless, but a dead RFC 2119 or regex101 link would be an additional, separate defect this run cannot see |
| 🔗 Provenance seeded-bug self-check | Failed for the same reason: a well-formed but dead URL would pass this run undetected | Re-run the Provenance lens in a networked environment |
| Editorial and formatting defects in the artifact | Excluded by the Compass, which asks only where the adopting team must make a call. Observed but not raised: the trailing space at line 144; the repeated `1.` ordered-list markers throughout sections 1-11 (valid Markdown, renders as 1-11) | If a separate editorial review of the artifact is ever commissioned, set a Compass that admits these |
| Whether the specification is *good* | Explicitly out of scope: this is an adoption review. No finding claims the specification is deficient — only that specific decisions are left to the adopter | Do not read the 10 Majors as a quality judgment on SemVer 2.0.0 |
| Conformance of the two regexes (lines 346, 357) to the BNF grammar (lines 149-211) | Establishing equivalence requires executing both against a generated corpus; no test runner was available and the artifact set contains no test target. SHI-1 raises the *undeclared precedence* between them, which is a textual fact, but not whether they actually diverge | Generate a corpus from the BNF and run both regexes against it before choosing an implementation |
| Interaction with Go's own module and versioning conventions | The Compass restricts the review to "working only from this text". Go-specific rules that exist outside the artifact were deliberately not imported as evidence | Reconcile `RELEASING.md` against the Go module system's own rules in a separate pass |
| Second independent run | Only one run exists, so capture–recapture cannot be computed and the Exit Estimate rests on a weak per-lens-yield basis | Commission a second independent run against the frozen artifact; with stable Major counts and overlap m > 0 the estimate becomes computable |

### Defect Prevention

The Major findings here are not defects an author "created" in the ordinary
sense — this is an adoption review of a frozen public specification, and the
upstream cause is a structural property of how normative specifications get
written. The process changes below are therefore addressed to the adopting
team's own specification and policy work, which is where they can actually bind.

| Major(s) | Upstream cause | Process change |
|----------|----------------|----------------|
| BOU-1, SIM-1 | Normative rules were written over terms the same document never delimits ("public API", "substantial"). The rule reads as precise because it contains a MUST, so the undefined term is never noticed at review time | Add a checklist item to our own spec/RFC template: every term appearing in a MUST or SHOULD clause must be either defined in the document or listed in an explicit "defined by the adopter" section. A term in neither category fails review |
| VAR-1, VAR-2 | Rules were written for the expected case and guarded (`x > 0`) without anyone enumerating the input space the guards exclude, and the collision between two MUSTs was discovered late and answered in an FAQ rather than in the rules | Require a decision-table appendix for any document that assigns outcomes to inputs: rows are input classes, columns are outcomes, and every cell must be filled or explicitly marked undefined. An empty cell is a review blocker. This is the single change that would have caught both |
| TRU-2, SHI-1 | The same normative content was restated for readability (summary, introduction, grammar, regex) with no marked authority order, so restatements drifted and multiplied | Template rule: exactly one section of any normative document is authoritative, it is labeled as such, and every restatement carries a pointer to it. CI check: flag any document containing more than one definition of the same accept-set |
| OBS-1, W5H-2, W5H-3 | Lifecycle questions — what a release discloses, how long a deprecation lives, what happens to a bad release — were treated as operational detail rather than as part of the contract, and landed in an FAQ at advisory strength | Add a mandatory "Lifecycle" section to the release-policy template with three required subsections: disclosure signal, deprecation window (in releases *and* calendar time), retraction procedure. Empty subsections block sign-off |
| NAM-1 | Identifier syntax was specified without specifying identifier semantics, because syntax is checkable and semantics is not | Require any identifier scheme we publish to ship a worked ordering example covering the full vocabulary, with the sort verified by a test rather than by reading |

---

## FINDINGS INDEX

| ID | Lens | Cycle | Line(s) | Severity | Verdict | Claim (one sentence) | Confidence |
|----|------|-------|---------|----------|---------|----------------------|------------|
| SUB-1 | Subtract | 1 | examples/artifacts/semver-2.0.0.md:104-110 | Minor | Fix | Build metadata is optional and excluded from precedence with no stated purpose or consumer obligation, so the team must decide unilaterally whether to emit it and what its parser does on receiving it. | High |
| SIM-1 | Simplify | 1 | examples/artifacts/semver-2.0.0.md:83-85 | Major | Fix | The MAY-increment-minor-for-substantial-private-improvement clause supplies no threshold for "substantial", so the team must define one or accept that the minor digit stops being a function of the change set. | High |
| NAM-1 | Name | 1 | examples/artifacts/semver-2.0.0.md:101-102 | Major | Fix | Pre-release identifiers carry no required meaning and no blessed vocabulary, so the team must invent its own and hand-verify that it sorts in the intended order. | High |
| TRU-1 | Truth | 1 | examples/artifacts/semver-2.0.0.md:62-65 | Minor | Discard:Integrity | "Each element MUST increase numerically" appears to conflict with the reset-to-0 MUSTs, but the clause's own example scopes it to a single element advancing, so no adopter is left guessing. | Low |
| TRU-2 | Truth | 1 | examples/artifacts/semver-2.0.0.md:42-45 | Major | Fix | The Introduction's "backward compatible API additions/changes increment the minor version" is broader than normative rule 7's "new functionality", so the team must decide which restatement binds a compatible change that adds no functionality. | Medium |
| BOU-1 | Boundary | 1 | examples/artifacts/semver-2.0.0.md:58-60 | Major | Fix | The public API must be declared but is never delimited, so the team must define the boundary construct by construct for Go before any increment rule can be applied. | High |
| SHI-1 | Shield | 1 | examples/artifacts/semver-2.0.0.md:337 | Major | Fix | Prose, BNF grammar and two "suggested" regexes each define the valid-version accept-set with no stated precedence between them, so the team must pick which one its parser implements. | Medium |
| PRO-1 | Provenance | 1 | examples/artifacts/semver-2.0.0.md:242-244 | Minor | Fix | The instruction to "Link to this website from your README" names no URL anywhere in the artifact, so the team must decide which authority its README cites. | High |
| PRO-2 | Provenance | 1 | examples/artifacts/semver-2.0.0.md:1 | Minor | Fix | The artifact identifies itself only by a version string in its title, with no date, revision or hash, so the team must decide whether to vendor a pinned copy or accept an unpinnable normative dependency. | High |
| VAR-1 | Variety | 1 | examples/artifacts/semver-2.0.0.md:70-71 | Major | Fix | Every increment rule is guarded on a major version above zero, so no normative mapping exists for any change made below 1.0.0 and the team must author its whole 0.y.z policy. | High |
| VAR-2 | Variety | 1 | examples/artifacts/semver-2.0.0.md:77-79 | Major | Fix | A change that both fixes incorrect behavior and breaks a consumer satisfies two conflicting MUSTs, and the FAQ's "use your best judgment" declines to break the tie, so the team must. | High |
| OBS-1 | Observability | 1 | examples/artifacts/semver-2.0.0.md:88-89 | Major | Fix | A version increment is a lower bound on what changed rather than a description of it, and no supplementary signal is required, so the team must decide what it publishes alongside the number. | High |
| EFF-1 | Efficiency | 1 | examples/artifacts/semver-2.0.0.md:325-327 | Minor | Skip:Cobra | No bound is set on string length, identifier count or numeric magnitude, but imposing one would make our parser reject spec-valid input and break the contract it publishes to its own consumers. | High |
| W5H-1 | W5H1 | 1 | examples/artifacts/semver-2.0.0.md:367-368 | Minor | Skip:Compass | The artifact names an original author and a feedback channel but no owner or body empowered to settle an interpretation dispute. | High |
| W5H-2 | W5H1 | 1 | examples/artifacts/semver-2.0.0.md:319-321 | Major | Fix | The only stated deprecation window is a SHOULD-strength floor of one minor release with no calendar time, so the team must set its own. | High |
| W5H-3 | W5H1 | 1 | examples/artifacts/semver-2.0.0.md:67-68 | Major | Fix | The immutability rule is silent on whether withdrawing a release counts as modifying it, so the team must decide its retraction policy before it needs one. | High |
| W5H-4 | W5H1 | 1 | examples/artifacts/semver-2.0.0.md:349-352 | Minor | Fix | The FAQ steers implementers to a copied 200-character regex over the document's own complete BNF grammar without comparing the two, leaving the build-vs-copy call to the team. | Medium |

**Index row count: 17.** Every count stated elsewhere in this review derives from
this table: 17 raised, 16 survived (raised and not `Discard:Integrity`), 14
fixed (verdict `Fix`), 10 Major raised, 1 `Skip:Cobra`, 1 `Skip:Compass`, 1
`Discard:Integrity`. All findings were raised in cycle 1; the run ends after one
cycle by construction as a review-only run, so done-rule condition 1 was never
exercised.
