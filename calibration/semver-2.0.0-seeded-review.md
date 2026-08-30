# Diffract Review — Semantic Versioning 2.0.0 (adoption review)

> ## ⚠️ This reviews a deliberately corrupted document
>
> The artifact under review is
> [`artifacts/semver-2.0.0-seeded.md`](artifacts/semver-2.0.0-seeded.md) — a
> copy of Semantic Versioning 2.0.0 **with defects planted in it** to test what
> a reviewer finds. It is not the specification.
>
> **Four findings below describe errors we introduced ourselves.** `TRU-1`,
> `TRU-2`, `VAR-2` and `SUB-1` correspond to seeds `S1`, `S4`, `S2` and `S3` in
> [`seeds.md`](seeds.md). The real specification does not say that MAJOR is
> incremented for backward compatible additions, does not answer that `"v1.2.3"`
> is a semantic version, does not omit uppercase `Q` from its grammar, and does
> not duplicate an alternative in `<valid semver>`. Those are ours.
>
> Do not cite this review as commentary on Semantic Versioning. The review of
> the **unmodified** text is
> [`examples/semver-2.0.0-review.md`](../examples/semver-2.0.0-review.md), and
> the unmodified text itself is
> [`examples/artifacts/semver-2.0.0.md`](../examples/artifacts/semver-2.0.0.md).
>
> It is published as evidence: the score in [`results.md`](results.md) is a
> number, and this is the run that produced it. The reviewer worked blind —
> only `PROMPT.md` and the artifact, with the modification notice stripped, no
> repository access, no git, no network, and no sight of the answer key or of
> any prior review. Its form is machine-verified by
> [`scripts/check_review.py`](../scripts/check_review.py).


**Tags:** `[async — no PLAN confirmation]` `[fixes listed, not applied — convergence untested]`

Artifact: `calibration/artifacts/semver-2.0.0-seeded.md`
Instrument: Diffract 0.3.0

---

## PLAN

### Entry criteria — deterministic checks

Review attention must not be spent on defects a tool reports for free. This is
a prose artifact with no build, test, or lint target, so the non-code checks
named in the instrument were run, plus what the environment offered. Each check
and its result:

| # | Check | Tool / method | Result |
|---|-------|---------------|--------|
| 1 | Code fences balance | `grep -n '```'` | **Pass** — 6 fence markers at lines 149, 211, 345, 347, 356, 358; three balanced pairs. |
| 2 | Internal anchors resolve | `grep -n '](#'` | **Pass (vacuous)** — the document contains no in-document anchor links, so none can dangle. |
| 3 | External links resolve | — | **Not run** — no network access in this run. Six external URLs exist (lines 56, 343, 354, 364, 368, 373); none was fetched. Recorded in Gap Analysis. |
| 4 | Link syntax well-formed | `grep -nE '\[[^]]+\]\([^)]+\)'` + multi-line inspection | **Pass** — all six links are syntactically closed, including the two that wrap across lines (363–364, 367–368). |
| 5 | Version strings agree across the artifact set | `grep -n '2\.0\.0'` | **Pass** — the artifact set is one file. The only self-identifying version string is `Semantic Versioning 2.0.0` (line 1). The other `2.0.0` hits (122, 267) are illustrative examples, not identity claims. No disagreement possible. |
| 6 | Markdown lint | `which markdownlint mdl vale` | **Not run** — no markdown linter, prose linter, or spell checker on PATH. Recorded in Gap Analysis. |
| 7 | Line count agrees with the commission | `wc -l`, `awk END{NR}` | **Discrepancy** — the file is **373** lines, not the 374 stated in the task. The file ends with a single newline after line 373; the count difference is a trailing-newline convention, not missing content. All line numbers in this review were read from the file itself. |

**Gate outcome.** This is the instrument's fifth PLAN case — *some checks run,
others have nothing to run against*. Checks 1, 2, 4, 5 and 7 ran and passed;
checks 3 and 6 could not run in this environment. The gate passes on the checks
that ran; this is **not** a waiver, and no `[entry waived]` tag is carried. What
went unchecked is recorded in the Gap Analysis.

### Governors

```
Diffract: 0.3.0
🧭 Compass: We are adopting this versioning specification for a Go library
            this quarter. Working only from this text, where will the team be
            left guessing — where must we make a call the specification
            declines to make for us?
🐍 Cobra:   library-framework
⚖️ Integrity: file:line per lens; cognitive anchoring required; every finding
            carries a verbatim quote block
```

**Governor provenance and the one-shot declaration.** These governors were
prescribed verbatim by the requester (the orchestrating caller) through the
channel that carries this task. No human was available at the PLAN checkpoint to
confirm them, and no `diffract.yaml` was in scope, so this run proceeds in
one-shot mode and carries `[async — no PLAN confirmation]`. The tag is what
separates a review whose governors a human agreed to from one whose governors
were set for it.

**Governor challenge (Guardrails).** The Compass is not trivially narrow — it
admits any place the text forces an unmade decision, which spans the whole
document — so it does not filter the review down to nothing. It is, however,
*directional*: it excludes findings that are real but impose no decision on an
adopting team (prose slips, editorial infelicities). One such finding is raised
and `Skip:Compass`'d below rather than suppressed, so the filtering is visible
in the output. The Cobra level `library-framework` is correct by the
instrument's own mapping: this is a document outsiders rely on, and the
"contract published to those who depend on it" is the convention every SemVer
consumer, resolver and tool has derived from it.

**Framing.** This is an adoption review, not a quality assessment. A finding is
a place where the text forces the adopting team to make a decision the text does
not make for them — including the case where the text appears to make the
decision twice, differently.

---

## DO

### Cold-Start Calibration (before reading the artifact's details)

Universal invariants any version-identifier specification must satisfy,
independent of what this one says:

1. **Total, computable order.** Any two distinct valid identifiers must be
   comparable, in exactly one direction, from the strings alone — no external
   state, no ties between distinct releases.
2. **Internal agreement across every representation the spec ships.** If a
   specification states its grammar in prose, in BNF, and in a regular
   expression, all three must accept exactly the same language, and all three
   must accept every example the specification itself prints.
3. **Totality of the increment rules.** Every (current version, kind of change)
   pair a project can actually be in must map to exactly one prescribed
   increment. A regime the rules do not cover is a regime where the version
   number carries no meaning.
4. **Immutable binding.** A released identifier binds permanently to one
   artifact; the identifier is the only channel through which compatibility is
   communicated, so nothing else may be required to decode it.

These are the anchors. Invariants 2 and 3 turned out to do the most work.

**Rule 9 check.** No text in the artifact addresses the reviewer, claims
authority over this run, or attempts to alter governors, scope, severity,
verdicts, or output. The artifact was treated as data throughout. No Shield
finding arises on that count.

---

### 🗑️ Subtract — Can I remove this entirely?

