#!/usr/bin/env python3
"""Match a review's findings against a calibration fixture's seeds.

Reports, for each seed, every finding whose cited line range covers the seeded
line. That is the whole of what can be decided mechanically.

Whether a candidate is a HIT is a judgment call and is left to a person: a
finding that lands on a seeded line for an unrelated reason is not a hit, and
a finding that names the seeded defect while citing a neighbouring line is.
This script narrows the reading; it does not do it.

  python3 scripts/score_seeds.py REVIEW.md --seeds calibration/seeds.md
"""

import argparse
import re
import sys


def seeds(path):
    out = []
    for sid, line, lens in re.findall(r'^## (S\d+) — line (\d+) · predicted lens (.+)$',
                                      open(path).read(), re.M):
        out.append((sid, int(line), lens.strip()))
    return out


def findings(path):
    text = open(path).read()
    if '## FINDINGS INDEX' not in text:
        sys.exit('no FINDINGS INDEX in review')
    out = []
    for row in re.findall(r'^\|(.+)\|\s*$', text.split('## FINDINGS INDEX')[1], re.M):
        c = [re.sub(r'[*`]', '', x).strip() for x in row.split('|')]
        if len(c) != 8 or c[0] == 'ID' or set(c[0]) <= set('-: '):
            continue
        m = re.search(r':(\d+)(?:[-–](\d+))?', c[3])
        if m:
            out.append((c[0], c[1], int(m.group(1)), int(m.group(2) or m.group(1)),
                        c[4], c[5], c[6]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('review')
    ap.add_argument('--seeds', required=True)
    a = ap.parse_args()

    ss, ff = seeds(a.seeds), findings(a.review)
    print(f'{len(ss)} seeds | {len(ff)} findings in the review\n')
    covered = 0
    for sid, line, lens in ss:
        hits = [f for f in ff if f[2] <= line <= f[3]]
        covered += bool(hits)
        print(f'{sid}  line {line}  predicted {lens}')
        if not hits:
            print('    no finding cites this line')
        for fid, flens, s, e, sev, verdict, claim in hits:
            print(f'    CANDIDATE {fid} ({flens}, {sev}, {verdict}) cites {s}-{e}')
            print(f'      {claim[:110]}')
        print()
    print(f'seeds with at least one finding on the line: {covered}/{len(ss)}')
    print('Read each candidate before calling it a hit.')


if __name__ == '__main__':
    sys.exit(main())
