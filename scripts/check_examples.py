#!/usr/bin/env python3
"""Run every review this repository publishes through the scripts it ships.

A review is any Markdown file directly under `examples/` or `calibration/`
with a `## FINDINGS INDEX` heading at line start, the heading PROMPT.md
mandates as a review's last section. Adding a review there is enough to have
it checked; no list names them (issue #58).

Each review names its own artifact, in the `Artifact` row of its Scorecard,
so the mapping from review to artifact lives in the review and nowhere else:

- the first backticked span in that row that is a path under the repository
  root is the artifact, passed to check_review.py as `--artifact`;
- a backticked span that contains a `/` and names no file is a failure, so a
  moved or renamed artifact is not mistaken for an anonymized one;
- a row with no backticked path means the artifact is not in the repository,
  and the review runs with `--no-artifact`, which check_review.py refuses for
  a review whose Integrity governor requires quotes;
- a review with no `Artifact` row fails.

Each review is then run through render_scorecard.py, which exits non-zero if
it had to correct a count.

Run from anywhere:  python3 scripts/check_examples.py
Exit code 0 = every review passes both scripts. Standard library only.
"""

import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'scripts')
DIRS = ('examples', 'calibration')
INDEX = re.compile(r'^## FINDINGS INDEX\s*$', re.M)
ARTIFACT_ROW = re.compile(r'^\| *Artifact *\|(.*)\|\s*$', re.M)


def reviews(root):
    """Repository-relative paths of the published reviews, sorted."""
    found = []
    for folder in DIRS:
        for path in sorted(glob.glob(os.path.join(root, folder, '*.md'))):
            with open(path) as handle:
                if INDEX.search(handle.read()):
                    found.append(os.path.relpath(path, root))
    return found


def artifact_of(text, root):
    """(artifact path or None, failure or None) from the Scorecard row."""
    row = ARTIFACT_ROW.search(text)
    if row is None:
        return None, 'no "| Artifact |" Scorecard row names the artifact'
    for span in re.findall(r'`([^`]+)`', row.group(1)):
        if os.path.isfile(os.path.join(root, span)):
            return span, None
        if '/' in span:
            return None, f'the Artifact row names {span}, which is not a file'
    return None, None


def run(root, script, *args):
    done = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args],
                          cwd=root, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def main():
    root = ROOT
    failures = []
    found = reviews(root)
    if not found:
        failures.append(f'no review found under {" or ".join(DIRS)}/')
    for review in found:
        with open(os.path.join(root, review)) as handle:
            artifact, failure = artifact_of(handle.read(), root)
        if failure:
            failures.append(f'{review}: {failure}')
            continue
        given = ['--artifact', artifact] if artifact else ['--no-artifact']
        print(f'{review}: {" ".join(given)}')
        for script, args in (('check_review.py', [review, *given]),
                             ('render_scorecard.py', [review])):
            code, out = run(root, script, *args)
            if code != 0:
                print(out)
                failures.append(f'{review}: {script} exited {code}')
    print()
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print(f'{len(found)} reviews pass check_review.py and render_scorecard.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