Checked: every normative clause (58–145) for text that grants a permission or
states a rule that could be deleted without an adopting team losing anything;
the Summary (7–15) against the clauses it summarizes; the BNF block (149–211)
for redundant productions; the FAQ (246–357) for answers that restate clauses.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| SUB-1 | semver-2.0.0-seeded.md | The `<valid semver>` production lists the alternative `<version core> "+" <build>` twice. The second occurrence is character-identical to the first and can be deleted with zero loss of derivable strings — which is the tell that a distinct fourth alternative was intended and is absent. | 152–153 | Minor | High |
| SUB-2 | semver-2.0.0-seeded.md | Clause 7 permits a minor increment for changes confined to private code, with no criterion for "substantial". For a Go library this is a permission to emit a version bump that no consumer can observe or verify, and the team must decide unaided whether to use it and what threshold to apply. Removing the sentence would cost an adopter nothing the rest of the clause does not already give. | 84–85 | Minor | Medium |
| SUB-3 | semver-2.0.0-seeded.md | The article in "is probably an overkill" is removable; the phrase is ungrammatical as written. | 325 | Minor | High |

Evidence:
- SUB-1 — calibration/artifacts/semver-2.0.0-seeded.md:152-153
  >                  | <version core> "+" <build>
  >                  | <version core> "+" <build>
- SUB-2 — calibration/artifacts/semver-2.0.0-seeded.md:84-85
  > incremented if substantial new functionality or improvements are introduced
  > within the private code. It MAY include patch level changes. Patch version
- SUB-3 — calibration/artifacts/semver-2.0.0-seeded.md:325
  > No, but use good judgment. A 255 character version string is probably an overkill,

---

### ✂️ Simplify — Can this be simpler without losing capability?

Checked: the three places the document constrains identifier syntax — clause 2
(62–65), clause 9 (93–102), clause 10 (104–110) — and the corresponding BNF
productions (173–203), looking for one rule expressed as several.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| SIM-1 | semver-2.0.0-seeded.md | The leading-zero prohibition is scoped three different ways and is not uniform: forbidden for X, Y, Z (clause 2, line 63), forbidden for *numeric* pre-release identifiers (clause 9, lines 96–97), and silently **permitted** for build identifiers — the document's own example `1.0.0-alpha+001` (line 109) depends on that asymmetry. A team writing one shared identifier validator, the obvious simplification, must first discover from three separate places that the rule is not shared. | 96–97 | Minor | Medium |

Evidence:
- SIM-1 — calibration/artifacts/semver-2.0.0-seeded.md:96-97
  > [0-9A-Za-z-]. Identifiers MUST NOT be empty. Numeric identifiers MUST
  > NOT include leading zeroes. Pre-release versions have a lower

---

### 🏷️ Name — Does the name match the thing?

Checked: every load-bearing term the normative clauses use as if defined —
"public API", "backward compatible", "bug fix", "incorrect behavior", "marked as
deprecated", "private code" — traced to the place the document defines it, if
any.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| NAM-1 | semver-2.0.0-seeded.md | "Public API" is the term every increment rule pivots on, and the document requires that one be declared without ever saying what may be in it. For a Go library the candidate surfaces are distinct and the choice is consequential: exported identifiers only; exported identifiers plus documented behavior; plus struct field order and embedding; plus error values and sentinel types; plus the module's own minimum Go version. The specification declines to choose, and every later rule inherits the ambiguity. | 58–60 | Major | High |
| NAM-2 | semver-2.0.0-seeded.md | "Bug fix" is defined as "an internal change that fixes incorrect behavior", and "incorrect behavior" is left undefined. In Go the common case is behavior that is wrong but undocumented and depended upon: correcting it is simultaneously an internal change (patch, by this definition) and an observable break (major, by clause 8). The name does not match a single thing, and the team must draw the line itself. | 78–79 | Major | Medium |

Evidence:
- NAM-1 — calibration/artifacts/semver-2.0.0-seeded.md:58-60
  > 1. Software using Semantic Versioning MUST declare a public API. This API
  > could be declared in the code itself or exist strictly in documentation.
  > However it is done, it SHOULD be precise and comprehensive.
- NAM-2 — calibration/artifacts/semver-2.0.0-seeded.md:78-79
  > compatible bug fixes are introduced. A bug fix is defined as an internal
  > change that fixes incorrect behavior.

---

### 📌 Truth — Is this knowledge in exactly one place?

Checked: every statement that appears in more than one place — the Summary
(7–15) against clauses 6–8 (77–91); the FAQ (246–357) against the clauses it
answers for; the definition of a valid version string across prose, BNF and the
two regular expressions.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| TRU-1 | semver-2.0.0-seeded.md | The Summary and clause 8 give MAJOR two different definitions. The Summary says MAJOR is incremented "when you add functionality in a backward compatible" manner — the definition it also gives, verbatim, for MINOR on the very next line — while clause 8 (88–89) says MAJOR is for backward *incompatible* changes. A reader who takes the Summary at face value inverts the central rule of the specification. The duplicated sentence is also truncated: line 9 lacks the "manner" continuation that line 10 has at line 11. | 9–10 | Major | High |
| TRU-2 | semver-2.0.0-seeded.md | The FAQ answers that `"v1.2.3"` **is** a semantic version. This contradicts clause 2 (62–64), which requires the form X.Y.Z of non-negative integers; the BNF, whose `<version core>` admits no prefix (155–161); both regular expressions, which are `^`-anchored on a digit class (346, 357); and the closing sentence of the same FAQ answer (334–335), which says the tag is `v1.2.3` and the semantic version is `1.2.3`. The team cannot tell from this text whether its Go module tags are versions or names for versions. | 331 | Major | High |
| TRU-3 | semver-2.0.0-seeded.md | The set of valid version strings is defined independently in four places — prose clauses 2/9/10, the BNF (149–211), and two regular expressions (346, 357) — with no statement of which governs. They do not agree (see VAR-1, VAR-2: both regexes accept strings the BNF cannot derive). Implementing against this document means choosing an authority the document never names. | 339–341 | Major | Medium |

Evidence:
- TRU-1 — calibration/artifacts/semver-2.0.0-seeded.md:9-10
  > 1. MAJOR version when you add functionality in a backward compatible
  > 1. MINOR version when you add functionality in a backward compatible
- TRU-2 — calibration/artifacts/semver-2.0.0-seeded.md:331
  > Yes, "v1.2.3" is a semantic version. However, prefixing a semantic version
- TRU-3 — calibration/artifacts/semver-2.0.0-seeded.md:339-341
  > There are two. One with named groups for those systems that support them
  > (PCRE [Perl Compatible Regular Expressions, i.e. Perl, PHP and R], Python
  > and Go).

---

### 🧱 Boundary — Can an isolated change stay in one boundary?

