# Contributing to Diffract

Thank you for your interest in improving Diffract!

## How to Contribute

### Report a Gap

If you applied Diffract and found something the lenses didn't catch, open
an issue describing:

1. **What you were reviewing** (language, architecture style)
2. **What the lenses missed** (the specific finding)
3. **Which lens should have caught it** (or whether a new lens is needed)
4. **Evidence** that none of the existing 9 lenses cover it

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
3. Add it to `examples/` as a pull request

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
