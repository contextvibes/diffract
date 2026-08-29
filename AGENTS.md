# Instructions for Coding Agents

Two reasons an agent is in this repo. Find yours.

## Running a Diffract review

Read [PROMPT.md](PROMPT.md) and follow it exactly. It is self-contained:
governors, lenses, verdicts, severity, and every counting term are defined
there and nowhere else. Do not improvise the process from this file or from
the README — they describe the instrument; PROMPT.md *is* the instrument.

- PROMPT.md's PLAN checkpoint and its one-shot tagging rules apply to
  autonomous agents too — being an agent does not exempt you from them.
- Repo-level configuration, if present, lives in `diffract.yaml`
  (see [examples/diffract.yaml](examples/diffract.yaml)).

## Working on this repo

House rules, learned from shipped defects. Each rule points at its source
of truth — never restate a definition here or anywhere else.

1. **Counting terms are defined in PROMPT.md only** (`raised`, `survived`,
   `fixed`, `Major`/`Minor`). Other files reference them. Release 0.2.3
   shipped because two files defined `survived` differently.
2. **Changing PROMPT.md stales every measured reviewer tier**
   ([docs/calibration.md](docs/calibration.md)). Batch instrument changes
   into one release; never edit PROMPT.md casually.
3. **A PR that touches PROMPT.md's templates re-diffs `examples/` in the
   same PR** — checklist in [CONTRIBUTING.md](CONTRIBUTING.md).
4. **The version string lives in two places** — the README badge and the
   PROMPT.md header. Change both or neither; a release once shipped with
   them disagreeing.
5. **CHANGELOG.md is narrative** — prose explaining why, not bullet-only
   lists. Match the existing entries.
6. **In any review output, `## FINDINGS INDEX` is authoritative** — every
   count stated elsewhere is derived by counting its rows. The rule and
   the counting definitions live in PROMPT.md.
7. **Attribute honestly.** No component of Diffract is original; new ideas
   enter with their sources named in README's References table. Overclaiming
   is this repo's cardinal sin — its research docs publish its failures.
