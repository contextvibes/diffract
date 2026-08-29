#!/usr/bin/env python3
"""Mechanical release checks for the Diffract repository.

Implements the deterministic entry checks PROMPT.md mandates for non-code
artifacts, plus the repo's own release gates that can be checked without
judgment: link and anchor resolution, code-fence balance, version-string
agreement, and a README-vs-PROMPT lens-table diff. Standard library only.

Run from the repository root: python3 scripts/check.py
Exit code 0 = all checks pass; 1 = at least one failure (each is printed).
"""

import glob
import os
import re
import sys

SKIP_DIRS = ('.claude', 'node_modules', '.git')

failures = []


def md_files():
    for path in sorted(glob.glob('**/*.md', recursive=True)):
        if any(part in path.split(os.sep) for part in SKIP_DIRS):
            continue
        yield path


def strip_fenced(text):
    return re.sub(r'```.*?```', '', text, flags=re.S)


def anchors_of(path):
    """GitHub-style slugs for every heading outside fenced code blocks."""
    slugs = set()
    for heading in re.findall(r'^#+\s+(.*)$', strip_fenced(open(path).read()), re.M):
        slug = heading.strip().lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slugs.add(re.sub(r'\s', '-', slug.strip()))
    return slugs


def check_versions():
    readme = open('README.md').read()
    prompt = open('PROMPT.md').read()
    changelog = open('CHANGELOG.md').read()
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
        markers = len(re.findall(r'^```', open(path).read(), re.M))
        if markers % 2:
            failures.append(f"{path}: unbalanced code fences ({markers} markers)")


def check_links():
    for path in md_files():
        text = strip_fenced(open(path).read())
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
    prompt = open('PROMPT.md').read()
    readme = open('README.md').read()
    section = re.search(r'#### The 10 Lenses.*?#### W5H1', prompt, re.S)
    if not section:
        failures.append('PROMPT.md: lens list section not found')
        return
    normative = [(re.sub(r'\*', '', name).strip(), q.strip())
                 for name, q in re.findall(r'^\d+\. (.+?) — (.+)$', section.group(0), re.M)]
    reproduced = [(re.sub(r'\*', '', name).strip(), q.strip())
                  for name, q in re.findall(r'^\| \d+ \| (.+?) \| (.+?) \|$', readme, re.M)]
    if len(normative) != 10:
        failures.append(f'PROMPT.md: expected 10 lenses, parsed {len(normative)}')
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
