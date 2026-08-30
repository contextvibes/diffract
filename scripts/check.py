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


def at_root():
    """Whether the working directory looks like a Diffract checkout.

    md_files() globs Markdown recursively from here. Run from a parent
    directory it gates unrelated documents; run from `/` it walks the
    filesystem and does not return (cycle-7 EFF-1).
    """
    return os.path.exists('PROMPT.md') and os.path.exists('README.md')


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


_anchor_cache = {}


def anchors_of(path):
    """GitHub-style slugs for every heading outside fenced code blocks.

    Cached: without it the target is re-read and re-parsed once per anchored
    link, and one unreadable target appends one failure per link to it.
    """
    if path in _anchor_cache:
        return _anchor_cache[path]
    slugs = _anchor_cache.setdefault(path, set())
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
    """The version strings that are present must agree.

    An absent file used to cancel the comparison entirely, so on a partial
    checkout the two files that *were* present were never compared while a
    `FAIL:` line printed that read as though they had been — inside the file
    whose docstring promises that every check is independent (cycle-7 VAR-2).
    """
    sources = {
        'README badge': ('README.md', r'version-([\d.]+)-green'),
        'PROMPT.md header': ('PROMPT.md', r'\*\*Version: ([\d.]+)\*\*'),
        'CHANGELOG latest entry': ('CHANGELOG.md', r'^## \[([\d.]+)\] — '),
    }
    values = {}
    for label, (path, pattern) in sources.items():
        text = read(path)
        if text is None:
            continue
        found = re.search(pattern, text, re.M)
        if found is None:
            failures.append(f'version string not found in: {label}')
        else:
            values[label] = found.group(1)
    if len(set(values.values())) > 1:
        failures.append(f'version strings disagree: {values}')


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


def check_enforced_strings():
    """Every section check_review.py demands of a review is mandated in PROMPT.md.

    The general form of a defect this repository has now shipped four times: a
    rule enforced by a script and stated in no document, or stated in a
    document and enforced by nothing. The lens list and the Scorecard row set
    are already derived from PROMPT.md rather than hard-coded; the mandated
    sections cannot be derived the same way — they are prose, not a table — so
    this gate holds the two ends together instead. A trace added to the
    checker fails the release until PROMPT.md mandates it.
    """
    prompt = read('PROMPT.md')
    if prompt is None:
        return
    for phrase, purpose in (check_review.MANDATED_TRACES
                            + check_review.CONDITIONAL_TRACES):
        if phrase not in prompt:
            failures.append(
                f'check_review.py requires a {phrase!r} section of every review '
                f'({purpose}), but PROMPT.md never mandates it')


def main():
    if not at_root():
        print('FAIL: run from a Diffract checkout: no PROMPT.md and README.md here')
        return 1
    check_versions()
    check_fences()
    check_links()
    check_lens_table()
    check_enforced_strings()
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print('all checks pass')
    return 0


if __name__ == '__main__':
    sys.exit(main())
