#!/usr/bin/env python3
"""Mechanical form checks for a Diffract review.

Takes a review and the artifact(s) it reviewed, and reports form violations:
missing or misordered lens sections, nothing-found lenses without cognitive
anchoring, a missing CHECK table or competing-hypotheses block, missing
mandated sections, illegal verdict or severity values, Scorecard rows that
are absent or disagree with the Findings Index, and Evidence quotes that do
not appear verbatim at the place they cite.

This checks form, never judgment. It cannot tell you whether a finding is
real, whether its severity is right, or whether a lens was applied well.
What it does check, it names in its output: a pass states each check by
name, so a pass on a conforming review is distinguishable from a pass that
never looked (issue: cycle-6 OBS-1).

The normative lens list and the Scorecard row set are read from PROMPT.md at
runtime rather than hard-coded, so the enforced form follows the instrument.
`--prompt` overrides which PROMPT.md that is; the default is the one shipped
beside this script, and the run reports which file it used. Point it at a
PROMPT.md belonging to the artifact under review and the artifact defines the
norm it is judged by — the hazard PROMPT.md states for `render_scorecard.py`,
one step removed.

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

# Every mandated step whose only proof of having run is a trace in the output.
# Each phrase is required in the review and, by scripts/check.py's release
# gate, in PROMPT.md too — so a requirement can never live only in this file.
# Before cycle 7 three of these were mandated by PROMPT.md and checked by
# nothing, and a review with all three deleted printed `all checks pass`.
MANDATED_TRACES = [
    ('Cold-Start Calibration', 'the invariants written down before the lenses'),
    ('Scope and Nothing-Found Verification', 'the form and anchoring check'),
    ('Stockholm & Hammer', 'the audit of adopted explanations and reached-for tools'),
    ('Gap Analysis', 'what the review could not reach'),
    ('Defect Prevention', 'the upstream cause of each Major'),
]

# Required only when the review has a Low-Confidence finding to weigh.
CONDITIONAL_TRACES = [
    ('Competing Hypotheses', 'the rival explanations weighed for a Low finding'),
]

HYPOTHESES = re.compile(r'^(?:#+\s+|\*\*)[^\n]*Competing Hypotheses', re.I)



failures = []


def plain(text):
    """Strip markdown emphasis so cell values compare as literal strings."""
    return re.sub(r'[*`]', '', text).strip()


def outside_fences(lines):
    """Per line, whether it sits outside a ``` fenced block."""
    inside, live = False, []
    for line in lines:
        if re.match(r'^\s*```', line):
            live.append(False)
            inside = not inside
        else:
            live.append(not inside)
    return live


def heading_span(lines, name, level=None, prefix=False):
    """(start, end) line indices of the named heading's section, or None.

    The one section locator in this file. A heading matches only at the start
    of a line, only outside a fenced block, and — where a level is given —
    only at that level; the section runs to the next heading of the same or
    higher level.

    Every section lookup here used to be `str.split()` on the literal heading
    text. That reads a heading quoted inside an Evidence block as the section
    itself, and the Integrity rule requires a review of Diffract to quote
    Diffract's own headings verbatim, so a conforming self-review could not
    pass this checker (cycle-7 SHI-1). The same substring matching made a
    `§ Heading` citation resolve to a template copy inside a fence (VAR-6).
    """
    want = re.sub(r'\s+', ' ', plain(name)).strip().lower()
    live = outside_fences(lines)
    for i, line in enumerate(lines):
        m = re.match(r'^(#+)\s+(.*)$', line)
        if not (live[i] and m):
            continue
        if level is not None and len(m.group(1)) != level:
            continue
        head = re.sub(r'\s+', ' ', plain(m.group(2))).strip().lower()
        if head != want and not (prefix and head.startswith(want)):
            continue
        depth = len(m.group(1))
        for j in range(i + 1, len(lines)):
            n = re.match(r'^(#+)\s+', lines[j])
            if n and live[j] and len(n.group(1)) <= depth:
                return i, j
        return i, len(lines)
    return None


def section(review, name, level=None):
    """The named section's body text, or None. Heading line excluded."""
    lines = review.split('\n')
    span = heading_span(lines, name, level=level, prefix=True)
    return None if span is None else '\n'.join(lines[span[0] + 1:span[1]])