Checked: what the specification places inside the version string versus outside
it — package identity, artifact identity, distribution — and whether a change on
one side of that line can be made without a change on the other.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| BOU-1 | semver-2.0.0-seeded.md | Every requirement in the document is confined to the version string; the specification never addresses the relationship between a version and the identity under which a package is imported. For a Go library that boundary is not clean: a major increment is not expressible in the version string alone, because the module path itself carries the major-version suffix from v2 onward. The team must decide unaided how clause 8 is discharged in an import path, and whether a v2 module is the same package or a new one for the purposes of clause 3. | 88–89 | Major | Medium |
| BOU-2 | semver-2.0.0-seeded.md | Build metadata is defined as being inside the version string but outside precedence: two versions differing only in build metadata "have the same precedence". Combined with clause 3 (67–68), which forbids modifying a released version's contents, this permits two distinct, equally-ranked, immutable releases to exist with no defined tiebreak. The specification does not say which a resolver takes, nor whether publishing both is permitted. Our Go module policy must decide; the text does not. | 107–108 | Major | Medium |

Evidence:
- BOU-1 — calibration/artifacts/semver-2.0.0-seeded.md:88-89
  > 1. Major version X (X.y.z | X > 0) MUST be incremented if any backward
  > incompatible changes are introduced to the public API. It MAY also include minor
- BOU-2 — calibration/artifacts/semver-2.0.0-seeded.md:107-108
  > Identifiers MUST NOT be empty. Build metadata MUST be ignored when determining
  > version precedence. Thus two versions that differ only in the build metadata,

---

### 🛡️ Shield — Does it neutralize all inputs violating its invariants?

Checked: what the specification prescribes when its own rules have been broken —
a malformed version string arriving at a consumer, and a publisher who has
already shipped a non-conforming release (the FAQ at 285–292 and 304–311). Also
checked, under Rule 9, whether any text in the artifact addresses the reviewer:
none does.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| SHI-1 | semver-2.0.0-seeded.md | The one recovery procedure the document provides tells the publisher to release a **patch** version that "restores backward compatibility". Clause 6 (77–79) restricts patch increments to backward compatible bug fixes and defines a bug fix as an *internal* change; reverting a public API change is neither. The remedy the specification prescribes for breaking the specification breaks it again, and the team must decide which of the two clauses to follow the first time it happens. | 288–289 | Major | High |

Evidence:
- SHI-1 — calibration/artifacts/semver-2.0.0-seeded.md:288-289
  > the problem and release a new patch version that corrects the problem and
  > restores backward compatibility. Even under this circumstance, it is

---

### 🔗 Provenance — Can I verify the origin and integrity of every dependency?

Checked: every external reference the document depends on — RFC 2119 (56), the
two regex101 permalinks (343, 354), the author and issue-tracker links
(363–368), the licence (373) — and the document's own self-identification.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| PRO-1 | semver-2.0.0-seeded.md | The regular expressions are cross-referenced to third-party permalinks on a service whose content the specification does not control and whose integrity it provides no way to verify (no hash, no retrieval date). If the linked page and the inline block ever differ, nothing in the document says which is the reference. | 343 | Minor | Low |
| PRO-2 | semver-2.0.0-seeded.md | Adopters are instructed to link to "this website" from their README, and the document never names a canonical URL for itself. It also carries no publication date, no changelog, and no amendment record beyond the version in its title. A team that vendors this text — as we are doing — has no citable origin to point at. | 242–243 | Minor | Medium |

Evidence:
- PRO-1 — calibration/artifacts/semver-2.0.0-seeded.md:343
  > See: <https://regex101.com/r/Ly7O1x/3/>
- PRO-2 — calibration/artifacts/semver-2.0.0-seeded.md:242-243
  > Versioning is to declare that you are doing so and then follow the rules. Link
  > to this website from your README so others know the rules and can benefit from

---

### 🎯 Variety — Does every possible input map to a defined output?

Checked: the grammar (149–211) against every example string the document prints
(101–102, 109–110, 122, 127, 144–145); the increment rules (77–91) against every
project state, including the pre-1.0 regime; the ordering rules (112–145) for
version pairs they do not rank.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| VAR-1 | semver-2.0.0-seeded.md | The grammar has no production combining a pre-release and build metadata: `<valid semver>` offers core, core+pre-release, core+build, and core+build again (150–153). The document's own examples `1.0.0-alpha+001` and `1.0.0-beta+exp.sha.5114f85` are therefore not derivable from the grammar it publishes, while clause 10 (104–105) explicitly permits them. A validator built from the BNF rejects strings the prose requires it to accept. | 109–110 | Major | High |
| VAR-2 | semver-2.0.0-seeded.md | The `<letter>` production omits uppercase **"Q"**: the second line runs "P" straight to "R", while lowercase "q" is present (209). Clause 9 (95–96) permits any of `[0-9A-Za-z-]` in a pre-release identifier, so `1.0.0-Q1` is valid by prose and by both regexes, and underivable by the grammar. | 205–206 | Major | High |
| VAR-3 | semver-2.0.0-seeded.md | The increment rules are all guarded on a non-zero major: clause 6 `x > 0` (77), clause 7 `x > 0` (81), clause 8 `X > 0` (88). Nothing normative governs increments while in 0.y.z, and clause 4 says only that anything MAY change. The pre-1.0 phase — which is where our library will spend this quarter — has no rule at all: the team must invent its own meaning for 0.x bumps, and consumers cannot rely on it. | 70–71 | Major | High |
| VAR-4 | semver-2.0.0-seeded.md | "Each element MUST increase numerically" does not say whether it must increase *by one*. The example given (1.9.0 → 1.10.0 → 1.11.0) is consistent with both readings, so the document does not settle whether skipping (1.0.0 → 1.5.0, or a deliberately abandoned tag) is conforming. Any team that tags from CI must decide. | 65 | Minor | Medium |

Evidence:
- VAR-1 — calibration/artifacts/semver-2.0.0-seeded.md:109-110
  > have the same precedence. Examples: 1.0.0-alpha+001, 1.0.0+20130313144700,
  > 1.0.0-beta+exp.sha.5114f85, 1.0.0+21AF26D3\-\-\-\-117B344092BD.
- VAR-2 — calibration/artifacts/semver-2.0.0-seeded.md:205-206
  > <letter> ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J"
  >            | "K" | "L" | "M" | "N" | "O" | "P" | "R" | "S" | "T"
- VAR-3 — calibration/artifacts/semver-2.0.0-seeded.md:70-71
  > 1. Major version zero (0.y.z) is for initial development. Anything MAY change
  > at any time. The public API SHOULD NOT be considered stable.
- VAR-4 — calibration/artifacts/semver-2.0.0-seeded.md:65
  > Each element MUST increase numerically. For instance: 1.9.0 -> 1.10.0 -> 1.11.0.

---

### 🔍 Observability — Can I determine system state from outputs?

