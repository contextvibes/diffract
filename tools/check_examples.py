#!/usr/bin/env python3
"""Run every review this repository publishes through the scripts it ships.

Repository tooling, not instrument: this file is outside `scripts/` and
`scripts/MANIFEST`, and enforces nothing on a review that PROMPT.md asks of
it. It only decides which published reviews CI checks, and with what.

A review is any Markdown file directly under `examples/` or `calibration/`
with a level-2 `FINDINGS INDEX` heading, located outside fences by
check_review.py's own section locator, so a review that quotes the heading
in a fence is not one for that alone. Adding a review there is enough to
have it checked; no list names them (issue #58).

Each review names its own artifacts, in the `Artifact` row of its
`### Scorecard` table (outside fences), so the mapping from review to
artifact lives in the review and nowhere else:

- every backticked span on that row that is a file under the repository root
  is passed to check_review.py as its own `--artifact`;
- a span that is absolute or climbs out with `..` fails;
- a span that contains a `/` and names no file fails, so a moved artifact is
  not mistaken for an anonymized review. A commit or ref written with a `/`
  must therefore be left out of backticks on that row; this is a convention
  of this repository's published reviews, not a rule of the instrument;
- a row with no file span means the artifact is not in the repository, and
  the review runs with `--no-artifact`, which check_review.py refuses for a
  review whose Integrity governor requires quotes;
- a review with no `Artifact` row in its Scorecard fails.

Each review then runs through check_review.py and render_scorecard.py; the
second exits non-zero if it had to correct a count.

Run from anywhere:  python3 tools/check_examples.py
Exit code 0 = every review passes both scripts. Standard library only.
"""

import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'scripts')
sys.path.insert(0, SCRIPTS)
from check_review import heading_span, outside_fences, section  # noqa: E402

DIRS = ('examples', 'calibration')
CHECKS = ('check_review.py', 'render_scorecard.py')
ARTIFACT_ROW = re.compile(r'^\| *Artifact *\|(.*)\|\s*$')


def reviews(root):
    """Repository-relative paths of the published reviews, sorted."""
    found = []
    for folder in DIRS:
        for path in sorted(glob.glob(os.path.join(root, folder, '*.md'))):
            with open(path) as handle:
                lines = handle.read().split('\n')
            if heading_span(lines, 'FINDINGS INDEX', level=2) is not None:
                found.append(os.path.relpath(path, root))
    return found


def artifacts_of(text, root):
    """([artifact paths], failure or None) from the Scorecard's Artifact row."""
    table = section(text, 'Scorecard', level=3)
    lines = (table or '').split('\n')
    row = next((ARTIFACT_ROW.match(line) for line, live
                in zip(lines, outside_fences(lines))
                if live and ARTIFACT_ROW.match(line)), None)
    if row is None:
        return [], 'no "| Artifact |" row in its ### Scorecard names the artifact'
    found = []
    for span in re.findall(r'`([^`]+)`', row.group(1)):
        if os.path.isabs(span) or '..' in span.split('/'):
            return [], f'the Artifact row names {span}, which is outside the repository'
        if os.path.isfile(os.path.join(root, span)):
            found.append(span)
        elif '/' in span:
            return [], f'the Artifact row names {span}, which is not a file'
    return found, None


def run(root, script, *args):
    done = subprocess.run([sys.executable, os.path.join(root, 'scripts', script), *args],
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
            artifacts, failure = artifacts_of(handle.read(), root)
        if failure:
            failures.append(f'{review}: {failure}')
            continue
        given = ([a for path in artifacts for a in ('--artifact', path)]
                 or ['--no-artifact'])
        print(f'{review}: {" ".join(given)}')
        for script in CHECKS:
            args = [review, *given] if script == 'check_review.py' else [review]
            code, out = run(root, script, *args)
            print(f'  {script} exit {code}')
            if code != 0:
                print(out)
                failures.append(f'{review}: {script} exited {code}')
    print()
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print(f'{len(found)} reviews pass {" and ".join(CHECKS)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
