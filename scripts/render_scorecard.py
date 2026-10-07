#!/usr/bin/env python3
"""Derive a review's Scorecard counts from its own Findings Index.

The Scorecard restates the index. Nothing in its count rows is new
information, and two releases were spent instructing reviewers to do the
arithmetic carefully while runs kept stating counts that contradicted their
own index. This does the arithmetic instead. See issue #32.

The governing constraint is that output must be **identical, not different**:
this produces the document the reviewer would have produced with the counts
done correctly, so a run that uses it stays comparable with one that does not.
Two consequences, both deliberate:

- Only counts are derived. Severity, verdict, confidence, and every prose row
  are the reviewer's and are never touched. The mechanical layer computes
  facts about text; it does not decide what a defect is.
- Rows carrying reviewer reasoning are corrected, not overwritten. A
  `Most productive lens` row that explains how a tie was broken is left alone
  when it agrees with the index, because rewriting it to a bare count would
  delete information the index cannot reproduce.

Two rows are never derived, because the index does not record what they
measure. `Fixes applied` depends on what happened to the artifact. `PDCA cycles
run` cannot be read from the highest `Cycle` value: a final cycle that raises
nothing is what convergence *is*, so it leaves no row behind —
`examples/web-service.md` correctly reports 2 cycles with every finding in
cycle 1. Deriving either would corrupt a correct review.

A pre-0.4.0 `Fixed` row is reported and left in place; migrating it is a format
change, not arithmetic.

Run from the repository root:
    python3 scripts/render_scorecard.py REVIEW.md           # print to stdout
    python3 scripts/render_scorecard.py REVIEW.md --write   # rewrite in place
Exit 0 if the review's counts already agreed, 1 if any were corrected, 2 if
something was refused rather than corrected — an index the checker rejects, no
Scorecard, or a `Lenses run` claim higher than the lens sections present.

`Lenses run` is corrected in one direction only. A number lower than the
sections present is a counting slip and is corrected like any count. A number
higher is a coverage claim the review body contradicts: a skipped lens fails,
and is never corrected away (issue #50).
"""

import argparse
import re
import sys

import check_review


# The count arithmetic lives in check_review.derived_counts: this module and
# the checker must agree about what a Scorecard row means, and when each kept
# its own copy they had already drifted apart by the time cycle 6 found them.
derived_counts = check_review.derived_counts


def lens_totals(rows):
    """Per-lens row counts. W5H1 is excluded: it is a question set, not a lens.

    This is PROMPT.md's rule for the `Most productive lens` row, not a policy
    of this script. It was the script's alone until cycle 6, which is a defect
    of the kind this module exists to prevent: a hand count and a scripted
    count could disagree while PROMPT.md claimed they never would.

    The reason for the rule: W5H1 routinely out-raises every lens — 4 findings
    against a leader of 2 in examples/semver-2.0.0-review.md — so counting it
    would make it the answer on almost any review.
    """
    totals = {}
    for row in rows:
        if row[1] == 'W5H1':
            continue
        totals[row[1]] = totals.get(row[1], 0) + 1
    return totals


def leading_lens(rows):
    """(first tied lens by name, its count, every tied lens).

    A tie is exactly where the reviewer's own reasoning belongs, so the row
    is accepted when it names any tied lens, and only a row naming none is
    rewritten — to the first by name, the others listed as tied. PROMPT.md
    states this rule under Scorecard. (This docstring used to say ties were
    broken by Majors; the code never did that.)
    """
    totals = lens_totals(rows)
    if not totals:
        return None, 0, []
    top = max(totals.values())
    tied = sorted(k for k, v in totals.items() if v == top)
    return tied[0], top, tied


def substitute_leading_number(value, want):
    """Replace the first integer in a Scorecard value, keeping its suffix."""
    return re.sub(r'\d+', str(want), value, count=1)


