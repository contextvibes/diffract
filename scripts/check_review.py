#!/usr/bin/env python3
"""Mechanical form checks for a Diffract review.

Takes a review and the artifact(s) it reviewed, and reports form violations:
missing or misordered lens sections, nothing-found lenses without cognitive
anchoring, illegal verdict or severity values, Scorecard counts that disagree
with the Findings Index, and Evidence quotes that do not appear verbatim at
their cited lines.

This checks form, never judgment. It cannot tell you whether a finding is
real, whether its severity is right, or whether a lens was applied well.

The normative lens list is read from PROMPT.md at runtime rather than
hard-coded, so this cannot drift from the instrument it enforces.

  python3 scripts/check_review.py REVIEW.md --artifact PATH [--artifact PATH]

Exit code 0 = all checks pass; 1 = at least one failure (each is printed).
"""

import argparse
import hashlib
import os
import re
import sys

VERDICTS = {'Fix', 'Skip:Compass', 'Skip:Cobra', 'Discard:Integrity'}
SEVERITIES = {'Major', 'Minor'}
ANCHOR = 'A finding would look like:'
CLOSER = 'No findings matching this pattern.'

failures = []


def plain(text):
    """Strip markdown emphasis so cell values compare as literal strings."""
    return re.sub(r'[*`]', '', text).strip()