Checked: what a consumer can learn from a version number alone, and what the
specification requires a publisher to emit alongside it — searched the whole
document for any required changelog, machine-readable API declaration,
conformance statement, or compliance signal.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| OBS-1 | semver-2.0.0-seeded.md | The document asserts that version numbers convey meaning about the underlying code, and then requires nothing that would let a consumer check the assertion. There is no mandated changelog, no machine-readable declaration of the public API (clause 1 permits it to "exist strictly in documentation"), and no conformance test. Observing 1.4.0 → 1.5.0 tells a consumer what the publisher claims, not what happened. Our team must decide what verification gate — API diff, exported-symbol snapshot — stands behind our own tags, because the specification supplies none. | 47–49 | Major | Medium |
| OBS-2 | semver-2.0.0-seeded.md | When a release is known to violate the spec, disclosure is left to the publisher's discretion — "If it's appropriate". There is no required marker, so a non-conforming release is indistinguishable from a conforming one in the version stream, and downstream automation has nothing to read. | 290–291 | Minor | Low |

Evidence:
- OBS-1 — calibration/artifacts/semver-2.0.0-seeded.md:47-49
  > We call this system "Semantic Versioning." Under this scheme, version numbers
  > and the way they change convey meaning about the underlying code and what has
  > been modified from one version to the next.
- OBS-2 — calibration/artifacts/semver-2.0.0-seeded.md:290-291
  > unacceptable to modify versioned releases. If it's appropriate,
  > document the offending version and inform your users of the problem so that

---

### ⚡ Efficiency — Is resource use proportional to work required?

Checked: the cost of executing every rule the document imposes — the precedence
algorithm (112–145) for comparison cost and lookahead, the grammar (149–211) for
ambiguity that would force backtracking, and the increment rules (77–91) for
work demanded that is disproportionate to the information conveyed.

A finding would look like: a precedence rule that cannot be evaluated in a
single left-to-right pass over the dot-separated identifiers — for example, a
tiebreak that depends on identifiers to the *right* of the first difference, or
on the total length of the pre-release field, forcing a resolver to parse and
retain the whole string before it can order two versions; or a mandated
increment that requires recomputing state the publisher cannot cheaply obtain.
Clause 11.4 is strictly left-to-right with a single set-size tiebreak applied
only after all preceding identifiers compare equal (141–142), so ordering is
linear in the string and stops at the first difference; the increment rules
demand only a comparison against the previously declared API.

No findings matching this pattern.

---

### ❓ W5H1 — What's missing?

Checked: **Why** — rationale for the non-obvious MUSTs; **Who** — ownership and
arbitration; **When** — expiry, windows and timeouts; **How** — whether the
validation machinery the document ships is the right tool.

| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| W5H-1 | semver-2.0.0-seeded.md | **Why.** Clause 7 makes deprecation alone a MUST-increment trigger — the only place in the document where a release is mandated for a change that alters no behavior — and gives no rationale. It also never says what "marked as deprecated" *is*. In Go the convention is a `// Deprecated:` comment paragraph, which is neither enforced nor detectable by the compiler. The team must decide what marking counts and therefore when this MUST fires. | 82–83 | Major | Medium |
| W5H-2 | semver-2.0.0-seeded.md | **Who.** The document names an original author and an issue tracker, and no owner, maintainer, or interpretive authority. Every ambiguity in this review (NAM-1, NAM-2, VAR-3, VAR-4) and every internal contradiction (TRU-1, TRU-2, TRU-3, SHI-1) needs an arbiter, and adopting the text does not give us one. Our team must name the internal owner who resolves SemVer disputes, because the specification does not designate one. | 363–365 | Major | Medium |
| W5H-3 | semver-2.0.0-seeded.md | **When.** The only stated deprecation window is "at least one minor release", in a non-normative FAQ answer, with no duration, no minimum support period, and no expiry for a deprecated symbol. A library on a quarterly cadence needs a policy the text does not provide. | 319–320 | Minor | Medium |
| W5H-4 | semver-2.0.0-seeded.md | **How (tech-stack neutralization).** The document ships two hand-maintained validation mechanisms — a hand-written BNF and two large hand-written regexes — and explicitly offers the regexes to Go users. Both are golden hammers here: the vanilla path for a Go library is the standard library-adjacent parser the module system already uses, and it is the one artifact whose behavior is testable rather than transcribed. The document neither says which of its own three descriptions is authoritative nor acknowledges that a language's own parser might be, and they demonstrably disagree (VAR-1, VAR-2). | 351–352 | Major | Medium |

Evidence:
- W5H-1 — calibration/artifacts/semver-2.0.0-seeded.md:82-83
  > compatible functionality is introduced to the public API. It MUST be
  > incremented if any public API functionality is marked as deprecated. It MAY be
