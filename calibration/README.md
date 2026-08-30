# Calibration fixtures

A seeded fixture is a public document with deliberate, known defects planted in
it. Running a reviewer against one measures something no ordinary review can:
not whether the findings look reasonable, but **how many of the defects that are
definitely there were actually found**.

`docs/calibration.md` describes the method. This directory holds the artifacts.

## Contents

| Fixture | Base artifact | Seeds | Answer key |
|---------|---------------|-------|------------|
| [`artifacts/semver-2.0.0-seeded.md`](artifacts/semver-2.0.0-seeded.md) | Semantic Versioning 2.0.0 | 4 | [`seeds.md`](seeds.md) — **opening it spoils the fixture** |

The review that fixture has been scored against is
[`semver-2.0.0-seeded-review.md`](semver-2.0.0-seeded-review.md). It reports
four defects that were planted, so it is not commentary on Semantic Versioning
and says so at the top.

Scored runs are recorded in [`results.md`](results.md).

## Blindness is procedural, not secret

The answer key sits in the same public repository as the fixture. Anyone can
read it, and so can any agent given repository access. A fixture in a public
repo can never be blind by secrecy.

It is blind by **procedure**: the reviewer is run in a directory containing only
`PROMPT.md` and the seeded artifact, with no repository access, no git and no
network. That is how the published reviews in `examples/` were produced, and it
is the only condition under which a score from this fixture means anything.

A run that had repository access is not a calibration run. Report it as void
rather than as a low score.

## What may be seeded

Every seed must satisfy three rules.

**Objectively checkable.** A seed is a defect a reader can demonstrate from the
document alone — an internal contradiction, a grammar that rejects what the
prose permits, an example that violates its own stated rule. Nothing that turns
on taste, house style or the reviewer's priorities: those produce arguments
about scoring rather than scores.

**Disjoint from every published review.** No seed may sit in territory that a
review published in `examples/` already reports. Otherwise a reviewer that has
read the published review scores well without having looked at the artifact.
Disjointness is checked against the cited line ranges of every published review
before a seed is accepted, and every new published review shrinks the pool of
legal seeds.

**Line-preserving.** Seeds edit within existing lines and never add or remove
them, so a seeded line number is stable as seeds are added or retired.

## A scored fixture is frozen

Once a run has been scored against a fixture, that file does not change — the
same rule `examples/artifacts/` applies to upstream texts, for the same reason.
Any edit invalidates every line number and quote in the reviews that cite it,
including the citations a published review is checked by.

Weaknesses found in a seed are therefore recorded in `seeds.md` and fixed in a
**new fixture version**, scored separately, never by editing a fixture that
already has results against it.

## Running one

Copy `PROMPT.md` and the seeded artifact into an empty directory. Nothing else
goes in it — in particular no review of the same base artifact, published or
otherwise.

**Strip the trailing modification notice from the copy.** It states that the
file has been altered for calibration, which primes a reviewer to hunt for
planted defects and inflates the score. The notice exists to mark the
distributed derivative as CC BY requires; a scratch copy used for one run is
not distributed. It sits at the end of the file so removing it leaves every
line number unchanged.

Run the reviewer there with no repository access, no git and no network, then
check the form of what comes back:

```
python3 scripts/check_review.py REVIEW.md --artifact calibration/artifacts/semver-2.0.0-seeded.md
```

Then open `seeds.md` and score: a seed is **found** if a finding names the same
defect, at the seeded line, for a reason that matches. A finding that lands on a
seeded line for an unrelated reason is not a hit.

Recall is the headline number, but the interesting one is usually which lens
caught which seed, and whether the seeds a reviewer misses cluster.

## Licensing

`artifacts/semver-2.0.0-seeded.md` is a **modified** copy of Semantic Versioning
2.0.0 by Tom Preston-Werner, used under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/),
which permits derivatives provided modifications are indicated. They are: in the
file's own header, in its filename, and in `seeds.md`. It is not covered by this
repository's MIT `LICENSE`.

It is not the specification and must not be cited, implemented against or read
as one. The unmodified text is at
[`examples/artifacts/semver-2.0.0.md`](../examples/artifacts/semver-2.0.0.md).
