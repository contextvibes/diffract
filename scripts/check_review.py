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

The normative lens list, the Scorecard row set, the mandated traces, and
every closed vocabulary are read at runtime from the machine-readable
specification block fenced in PROMPT.md, not hard-coded and not scraped from
its prose, so the enforced form follows the instrument (issue #51). `--prompt` overrides which
PROMPT.md that is; the default is the one shipped beside this script, and
the run reports which file it used. Point it at a PROMPT.md belonging to the
artifact under review and the artifact defines the norm it is judged by —
the hazard PROMPT.md states for `render_scorecard.py`, one step removed.

  python3 scripts/check_review.py REVIEW.md --artifact PATH [--artifact PATH]
  python3 scripts/check_review.py REVIEW.md --no-artifact

`--no-artifact` is for a review whose artifact is not available, such as an
anonymized example. It skips the checks that need the artifact — artifact
hashes, citation existence, and Evidence quote verification — and says so
in its output. It refuses any review that carries an Evidence quote, or
whose Integrity governor requires one per finding: a quote that is present
is verified or the review fails, and without the artifact it cannot be
verified (#54).

Exit code 0 = all checks pass; 1 = at least one failure (each is printed).
"""

import argparse
import hashlib
import json
import os
import re
import sys

# How a finding ID is recognised in a table or a citation: wider than the
# grammar, on purpose. A row whose ID breaks PROMPT.md's grammar is found here
# and then failed by index_rows against the grammar PROMPT.md defines, rather
# than passed over as if it were not a finding at all.
ID_SHAPE = r'[A-Z0-9]{2,4}-\d+'

# The traces a review must carry, and the vocabulary every check below
# applies, are read from PROMPT.md's machine-readable specification block
# (issue #51). They were constants here until then, held to PROMPT.md by a
# release gate that searched its prose for each phrase.
SPEC_BLOCK = re.compile(r'^```json diffract-spec\n(.*?)^```[ \t]*$', re.S | re.M)



def plain(text):
    """Strip markdown emphasis so cell values compare as literal strings."""
    return re.sub(r'[*`]', '', text).strip()


def split_row(line):
    """The raw cells of a Markdown table row, or None if it is not one.

    Escape-aware: `\\|` is a literal pipe inside a cell, as in GitHub's
    table syntax, and does not end the cell. Splitting on every `|` shifted
    every column after a cell that contained one, and failed a correct review
    with "illegal verdict" or a missing Scorecard row — PROMPT.md writes the
    Cobra levels pipe-separated, so restating them in a Governors row was
    enough (cycle-6 VAR-3, issue #43). Cells come back stripped but still
    escaped, so a caller that rewrites a row can write it back unchanged;
    `unescape()` gives the value.
    """
    line = line.rstrip()
    if not (line.startswith('|') and line.endswith('|') and len(line) > 1):
        return None
    cells = re.split(r'(?<!\\)\|', line[1:-1])
    return [c.strip() for c in cells]


def unescape(cell):
    """A cell's value: escaped pipes restored and emphasis stripped."""
    return plain(cell.replace('\\|', '|'))


def table_rows(body):
    """Raw cells of every table row in a body, header and rule rows dropped."""
    rows = []
    for line in body.split('\n'):
        cells = split_row(line)
        if cells is None or all(re.match(r'^:?-*:?$', c) for c in cells):
            continue
        rows.append(cells)
    return rows


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



def read_text(path):
    with open(path) as handle:
        return handle.read()


def default_prompt():
    """PROMPT.md next to this script's repository root."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'PROMPT.md')


# What the specification block must hold, and the type of each entry. A
# block that breaks this shape is one failure and an empty vocabulary, never
# an exception in whichever check first touched the missing part.
SPEC_SHAPE = {
    'lenses': list, 'question_set': dict, 'verdicts': list, 'severities': list,
    'confidences': list, 'tags': list, 'config': dict, 'lens_output': dict,
    'scorecard_rows': list, 'lenses_run_form': str, 'traces': dict,
}
SPEC_ITEMS = {
    'lenses': ('name', 'icon', 'prefix', 'question'),
    'question_set': ('name', 'prefix'),
    'config': ('keys', 'values', 'defaults', 'ranges'),
    'lens_output': ('always', 'nothing_found'),
    'traces': ('mandated', 'conditional'),
}


def spec_shape_failures(data):
    """Every way the parsed block departs from SPEC_SHAPE, as messages."""
    if not isinstance(data, dict):
        return ['is not a JSON object']
    wrong = []
    for key, kind in SPEC_SHAPE.items():
        if not isinstance(data.get(key), kind):
            wrong.append(f'{key!r} is missing or not a {kind.__name__}')
    if wrong:
        return wrong
    for lens in data['lenses']:
        if not (isinstance(lens, dict) and all(
                isinstance(lens.get(k), str) for k in SPEC_ITEMS['lenses'])):
            wrong.append(f'lens entry {lens!r} lacks one of {SPEC_ITEMS["lenses"]}')
    for key in ('question_set', 'config', 'lens_output', 'traces'):
        for item in SPEC_ITEMS[key]:
            if item not in data[key]:
                wrong.append(f'{key!r} has no {item!r}')
    if '{run}' not in data['lenses_run_form'] or '{total}' not in data['lenses_run_form']:
        wrong.append("'lenses_run_form' names neither {run} nor {total}")
    for kind in ('mandated', 'conditional'):
        for trace in data['traces'].get(kind) or []:
            if not (isinstance(trace, dict) and isinstance(trace.get('name'), str)
                    and isinstance(trace.get('purpose'), str)):
                wrong.append(f'{kind} trace {trace!r} lacks a name or purpose')
            elif kind == 'conditional' and not isinstance(trace.get('when_confidence'), str):
                wrong.append(f'conditional trace {trace["name"]!r} has no when_confidence')
    ranges = data['config'].get('ranges')
    for key, span in (ranges.items() if isinstance(ranges, dict) else []):
        if not (isinstance(span, list) and len(span) == 2
                and all(isinstance(n, int) for n in span)):
            wrong.append(f'range for {key!r} is not [low, high]')
    return wrong


def spec(prompt_path, failures):
    """PROMPT.md's machine-readable specification block, parsed, or {}.

    The one place the scripts read PROMPT.md's closed lists from. Before
    issue #51 each list was scraped out of the prose at its own site by its
    own regex, and a rule that lived in no list (the mandated traces) was a
    constant here, held to PROMPT.md by a phrase search. The block is fenced
    in PROMPT.md itself, so a reviewer reads the same lists the scripts do,
    and `scripts/check.py` fails the release when it and the prose disagree.
    """
    try:
        text = read_text(prompt_path)
    except OSError as e:
        failures.append(f'{prompt_path}: cannot read: {e}')
        return {}
    blocks = SPEC_BLOCK.findall(text)
    if len(blocks) != 1:
        failures.append(f'{prompt_path}: expected one ```json diffract-spec block, '
                        f'found {len(blocks)}')
        return {}
    try:
        data = json.loads(blocks[0])
    except ValueError as e:
        failures.append(f'{prompt_path}: the diffract-spec block is not valid JSON: {e}')
        return {}
    wrong = spec_shape_failures(data)
    if wrong:
        failures.extend(f'{prompt_path}: diffract-spec block: {w}' for w in wrong)
        return {}
    return data


def normative_lens_rows(prompt_path, failures):
    """(icon and name, question) per lens, in order, from the spec block.

    `scripts/check.py` diffs README's lens table against this rather than
    reading PROMPT.md a second time: two copies of an anti-drift parser are
    themselves something to drift.
    """
    lenses = spec(prompt_path, failures).get('lenses', [])
    if lenses and len(lenses) != 10:
        failures.append(f'{prompt_path}: expected 10 lenses, the spec block has {len(lenses)}')
    return [(f"{lens['icon']} {lens['name']}", lens['question']) for lens in lenses]


def normative_lenses(prompt_path, failures):
    """The ten lens names, in order, without their icons."""
    return [lens['name'] for lens in spec(prompt_path, failures).get('lenses', [])]


# The Scorecard row set of the instrument that produced a review. 0.4.0 and
# later are read from PROMPT.md; earlier reviews are frozen evidence (see
# CONTRIBUTING.md, Release Gates) and are checked against the set that was
# normative when they were written. This stays here, not in the spec block:
# PROMPT.md specifies the current instrument, and a superseded row list in it
# would be a second specification of the past (issue #41, call 1).
PRE_040_ROWS = [
    'Reviewer', 'Artifact', 'Instrument', 'Governors', 'Entry checks',
    'Findings raised', 'Major findings raised', 'Fixed', 'Cobra-skipped',
    'Compass-skipped', 'Integrity-discarded', 'PDCA cycles run', 'Lenses run',
    'Most productive lens', 'Estimated remaining Majors', 'Calibration', 'Tags',
]


def normative_scorecard_rows(prompt_path, failures):
    """The Scorecard rows, in order, from the spec block.

    Read rather than hard-coded for the same reason the lens list is: a row
    added to the template is a row the checker must require, and a checker
    that has to be edited in step with the document it enforces will
    eventually not be (issue #39).
    """
    data = spec(prompt_path, failures)
    rows = data.get('scorecard_rows', [])
    if data and not rows:
        failures.append(f'{prompt_path}: the spec block lists no Scorecard rows')
    return rows


def normative_vocabulary(prompt_path, failures):
    """Every closed vocabulary PROMPT.md enumerates, from its spec block.

    Hard-coded once, so a value added to PROMPT.md failed every review that
    used it, against the wrong instrument and without saying so (cycle-6
    W5H-3); then scraped from the prose, one regex per site (#39, #41); now
    read from the block (#51), which `scripts/check.py` holds to the prose.
    The keys are the ones the callers have always used.
    """
    data = spec(prompt_path, failures)
    vocab = {key: [] for key in (
        'verdicts', 'severities', 'confidences', 'tags', 'config_keys',
        'literals_always', 'literals_nothing_found', 'traces_mandated',
        'traces_conditional')}
    vocab.update(config_values={}, config_defaults={}, config_ranges={},
                 id_prefixes={}, lenses_run_form='')
    if not data:
        return vocab
    for key in ('verdicts', 'severities', 'confidences'):
        vocab[key] = list(data[key])
    vocab['tags'] = sorted(data['tags'])
    config = data['config']
    vocab['config_keys'] = list(config['keys'])
    vocab['config_values'] = {k: list(v) for k, v in config['values'].items()}
    vocab['config_defaults'] = dict(config['defaults'])
    vocab['config_ranges'] = {k: tuple(v) for k, v in config['ranges'].items()}
    # Finding IDs are `<lens abbreviation>-<n>`. The checker accepted any two
    # to four capitals before, a grammar PROMPT.md never stated (issue #41).
    vocab['id_prefixes'] = {lens['name']: lens['prefix'] for lens in data['lenses']}
    vocab['id_prefixes'][data['question_set']['name']] = data['question_set']['prefix']
    # Text both lens-output templates carry is required of every lens
    # section; text only Output B carries, of a lens that found nothing.
    vocab['literals_always'] = list(data['lens_output']['always'])
    vocab['literals_nothing_found'] = list(data['lens_output']['nothing_found'])
    vocab['lenses_run_form'] = data['lenses_run_form'].replace(
        '{total}', str(len(data['lenses'])))
    vocab['traces_mandated'] = [(t['name'], t['purpose'])
                                for t in data['traces']['mandated']]
    vocab['traces_conditional'] = [(t['name'], t['purpose'], t['when_confidence'])
                                   for t in data['traces']['conditional']]

    for key in ('verdicts', 'severities', 'confidences', 'tags', 'config_keys',
                'config_values', 'id_prefixes', 'literals_always',
                'literals_nothing_found', 'traces_mandated'):
        if not vocab[key]:
            failures.append(f'{prompt_path}: the spec block lists no {key}')
    return vocab


def lenses_run_pattern(vocab):
    """A regex for the opening of a `Lenses run` value, its count captured."""
    form = vocab.get('lenses_run_form') or ''
    if '{run}' not in form:
        return None
    head, tail = form.split('{run}', 1)
    return re.compile(r'\s*' + re.escape(head) + r'(\d+)' + re.escape(tail) + r'(?!\d)')


def trace_heading(name):
    """A regex for a heading or a bold label opening a line that names a trace."""
    return re.compile(r'^(?:#+\s+|\*\*)[^\n]*' + re.escape(name), re.I)


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


def lens_name(cell):
    """A Lens cell's name without its icon: '🗑️ Subtract' -> 'Subtract'."""
    return re.sub(r'^[\W_]+', '', plain(cell))


def lens_sections(review, lenses):
    """Map lens name -> section body, for headings that name a lens."""
    found, order = {}, []
    live = outside_fences(review.split('\n'))
    for m in re.finditer(r'^### (.+?)$\n(.*?)(?=^### |^## |\Z)', review, re.M | re.S):
        # A quoted template inside a fence is not a lens section (cycle-8 VAR-2).
        if not live[review.count('\n', 0, m.start())]:
            continue
        head = plain(m.group(1))
        for name in lenses + ['W5H1']:
            if re.match(r'^[\W\d_]*' + re.escape(name) + r'(?!\w)', head):
                # The done-rule mandates up to 3 PDCA cycles, so a conforming
                # review repeats every lens once per cycle. Bodies accumulate
                # and the order records first appearance; keeping only the last
                # body and appending a duplicate rejected multi-cycle reviews
                # twice over (cycle-8b VAR-1).
                found[name] = found.get(name, '') + '\n' + m.group(2)
                if name not in order:
                    order.append(name)
                break
    return found, order


def declared_scope(review, vocab):
    """How many lenses the Scorecard says were run, or None if it does not say.

    Rule 6 lets a review narrow its scope, and PROMPT.md's Scope verification
    says so in as many words: a section is required for every lens "in the
    run's declared scope (all ten, unless narrowed under Rule 6)". This
    checker required all ten unconditionally until cycle 7, which made the one
    documented way to narrow a review the one way to fail this check.
    """
    stated = lenses_run_row(review, vocab)
    return None if stated is None else stated[0]


def lenses_run_row(review, vocab):
    """(number, full value) of the Scorecard's `Lenses run` row, or None.

    Read only in the form the spec block gives, `X of 10`. A value in any
    other form is None here, and check_scorecard fails it (issue #41, call 6).
    """
    body = section(review, 'Scorecard', level=3)
    pattern = lenses_run_pattern(vocab)
    if body is None or pattern is None:
        return None
    value = scorecard_cells(body).get('Lenses run')
    m = value and pattern.match(value)
    return (int(m.group(1)), value) if m else None


def scorecard_cells(table):
    """{metric: value} for every two-cell row of a Scorecard table body."""
    return {unescape(cells[0]): unescape(cells[1])
            for cells in table_rows(table) if len(cells) == 2}


def check_lenses(review, lenses, scope, vocab, failures):
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
    else:
        # A narrowed scope is declared, not inferred: PROMPT.md's template
        # makes the row "name any omitted". A row reading "9 of 10 — none
        # omitted" over nine sections is a skipped lens with its count edited
        # to match, which is how render_scorecard.py used to launder one
        # (issue #50).
        stated = (lenses_run_row(review, vocab) or (None, ''))[1].lower()
        unnamed = [n for n in lenses if n not in found and n.lower() not in stated]
        if unnamed:
            failures.append(
                f'Scorecard declares {scope} of {len(lenses)} lenses run but its '
                f'Lenses run row does not name the omitted: {", ".join(unnamed)}')

    expected = present + (['W5H1'] if 'W5H1' in found else [])
    if order != expected:
        failures.append(f'lens sections out of normative order: {order}')

    for name, body in found.items():
        for literal in vocab['literals_always']:
            if literal not in body:
                failures.append(f"{name}: no {literal!r} line")
        if re.search(r'^\|\s*' + ID_SHAPE, body, re.M):
            continue
        for literal in vocab['literals_nothing_found']:
            if literal not in body:
                failures.append(f'{name}: nothing-found lens without "{literal}"')


def check_index_completeness(review, rows, lenses, failures):
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
        for fid in re.findall(r'^\|\s*(' + ID_SHAPE + r')\s*\|', found[name], re.M):
            raised.setdefault(fid, name)
    indexed = {r[0] for r in rows}
    for fid, name in sorted(raised.items()):
        if fid not in indexed:
            failures.append(f'{fid}: raised in the {name} lens table, no index row')
    for fid in sorted(indexed - set(raised)):
        failures.append(f'{fid}: in the Findings Index, raised in no lens table')


def index_rows(review, vocab, failures):
    """The Findings Index rows, each checked against PROMPT.md's vocabularies:
    the ID grammar and its lens, the verdict, the severity, the Confidence."""
    body = section(review, 'FINDINGS INDEX', level=2)
    if body is None:
        failures.append('no "## FINDINGS INDEX" section')
        return []
    rows = [[unescape(c) for c in cells] for cells in table_rows(body)
            if unescape(cells[0]) != 'ID']
    for row in rows:
        if len(row) != 8:
            failures.append(f'index row is {len(row)} columns, expected 8: {row[:1]}')
            continue
        prefix = vocab['id_prefixes'].get(lens_name(row[1]))
        if not re.fullmatch(r'[A-Z0-9]+-\d+', row[0]) or (
                prefix and row[0].split('-')[0] != prefix):
            want = f'{prefix}-<n>' if prefix else '<lens abbreviation>-<n>'
            failures.append(f'{row[0]}: ID is not {want} for lens {row[1]!r}')
        if lens_name(row[1]) not in vocab['id_prefixes']:
            failures.append(f'{row[0]}: Lens {row[1]!r} is not a lens or W5H1')
        if row[7] not in vocab['confidences']:
            failures.append(f'{row[0]}: illegal Confidence {row[7]!r}')
        if row[5] not in vocab['verdicts']:
            failures.append(f'{row[0]}: illegal verdict {row[5]!r}')
        if row[4] not in vocab['severities']:
            failures.append(f'{row[0]}: illegal severity {row[4]!r}')
    return [r for r in rows if len(r) == 8]


def check_scorecard(review, rows, prompt_path, vocab, failures):
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
    card = scorecard_cells(table)

    version = instrument_version(review)
    if version is None:
        failures.append('Scorecard states no "Instrument | Diffract X.Y" row')
        required = normative_scorecard_rows(prompt_path, failures)
    elif version >= (0, 4):
        required = normative_scorecard_rows(prompt_path, failures)
    else:
        required = PRE_040_ROWS
    for key in required:
        if key not in card:
            failures.append(f'Scorecard has no {key!r} row')

    # An unreadable `Lenses run` value used to be skipped: the scope it
    # declares could not be read, so all ten lenses were required and nothing
    # said why. PROMPT.md now states the form, and a value outside it fails
    # as itself (issue #41, call 6).
    form = vocab.get('lenses_run_form')
    if 'Lenses run' in card and form and lenses_run_row(review, vocab) is None:
        failures.append(
            f"Scorecard 'Lenses run' value {card['Lenses run'][:40]!r} does not "
            f"open in PROMPT.md's form {form.replace('{run}', 'X')!r}")

    expected = {k: v for k, v in derived_counts(rows).items() if k in card}
    for key, want in expected.items():
        m = re.match(r'\s*(\d+)', card[key])
        if not m:
            failures.append(f'Scorecard {key!r} states no number: {card[key][:40]!r}')
        elif int(m.group(1)) != want:
            failures.append(f'Scorecard {key} = {m.group(1)}, index says {want}')


def hypotheses_region(check_body, heading):
    """The competing-hypotheses blocks of a CHECK section, joined, or None.

    Bounded deliberately. The per-finding check used to search the whole CHECK
    section — which contains the CHECK table, which lists every finding ID — so
    it passed on any ID whatever was written beneath the table, while the pass
    message reported competing-hypotheses blocks as checked (cycle-7 OBS-1).
    """
    lines = check_body.split('\n')
    live = outside_fences(lines)
    starts = [i for i, line in enumerate(lines) if live[i] and heading.match(line)]
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
                    and not heading.match(lines[j])):
                break
            j += 1
        region.extend(lines[i:j])
    return '\n'.join(region)


def check_structure(review, rows, vocab, failures):
    """The mandated output elements that prove a mandated step ran.

    A step whose only evidence is the reviewer's word is not checkable, so
    PROMPT.md mandates that each leaves a trace in the output. This looks for
    every mandated trace the spec block lists, and — for each conditional
    trace, where a finding has the Confidence it names — for a block under
    that name that actually names the finding.

    Both halves failed before cycle 7: three mandated traces were unlisted
    (OBS-2), and the per-finding hypotheses check searched a region that always
    contained the finding ID and so could never fail (OBS-1).
    """
    lines = review.split('\n')
    # PROMPT.md heads this phase '### CHECK' and never said what level a
    # REVIEW must use, while this demanded level 2 — so a review that copied
    # the instrument's own level could not pass (cycle-8 TRU-2, cycle-8b
    # BOU-1). Both are accepted here and PROMPT.md now states the rule.
    # `or` is wrong for the fallback: a section present but empty is falsy.
    check_body = section(review, 'CHECK', level=2)
    if check_body is None:
        check_body = section(review, 'CHECK', level=3)
    if check_body is None:
        failures.append('no "## CHECK" or "### CHECK" section')
        return []
    if not re.search(r'^\|.*\|.*\|', check_body, re.M):
        failures.append('CHECK section contains no table')

    checked = []
    for phrase, purpose in vocab['traces_mandated']:
        checked.append(phrase)
        if not stated_at_line_start(lines, phrase):
            failures.append(f'no {phrase!r} section — {purpose}')

    for name, purpose, when in vocab['traces_conditional']:
        due = [r[0] for r in rows if r[7] == when]
        if not due:
            continue
        checked.append(name)
        region = hypotheses_region(check_body, trace_heading(name))
        if region is None:
            failures.append(
                f'{len(due)} {when}-Confidence finding(s) but no "{name}" '
                f'block below the CHECK table: {", ".join(due)}')
            continue
        for fid in due:
            if fid not in region:
                failures.append(
                    f'{fid}: {when} Confidence, named in no {name.lower()} block')
    return checked


def requires_quotes(review, failures):
    """Whether this run's Integrity governor demands a quote block per finding.

    The Integrity governor (PROMPT.md, PLAN) makes evidence rules a per-run
    parameter the requester sets,
    not a fixed rule of the instrument, so the requirement is read from the
    review's own declared governors rather than assumed. Quotes that are
    present are verified either way: an unrequested quote that misquotes the
    artifact is still a fabrication.
    """
    # Anchored at column 0, with no blockquote marker: an unanchored search
    # took the first 'Integrity:' anywhere in the review, so a line quoted from
    # the artifact could turn the evidence requirement off for the whole run
    # (cycle-8 SHI-3). Fences are deliberately NOT skipped — the governors are
    # declared inside one. The residual limit: a review that reproduces a
    # governor block at column 0 inside a fence before declaring its own is
    # still read from the quote.
    lines = review.split('\n')
    for i, line in enumerate(lines):
        m = re.match(r'^(?![ \t>])[^\w>]*\*{0,2}Integrity:\*{0,2}(.*)', line)
        if not m:
            continue
        tail = [m.group(1)]
        for nxt in lines[i + 1:]:
            if not re.match(r'^[ \t]{2,}\S', nxt):
                break
            tail.append(nxt)
        return bool(re.search(r'verbatim|quote', '\n'.join(tail), re.I))
    failures.append('no Integrity governor line found')
    return False


QUOTE_BLOCK = r'((?:^\s+> ?.*$\n?)+)'
LINE_CITE = r'^- (' + ID_SHAPE + r') — (\S+?):(\d+)(?:[-–](\d+))?\s*$\n' + QUOTE_BLOCK
HEAD_CITE = r'^- (' + ID_SHAPE + r') — (\S+?) § (.+?)\s*$\n' + QUOTE_BLOCK


def dedent_quote(block):
    return [re.sub(r'^\s+> ?', '', l) for l in block.rstrip('\n').split('\n')]


def squash(lines):
    return [re.sub(r'\s+', ' ', x).strip() for x in lines]


def quoted_in_place(quote, lines):
    """Whether `quote` appears in `lines` with the artifact's own line breaks.

    A quote under a heading may begin and end mid-line, so its first line is
    matched as the end of an artifact line and its last as the start of one;
    every line between must be whole. Matching the joined text instead
    accepted a reflowed quote, which PROMPT.md forbids (issue #41).
    """
    n = len(quote)
    if n == 1:
        return any(quote[0] in line for line in lines)
    for i in range(len(lines) - n + 1):
        if (lines[i].endswith(quote[0]) and lines[i + n - 1].startswith(quote[-1])
                and lines[i + 1:i + n - 1] == quote[1:-1]):
            return True
    return False


def heading_body(lines, heading):
    """Lines of the named heading's section, heading line included, or None."""
    span = heading_span(lines, heading)
    return None if span is None else lines[span[0]:span[1]]


def path_parts(path):
    """A path's components after normalisation, absolute paths keeping '/'."""
    norm = os.path.normpath(path)
    parts = [p for p in norm.split(os.sep) if p not in ('', '.')]
    return (['/'] if os.path.isabs(norm) else []) + parts


def resolve_citation(path, artifacts):
    """(display name, lines) of the one supplied artifact a citation names.

    A cited path names a supplied artifact when its components are a suffix of
    that artifact's absolute path: `semver.md`, `artifacts/semver.md` and the
    full path all name `examples/artifacts/semver.md`; `vendor/semver.md` does
    not. Citations used to resolve by basename alone, so a quote verified
    against a file the review never cited and the checker reported it
    "verbatim at its citation" (issue #49). Suffix rather than equality,
    because a blind reviewer is handed files in a layout it cannot see and
    cites them relative to whatever it was shown.

    Returns (None, reason) when no artifact, or more than one, matches.
    """
    want = path_parts(path)
    hits = [(name, lines) for name, (parts, lines) in artifacts.items()
            if want and parts[len(parts) - len(want):] == want]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        return None, f'cites {path}, not among the supplied artifacts'
    return None, (f'cites {path}, which names more than one supplied artifact: '
                  f'{", ".join(n for n, _ in hits)}')


def check_evidence(review, rows, artifacts, require, failures):
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
        name, lines = resolve_citation(path, artifacts)
        if name is None:
            failures.append(f'{fid}: {lines}')
            continue
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
        name, lines = resolve_citation(path, artifacts)
        if name is None:
            failures.append(f'{fid}: {lines}')
            continue
        section = heading_body(lines, heading)
        if section is None:
            failures.append(f'{fid}: {name} has no heading {heading!r}')
            continue
        if not quoted_in_place(squash(dedent_quote(block)), squash(section)):
            failures.append(
                f'{fid}: quote does not appear under {name} § {heading}\n'
                f'       quoted: {dedent_quote(block)[0][:64]!r}')
            continue
        verified += 1

    if require:
        for fid in sorted(ids - seen):
            failures.append(f'{fid}: Integrity requires a quote block, none found')
    return verified, blocks


def implementation():
    """One line naming the checker that ran: its hash, and the manifest's.

    A pass names the instrument it enforced; it must name the implementation
    too, or a run against one revision of this file is indistinguishable from
    a run against the next (issue #46). scripts/check.py holds the scripts to
    scripts/MANIFEST; this only reports whether this file agrees with it.
    """
    here = os.path.abspath(__file__)
    with open(here, 'rb') as handle:
        mine = hashlib.sha256(handle.read()).hexdigest()
    manifest = os.path.join(os.path.dirname(here), 'MANIFEST')
    try:
        with open(manifest, 'rb') as handle:
            data = handle.read()
    except OSError:
        return f'checker sha256 {mine} (no scripts/MANIFEST beside it)'
    listed = re.search(r'^([0-9a-f]{64})  check_review\.py$', data.decode(), re.M)
    agrees = 'matches' if listed and listed.group(1) == mine else 'does NOT match'
    return (f'checker sha256 {mine}, {agrees} scripts/MANIFEST '
            f'(sha256 {hashlib.sha256(data).hexdigest()})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('review')
    given = ap.add_mutually_exclusive_group(required=True)
    given.add_argument('--artifact', action='append', default=[])
    given.add_argument('--no-artifact', action='store_true',
                       help='the artifact is not available: skip the checks '
                            'that need it; refused if Integrity requires quotes')
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
        # Keyed by the path as supplied, matched by path suffix: two artifacts
        # that share a basename are told apart by a citation that names
        # enough of the path, and a citation too short to is a failure of
        # that citation rather than of the run (issue #49).
        name = os.path.normpath(path)
        artifacts[name] = (path_parts(os.path.abspath(path)), data.decode().split('\n'))
        print(f'artifact {name} sha256 {hashlib.sha256(data).hexdigest()}')

    # What this run enforced, and where it got it: a pass is only meaningful
    # against a named instrument (cycle-6 PRO-2).
    prompt_version = re.search(r'\*\*Version: ([\d.]+)\*\*', open(args.prompt).read())
    print(f'instrument {args.prompt} '
          f'version {prompt_version.group(1) if prompt_version else "unknown"}')
    print(implementation())
    if args.no_artifact:
        print('artifact: none supplied (--no-artifact)')

    # Collected here and passed to every check, never held at module level:
    # a module-global list leaked one call's failures into the next, and each
    # caller had to remember to clear it by hand (cycle-7 BOU-1, issue #47).
    failures = []
    lenses = normative_lenses(args.prompt, failures)
    vocab = normative_vocabulary(args.prompt, failures)
    check_lenses(review, lenses, declared_scope(review, vocab), vocab, failures)
    rows = index_rows(review, vocab, failures)
    check_index_completeness(review, rows, lenses, failures)
    check_scorecard(review, rows, args.prompt, vocab, failures)
    ran = check_structure(review, rows, vocab, failures) or []
    require = requires_quotes(review, failures)
    if args.no_artifact:
        # Without the artifact, a quote is the reviewer's word. A run whose
        # Integrity governor makes the quotes its evidence cannot pass on the
        # reviewer's word, so it is refused rather than passed unverified.
        # Neither can an unrequested quote: one that misquotes the artifact is
        # still a fabrication, and every quote present is verified or fails.
        blocks = (len(re.findall(LINE_CITE, review, re.M))
                  + len(re.findall(HEAD_CITE, review, re.M)))
        if require:
            failures.append('--no-artifact: the Integrity governor requires a '
                            'verbatim quote per finding, and quotes cannot be '
                            'verified without the artifact; supply --artifact')
        elif blocks:
            failures.append(f'--no-artifact: {blocks} Evidence quote block(s) '
                            'present, and none can be verified without the '
                            'artifact; supply --artifact')
        print(f'index rows {len(rows)} | quote blocks {blocks} '
              f'(required: {"yes" if require else "no"}) | NOT verified: no artifact')
    else:
        verified, blocks = check_evidence(review, rows, artifacts, require, failures)
        print(f'index rows {len(rows)} | quote blocks {blocks} '
              f'(required: {"yes" if require else "no"}) | verified verbatim {verified}')
    print()
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    # Built from the phrases check_structure actually looked for on THIS run,
    # not from the tables it could have looked for. Joining both tables
    # reported the conditional Competing Hypotheses check as run on reviews
    # that have no Low-Confidence finding, where it returns before looking —
    # reintroducing, inside the fix for it, the defect it was named for
    # (cycle-7 OBS-1, found again as cycle-8 OBS-1 and cycle-8b OBS-1).
    traces = '; '.join(ran)
    evidence = ('' if args.no_artifact else
                'every Evidence quote verbatim at its citation; ')
    print('checked: lens sections present, in normative order, and agreeing '
          'with the declared scope; cognitive anchoring on nothing-found '
          'lenses; every finding in a lens table carried into the Findings '
          'Index and every index row raised by a lens; the CHECK table; index '
          'IDs, lenses, verdicts, severities and Confidence legal; every '
          'mandated Scorecard row present '
          'and every derived count equal to the index; '
          f'{evidence}and these mandated sections: {traces}.')
    if args.no_artifact:
        print('skipped (--no-artifact): the artifact hash, and whether any '
              'Evidence citation resolves — the review carries no Evidence '
              'quotes, and no artifact was supplied, so nothing in this '
              'review was checked against what it reviewed.')
    print('not checked: whether any finding is real, whether a severity is '
          'right, whether a lens was applied well, whether the cycle bound or '
          'the done-rule was respected, or whether the Exit Estimate has a '
          'basis.')
    print('all checks pass')
    return 0


if __name__ == '__main__':
    sys.exit(main())