- W5H-2 — calibration/artifacts/semver-2.0.0-seeded.md:363-365
  > The Semantic Versioning specification was originally authored by [Tom
  > Preston-Werner](https://tom.preston-werner.com), inventor of Gravatar and
  > cofounder of GitHub.
- W5H-3 — calibration/artifacts/semver-2.0.0-seeded.md:319-320
  > in place. Before you completely remove the functionality in a new major release
  > there should be at least one minor release that contains the deprecation so
- W5H-4 — calibration/artifacts/semver-2.0.0-seeded.md:351-352
  > with ECMA Script (JavaScript), PCRE (Perl Compatible Regular Expressions,
  > i.e. Perl, PHP and R), Python and Go.

---

## CHECK

### Competing Hypotheses (Low-Confidence findings only)

Two findings were raised at Low confidence. Each is weighed before its verdict;
the surviving hypothesis is the one the evidence *least disconfirms*.

**PRO-1 — regex101 permalinks as unverifiable references.**

| Hypothesis | Discriminating evidence |
|---|---|
| H1: the defect is real — the document leans on a mutable third-party page with no integrity anchor | Would predict the document depending on the link for content. It does not: both regexes are reproduced inline (346, 357), so the text is self-contained without the URL. **Disconfirmed.** |
| H2: the artifact's intent explains it — the links are conveniences, and the section is offered as advice | The section is headed "Is there a suggested regular expression…" (337) and the URLs are introduced with a bare "See:" (343, 354). Nothing presents them as normative. **Least disconfirmed.** |
| H3: the reviewer misread — the links are the normative source | Contradicted by the inline reproduction and by the word "suggested". **Disconfirmed.** |

Surviving hypothesis: H2. The observation is explained by the artifact's stated
intent, so the finding is not established as a defect. Verdict follows:
`Discard:Integrity`. (The real disagreement between the regexes and the BNF is
carried by VAR-1, VAR-2 and TRU-3, which do not depend on the external links.)

**OBS-2 — discretionary disclosure of a non-conforming release.**

| Hypothesis | Discriminating evidence |
|---|---|
| H1: the defect is real — nothing in the document requires a non-conforming release to be identifiable | Would predict no mandatory disclosure anywhere in the text. A full read finds none; the only disclosure sentence is conditional ("If it's appropriate", 290). **Least disconfirmed.** |
| H2: the artifact's intent explains it — the FAQ is deliberately advisory, and clause 3's immutability rule already preserves the offending release for inspection | Immutability (67–68) preserves the *artifact* but attaches no compliance claim to it; a consumer still cannot tell a broken release from a sound one by reading versions. H2 would predict a normative disclosure duty in the clauses; there is none. **Disconfirmed.** |
| H3: the reviewer misread — a disclosure duty exists elsewhere | Searched clauses 1–11 and the whole FAQ; no other disclosure sentence exists. **Disconfirmed.** |

Surviving hypothesis: H1. Verdict follows to the governors below.

### Governor vetting

Governors applied in order — Integrity, then Compass, then Cobra — first failure
decides.

| Finding | ⚖️ Integrity | 🧭 Compass | 🐍 Cobra | Verdict |
|---------|-------------|-----------|---------|---------|
| SUB-1: `<valid semver>` alternative duplicated | Looked; both lines quoted verbatim, byte-identical. Objective. | Yes — a team building a validator from the BNF must decide what the fourth alternative was meant to be. | Fixing restores a derivation; breaks no published contract. | `Fix` |
| SUB-2: minor bump permitted for invisible private changes | Looked; clause 7 quoted. Objective. | Yes — the team must decide whether to use this permission. | **Removing a published MAY breaks the contract downstream consumers built on**: tools and publishers that bump minor for internal work are conforming today, and deleting the permission makes them non-conforming. `library-framework` says skip. | `Skip:Cobra` |
| SUB-3: "an overkill" | Looked; quoted. Objective. | **No** — a grammatical slip forces no decision on an adopting team; it is outside this review's goal. | not reached | `Skip:Compass` |
| SIM-1: leading-zero rule non-uniform across three scopes | Looked; all three scopes read, asymmetry confirmed against example 1.0.0-alpha+001. | Yes — the team must decide whether one validator or three. | Clarifying the asymmetry changes no accepted string. | `Fix` |
| NAM-1: "public API" undefined | Looked; clause 1 quoted in full. Objective. | Yes — this is the largest unmade decision in the document for a Go library. | Defining our own surface breaks nothing published. | `Fix` |
| NAM-2: "bug fix" / "incorrect behavior" undefined | Looked; definition quoted. Objective. | Yes — undocumented-behavior fixes are routine and the rule does not classify them. | No contract break. | `Fix` |
| TRU-1: Summary defines MAJOR as MINOR | Looked; lines 9–10 quoted, contradiction with 88–89 confirmed in the same file. | Yes — a reader following the Summary inverts the rule. | Correcting a contradiction restores the contract rather than breaking it. | `Fix` |
| TRU-2: FAQ says "v1.2.3" is a semantic version | Looked; quoted, and contradicted by 62–64, 155–161, 346, 357 and 334–335. | Yes — our Go module tags are exactly this string. | Fixing aligns the document with the grammar every consumer already implements. | `Fix` |
| TRU-3: valid-version language defined in four places | Looked; all four located and compared. | Yes — the team must pick an authority. | Naming one authority does not change the accepted language. | `Fix` |
| BOU-1: version identity vs package identity unaddressed | Looked; clause 8 quoted. The Go-side consequence is our context, not a claim about the text; the claim about the text is that it is silent. | Yes — a v2 decision is due this quarter. | Adding guidance breaks nothing. | `Fix` |
| BOU-2: equal-precedence distinct releases, no tiebreak | Looked; clauses 10 and 3 quoted and read together. | Yes — resolver behavior must be decided. | Stating a tiebreak would change ordering for existing consumers — but no ordering is defined today, so nothing published is broken. | `Fix` |
| SHI-1: recovery procedure prescribes a non-conforming patch | Looked; FAQ and clause 6 quoted. Objective. | Yes — the first mis-release forces this call. | Correcting the FAQ aligns it with the clause; the clause is the contract. | `Fix` |
| PRO-1: regex101 links unverifiable | **Fails** — competing hypotheses above leave the artifact's stated intent ("suggested", inline reproduction) as the least-disconfirmed explanation. Not established as a defect. | not reached | not reached | `Discard:Integrity` |
| PRO-2: "this website" unnamed; no date or changelog | Looked; quoted. Objective. | Yes — a vendored copy needs a citable origin. | Adding a canonical URL breaks nothing. | `Fix` |
| VAR-1: grammar cannot derive pre-release + build | Looked; grammar and the examples it fails to derive both quoted. | Yes — our validator must accept these strings. | Adding the missing alternative widens the accepted language to what the prose already requires. | `Fix` |
| VAR-2: `<letter>` omits uppercase Q | Looked; both lines quoted, lowercase "q" confirmed present at 209. | Yes — an identifier containing Q is legal by prose and rejected by the grammar. | Restoring Q matches clause 9; no consumer relied on Q being illegal. | `Fix` |
| VAR-3: no increment rule in the 0.y.z regime | Looked; the three `x > 0` guards and clause 4 all quoted/located. | Yes — this is the regime we are in now. | Adding pre-1.0 guidance breaks nothing; the regime is explicitly unconstrained today. | `Fix` |
| VAR-4: "increase numerically" — by one, or monotonically? | Looked; quoted. Objective ambiguity, not opinion. | Yes — CI tagging must pick a reading. | Either reading is compatible with existing practice; stating one breaks nothing. | `Fix` |
| OBS-1: no verifiable compliance signal | Looked; the assertion at 47–49 quoted and the whole document searched for a mandated signal. | Yes — the team must supply the gate the spec omits. | Adding a recommendation breaks nothing. | `Fix` |
| OBS-2: disclosure of a broken release is discretionary | Passes on the surviving hypothesis H1 above; the absence was verified by full-document search, not assumed. | Yes — our disclosure policy must be decided. | No contract break. | `Fix` |
| W5H-1: deprecation MUST has no rationale and no defined marking | Looked; clause 7 quoted. Objective. | Yes — the team must decide what marking triggers the MUST. | No contract break. | `Fix` |
| W5H-2: no owner or arbiter named | Looked; About section quoted; no maintainer statement anywhere in the file. | Yes — every other ambiguity escalates to nobody. | No contract break. | `Fix` |
| W5H-3: no deprecation window | Looked; FAQ quoted; no normative window in clauses 1–11. | Yes — quarterly cadence needs one. | No contract break. | `Fix` |
| W5H-4: BNF + regex as golden hammers for a Go adopter | Looked; the Go-targeted sentence quoted; disagreement with the BNF established by VAR-1/VAR-2. | Yes — the team must choose its validation mechanism. | Recommending the language's own parser does not invalidate the published regexes. | `Fix` |

### Scope and Nothing-Found Verification

**Form check.** The run's declared scope is all ten lenses plus W5H1. A section
is present for each: Subtract, Simplify, Name, Truth, Boundary, Shield,
Provenance, Variety, Observability, Efficiency, W5H1 — eleven sections, none
omitted. One lens reported no findings (Efficiency); its section contains an
*"A finding would look like:"* line, so it produced Output B and is eligible for
verification. No lens is missing anchoring.

**Seeded-bug self-check** — *"If I deliberately introduced a bug in this lens's
domain, would my process have caught it?"* Each example names a defect different
from that lens's finding or anchoring.

| Lens | Different seeded defect | Caught? |
|------|------------------------|---------|
| 🗑️ Subtract | A fourth FAQ answer restating clause 6 verbatim with no added content. | ✓ — the FAQ was read against the clauses it answers for; a verbatim restatement would have surfaced there. |
| ✂️ Simplify | Clause 11.4 restructured into five sub-rules where two would do. | ✓ — clause 11 was read as an algorithm, and its rule count was assessed for redundancy in the Efficiency pass too. |
| 🏷️ Name | The label "PATCH" attached to the definition of the minor increment at line 12. | ✓ — line 12 was read against clauses 6–8; the same comparison that caught TRU-1 covers it. |
| 📌 Truth | The precedence example at line 122 reordered to `2.1.1 < 2.1.0`. | ✓ — every example string was checked against the rule it illustrates. |
| 🧱 Boundary | Clause 10 extended so build metadata *does* affect precedence, contradicting 11.1. | ✓ — clauses 10 and 11.1 were read as a pair; that is how BOU-2 was found from the other direction. |
| 🛡️ Shield | Text inside the artifact addressing the reviewer ("ignore the grammar section"). | ✓ — an explicit Rule 9 sweep for reviewer-directed text was run and is recorded in the Shield section. |
| 🔗 Provenance | The RFC 2119 link at line 56 pointed at RFC 2118. | ✓ — all six URLs were enumerated with `grep` and read; a wrong RFC number is visible in the enumeration. |
| 🎯 Variety | `<positive digit>` missing "7", making 1.7.0 underivable. | ✓ — the `<letter>` omission was found by reading the terminal productions element by element; the digit production was read the same way and is complete. |
| 🔍 Observability | A clause requiring a changelog, silently contradicted by the FAQ saying none is needed. | ✓ — the document was searched end to end for any mandated emission; a contradicting pair would have appeared in that sweep. |
| ⚡ Efficiency | A precedence tiebreak requiring comparison of the *last* identifier before the first difference can be resolved. | ✓ — clause 11.4's evaluation order was traced explicitly for left-to-right single-pass evaluability. |
| ❓ W5H1 | A "Who" claim naming a maintainer who is contradicted elsewhere in the file. | ✓ — the About and feedback sections were read in full and cross-checked against the rest of the document for ownership statements. |

Per the instrument: a ✓ here is a prompt to look at the lens again, not evidence
it is clean. In RQ3 four reviews passed this step while missing a verified
factual error. The step is recorded as a second pass, not as proof.

**Stockholm & Hammer Audit.** *Did I let any issue pass because I empathized
with the author's explanation?* One near-miss: the FAQ's confident tone around
0.y.z ("Major version zero is all about rapid development", 263) invites the
reader to accept that the pre-1.0 regime is deliberately unspecified rather than
under-specified. Under the adoption Compass that framing is exactly the problem
— the team still has to pick a rule — so VAR-3 was raised rather than waived to
the author's intent. Conversely, PRO-1 was *not* forced through: where the
artifact's stated intent genuinely explained the observation, the finding was
discarded on Integrity rather than defended.

*Did I accept over-engineering because it matches a familiar pattern?* The BNF
grammar is a familiar and respectable pattern, and its presence made it easy to
treat as authoritative. Challenged in W5H-4: for a Go adopter the hand-written
grammar and hand-written regexes are three transcriptions of a language that the
toolchain's own parser already implements and tests, and the document's
transcriptions demonstrably disagree with each other. The simpler, vanilla
option was named rather than assumed away.

**Adversarial decoupling note.** Prior familiarity with this specification was
treated as a source of hypotheses, never as evidence. Every finding above is
anchored to a line quoted from the file in front of me, and where recollection
and the text disagreed, the text was reviewed as it stands.

---

## LEARN

### Fixes — listed, not applied

This is a review-only run commissioned as blind calibration: no fixes were
applied to the artifact. Tagged `[fixes listed, not applied — convergence
untested]`. All 21 `Fix` verdicts, with location and replacement:

| ID | Location | Fix |
|----|----------|-----|
| SUB-1 | line 153 | Replace the duplicated alternative with the missing one: `                 \| <version core> "-" <pre-release> "+" <build>` |
| SIM-1 | line 107 | After "Identifiers MUST NOT be empty." in clause 10, add: "Build metadata identifiers MAY include leading zeroes; the restriction in clause 9 applies to pre-release identifiers only." |
| NAM-1 | after line 60 | Add to clause 1: "A declaration SHOULD state which of the following are inside the public API: exported names, documented behavior, struct layout, error values, and minimum toolchain version." For our adoption: record the chosen surface in the library's `CONTRIBUTING.md` before the first tag. |
| NAM-2 | line 79 | Replace "change that fixes incorrect behavior." with "change that fixes behavior contradicting the declared public API. A change to behavior the declared API does not specify is not a bug fix under this specification; classify it against clause 7 or 8." |
| TRU-1 | line 9 | Replace with: `1. MAJOR version when you make incompatible API changes` |
| TRU-2 | line 331 | Replace "Yes, "v1.2.3" is a semantic version." with "No, "v1.2.3" is not a semantic version." — this is the reading the rest of the same answer (334–335), clause 2, the grammar and both regexes already require. |
| TRU-3 | after line 148 | Add one sentence before the grammar: "Where this grammar, the regular expressions in the FAQ, and the prose clauses disagree, the prose clauses govern." |
| BOU-1 | after line 91 | Add to clause 8: "This specification governs the version identifier only. Where a packaging system encodes the major version in the package identity, satisfying this clause may also require changing that identity." |
| BOU-2 | after line 109 | Add: "Two versions differing only in build metadata denote the same release. A distribution system MUST NOT publish both as distinct releases." |
| SHI-1 | line 288 | Replace "release a new patch version" with "release a new minor version" — a revert of a public API change is not an internal change, and clause 6 does not admit it. |
| PRO-2 | line 243 | Replace "this website" with the canonical URL of the specification, and add a publication date beneath the title at line 2. |
| VAR-1 | line 153 | Same edit as SUB-1; it is the same line. Both IDs are discharged by it. |
| VAR-2 | line 206 | Replace with: `           \| "K" \| "L" \| "M" \| "N" \| "O" \| "P" \| "Q" \| "R" \| "S" \| "T"` |
| VAR-3 | after line 71 | Add to clause 4: "While the major version is zero, MINOR SHOULD be incremented for backward incompatible changes and PATCH for all other changes." For our adoption: adopt this rule explicitly for the 0.x phase this quarter. |
| VAR-4 | line 65 | Replace "Each element MUST increase numerically." with "Each element MUST increase numerically by one from the value in the preceding release of that element." (or, if skipping is intended, "MUST increase numerically; increments greater than one are permitted.") — the choice must be stated. |
| OBS-1 | after line 60 | Add: "A publisher SHOULD make available, for each release, a record of the changes to the public API sufficient for a consumer to verify the increment." For our adoption: gate releases on an exported-API diff in CI. |
| OBS-2 | line 290 | Replace "If it's appropriate, document" with "Document". |
| W5H-1 | line 83 | After "marked as deprecated", add: "— that is, annotated as deprecated in the declared public API — because consumers need a release in which the deprecation is visible before removal." |
| W5H-2 | after line 368 | Add a "Maintenance" line naming the current maintaining body and the process by which the specification is amended. For our adoption: name the internal owner who arbitrates SemVer questions. |
| W5H-3 | line 320 | Replace "at least one minor release" with "at least one minor release and at least <N> days"; N must be stated. For our adoption: set N in the library's support policy. |
| W5H-4 | after line 341 | Add: "These expressions are provided for convenience. Where a language's standard tooling implements this specification, that implementation SHOULD be preferred over transcribing this expression." |

### Verification

The PLAN entry checks were re-run against the artifact after analysis. Because
no fixes were applied, the artifact is byte-identical to the reviewed copy
(sha256 `45f55de2…07a`) and all results are unchanged: fences balance (3 pairs),
no internal anchors to dangle, link syntax well-formed, one self-identifying
version string, 373 lines. Checks 3 (external link resolution) and 6 (markdown
lint) remain not run for the same environmental reasons.

### Scorecard

| Metric | Value |
|--------|-------|
| Reviewer | claude-opus-5, Diffract blind-calibration agent, single-pass agentic run, no network |
| Artifact | `calibration/artifacts/semver-2.0.0-seeded.md` — "Semantic Versioning 2.0.0", 373 lines, sha256 `45f55de28671f910268778a9b83b2891393ca9bc3c40907d9b6ee0fb3f0e007a` |
| Instrument | Diffract 0.3.0 |
| Governors | 🧭 Adoption for a Go library — where must the team make a call the specification declines to make? · 🐍 Library/Framework · ⚖️ file:line per lens, cognitive anchoring required, verbatim quote block per finding |
| Entry checks | Fences balance: pass · Internal anchors: pass (none present) · Link syntax: pass · Version strings agree: pass · Line count: 373 (task said 374; trailing-newline convention) · External link resolution: **not run** (no network) · Markdown lint: **not run** (no linter on PATH) |
| Findings raised | 24 |
| Major findings raised | 15 |
| Fixed | 21 (verdict `Fix`; listed, not applied — see tag) |
| Cobra-skipped | 1 |
| Compass-skipped | 1 |
| Integrity-discarded | 1 |
| PDCA cycles run | 1 — converged: not testable (review-only) |
| Lenses run | 10 of 10 — none omitted; W5H1 also run |
| Most productive lens | 🎯 Variety (4 findings) — W5H1 also produced 4, but it is not one of the ten lenses |
| Estimated remaining Majors | 4 — basis: per-lens yield. Nine of eleven reporting units produced Majors at a mean of 1.7 each; the mechanical class (contradictions between clause, example and grammar) was exhausted by direct enumeration of every clause and every printed example, so residual risk is concentrated where enumeration was not possible — the two regular expressions, which were read but never executed against a test corpus, and the precedence rules of clause 11, which were reasoned over but not differentially tested against the BNF. Capture–recapture is not a valid basis here: this is a single run. |
| Calibration | not tested |
| Tags | `[async — no PLAN confirmation]` `[fixes listed, not applied — convergence untested]` |

### Gap Analysis

| Gap | Reason | Recommendation |
|-----|--------|---------------|
| External link resolution (6 URLs at lines 56, 343, 354, 364, 368, 373) | No network access in this run; entry check 3 could not be executed | Re-run a link checker with network before adoption; RFC 2119 and the two regex101 permalinks are load-bearing |
| Markdown / prose lint | No markdownlint, mdl, vale or aspell on PATH | Add a markdown linter to the calibration environment so prose defects are found by tool, not by reviewer attention |
| Differential testing of the three grammar representations | No execution environment for the regexes; VAR-1 and VAR-2 were established by reading, not by running | Generate a corpus from the BNF and run both regexes against it; the disagreements found by reading are likely a lower bound |
| Instrument-internal citations (`docs/lenses.md`, `docs/calibration.md`, `docs/research/rq3-…`, `docs/research/rq5-…`, `CHANGELOG.md`, `examples/diffract.yaml`) | The run is confined to a two-file directory; these repo-relative paths cited by PROMPT.md could not be opened | Per the instrument's own rule, these citations are unverifiable in this run, not void; verify them in a run with repository access |
| The Go side of the adoption | The artifact is the only thing in scope; no module, no code, no toolchain was inspected | The decisions this review identifies (NAM-1 API surface, VAR-3 pre-1.0 rule, BOU-1 v2 path, W5H-3 window) must be written down in the library's own policy, and that document reviewed separately |
| Sampling | None — the declared sample is the whole file, all 373 lines, read line by line. No extrapolation from a sample was needed | — |
| Second reviewer | Single run by a single reviewer | Capture–recapture and calibration require at least three runs by this reviewer against this frozen artifact plus a second reviewer's set |

### Defect Prevention

| Major(s) | Upstream cause | Process change |
|----------|----------------|----------------|
| TRU-1, TRU-2, SHI-1 | Human-readable restatements (Summary, FAQ) were edited without re-deriving them from the normative clauses, so a summary drifted into stating the opposite of the clause it summarizes and a FAQ answer contradicts its own closing sentence | Add a CI check that extracts every MUST/MAY sentence from the clauses and every claim from Summary and FAQ, and fails the build when a summary or FAQ sentence is not traceable to a clause. Failing that: a release checklist item requiring Summary and FAQ to be re-read against clauses 1–11 whenever any clause changes |
| VAR-1, VAR-2, TRU-3 | The BNF is maintained by hand, in a separate section, with no mechanical link to the prose or the regexes — so an omitted alternative and an omitted terminal survive review because no reader enumerates 52 letters | CI gate: generate strings from the BNF and assert both published regexes accept exactly them, and assert every example string printed anywhere in the document is derivable from the BNF. This one gate catches VAR-1, VAR-2 and TRU-2 |
| NAM-1, NAM-2, W5H-1 | Terms were introduced in prose at the point of first use and never given a definitions section, so "public API", "incorrect behavior" and "marked as deprecated" each carry the weight of a definition without being one | Template change: require a Definitions section listing every term used inside a MUST/SHOULD sentence, and a checklist item that no normative sentence may use an undefined term |
| VAR-3 | The clause guards (`x > 0`) were written per-clause with no completeness check over the space of project states, leaving the 0.y.z regime uncovered by construction | Checklist item for any rule set with guards: enumerate the guard conditions and prove they partition the state space; an uncovered region is a defect even when every individual clause is correct |
| BOU-1, BOU-2, OBS-1, W5H-2, W5H-4 | The specification's scope boundary was never stated, so silence about package identity, resolver behavior, verification and ownership reads as neither "out of scope" nor "unspecified" | Template change: an explicit "Scope and non-goals" section, plus a maintenance/ownership block naming who arbitrates interpretation |

### Calibration Test

Not tested. A single run cannot be calibrated: one run per reviewer cannot
separate a miscalibrated reviewer from run-to-run noise. This run does not
belong to a declared set of at least three by this reviewer against this frozen
artifact, and no second reviewer's set is available for comparison. The
Scorecard's Calibration row reads "not tested" accordingly. The Confidence
values recorded in the index below are DO-time forecasts, unchanged by CHECK, so
they remain Brier-scorable if this run is later joined to a set.

---

## FINDINGS INDEX

| ID | Lens | Cycle | Line(s) | Severity | Verdict | Claim (one sentence) | Confidence |
|----|------|-------|---------|----------|---------|----------------------|------------|
| SUB-1 | Subtract | 1 | semver-2.0.0-seeded.md:152-153 | Minor | Fix | The `<valid semver>` production lists the same alternative twice, so one line is deletable with zero loss and the intended fourth alternative is absent. | High |
| SUB-2 | Subtract | 1 | semver-2.0.0-seeded.md:84-85 | Minor | Skip:Cobra | Clause 7 permits a minor increment for unobservable private changes with no criterion for "substantial", leaving the adopting team to invent a threshold. | Medium |
| SUB-3 | Subtract | 1 | semver-2.0.0-seeded.md:325 | Minor | Skip:Compass | "is probably an overkill" carries a removable article and is ungrammatical as written. | High |
| SIM-1 | Simplify | 1 | semver-2.0.0-seeded.md:96-97 | Minor | Fix | The leading-zero rule is stated in three scopes and does not hold uniformly — build identifiers are exempt — so a single shared validator cannot be written from any one of them. | Medium |
| NAM-1 | Name | 1 | semver-2.0.0-seeded.md:58-60 | Major | Fix | "Public API", the term every increment rule pivots on, is required to be declared but never defined, so the adopting team must choose the surface unaided. | High |
| NAM-2 | Name | 1 | semver-2.0.0-seeded.md:78-79 | Major | Fix | "Bug fix" is defined in terms of undefined "incorrect behavior", so a fix to undocumented-but-depended-on behavior classifies as both patch and major. | Medium |
| TRU-1 | Truth | 1 | semver-2.0.0-seeded.md:9-10 | Major | Fix | The Summary gives MAJOR the same definition it gives MINOR, contradicting clause 8 and inverting the central rule for anyone who reads the Summary first. | High |
| TRU-2 | Truth | 1 | semver-2.0.0-seeded.md:331 | Major | Fix | The FAQ answers that "v1.2.3" is a semantic version, contradicting clause 2, the grammar, both regexes and the closing sentence of the same answer. | High |
| TRU-3 | Truth | 1 | semver-2.0.0-seeded.md:339-341 | Major | Fix | The set of valid version strings is defined in four independent places that disagree, and the document never says which governs. | Medium |
| BOU-1 | Boundary | 1 | semver-2.0.0-seeded.md:88-89 | Major | Fix | The specification confines every rule to the version string and says nothing about package identity, so how a major increment is expressed in a Go import path is a call the team must make alone. | Medium |
| BOU-2 | Boundary | 1 | semver-2.0.0-seeded.md:107-108 | Major | Fix | Build metadata is excluded from precedence while releases are immutable, permitting two distinct equally-ranked releases with no defined tiebreak. | Medium |
| SHI-1 | Shield | 1 | semver-2.0.0-seeded.md:288-289 | Major | Fix | The prescribed recovery from a broken release is a patch version that restores compatibility, which clause 6 does not permit, so the remedy violates the specification. | High |
| PRO-1 | Provenance | 1 | semver-2.0.0-seeded.md:343 | Minor | Discard:Integrity | The regexes are cross-referenced to mutable third-party permalinks with no integrity anchor — not established as a defect, since both regexes are reproduced inline and the section is explicitly advisory. | Low |
| PRO-2 | Provenance | 1 | semver-2.0.0-seeded.md:242-243 | Minor | Fix | Adopters are told to link to "this website" and the document names no canonical URL, publication date, or changelog for itself. | Medium |
| VAR-1 | Variety | 1 | semver-2.0.0-seeded.md:109-110 | Major | Fix | The grammar has no production combining pre-release and build metadata, so the document's own examples 1.0.0-alpha+001 and 1.0.0-beta+exp.sha.5114f85 are not derivable from it. | High |
| VAR-2 | Variety | 1 | semver-2.0.0-seeded.md:205-206 | Major | Fix | The `<letter>` production omits uppercase "Q", so identifiers legal by clause 9 and by both regexes cannot be derived from the grammar. | High |
| VAR-3 | Variety | 1 | semver-2.0.0-seeded.md:70-71 | Major | Fix | All three increment clauses are guarded on a non-zero major, so the 0.y.z regime — where the library will spend this quarter — has no normative increment rule at all. | High |
| VAR-4 | Variety | 1 | semver-2.0.0-seeded.md:65 | Minor | Fix | "Each element MUST increase numerically" does not say whether it must increase by one, leaving skipped versions unclassified. | Medium |
| OBS-1 | Observability | 1 | semver-2.0.0-seeded.md:47-49 | Major | Fix | The document asserts that version changes convey meaning while requiring no changelog, machine-readable API declaration, or conformance test that would let a consumer verify the claim. | Medium |
| OBS-2 | Observability | 1 | semver-2.0.0-seeded.md:290-291 | Minor | Fix | Disclosure of a known non-conforming release is left to the publisher's discretion, so a broken release is indistinguishable from a sound one downstream. | Low |
| W5H-1 | W5H1 | 1 | semver-2.0.0-seeded.md:82-83 | Major | Fix | Deprecation is the only behavior-preserving change that MUST force a release, with no rationale given and no definition of what "marked as deprecated" means. | Medium |
| W5H-2 | W5H1 | 1 | semver-2.0.0-seeded.md:363-365 | Major | Fix | The document names an original author and an issue tracker but no maintainer or interpretive authority, so every ambiguity it contains escalates to nobody. | Medium |
| W5H-3 | W5H1 | 1 | semver-2.0.0-seeded.md:319-320 | Minor | Fix | The only deprecation window is "at least one minor release", stated non-normatively, with no duration or support period. | Medium |
| W5H-4 | W5H1 | 1 | semver-2.0.0-seeded.md:351-352 | Major | Fix | The document offers a hand-written BNF and hand-written regexes to Go adopters as the validation mechanism, without naming an authority among them or acknowledging the language's own parser — and the transcriptions disagree. | Medium |
