# Contributing to Diffract

Thank you for your interest in improving Diffract!

## How to Contribute

### Report a Gap

If you applied Diffract and found something the lenses didn't catch, open
an issue describing:

1. **What you were reviewing** (language, architecture style)
2. **What the lenses missed** (the specific finding)
3. **Which lens should have caught it** (or whether a new lens is needed)
4. **Evidence** that none of the existing 10 lenses cover it

### Propose a Lens Change

To propose adding, removing, or modifying a lens:

1. **Root principle** — what first principle outside software is it grounded in?
2. **Uniqueness proof** — what does it catch that no other lens catches?
3. **The question** — express it as a single yes/no question
4. **Evidence format** — what does the output look like?
5. **Adversarial assumption** — what does it assume about the artifact
   being non-adversarial? Mechanisms imported from human-inspection
   industries assume the artifact cannot talk back; an artifact reviewed
   by an LLM can.

### Share a Review Example

If you've completed a full Diffract review and want to share it:

1. Anonymize all project-specific details
2. Include the PLAN (governors), DO (findings), CHECK (vetting), and LEARN (retro)
3. Check it against the template-conformance checklist below
4. Add it to `examples/` as a pull request

**Template-conformance checklist** — examples in `examples/` demonstrate
the templates in [PROMPT.md](PROMPT.md), so they must match them. Before
submitting (and whenever a PR changes PROMPT.md's templates, in that same
PR), diff each example's section and table headers against PROMPT.md and
confirm:

- [ ] A version line under the title states which PROMPT.md revision the
      example was written against ("Written against Diffract vX.Y.Z")
- [ ] All 10 lens sections are present, in the prescribed 1–10 order, and
      any cognitive anchoring fits the reviewed artifact's language
- [ ] PLAN shows either a confirmation exchange or the
      `[async — no PLAN confirmation]` tag, and DO opens with Cold-Start
      Calibration
- [ ] Lens finding tables carry the
      `ID | File | Finding | Line | Severity | Confidence` columns, with
      IDs in PROMPT.md's `<lens abbreviation>-<n>` grammar;
      the CHECK table carries the
      `⚖️ Integrity | 🧭 Compass | 🐍 Cobra | Verdict` columns
- [ ] Every Low-Confidence finding carries a competing-hypotheses block
      before its verdict (rival explanations + the evidence that
      discriminates), per PROMPT.md's CHECK
- [ ] CHECK includes Scope and Nothing-Found Verification, with a
      seeded-bug example for every lens in scope that differs from any
      DO-time anchoring; LEARN includes
      fix application + verification, Scorecard (with "Reviewer",
      "Artifact", "Instrument", "Governors", "Entry checks",
      "Major findings raised", "Lenses run",
      "Estimated remaining Majors", and
      "Tags" rows), Gap Analysis, and Defect Prevention
- [ ] The review ends with `## FINDINGS INDEX` carrying the `Cycle`
      column, and every count stated elsewhere matches its row count

### Improve Documentation

Clarity improvements, additional examples, and translations are welcome.

### Share a Calibration Result

If you've run Diffract with two independent reviewers (human or AI):

1. Record results using the template in [docs/calibration.md](docs/calibration.md)
2. Note which lenses produced the same findings and which diverged
3. Submit as a PR or issue

## Development Principles

Diffract follows its own framework. Changes to the framework should be
validated by running Diffract on itself:

1. Does the change pass the 🗑️ Subtract lens? (Is it necessary?)
2. Does it pass the 📌 Truth lens? (Is it in one place?)
3. Does it pass the 🏷️ Name lens? (Is it well-named?)
4. Is the finding that motivated the change falsifiable?

## Release Gates

Defect-prevention rules from this repo's own reviews — each gate traces to
a defect that shipped, or survived multiple releases, before a review
caught it:

- [ ] **Research blockers are closed or deferred.** Every blocker a
      research report (`docs/research/`) names is either fixed or
      explicitly deferred in the release's CHANGELOG entry. (RQ5 named
      the "Start simple" contradiction and the W5H1 gap; both survived
      two releases because report findings had no pipeline into fixes.)
- [ ] **No mandated column without a definition.** Every table column a
      PROMPT.md template mandates has an inline definition in PROMPT.md.
      (The Findings Index `Confidence` column shipped undefined.)