def default_prompt():
    """PROMPT.md next to this script's repository root."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'PROMPT.md')


def normative_lenses(prompt_path):
    """The ten lens names, in order, as PROMPT.md defines them."""
    prompt = open(prompt_path).read()
    section = re.search(r'#### The 10 Lenses.*?#### W5H1', prompt, re.S)
    if not section:
        failures.append(f'{prompt_path}: lens list section not found')
        return []
    names = [plain(n) for n, _ in
             re.findall(r'^\d+\. (.+?) — (.+)$', section.group(0), re.M)]
    if len(names) != 10:
        failures.append(f'{prompt_path}: expected 10 lenses, parsed {len(names)}')
    return [n.split(None, 1)[-1] if ' ' in n else n for n in names]


def lens_sections(review, lenses):
    """Map lens name -> section body, for headings that name a lens."""
    found, order = {}, []
    for m in re.finditer(r'^### (.+?)$\n(.*?)(?=^### |^## |\Z)', review, re.M | re.S):
        head = plain(m.group(1))
        for name in lenses + ['W5H1']:
            if re.search(r'(?:^|\s)' + re.escape(name) + r'(?:\s|$|—)', head):
                found[name] = m.group(2)
                order.append(name)
                break
    return found, order


def check_lenses(review, lenses):
    found, order = lens_sections(review, lenses)
    expected = lenses + ['W5H1']
    missing = [n for n in expected if n not in found]
    if missing:
        failures.append(f"no section for: {', '.join(missing)}")
    if order != expected and not missing:
        failures.append(f'lens sections out of normative order: {order}')
    for name, body in found.items():
        if 'Checked:' not in body:
            failures.append(f"{name}: no 'Checked:' line")
        if re.search(r'^\|\s*[A-Z0-9]{3}-\d', body, re.M):
            continue
        if ANCHOR not in body:
            failures.append(f'{name}: nothing-found lens without "{ANCHOR}"')
        if CLOSER not in body:
            failures.append(f'{name}: nothing-found lens without "{CLOSER}"')


def index_rows(review):
    if '## FINDINGS INDEX' not in review:
        failures.append('no "## FINDINGS INDEX" section')
        return []
    body = review.split('## FINDINGS INDEX')[1]
    rows = []
    for line in re.findall(r'^\|(.+)\|\s*$', body, re.M):
        if re.match(r'^[\s|:-]+$', line) or line.strip().startswith('ID '):
            continue
        rows.append([plain(c) for c in line.split('|')])
    for row in rows:
        if len(row) != 8:
            failures.append(f'index row is {len(row)} columns, expected 8: {row[:1]}')
            continue
        if row[5] not in VERDICTS:
            failures.append(f'{row[0]}: illegal verdict {row[5]!r}')
        if row[4] not in SEVERITIES:
            failures.append(f'{row[0]}: illegal severity {row[4]!r}')
    return [r for r in rows if len(r) == 8]


def check_scorecard(review, rows):
    """Every derived Scorecard count must equal a count of index rows.

    Three rows are deliberately not reconciled. 'Fixes applied' and 'PDCA
    cycles run' are not derivable from the index at all — see the counting
    policy in PROMPT.md. Pre-0.4.0 'Fixed' conflated verdict Fix with fixes
    applied (issue #33), so it is accepted unchecked; a review that states the
    0.4.0 'Fix verdicts' row instead has it reconciled.
    """
    if '### Scorecard' not in review:
        failures.append('no "### Scorecard" section')
        return
    table = re.split(r'^### ', review.split('### Scorecard')[1], maxsplit=1, flags=re.M)[0]
    card = {plain(k): v.strip() for k, v in
            re.findall(r'^\| ([^|]+?) \| ([^|]*?) \|\s*$', table, re.M)}
    expected = {
        'Findings raised': len(rows),
        'Major findings raised': sum(1 for r in rows if r[4] == 'Major'),
        'Cobra-skipped': sum(1 for r in rows if r[5] == 'Skip:Cobra'),
        'Compass-skipped': sum(1 for r in rows if r[5] == 'Skip:Compass'),
        'Integrity-discarded': sum(1 for r in rows if r[5] == 'Discard:Integrity'),
    }
    if 'Fix verdicts' in card:
        expected['Fix verdicts'] = sum(1 for r in rows if r[5] == 'Fix')
    for key, want in expected.items():
        if key not in card:
            failures.append(f'Scorecard has no {key!r} row')
            continue
        m = re.match(r'\s*(\d+)', card[key])
        if not m:
            failures.append(f'Scorecard {key!r} states no number: {card[key][:40]!r}')
        elif int(m.group(1)) != want:
            failures.append(f'Scorecard {key} = {m.group(1)}, index says {want}')


def requires_quotes(review):
    """Whether this run's Integrity governor demands a quote block per finding.

    PROMPT.md:92 makes evidence rules a per-run parameter the requester sets,
    not a fixed rule of the instrument, so the requirement is read from the
    review's own declared governors rather than assumed. Quotes that are
    present are verified either way: an unrequested quote that misquotes the
    artifact is still a fabrication.
    """
    m = re.search(r'Integrity:(.*(?:\n[ \t]{2,}\S.*)*)', review)
    if not m:
        failures.append('no Integrity governor line found')
        return False
    return bool(re.search(r'verbatim|quote', m.group(1), re.I))


def check_evidence(review, rows, artifacts, require):
    ids = {r[0] for r in rows}
    seen = set()
    verified = 0
    blocks = re.findall(
        r'^- ([A-Z0-9]{2,4}-\d+) — (\S+?):(\d+)(?:[-–](\d+))?\s*$\n((?:^\s+> ?.*$\n?)+)',
        review, re.M)
    for fid, path, start, end, block in blocks:
        seen.add(fid)
        if fid not in ids:
            failures.append(f'{fid}: Evidence for a finding with no index row')
        name = os.path.basename(path)
        if name not in artifacts:
            failures.append(f'{fid}: cites {path}, not among the supplied artifacts')
            continue
        lines = artifacts[name]
        a, b = int(start), int(end or start)
        if not 1 <= a <= b <= len(lines):
            failures.append(f'{fid}: line range {a}-{b} outside {name} (1-{len(lines)})')
            continue
        quote = [re.sub(r'^\s+> ?', '', l) for l in block.rstrip('\n').split('\n')]
        window = lines[a - 1:b]
        squash = lambda ls: [re.sub(r'\s+', ' ', x).strip() for x in ls]
        if quote != window and squash(quote) != squash(window):
            failures.append(
                f'{fid}: quote does not appear at {name}:{a}-{b}\n'
                f'       quoted: {quote[0][:64]!r}\n'
                f'       actual: {(window[0][:64] if window else "")!r}')
            continue
        verified += 1
    if require:
        for fid in sorted(ids - seen):
            failures.append(f'{fid}: Integrity requires a quote block, none found')
    return verified, len(blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('review')
    ap.add_argument('--artifact', action='append', default=[], required=True)
    ap.add_argument('--prompt', default=default_prompt())
    args = ap.parse_args()

    review = open(args.review).read()
    artifacts = {}
    for path in args.artifact:
        data = open(path, 'rb').read()
        artifacts[os.path.basename(path)] = data.decode().split('\n')
        print(f'artifact {os.path.basename(path)} '
              f'sha256 {hashlib.sha256(data).hexdigest()}')

    lenses = normative_lenses(args.prompt)
    check_lenses(review, lenses)
    rows = index_rows(review)
    check_scorecard(review, rows)
    require = requires_quotes(review)
    verified, blocks = check_evidence(review, rows, artifacts, require)

    print(f'index rows {len(rows)} | quote blocks {blocks} '
          f'(required: {"yes" if require else "no"}) | verified verbatim {verified}')
    print()
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print('all checks pass')
    return 0


if __name__ == '__main__':
    sys.exit(main())
