#!/usr/bin/env python3
"""Print the GitHub Release notes for a version tag, from CHANGELOG.md.

The release workflow (.github/workflows/release.yml) runs this on every
pushed `vX.Y.Z` tag and publishes what it prints. CHANGELOG.md is narrative
and written by hand, so the notes are taken from it, not generated from
commits: the body of the tag's `## [X.Y.Z] — YYYY-MM-DD` entry, without its
heading, as the backfilled Releases carry it.

It refuses, with exit code 1 and one `FAIL:` line each, a tag that:
- is not `vX.Y.Z`;
- has no CHANGELOG entry, or one that is empty;
- is not the newest entry (a tag on an old version would publish stale
  notes as Latest);
- disagrees with the README badge or the PROMPT.md header.

Run from the repository root: python3 scripts/release_notes.py v0.5.0
Standard library only.
"""

import re
import sys

ENTRY = re.compile(r'^## \[(\d+\.\d+\.\d+)\] — (\d{4}-\d{2}-\d{2})[^\n]*$', re.M)
SOURCES = {
    'README badge': ('README.md', r'version-([\d.]+)-green'),
    'PROMPT.md header': ('PROMPT.md', r'\*\*Version: ([\d.]+)\*\*'),
}


def entries(text):
    """[(version, date, body)] for each entry, newest first."""
    found = list(ENTRY.finditer(text))
    out = []
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        # A `## ` heading that is not an entry also ends one; check.py
        # fails the repository if one appears below the first entry.
        rest = text[m.end():end]
        stop = re.search(r'^## (?!\[)', rest, re.M)
        body = rest[:stop.start()] if stop else rest
        out.append((m.group(1), m.group(2), body.strip('\n')))
    return out


def notes(tag, changelog, files):
    """(notes, failures) for `tag`; `files` maps a path to its text or None."""
    failures = []
    m = re.fullmatch(r'v(\d+\.\d+\.\d+)', tag)
    if not m:
        return None, [f'tag {tag!r} is not vX.Y.Z']
    version = m.group(1)
    for label, (path, pattern) in SOURCES.items():
        text = files.get(path)
        found = re.search(pattern, text) if text is not None else None
        if found is None:
            failures.append(f'version string not found in: {label}')
        elif found.group(1) != version:
            failures.append(f'{label} reads {found.group(1)}, tag is {tag}')
    all_entries = entries(changelog)
    versions = [v for v, _, _ in all_entries]
    if version not in versions:
        failures.append(f'CHANGELOG.md has no "## [{version}] — <date>" entry')
        return None, failures
    if versions[0] != version:
        failures.append(f'{tag} is not the newest CHANGELOG entry ({versions[0]} is)')
    _, _, body = all_entries[versions.index(version)]
    if not body.strip():
        failures.append(f'CHANGELOG.md entry {version} is empty')
    if failures:
        return None, failures
    return body.strip('\n') + '\n', []


def read(path):
    try:
        with open(path) as handle:
            return handle.read()
    except OSError:
        return None


def main():
    if len(sys.argv) != 2:
        print('usage: release_notes.py vX.Y.Z')
        return 2
    changelog = read('CHANGELOG.md')
    if changelog is None:
        print('FAIL: cannot read CHANGELOG.md; run from the repository root')
        return 1
    files = {path: read(path) for path, _ in SOURCES.values()}
    text, failures = notes(sys.argv[1], changelog, files)
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}', file=sys.stderr)
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
