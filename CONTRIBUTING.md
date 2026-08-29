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
- [ ] Lens finding tables carry the `# | File | Finding | Line | Severity`
      columns; the CHECK table carries the
      `⚖️ Integrity | 🧭 Compass | 🐍 Cobra | Verdict` columns
- [ ] CHECK includes Nothing-Found Verification; LEARN includes
      fix application + verification, Scorecard (with "Major findings" and
      "Estimated remaining Majors" rows), Gap Analysis, and Defect
      Prevention
- [ ] The review ends with `## FINDINGS INDEX`, and every count stated
      elsewhere matches its row count

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

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