def stated_at_line_start(lines, phrase):
    """Whether a heading or bold label outside a fence carries this phrase.

    Presence, not parsing: a step's trace may be a heading at any level or a
    bold label, and reviews use both. Requiring line start and excluding
    fences keeps a review that merely *quotes* the phrase from satisfying it.
    """
    live = outside_fences(lines)
    pattern = re.compile(r'^(?:#+\s+|\*\*)[^\n]*' + re.escape(phrase), re.I)
    return any(live[i] and pattern.match(line) for i, line in enumerate(lines))



def default_prompt():
    """PROMPT.md next to this script's repository root."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'PROMPT.md')


def normative_lens_rows(prompt_path):
    """(name, question) per lens, in order, verbatim from PROMPT.md's list.

    The one parser for the normative lens list. `scripts/check.py` diffs
    README's reproduction against it rather than parsing PROMPT.md a second
    time: two copies of an anti-drift parser are themselves something to
    drift.
    """
    prompt = open(prompt_path).read()
    section = re.search(r'#### The 10 Lenses.*?#### W5H1', prompt, re.S)
    if not section:
        failures.append(f'{prompt_path}: lens list section not found')
        return []
    rows = [(plain(n), q.strip()) for n, q in
            re.findall(r'^\d+\. (.+?) — (.+)$', section.group(0), re.M)]
    if len(rows) != 10:
        failures.append(f'{prompt_path}: expected 10 lenses, parsed {len(rows)}')
    return rows


def normative_lenses(prompt_path):
    """The ten lens names, in order, without their icons."""
    names = [n for n, _ in normative_lens_rows(prompt_path)]
    return [n.split(None, 1)[-1] if ' ' in n else n for n in names]


# The Scorecard row set of the instrument that produced a review. 0.4.0 and
# later are read from PROMPT.md; earlier reviews are frozen evidence (see
# CONTRIBUTING.md, Release Gates) and are checked against the set that was
# normative when they were written.
PRE_040_ROWS = [
    'Reviewer', 'Artifact', 'Instrument', 'Governors', 'Entry checks',
    'Findings raised', 'Major findings raised', 'Fixed', 'Cobra-skipped',
    'Compass-skipped', 'Integrity-discarded', 'PDCA cycles run', 'Lenses run',
    'Most productive lens', 'Estimated remaining Majors', 'Calibration', 'Tags',
]


def normative_scorecard_rows(prompt_path):
    """The Scorecard rows, in order, as PROMPT.md's template defines them.

    Read rather than hard-coded for the same reason the lens list is: a row
    added to the template is a row the checker must require, and a checker
    that has to be edited in step with the document it enforces will
    eventually not be (issue #39).
    """
    prompt = open(prompt_path).read()
    template = re.search(r'### Scorecard\n\| Metric \| Value \|\n.*?```', prompt, re.S)
    if not template:
        failures.append(f'{prompt_path}: Scorecard template not found')
        return []
    rows = [plain(k) for k in
            re.findall(r'^\| ([^|]+?) \| [^|]*? \|$', template.group(0), re.M)]
    return [r for r in rows if r != 'Metric']


def instrument_version(review):
    """(major, minor) of the instrument the review declares, or None."""
    m = re.search(r'^\| Instrument \| Diffract v?(\d+)\.(\d+)', review, re.M)
    return (int(m.group(1)), int(m.group(2))) if m else None


def derived_counts(rows):
    """The Scorecard rows that are a count of index rows and nothing else.

    Defined once and used by both this checker and render_scorecard.py: two
    copies of this arithmetic had already drifted apart before cycle 6 found
    them.  'Fixes applied' and 'PDCA cycles run' are absent deliberately —
    neither is derivable from the index (see the counting policy in
    PROMPT.md).
    """
    return {
        'Findings raised': len(rows),
        'Major findings raised': sum(1 for r in rows if r[4] == 'Major'),
        'Fix verdicts': sum(1 for r in rows if r[5] == 'Fix'),
        'Cobra-skipped': sum(1 for r in rows if r[5] == 'Skip:Cobra'),
        'Compass-skipped': sum(1 for r in rows if r[5] == 'Skip:Compass'),
        'Integrity-discarded': sum(1 for r in rows if r[5] == 'Discard:Integrity'),
    }


def lens_sections(review, lenses):
    """Map lens name -> section body, for headings that name a lens."""
    found, order = {}, []
    for m in re.finditer(r'^### (.+?)$\n(.*?)(?=^### |^## |\Z)', review, re.M | re.S):
        head = plain(m.group(1))
        for name in lenses + ['W5H1']:
            if re.match(r'^[\W\d_]*' + re.escape(name) + r'(?!\w)', head):
                found[name] = m.group(2)
                order.append(name)
                break
    return found, order


def declared_scope(review):
    """How many lenses the Scorecard says were run, or None if it does not say.

    Rule 6 lets a review narrow its scope, and PROMPT.md's Scope verification
    says so in as many words: a section is required for every lens "in the
    run's declared scope (all ten, unless narrowed under Rule 6)". This
    checker required all ten unconditionally until cycle 7, which made the one
    documented way to narrow a review the one way to fail this check.
    """
    body = section(review, 'Scorecard', level=3)
    if body is None:
        return None
    m = re.search(r'^\| Lenses run \|\s*(\d+)\s*(?:of|/)', body, re.M)
    return int(m.group(1)) if m else None


def check_lenses(review, lenses, scope=None):
    found, order = lens_sections(review, lenses)
    present = [n for n in lenses if n in found]

    if 'W5H1' not in found:
        # W5H1 is mandatory at every scope: PROMPT.md makes it not a lens but
        # not exempt either, and Rule 6 narrows lenses, not W5H1.
        failures.append('no section for: W5H1')
    if scope is None or scope >= len(lenses):
        missing = [n for n in lenses if n not in found]
        if missing:
            failures.append(f"no section for: {', '.join(missing)}")
    elif len(present) != scope:
        failures.append(
            f'Scorecard declares {scope} of {len(lenses)} lenses run, but '
            f'{len(present)} lens sections are present: {", ".join(present)}')

    expected = present + (['W5H1'] if 'W5H1' in found else [])
    if order != expected:
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


def check_index_completeness(review, rows, lenses):
    """Every finding raised in a lens table is in the index, and vice versa.

    PROMPT.md makes the index authoritative for every count in the review, so
    a finding that exists in its lens table and nowhere else is absent from
    the Scorecard, the Exit Estimate and the done-rule at once — and until
    cycle 7 nothing here noticed. A Major could be dropped between DO and the
    index and the checker would still print `all checks pass` (cycle-7 OBS-3).
    """
    found, _ = lens_sections(review, lenses)
    order = [n for n in lenses if n in found] + (['W5H1'] if 'W5H1' in found else [])
    raised = {}
    for name in order:
        for fid in re.findall(r'^\|\s*([A-Z0-9]{2,4}-\d+)\s*\|', found[name], re.M):
            raised.setdefault(fid, name)
    indexed = {r[0] for r in rows}
    for fid, name in sorted(raised.items()):
        if fid not in indexed:
            failures.append(f'{fid}: raised in the {name} lens table, no index row')
    for fid in sorted(indexed - set(raised)):
        failures.append(f'{fid}: in the Findings Index, raised in no lens table')


def index_rows(review):
    body = section(review, 'FINDINGS INDEX', level=2)
    if body is None:
        failures.append('no "## FINDINGS INDEX" section')
        return []
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


def check_scorecard(review, rows, prompt_path):
    """Every mandated Scorecard row is present, and every derived count is right.

    Presence and arithmetic are separate failures. Before cycle 6 only the
    arithmetic was checked, so a review that simply omitted eleven of the
    sixteen rows — 'Fix verdicts' among them — passed: the rows that were
    missing were the rows that went unreconciled.

    Three rows are deliberately not reconciled. 'Fixes applied' and 'PDCA
    cycles run' are not derivable from the index at all — see the counting
    policy in PROMPT.md. Pre-0.4.0 'Fixed' conflated verdict Fix with fixes
    applied (issue #33), so it is accepted unchecked; a review that states the
    0.4.0 'Fix verdicts' row instead has it reconciled.
    """
    table = section(review, 'Scorecard', level=3)
    if table is None:
        failures.append('no "### Scorecard" section')
        return
    card = {plain(k): v.strip() for k, v in
            re.findall(r'^\| ([^|]+?) \| ([^|]*?) \|\s*$', table, re.M)}

    version = instrument_version(review)
    if version is None:
        failures.append('Scorecard states no "Instrument | Diffract X.Y" row')
        required = normative_scorecard_rows(prompt_path)
    elif version >= (0, 4):
        required = normative_scorecard_rows(prompt_path)
    else:
        required = PRE_040_ROWS
    for key in required:
        if key not in card:
            failures.append(f'Scorecard has no {key!r} row')

    expected = {k: v for k, v in derived_counts(rows).items() if k in card}
    for key, want in expected.items():
        m = re.match(r'\s*(\d+)', card[key])
        if not m:
            failures.append(f'Scorecard {key!r} states no number: {card[key][:40]!r}')
        elif int(m.group(1)) != want:
            failures.append(f'Scorecard {key} = {m.group(1)}, index says {want}')


def hypotheses_region(check_body):
    """The competing-hypotheses blocks of a CHECK section, joined, or None.

    Bounded deliberately. The per-finding check used to search the whole CHECK
    section — which contains the CHECK table, which lists every finding ID — so
    it passed on any ID whatever was written beneath the table, while the pass
    message reported competing-hypotheses blocks as checked (cycle-7 OBS-1).
    """
    lines = check_body.split('\n')
    live = outside_fences(lines)
    starts = [i for i, line in enumerate(lines) if live[i] and HYPOTHESES.match(line)]
    if not starts:
        return None
    region = []
    for i in starts:
        head = re.match(r'^(#+)\s', lines[i])
        depth = len(head.group(1)) if head else 6
        j = i + 1
        while j < len(lines):
            nxt = re.match(r'^(#+)\s', lines[j])
            if (nxt and live[j] and len(nxt.group(1)) <= depth
                    and not HYPOTHESES.match(lines[j])):
                break
            j += 1
        region.extend(lines[i:j])
    return '\n'.join(region)


def check_structure(review, rows):
    """The mandated output elements that prove a mandated step ran.

    A step whose only evidence is the reviewer's word is not checkable, so
    PROMPT.md mandates that each leaves a trace in the output. This looks for
    every trace in MANDATED_TRACES, and — where a Low-Confidence finding
    exists — for a competing-hypotheses block that actually names it.

    Both halves failed before cycle 7: three mandated traces were unlisted
    (OBS-2), and the per-finding hypotheses check searched a region that always
    contained the finding ID and so could never fail (OBS-1).
    """
    lines = review.split('\n')
    check_body = section(review, 'CHECK', level=2)
    if check_body is None:
        failures.append('no "## CHECK" section')
        return
    if not re.search(r'^\|.*\|.*\|', check_body, re.M):
        failures.append('CHECK section contains no table')

    for phrase, purpose in MANDATED_TRACES:
        if not stated_at_line_start(lines, phrase):
            failures.append(f'no {phrase!r} section — {purpose}')

    low = [r[0] for r in rows if r[7] == 'Low']
    if not low:
        return
    region = hypotheses_region(check_body)
    if region is None:
        failures.append(
            f'{len(low)} Low-Confidence finding(s) but no "Competing Hypotheses" '
            f'block below the CHECK table: {", ".join(low)}')
        return
    for fid in low:
        if fid not in region:
            failures.append(
                f'{fid}: Low Confidence, named in no competing-hypotheses block')


def requires_quotes(review):
    """Whether this run's Integrity governor demands a quote block per finding.

    The Integrity governor (PROMPT.md, PLAN) makes evidence rules a per-run
    parameter the requester sets,
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


QUOTE_BLOCK = r'((?:^\s+> ?.*$\n?)+)'
LINE_CITE = r'^- ([A-Z0-9]{2,4}-\d+) — (\S+?):(\d+)(?:[-–](\d+))?\s*$\n' + QUOTE_BLOCK
HEAD_CITE = r'^- ([A-Z0-9]{2,4}-\d+) — (\S+?) § (.+?)\s*$\n' + QUOTE_BLOCK


def dedent_quote(block):
    return [re.sub(r'^\s+> ?', '', l) for l in block.rstrip('\n').split('\n')]


def squash(lines):
    return [re.sub(r'\s+', ' ', x).strip() for x in lines]


def heading_body(lines, heading):
    """Lines of the named heading's section, heading line included, or None."""
    span = heading_span(lines, heading)
    return None if span is None else lines[span[0]:span[1]]


def check_evidence(review, rows, artifacts, require):
    """Every Evidence quote must appear verbatim where it says it does.

    Two citation forms, both specified in PROMPT.md: `path:line` for code and
    anything else with stable line numbers, and `path § Heading` for the
    non-code artifacts PROMPT.md tells reviewers to cite by section instead.
    Before cycle 6 only the first was accepted, so a reviewer following the
    non-code citation rule could not pass this checker at all.
    """
    ids = {r[0] for r in rows}
    seen = set()
    verified = 0
    blocks = 0

    for fid, path, start, end, block in re.findall(LINE_CITE, review, re.M):
        blocks += 1
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
        quote = dedent_quote(block)
        window = lines[a - 1:b]
        if quote != window and squash(quote) != squash(window):
            failures.append(
                f'{fid}: quote does not appear at {name}:{a}-{b}\n'
                f'       quoted: {quote[0][:64]!r}\n'
                f'       actual: {(window[0][:64] if window else "")!r}')
            continue
        verified += 1

    for fid, path, heading, block in re.findall(HEAD_CITE, review, re.M):
        blocks += 1
        seen.add(fid)
        if fid not in ids:
            failures.append(f'{fid}: Evidence for a finding with no index row')
        name = os.path.basename(path)
        if name not in artifacts:
            failures.append(f'{fid}: cites {path}, not among the supplied artifacts')
            continue
        section = heading_body(artifacts[name], heading)
        if section is None:
            failures.append(f'{fid}: {name} has no heading {heading!r}')
            continue
        quote = squash(dedent_quote(block))
        haystack = squash(section)
        joined = ' '.join(haystack)
        if ' '.join(quote) not in joined:
            failures.append(
                f'{fid}: quote does not appear under {name} § {heading}\n'
                f'       quoted: {quote[0][:64]!r}')
            continue
        verified += 1

    if require:
        for fid in sorted(ids - seen):
            failures.append(f'{fid}: Integrity requires a quote block, none found')
    return verified, blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('review')
    ap.add_argument('--artifact', action='append', default=[], required=True)
    ap.add_argument('--prompt', default=default_prompt())
    args = ap.parse_args()

    try:
        review = open(args.review).read()
    except OSError as e:
        print(f'FAIL: cannot read review: {e}')
        return 1

    artifacts = {}
    for path in args.artifact:
        try:
            data = open(path, 'rb').read()
        except OSError as e:
            print(f'FAIL: cannot read artifact: {e}')
            return 1
        name = os.path.basename(path)
        if name in artifacts:
            print(f'FAIL: two artifacts share the basename {name!r}; '
                  f'Evidence citations could not tell them apart')
            return 1
        artifacts[name] = data.decode().split('\n')
        print(f'artifact {name} sha256 {hashlib.sha256(data).hexdigest()}')

    # What this run enforced, and where it got it: a pass is only meaningful
    # against a named instrument (cycle-6 PRO-2).
    prompt_version = re.search(r'\*\*Version: ([\d.]+)\*\*', open(args.prompt).read())
    print(f'instrument {args.prompt} '
          f'version {prompt_version.group(1) if prompt_version else "unknown"}')

    lenses = normative_lenses(args.prompt)
    check_lenses(review, lenses, declared_scope(review))
    rows = index_rows(review)
    check_index_completeness(review, rows, lenses)
    check_scorecard(review, rows, args.prompt)
    check_structure(review, rows)
    require = requires_quotes(review)
    verified, blocks = check_evidence(review, rows, artifacts, require)

    print(f'index rows {len(rows)} | quote blocks {blocks} '
          f'(required: {"yes" if require else "no"}) | verified verbatim {verified}')
    print()
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    # Built from the same table the checks read, so the claim and the check
    # cannot drift apart — which is how three mandated sections came to be
    # reported as checked while nothing looked for them (cycle-7 OBS-1/OBS-2).
    traces = '; '.join(p for p, _ in MANDATED_TRACES + CONDITIONAL_TRACES)
    print('checked: lens sections present, in normative order, and agreeing '
          'with the declared scope; cognitive anchoring on nothing-found '
          'lenses; every finding in a lens table carried into the Findings '
          'Index and every index row raised by a lens; the CHECK table; index '
          'verdicts and severities legal; every mandated Scorecard row present '
          'and every derived count equal to the index; every Evidence quote '
          f'verbatim at its citation; and these mandated sections: {traces}.')
    print('not checked: whether any finding is real, whether a severity is '
          'right, whether a lens was applied well, whether the cycle bound or '
          'the done-rule was respected, or whether the Exit Estimate has a '
          'basis.')
    print('all checks pass')
    return 0


if __name__ == '__main__':
    sys.exit(main())
