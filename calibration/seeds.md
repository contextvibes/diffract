# Answer key — `artifacts/semver-2.0.0-seeded.md`

> **Spoiler.** This file lists every defect planted in the fixture. Reading it
> disqualifies you, or any agent you are running, from producing a scoreable
> review of that artifact. See [`README.md`](README.md).

Base artifact: `examples/artifacts/semver-2.0.0.md`
(sha256 `33ebae1a97845991d0b916f3295a88b499e2ec71a6c1fe84c12429077b19ce08`)

Line numbers below are identical in the seeded file and the base artifact: the
seeds edit within existing lines, and the fixture's modification notice sits at
the end of the file precisely so the body's numbering is unaffected by it.

## S1 — line 9 · predicted lens 📌 Truth

| | |
|---|---|
| Was | `1. MAJOR version when you make incompatible API changes` |
| Now | `1. MAJOR version when you add functionality in a backward compatible` |

The summary at the head of the document now gives MAJOR the MINOR condition, so
it says the same thing as the line below it and contradicts the normative clause
requiring MAJOR to be incremented for backward incompatible changes. A reader
following the summary versions every breaking change as a minor release.

Expected to be the easiest seed: the contradiction is with a clause most readers
already know, and the duplicated wording is visible without cross-referencing.

**Known weakness.** The seeded sentence borrows the wrapped line below it
without its continuation, so line 9 dangles where the original did not. The
first scored run spotted that dangling wrap and used it as a tell, which means
S1 is partly detectable as a formatting artifact rather than as a
contradiction. It has deliberately **not** been corrected in place: this
fixture has been scored, and editing it would invalidate the citations of the
review published against it. A completed sentence belongs in a future fixture
version, scored separately.

## S2 — line 206 · predicted lens 🛡️ Shield

| | |
|---|---|
| Was | `\| "K" \| "L" \| "M" \| "N" \| "O" \| "P" \| "Q" \| "R" \| "S" \| "T"` |
| Now | `\| "K" \| "L" \| "M" \| "N" \| "O" \| "P" \| "R" \| "S" \| "T"` |

Uppercase `Q` is gone from the `<letter>` production. The grammar now rejects
pre-release and build identifiers that the prose explicitly permits, since the
prose defines the alphabet as `[0-9A-Za-z-]`. Grammar and prose disagree about
which versions are valid, and an implementer generating a parser from the BNF
produces one that rejects conforming input.

Expected to be the hardest seed: finding it requires enumerating a 52-element
production rather than reading it.

## S3 — line 153 · predicted lens 🎯 Variety

| | |
|---|---|
| Was | `\| <version core> "-" <pre-release> "+" <build>` |
| Now | `\| <version core> "+" <build>` |

The alternative permitting pre-release and build metadata together has been
replaced by a duplicate of the line above it. Versions carrying both are now
ungrammatical, although the document presents such a version as valid elsewhere.
The duplicate is what makes this hard: nothing is obviously missing, and the
production still looks complete.

## S4 — line 331 · predicted lens 🧱 Boundary

| | |
|---|---|
| Was | `No, "v1.2.3" is not a semantic version.` |
| Now | `Yes, "v1.2.3" is a semantic version.` |

The FAQ answer is reversed. It contradicts the grammar, which requires a version
core to begin with a numeric identifier, and it contradicts the rest of its own
paragraph, which goes on to call `"v1.2.3"` a tag name and `"1.2.3"` the
semantic version. A reviewer that reads the paragraph to its end cannot miss it.

## A note on predicted lenses

The lens named on each seed is a prediction, not a scoring criterion. A seed is
found or not found; the lens that finds it is an observation about the
instrument, not a requirement on the reviewer. In the first scored run three of
four seeds were found by a lens other than the predicted one.

## Disjointness

Checked against the cited line ranges of every review published in `examples/`
at the time each seed was added. No seed sits in territory any published review
reports. Re-check before adding a seed, and before publishing a new review.
