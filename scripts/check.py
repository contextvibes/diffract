#!/usr/bin/env python3
"""The entry-criteria gate for this repository, and its release checks.

This is the reference implementation of the deterministic entry checks
PROMPT.md mandates for non-code artifacts — a reviewer running Diffract
against this repo runs it at PLAN — plus the repo's own release gates that
can be checked without judgment: link and anchor resolution, code-fence
balance, version-string agreement, and a README-vs-PROMPT lens-table diff.
Standard library only.

Every check is independent: a file this repository does not have is one
`FAIL:` line, never an exception that cancels the checks after it. Diffract
reviews itself from partial checkouts — a blind reviewer is given the
artifact and nothing else — and a gate that aborts there reports nothing
while looking like it ran.

Run from the repository root: python3 scripts/check.py
Exit code 0 = all checks pass; 1 = at least one failure (each is printed).
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_review

SKIP_DIRS = ('.claude', 'node_modules', '.git')

failures = []


def md_files():
    for path in sorted(glob.glob('**/*.md', recursive=True)):
        if any(part in path.split(os.sep) for part in SKIP_DIRS):
            continue
        yield path


def strip_fenced(text):
    return re.sub(r'```.*?```', '', text, flags=re.S)


def strip_code(text):
    """Fenced blocks and inline code spans.

    Link checking must ignore both: a document that writes a link pattern
    inside backticks to explain it is not carrying that link. Heading slugs
    keep their inline code, so anchors_of() deliberately uses strip_fenced().
    """
    return re.sub(r'`+[^`\n]*`+', '', strip_fenced(text))


def anchors_of(path):
    """GitHub-style slugs for every heading outside fenced code blocks."""
    slugs = set()
    text = read(path)
    if text is None:
        return slugs
    for heading in re.findall(r'^#+\s+(.*)$', strip_fenced(text), re.M):
        slug = heading.strip().lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slugs.add(re.sub(r'\s', '-', slug.strip()))
    return slugs


def read(path):
    """File contents, or None with a recorded failure."""
    try:
        with open(path) as handle:
            return handle.read()
    except OSError as e:
        failures.append(f'cannot read {path}: {e.strerror}')
        return None


def check_versions():
    readme, prompt, changelog = read('README.md'), read('PROMPT.md'), read('CHANGELOG.md')
    if readme is None or prompt is None or changelog is None:
        return
    badge = re.search(r'version-([\d.]+)-green', readme)
    header = re.search(r'\*\*Version: ([\d.]+)\*\*', prompt)
    latest = re.search(r'^## \[([\d.]+)\] — ', changelog, re.M)
    values = {
        'README badge': badge and badge.group(1),
        'PROMPT.md header': header and header.group(1),
        'CHANGELOG latest entry': latest and latest.group(1),
    }
    missing = [k for k, v in values.items() if v is None]
    if missing:
        failures.append(f"version string not found in: {', '.join(missing)}")
        return
    if len(set(values.values())) != 1:
        failures.append(f"version strings disagree: {values}")


def check_fences():
    for path in md_files():
        text = read(path)
        if text is None:
            continue
        markers = len(re.findall(r'^```', text, re.M))
        if markers % 2:
            failures.append(f"{path}: unbalanced code fences ({markers} markers)")


def check_links():
    for path in md_files():
        raw = read(path)
        if raw is None:
            continue
        text = strip_code(raw)
        for match in re.finditer(r'\]\(([^)\s]+)\)', text):
            link = match.group(1)
            if link.startswith(('http://', 'https://', 'mailto:')):
                continue
            target_path, _, anchor = link.partition('#')
            base = os.path.dirname(path)
            target = os.path.normpath(os.path.join(base, target_path)) if target_path else path
            if target_path and not os.path.exists(target):
                failures.append(f"{path}: broken link {link}")
            elif anchor and target.endswith('.md') and anchor not in anchors_of(target):
                failures.append(f"{path}: broken anchor {link}")


def check_lens_table():
    readme = read('README.md')
    if readme is None or read('PROMPT.md') is None:
        return
    normative = check_review.normative_lens_rows('PROMPT.md')
    failures.extend(check_review.failures)
    check_review.failures.clear()
    if not normative:
        return
    reproduced = [(check_review.plain(name), q.strip())
                  for name, q in re.findall(r'^\| \d+ \| (.+?) \| (.+?) \|$', readme, re.M)]
    if normative != reproduced:
        failures.append(f'README lens table drifted from PROMPT.md: {set(normative) ^ set(reproduced)}')


def main():
    check_versions()
    check_fences()
    check_links()
    check_lens_table()
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print('all checks pass')
    return 0


if __name__ == '__main__':
    sys.exit(main())
