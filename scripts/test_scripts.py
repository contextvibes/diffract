#!/usr/bin/env python3
"""Regression fixtures for the scripts in this directory.

Each fixture is a mutation of a review this repository publishes, written to a
temporary file and run through the real scripts by their command lines: the
published reviews are the positive fixtures, and each mutation reproduces one
defect a blind cycle or an issue found, so the script that let it through
fails here if it ever lets it through again. Mutations rather than stored
copies, because a stored copy of a review is one more file that drifts from
the review it was copied from.

Run from anywhere:  python3 scripts/test_scripts.py
Exit code 0 = every fixture behaves as expected. Standard library only.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'scripts')

EXAMPLE = os.path.join(ROOT, 'examples', 'semver-2.0.0-review.md')
EXAMPLE_ARTIFACT = os.path.join(ROOT, 'examples', 'artifacts', 'semver-2.0.0.md')
SEEDED = os.path.join(ROOT, 'calibration', 'semver-2.0.0-seeded-review.md')
SEEDED_ARTIFACT = os.path.join(ROOT, 'calibration', 'artifacts', 'semver-2.0.0-seeded.md')
WEB = os.path.join(ROOT, 'examples', 'web-service.md')


def run(script, *args, cwd=ROOT):
    """(exit code, stdout + stderr) of one script run."""
    done = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args],
                          cwd=cwd, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def read(path):
    with open(path) as handle:
        return handle.read()


class Fixtures(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, text):
        path = os.path.join(self.tmp.name, name)
        with open(path, 'w') as handle:
            handle.write(text)
        return path

    def check(self, review, artifact):
        return run('check_review.py', review, '--artifact', artifact)

    # -- positive fixtures: everything this repository publishes passes ----

    def test_repository_checks_pass(self):
        code, out = run('check.py')
        self.assertEqual(code, 0, out)

    def test_published_reviews_pass(self):
        for review, artifact in ((EXAMPLE, EXAMPLE_ARTIFACT), (SEEDED, SEEDED_ARTIFACT)):
            code, out = self.check(review, artifact)
            self.assertEqual(code, 0, f'{review}\n{out}')
            self.assertIn('all checks pass', out)

    def test_published_scorecards_agree(self):
        for review in (WEB, EXAMPLE, SEEDED):
            code, out = run('render_scorecard.py', review)
            self.assertEqual(code, 0, f'{review}\n{out}')

    # -- issue #50: a skipped lens is never corrected away -----------------

    def without_efficiency(self):
        text = read(SEEDED)
        cut = re.sub(r'^### ⚡ Efficiency.*?(?=^### )', '', text, count=1, flags=re.M | re.S)
        self.assertNotEqual(cut, text)
        return cut

    def test_50_render_refuses_a_high_lenses_run(self):
        review = self.write('no-efficiency.md', self.without_efficiency())
        code, out = run('render_scorecard.py', review, '--write')
        self.assertEqual(code, 2, out)
        self.assertIn('REFUSED: Lenses run states 10', out)
        self.assertNotIn('CORRECTED: Lenses run', out)
        self.assertIn('| Lenses run | 10 of 10', read(review))
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn('no section for: Efficiency', out)

    def test_50_check_rejects_a_hand_laundered_lenses_run(self):
        text = self.without_efficiency().replace(
            '| Lenses run | 10 of 10', '| Lenses run | 9 of 10', 1)
        review = self.write('laundered.md', text)
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn('does not name the omitted: Efficiency', out)

    def test_50_a_declared_narrowing_still_passes(self):
        text = self.without_efficiency().replace(
            '| Lenses run | 10 of 10 — none omitted',
            '| Lenses run | 9 of 10 — Efficiency omitted by the requester', 1)
        review = self.write('narrowed.md', text)
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 0, out)

    def test_50_a_low_lenses_run_is_still_corrected(self):
        text = read(SEEDED).replace('| Lenses run | 10 of 10', '| Lenses run | 8 of 10', 1)
        review = self.write('low.md', text)
        code, out = run('render_scorecard.py', review)
        self.assertEqual(code, 1, out)
        self.assertIn('CORRECTED: Lenses run: 8 -> 10', out)

    # -- issue #49: a cited path must be a suffix of the supplied path -----

    def test_49_a_citation_to_another_directory_fails(self):
        text = read(EXAMPLE).replace(
            'examples/artifacts/semver-2.0.0.md:', 'totally/other/dir/semver-2.0.0.md:')
        self.assertIn('totally/other/dir/semver-2.0.0.md:', text)
        review = self.write('elsewhere.md', text)
        code, out = self.check(review, EXAMPLE_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn('cites totally/other/dir/semver-2.0.0.md', out)
        self.assertNotIn('all checks pass', out)

    def test_49_shorter_and_absolute_suffixes_pass(self):
        for cited in ('semver-2.0.0.md', 'artifacts/semver-2.0.0.md', EXAMPLE_ARTIFACT):
            text = read(EXAMPLE).replace('examples/artifacts/semver-2.0.0.md:', cited + ':')
            review = self.write('suffix.md', text)
            code, out = self.check(review, EXAMPLE_ARTIFACT)
            self.assertEqual(code, 0, f'{cited}\n{out}')

    def test_49_a_shared_basename_is_told_apart_by_its_path(self):
        twin = os.path.join(self.tmp.name, 'twin', 'semver-2.0.0.md')
        os.makedirs(os.path.dirname(twin))
        with open(twin, 'w') as handle:
            handle.write('not the artifact\n')
        code, out = run('check_review.py', EXAMPLE, '--artifact', EXAMPLE_ARTIFACT,
                        '--artifact', twin)
        self.assertEqual(code, 0, out)
        text = read(EXAMPLE).replace('examples/artifacts/semver-2.0.0.md:', 'semver-2.0.0.md:')
        review = self.write('ambiguous.md', text)
        code, out = run('check_review.py', review, '--artifact', EXAMPLE_ARTIFACT,
                        '--artifact', twin)
        self.assertEqual(code, 1, out)
        self.assertIn('names more than one supplied artifact', out)

    # -- issue #46: the scripts are held to scripts/MANIFEST ---------------

    def copy_of_repo(self):
        """A copy of the files check.py reads, scripts/ and its manifest included."""
        root = os.path.join(self.tmp.name, 'repo')
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        return root

    def manifest_failures(self, root):
        done = subprocess.run([sys.executable, os.path.join(root, 'scripts', 'check.py')],
                              cwd=root, capture_output=True, text=True)
        return done.returncode, [l for l in done.stdout.splitlines() if 'MANIFEST' in l]

    def test_46_an_edited_script_fails_the_manifest(self):
        root = self.copy_of_repo()
        self.assertEqual(self.manifest_failures(root), (0, []))
        with open(os.path.join(root, 'scripts', 'score_seeds.py'), 'a') as handle:
            handle.write('# edited\n')
        code, lines = self.manifest_failures(root)
        self.assertEqual(code, 1)
        self.assertIn('score_seeds.py does not match its scripts/MANIFEST hash', ' '.join(lines))

    def test_46_a_missing_or_unlisted_script_fails_the_manifest(self):
        root = self.copy_of_repo()
        os.remove(os.path.join(root, 'scripts', 'score_seeds.py'))
        with open(os.path.join(root, 'scripts', 'extra.py'), 'w') as handle:
            handle.write('')
        code, lines = self.manifest_failures(root)
        self.assertEqual(code, 1)
        joined = ' '.join(lines)
        self.assertIn('lists score_seeds.py, which is not in scripts/', joined)
        self.assertIn('scripts/extra.py is not in scripts/MANIFEST', joined)

    # -- issue #43 VAR-3: an escaped pipe is part of its cell ---------------

    def with_escaped_pipes(self):
        text = read(EXAMPLE)
        governors = '· 🐍 Library/Framework ·'
        claim = 'what its parser does on receiving it.'
        self.assertIn(governors, text)
        self.assertIn(claim, text)
        text = text.replace(
            governors, '· 🐍 Library/Framework (of prototype \\| production \\| library/framework) ·', 1)
        return text.replace(claim, 'what its parser does on receiving it: accept \\| strip \\| reject.')

    def test_43_escaped_pipes_do_not_shift_columns(self):
        review = self.write('pipes.md', self.with_escaped_pipes())
        code, out = self.check(review, EXAMPLE_ARTIFACT)
        self.assertEqual(code, 0, out)
        code, out = run('render_scorecard.py', review)
        self.assertEqual(code, 0, out)
        code, out = run('score_seeds.py', review, '--seeds',
                        os.path.join(ROOT, 'calibration', 'seeds.md'))
        self.assertEqual(code, 0, out)

    def test_43_an_unescaped_pipe_still_fails(self):
        text = read(EXAMPLE).replace(
            'what its parser does on receiving it.', 'accept | strip | reject.', 1)
        review = self.write('bare-pipes.md', text)
        code, out = self.check(review, EXAMPLE_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn('index row is 10 columns, expected 8', out)

    # -- issue #47: no failure state survives between calls ----------------

    def test_47_no_module_level_failure_list(self):
        sys.path.insert(0, SCRIPTS)
        try:
            import check
            import check_review
            import render_scorecard
        finally:
            sys.path.remove(SCRIPTS)
        self.assertFalse(hasattr(check_review, 'failures'))
        self.assertFalse(hasattr(check, 'failures'))
        broken = read(SEEDED).replace('| Major | Fix |', '| Major | Fixx |', 1)
        self.assertNotEqual(broken, read(SEEDED))
        _, _, _, refused = render_scorecard.render(broken)
        self.assertTrue(refused)
        rendered, changes, _, refused = render_scorecard.render(read(SEEDED))
        self.assertEqual((changes, refused), ([], []))
        self.assertEqual(rendered, read(SEEDED))

    # -- issue #39: restated vocabulary is held to PROMPT.md ---------------

    def drift_failures(self, root):
        done = subprocess.run([sys.executable, os.path.join(root, 'scripts', 'check.py')],
                              cwd=root, capture_output=True, text=True)
        return done.returncode, [l for l in done.stdout.splitlines()
                                 if 'MANIFEST' not in l and l.startswith('FAIL')]

    def edit(self, root, name, old, new):
        path = os.path.join(root, name)
        text = read(path)
        self.assertIn(old, text, name)
        with open(path, 'w') as handle:
            handle.write(text.replace(old, new, 1))

    def test_39_the_old_integrity_options_fail(self):
        root = self.copy_of_repo()
        self.edit(root, 'examples/diffract.yaml',
                  '# Options: file-line | file-line-with-anchoring |\n'
                  '#          file-line-with-anchoring-and-quotes (the PLAN default)',
                  '# Options: file-line, file-line-with-anchoring (default)')
        code, lines = self.drift_failures(root)
        self.assertEqual(code, 1)
        joined = ' '.join(lines)
        self.assertIn('Options for integrity list file-line | file-line-with-anchoring;', joined)
        self.assertIn("marks 'file-line-with-anchoring' as the integrity default", joined)

    def test_39_illegal_config_keys_and_values_fail(self):
        root = self.copy_of_repo()
        self.edit(root, 'examples/diffract.yaml', 'cobra: production', 'cobra: strict')
        self.edit(root, 'examples/diffract.yaml', 'max_cycles: 3', 'max_cycles: 5\nlenses: 3')
        self.edit(root, 'CONTRIBUTING.md', '`scope: full`', '`scope: repo`')
        code, lines = self.drift_failures(root)
        self.assertEqual(code, 1)
        joined = ' '.join(lines)
        self.assertIn("cobra: 'strict' is not a permitted value", joined)
        self.assertIn("max_cycles: '5' is outside 1–3", joined)
        self.assertIn("'lenses' is not a PROMPT.md config key", joined)
        self.assertRegex(joined, r"CONTRIBUTING.md:\d+: scope: 'repo' is not a permitted value")

    def test_39_verdicts_tags_and_bins_restated_wrongly_fail(self):
        root = self.copy_of_repo()
        self.edit(root, 'README.md', '`[entry waived: cannot run checks]`',
                  '`[entry skipped: cannot run checks]`')
        self.edit(root, 'CONTRIBUTING.md', '`[async — no PLAN confirmation]`',
                  '`[async: no PLAN confirmation]` or Skip:Scope')
        self.edit(root, 'PROMPT.md', '| Major/Minor | High/Medium/Low |',
                  '| Major/Minor | High/Low |')
        code, lines = self.drift_failures(root)
        self.assertEqual(code, 1)
        joined = ' '.join(lines)
        self.assertIn("tag '[entry skipped: cannot run checks]' matches no PROMPT.md tag", joined)
        self.assertIn("tag '[async: no PLAN confirmation]' matches no PROMPT.md tag", joined)
        self.assertIn("'Skip:Scope' is not a PROMPT.md verdict", joined)
        self.assertIn("'High/Low' is not PROMPT.md's High/Medium/Low", joined)

    def test_39_a_verdict_added_to_prompt_is_accepted_from_it(self):
        prompt = read(os.path.join(ROOT, 'PROMPT.md'))
        row = '| `Discard:Integrity` | Fails the evidence bar — not established as real |\n'
        self.assertIn(row, prompt)
        block = '"verdicts": ["Fix", "Skip:Compass", "Skip:Cobra", "Discard:Integrity"]'
        self.assertIn(block, prompt)
        # Added at both ends: the prose table and the spec block (issue #51).
        widened = self.write('PROMPT.md', prompt.replace(
            row, row + '| `Skip:Budget` | Real, but over the review budget |\n', 1).replace(
            block, block[:-1] + ', "Skip:Budget"]', 1))
        review = self.write('budget.md', read(SEEDED).replace('| Minor | Fix |', '| Minor | Skip:Budget |', 1))
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn("illegal verdict 'Skip:Budget'", out)
        code, out = run('check_review.py', review, '--artifact', SEEDED_ARTIFACT,
                        '--prompt', widened)
        self.assertNotIn('illegal verdict', out)

    # -- issue #41: every rule check_review applies is read from PROMPT.md --

    def test_41_an_id_whose_prefix_is_not_its_lens_fails(self):
        row = '| SUB-1 | Subtract | 1 |'
        text = read(SEEDED)
        self.assertIn(row, text)
        review = self.write('prefix.md', text.replace(row, '| SIM-1 | Subtract | 1 |', 1))
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn("SIM-1: ID is not SUB-<n> for lens 'Subtract'", out)

    def test_41_an_illegal_confidence_fails(self):
        text = read(SEEDED)
        start = text.index('| SUB-1 | Subtract | 1 |')
        end = text.index('\n', start)
        row = text[start:end]
        self.assertTrue(row.endswith('| High |'), row)
        review = self.write('confidence.md',
                            text[:start] + row[:-len('High |')] + 'Certain |' + text[end:])
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn("illegal Confidence 'Certain'", out)

    def test_41_a_template_literal_is_read_from_prompt(self):
        prompt = read(os.path.join(ROOT, 'PROMPT.md'))
        literal = 'No findings matching this pattern.'
        self.assertIn(literal, prompt)
        changed = self.write('PROMPT.md', prompt.replace(literal, 'Nothing matched this pattern.'))
        code, out = run('check_review.py', SEEDED, '--artifact', SEEDED_ARTIFACT,
                        '--prompt', changed)
        self.assertEqual(code, 1, out)
        self.assertIn('Nothing matched this pattern.', out)

    def test_41_a_slash_lenses_run_is_not_read_as_a_narrowing(self):
        # PROMPT.md's row is `X of 10`; the `X/10` form the checker also
        # accepted was a script-only rule, so it no longer declares a scope.
        text = self.without_efficiency().replace(
            '| Lenses run | 10 of 10 — none omitted',
            '| Lenses run | 9/10 — Efficiency omitted by the requester', 1)
        review = self.write('slash.md', text)
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn('no section for: Efficiency', out)
        # And the value itself fails, rather than being skipped (call 6 of
        # the #41 judgment calls, settled with #51's spec block).
        self.assertIn("'Lenses run' value '9/10", out)
        self.assertIn("does not open in PROMPT.md's form 'X of 10'", out)

    # -- issue #42: `scope: path` can name its path --------------------------

    def vocabulary(self, prompt=os.path.join(ROOT, 'PROMPT.md')):
        sys.path.insert(0, SCRIPTS)
        try:
            import check_review
        finally:
            sys.path.remove(SCRIPTS)
        failures = []
        vocab = check_review.normative_vocabulary(prompt, failures)
        self.assertEqual(failures, [])
        return vocab

    def test_42_path_is_a_config_key_with_no_value_list(self):
        vocab = self.vocabulary()
        self.assertEqual(vocab['config_keys'], ['version', 'compass', 'cobra', 'integrity',
                                                'scope', 'path', 'max_cycles'])
        self.assertNotIn('path', vocab['config_values'])
        self.assertEqual(vocab['config_values']['scope'], ['pr', 'full', 'path'])

    def test_42_a_config_that_sets_path_passes(self):
        root = self.copy_of_repo()
        self.edit(root, 'examples/diffract.yaml', 'scope: pr\n', 'scope: path\n')
        self.edit(root, 'examples/diffract.yaml', '# path: src/payments', 'path: src/payments')
        self.assertEqual(self.drift_failures(root), (0, []))

    def test_42_the_key_is_read_from_prompt_not_assumed(self):
        root = self.copy_of_repo()
        self.edit(root, 'examples/diffract.yaml', '# path: src/payments', 'path: src/payments')
        self.edit(root, 'PROMPT.md', '`scope`, `path` (the subtree a\n  `scope: path` run reviews), ',
                  '`scope`, ')
        # Removed from the prose alone, the block and the prose disagree.
        code, lines = self.drift_failures(root)
        self.assertEqual(code, 1)
        self.assertIn('the spec block disagrees with the diffract.yaml key list', ' '.join(lines))
        # Removed from both, the example config's key is no longer permitted.
        self.edit(root, 'PROMPT.md', '"scope", "path", "max_cycles"', '"scope", "max_cycles"')
        code, lines = self.drift_failures(root)
        self.assertEqual(code, 1)
        joined = ' '.join(lines)
        self.assertIn("'path' is not a PROMPT.md config key", joined)
        self.assertNotIn('the spec block disagrees', joined)


    # -- issue #40: the entry gate is keyed on what is missing ---------------

    def entry_tables(self):
        """PROMPT.md's two entry-gate tables, as lists of unescaped rows."""
        sys.path.insert(0, SCRIPTS)
        try:
            import check_review
        finally:
            sys.path.remove(SCRIPTS)
        text = read(os.path.join(ROOT, 'PROMPT.md'))
        start = text.index('**First, classify each check by what is missing for it**')
        end = text.index('Then propose governors')
        tables, current = [], None
        for line in text[start:end].split('\n'):
            cells = check_review.split_row(line)
            if cells is None:
                current = None
                continue
            if current is None:
                current = []
                tables.append(current)
            if not all(re.match(r'^:?-*:?$', c) for c in cells):
                current.append([check_review.unescape(c) for c in cells])
        self.assertEqual(len(tables), 2, tables)
        return [rows[1:] for rows in tables]

    def test_40_what_is_missing_decides_one_result_each(self):
        classify, _ = self.entry_tables()
        results = [row[2] for row in classify]
        self.assertEqual(len(results), 4, classify)
        self.assertEqual(len(set(results)), 4, results)
        tool, subset, none = (next(r for r in results if key in r) for key in
                              ('no tool', 'target not supplied', 'inapplicable'))
        self.assertEqual(len({tool, subset, none}), 3)
        # Rows are ordered and the first yes decides; the target rows come
        # first, so a check missing both is settled by its target.
        order = [r for r in results if r in (tool, subset, none)]
        self.assertEqual(order, [none, subset, tool])

    def test_40_the_three_cases_carry_three_different_tags(self):
        _, outcomes = self.entry_tables()
        self.assertEqual(len(outcomes), 6, outcomes)
        tag = {}
        for condition, _, row_tag in outcomes:
            if condition.startswith('Nothing failed'):
                tag[condition] = row_tag
        self.assertEqual(len(tag), 3, tag)
        # No check ran / some ran, some not run / some ran, rest inapplicable.
        self.assertEqual(sorted(tag.values()),
                         sorted(['[entry waived: cannot run checks]',
                                 '[entry partial: <checks not run>]', 'none']))
        # The partial tag says which of the two was missing, so a run that
        # lacked a tool and one that lacked a file stay apart in the record.
        prose = ' '.join(read(os.path.join(ROOT, 'PROMPT.md')).split())
        self.assertIn('names each check not run and what was missing for it — '
                      '`no tool` or `target not supplied`', prose)

    # -- issue #51: one machine-readable spec, held to the prose ------------

    SPEC_TAGS_LINE = '    "[exit unestimated]",\n'

    def test_51_the_spec_block_is_the_one_the_scripts_read(self):
        sys.path.insert(0, SCRIPTS)
        try:
            import check_review
        finally:
            sys.path.remove(SCRIPTS)
        failures = []
        data = check_review.spec(os.path.join(ROOT, 'PROMPT.md'), failures)
        self.assertEqual(failures, [])
        self.assertEqual(sorted(data), sorted(check_review.SPEC_SHAPE))
        vocab = self.vocabulary()
        self.assertEqual(vocab['traces_mandated'][0][0], 'Cold-Start Calibration')
        self.assertEqual(vocab['traces_conditional'],
                         [('Competing Hypotheses',
                           'the rival explanations weighed for a Low finding', 'Low')])
        self.assertEqual(vocab['lenses_run_form'], '{run} of 10')
        # The trace table and the phrase-search gate it needed are gone.
        source = read(os.path.join(SCRIPTS, 'check_review.py'))
        self.assertNotIn('MANDATED_TRACES', source)
        self.assertNotIn('CONDITIONAL_TRACES', source)

    def test_51_a_trace_added_to_the_block_is_required_of_a_review(self):
        prompt = read(os.path.join(ROOT, 'PROMPT.md'))
        last = '{"name": "Defect Prevention", "purpose": "the upstream cause of each Major"}'
        self.assertIn(last, prompt)
        added = self.write('PROMPT.md', prompt.replace(
            last, last + ',\n      {"name": "Root Cause Ledger", "purpose": "a test trace"}', 1))
        code, out = run('check_review.py', SEEDED, '--artifact', SEEDED_ARTIFACT,
                        '--prompt', added)
        self.assertEqual(code, 1, out)
        self.assertIn("no 'Root Cause Ledger' section — a test trace", out)

    def test_51_a_conditional_trace_follows_its_confidence(self):
        # Moving the conditional trace to Medium makes it due on reviews with
        # Medium findings; the seeded review has some and no block for them.
        prompt = read(os.path.join(ROOT, 'PROMPT.md'))
        moved = self.write('PROMPT.md', prompt.replace(
            '"when_confidence": "Low"', '"when_confidence": "Medium"', 1))
        text = read(SEEDED)
        self.assertRegex(text, r'\| Medium \|\n')
        code, out = run('check_review.py', SEEDED, '--artifact', SEEDED_ARTIFACT,
                        '--prompt', moved)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r'Medium Confidence, named in no competing hypotheses block'
                              r'|Medium-Confidence finding\(s\) but no "Competing Hypotheses"')

    def test_51_a_missing_or_broken_block_fails_cleanly(self):
        prompt = read(os.path.join(ROOT, 'PROMPT.md'))
        for name, text, want in (
                ('none.md', prompt.replace('```json diffract-spec', '```json', 1),
                 'expected one ```json diffract-spec block, found 0'),
                ('broken.md', prompt.replace(self.SPEC_TAGS_LINE, '    "[exit unestimated]"\n', 1),
                 'the diffract-spec block is not valid JSON'),
                ('shape.md', prompt.replace('"lenses_run_form"', '"lenses_run_shape"', 1),
                 "'lenses_run_form' is missing or not a str")):
            changed = self.write(name, text)
            code, out = run('check_review.py', SEEDED, '--artifact', SEEDED_ARTIFACT,
                            '--prompt', changed)
            self.assertEqual(code, 1, out)
            self.assertIn(want, out)
            self.assertNotIn('Traceback', out)
            code, out = run('render_scorecard.py', SEEDED, '--prompt', changed)
            self.assertEqual(code, 2, out)
            self.assertNotIn('Traceback', out)

    def test_51_prose_and_block_that_disagree_fail_the_release(self):
        # One edit at one end for each list the block carries; each must fail
        # check.py by name. Every edit is made in a fresh copy.
        cases = (
            ('"Skip:Cobra", "Discard:Integrity"]', '"Skip:Cobra", "Discard:Integrity", "Skip:Budget"]',
             'the Verdict table'),
            ('"severities": ["Major", "Minor"]', '"severities": ["Major", "Minor", "Nit"]',
             'the Severity paragraph'),
            ('"confidences": ["High", "Medium", "Low"]', '"confidences": ["High", "Low"]',
             'the Confidence paragraph'),
            (self.SPEC_TAGS_LINE, self.SPEC_TAGS_LINE + '    "[exit guessed]",\n',
             'the inline tag strings'),
            ('"question": "Can I remove this entirely?"', '"question": "Can I delete it?"',
             'the 10 Lenses list'),
            ('"prefix": "SUB"', '"prefix": "SUBT"', 'the finding ID abbreviations'),
            ('"prefix": "W5H"', '"prefix": "WH"', 'the finding ID abbreviations'),
            ('"cobra": ["prototype", "production", "library-framework"]',
             '"cobra": ["prototype", "production"]', 'the diffract.yaml permitted values'),
            ('"ranges": {"max_cycles": [1, 3]}', '"ranges": {"max_cycles": [1, 5]}',
             'the diffract.yaml ranges'),
            ('"always": ["Checked:"]', '"always": ["Checked:", "Read:"]',
             'the Output A and B templates'),
            ('    "W5H1 run",\n', '', 'the Scorecard template'),
            ('"lenses_run_form": "{run} of {total}"', '"lenses_run_form": "{run}/{total}"',
             "the Scorecard template's Lenses run value"),
            ('{"name": "Gap Analysis", "purpose": "what the review could not reach"},\n', '',
             'the CHECK trace list'),
            ('step\'s name: Cold-Start Calibration, ', 'step\'s name: ',
             'the CHECK trace list'),
            ('| Lenses run | X of 10 —', '| Lenses run | X/10 —',
             "the Scorecard template's Lenses run value"),
        )
        for old, new, site in cases:
            with self.subTest(site=site, old=old[:40]):
                shutil.rmtree(os.path.join(self.tmp.name, 'repo'), ignore_errors=True)
                root = self.copy_of_repo()
                self.edit(root, 'PROMPT.md', old, new)
                code, lines = self.drift_failures(root)
                self.assertEqual(code, 1, lines)
                self.assertIn(f'the spec block disagrees with {site}', ' '.join(lines))

    def test_51_a_prose_only_template_change_fails_the_release(self):
        # test_41's literal change edits both ends; one end alone is caught.
        root = self.copy_of_repo()
        self.edit(root, 'PROMPT.md', 'No findings matching this pattern.\n```',
                  'Nothing matched this pattern.\n```')
        code, lines = self.drift_failures(root)
        self.assertEqual(code, 1)
        self.assertIn('the spec block disagrees with the Output B template', ' '.join(lines))

    def test_51_the_block_lists_every_row_the_scripts_derive(self):
        root = self.copy_of_repo()
        self.edit(root, 'PROMPT.md', '    "Cobra-skipped",\n', '')
        self.edit(root, 'PROMPT.md', '| Cobra-skipped |', '| Cobra-skips |')
        code, lines = self.drift_failures(root)
        self.assertEqual(code, 1)
        self.assertIn("check_review.py derives a 'Cobra-skipped' Scorecard row", ' '.join(lines))

    def test_51_render_refuses_an_unreadable_lenses_run(self):
        text = read(SEEDED).replace('| Lenses run | 10 of 10', '| Lenses run | 10/10', 1)
        review = self.write('slash-full.md', text)
        code, out = run('render_scorecard.py', review)
        self.assertEqual(code, 2, out)
        self.assertIn("REFUSED: Lenses run value '10/10", out)
        code, out = self.check(review, SEEDED_ARTIFACT)
        self.assertEqual(code, 1, out)
        self.assertIn("'Lenses run' value '10/10", out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
