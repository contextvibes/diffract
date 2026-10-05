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


if __name__ == '__main__':
    unittest.main(verbosity=2)