def render(review, prompt_path=None):
    # A fresh list per call. It used to be a module global in check_review,
    # cleared here by hand; a second call that forgot inherited the first
    # call's failures and rejected a sound index (cycle-7 BOU-1, issue #47).
    failures = []
    vocab = check_review.normative_vocabulary(
        prompt_path or check_review.default_prompt(), failures)
    rows = check_review.index_rows(review, vocab, failures)
    if failures:
        return review, [], [], [f'index rejected: {f}' for f in failures]

    # Located by heading level and line start, not by splitting on the literal
    # text: a review that quotes '### Scorecard' inside an Evidence block —
    # which a review of Diffract must — was rewritten at the quote (SHI-1).
    lines = review.split('\n')
    span = check_review.heading_span(lines, 'Scorecard', level=3, prefix=True)
    if span is None:
        return review, [], [], ['no "### Scorecard" section']
    prefix, suffix = lines[:span[0] + 1], lines[span[1]:]
    table = '\n'.join(lines[span[0] + 1:span[1]])

    counts = derived_counts(rows)
    lead, lead_n, tied = leading_lens(rows)
    changes, notes, refused = [], [], []

    def fix_row(line):
        # Escape-aware, as check_review.py parses it: a value carrying a
        # literal `\|` is one cell, not two (cycle-6 VAR-3, issue #43).
        cells = check_review.split_row(line)
        if cells is None or len(cells) != 2:
            return line
        raw_key, value = cells
        key = check_review.unescape(raw_key)
        stated = re.match(r'\s*(\d+)', value)

        if key in counts:
            want = counts[key]
            if not stated:
                changes.append(f'{key}: no number stated, set to {want}')
                return f'| {raw_key} | {want} |'
            if int(stated.group(1)) != want:
                changes.append(f'{key}: {stated.group(1)} -> {want}')
                return f'| {raw_key} | {substitute_leading_number(value, want)} |'

        elif key == 'Lenses run':
            lenses = check_review.normative_lenses(
                prompt_path or check_review.default_prompt(), failures)
            found, _ = check_review.lens_sections(review, lenses)
            present = sum(1 for name in lenses if name in found)
            if stated and int(stated.group(1)) < present:
                # A low claim is a counting slip: the sections are there.
                changes.append(f'Lenses run: {stated.group(1)} -> {present}')
                return f'| {raw_key} | {substitute_leading_number(value, present)} |'
            if stated and int(stated.group(1)) > present:
                # A high claim is a coverage claim, and the missing sections
                # are the evidence against it. Correcting it down rewrote a
                # review that skipped a lens into one that declared skipping
                # it, and check_review.py then passed it (issue #50).
                missing = [n for n in lenses if n not in found]
                refused.append(
                    f'Lenses run states {stated.group(1)}, but only {present} '
                    f'lens sections are present (missing: {", ".join(missing)}); '
                    f'a skipped lens is never corrected away — run it, or narrow '
                    f'the scope and name it')

        elif key == 'Most productive lens' and lead:
            # Corrected only on contradiction: this row often carries the
            # reviewer's tie-breaking reasoning, which the index cannot restate.
            named = [t for t in tied if t.lower() in value.lower()]
            if not named:
                changes.append(
                    f'Most productive lens: names none of {tied} '
                    f'({lead_n} findings) -> rewritten')
                plural = 's' if lead_n != 1 else ''
                tie = f' — tied with {", ".join(t for t in tied if t != lead)}' if len(tied) > 1 else ''
                return f'| {raw_key} | {lead} ({lead_n} finding{plural}){tie} |'

        elif key == 'Fixed':
            notes.append(
                "Fixed: pre-0.4.0 row, left in place — split it into "
                "'Fix verdicts' and 'Fixes applied' (issue #33)")

        return line

    table = '\n'.join(fix_row(line) for line in table.split('\n'))
    refused.extend(f'instrument rejected: {f}' for f in failures)
    return '\n'.join(prefix + table.split('\n') + suffix), changes, notes, refused


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('review')
    ap.add_argument('--prompt', default=check_review.default_prompt())
    ap.add_argument('--write', action='store_true',
                    help='rewrite the review in place instead of printing it')
    args = ap.parse_args()

    review = open(args.review).read()
    rendered, changes, notes, refused = render(review, args.prompt)

    if args.write:
        open(args.review, 'w').write(rendered)
    else:
        sys.stdout.write(rendered)

    for note in notes:
        print(f'NOTE: {note}', file=sys.stderr)
    for change in changes:
        print(f'CORRECTED: {change}', file=sys.stderr)
    for refusal in refused:
        print(f'REFUSED: {refusal}', file=sys.stderr)
    if refused:
        return 2
    if not changes:
        print('scorecard already agrees with the index', file=sys.stderr)
    return 1 if changes else 0


if __name__ == '__main__':
    sys.exit(main())