- [ ] **README's spec statements diff clean against PROMPT.md** — the
      done-rule, lens questions, verdict names, and tag strings.
      (README shipped a superseded exit rule after 0.2.4 changed it.)
- [ ] **Version strings agree** — the README badge and the PROMPT.md
      header. (0.2.3 shipped with the header still reading 0.2.2.)
- [ ] **Template changes re-sync `examples/`** — the checklist above,
      in the same PR. **Exception: a review that is hash-pinned and
      quote-checkable is frozen at the instrument version that produced
      it** and is never re-synced; editing it destroys the property that
      makes it evidence. A release that leaves such a review behind says
      so in its CHANGELOG entry and states why. Illustrative examples
      carrying no hash re-sync as normal.
- [ ] **Prose that cites an example's metrics is diffed against that
      example's FINDINGS INDEX** whenever either file changes. (README
      shipped claiming "3 PDCA cycles" and the wrong most-productive
      lenses about an example whose own scorecard said otherwise.)
- [ ] **Quantified governor thresholds appear only in PROMPT.md** —
      ">30 minutes", "architectural changes", "published API contract"
      and their kin; other files link, never restate. (Cobra's operational
      definitions lived in docs/governors.md and drifted from PROMPT.md's
      glosses — the `survived` defect class, one governor over.)
- [ ] **A PR adding an execution path walks the full state matrix**:
      every reviewer-reachable stop state names its tag, every governor
      states its mapping for code, non-code, and agentic inputs, and
      every Rule states its behavior for instruction-artifact inputs —
      self-review is an advertised use. (Agentic mode shipped with
      untagged circuit-breaker stops; the non-code adaptation remapped
      Integrity but left Cobra code-only; Rule 9 turned self-review into
      a false-finding generator.)
- [ ] **Every mandated step names the output element that proves it
      ran**, and every mandated output element names the step it proves.
      A step whose execution cannot be located in the review document is
      auditable only by the reviewer claiming to have run it. (The
      competing-hypotheses step shipped with no mandated location and no
      Confidence column in the CHECK table; W5H1 shipped mandatory,
      exempt from every verification applied to lenses, and absent from
      the Scorecard — so a run that skipped it passed every self-check.)
- [ ] **A mandated check consumes only artifacts that exist by its
      phase.** (Nothing-Found Verification, in CHECK, shipped ordering a
      count check against the Findings Index, which is built in LEARN.)
- [ ] **A PR that adds an input channel to PROMPT.md** — a config key, a
      tag, a mode, a file the reviewer reads — **includes a written
      🛡️ Shield + 🎯 Variety pass over that channel** in the PR
      description. (Agentic mode's `diffract.yaml` shipped with governors
      obeyed unchallenged from the repo under review, and with the
      user-present-plus-config-present state undefined — the protocol was
      applied to its prose but never to its new attack and state surface.)
- [ ] **Every rule a script enforces has a sentence in PROMPT.md, and
      every rule PROMPT.md states that a script could enforce is enforced
      or explicitly listed as unenforced.** The scripts are not a second
      specification. (`check_review.py` shipped requiring a per-finding
      Evidence block in a format PROMPT.md never described, so a reviewer
      following the instrument could not pass the checker shipped with
      it; the same checker reconciled five Scorecard rows out of sixteen
      and passed a review that had dropped the other eleven.)
- [ ] **A fix to an enumerated space names the sibling cases and states
      the outcome for each.** When a defect is fixed for one config value,
      one scope, one input channel, or one branch of a rule, the PR says
      what the fix does for every other value of that same enumeration —
      or why the others are not affected. (Three consecutive releases
      fixed one instance of the artifact-configures-its-own-review defect
      and left its siblings open: the executable channel, then the
      declarative channel under `scope: pr`, then `scope: full`. Each fix
      was correct and none was general.)
- [ ] **Version-string equality is checked mechanically, not by eye** —
      `grep` the README badge against the PROMPT.md header before
      tagging. (The duplication is forced — the badge and the standalone
      paste each need a version — and prose rules around it have already
      failed once: 0.2.3 shipped with the header reading 0.2.2.)

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
