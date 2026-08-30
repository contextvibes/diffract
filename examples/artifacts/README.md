# Review artifacts

Frozen, third-party documents used as review targets in `examples/`. Each file
here is stored **verbatim** — no header, no reformatting, no corrections — so
that its content hash is reproducible from the upstream source and a review can
cite `file:line` against a fixed text.

Do not edit these files. A change here invalidates every line number, quote and
hash in the reviews that cite them.

## On reviewing documents we follow

Diffract versions itself with Semantic Versioning. We use these specifications.
We are not grading them.

Every review in `examples/` runs under an **adoption Compass**: the question is
where a team implementing against the text has to make a call the text declines
to make for them. A finding marks a decision point met during adoption. It is
not a claim that the document is defective, it is not a correction, and it is
not a request that anything change. We have filed nothing upstream and do not
intend to.

That careful readers reach different conclusions on some points is true of every
specification worth adopting. It is what makes one a useful review target rather
than a flawed one — a document nobody implements leaves no decisions to observe.

These texts are public, frozen and hash-pinned for one reason: a reader can
check every quote and every line number against the original. The example exists
to make the **review** verifiable. It is not a verdict on the **artifact**.

## Contents

| File | Upstream | License | sha256 |
|------|----------|---------|--------|
| `semver-2.0.0.md` | [semver/semver](https://github.com/semver/semver) `semver.md` | CC BY 3.0 | `33ebae1a97845991d0b916f3295a88b499e2ec71a6c1fe84c12429077b19ce08` |

## Licensing

These files are **not** covered by this repository's MIT `LICENSE`. Each is
licensed by its own author under the terms in the table above, and each retains
the attribution and license notices of its original.

`semver-2.0.0.md` is the Semantic Versioning 2.0.0 specification, authored by
Tom Preston-Werner, licensed [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
It is reproduced unmodified and carries its own `About` and `License` sections.

## Verifying

```
shasum -a 256 examples/artifacts/semver-2.0.0.md
```
