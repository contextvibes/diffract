#!/usr/bin/env python3
"""The entry-criteria gate for this repository, and its release checks.

This is the reference implementation of the deterministic entry checks
PROMPT.md mandates for non-code artifacts — a reviewer running Diffract
against this repo runs it at PLAN — plus the repo's own release gates that
can be checked without judgment: link and anchor resolution, code-fence
balance, version-string agreement, a README-vs-PROMPT lens-table diff, every
other file's verdicts, tags, Severity and Confidence lists and config values
against PROMPT.md's, PROMPT.md's prose against its own machine-readable
specification block, and the scripts against scripts/MANIFEST. Standard
library only.

Every check is independent: a file this repository does not have is one
`FAIL:` line, never an exception that cancels the checks after it. Diffract
reviews itself from partial checkouts — a blind reviewer is given the
artifact and nothing else — and a gate that aborts there reports nothing
while looking like it ran.

Run from the repository root: python3 scripts/check.py
Exit code 0 = all checks pass; 1 = at least one failure (each is printed).

`python3 scripts/check.py --write-manifest` regenerates scripts/MANIFEST after
a script changes; the check then holds the scripts to it.
"""

import glob
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_review

SKIP_DIRS = ('.claude', 'node_modules', '.git')


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


def anchors_of(path, cache, failures):
    """GitHub-style slugs for every heading outside fenced code blocks.

    Cached: without it the target is re-read and re-parsed once per anchored
    link, and one unreadable target appends one failure per link to it. The
    cache belongs to one run of check_links(), not to the module, for the
    reason the failure list does (issue #47).
    """
    if path in cache:
        return cache[path]
    slugs = cache.setdefault(path, set())
    text = read(path, failures)
    if text is None:
        return slugs
    for heading in re.findall(r'^#+\s+(.*)$', strip_fenced(text), re.M):
        slug = heading.strip().lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slugs.add(re.sub(r'\s', '-', slug.strip()))
    return slugs


def read(path, failures):
    """File contents, or None with a recorded failure."""
    try:
        with open(path) as handle:
            return handle.read()
    except OSError as e:
        failures.append(f'cannot read {path}: {e.strerror}')
        return None


def check_versions(failures):
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
        text = read(path, failures)
        if text is None:
            continue
        found = re.search(pattern, text, re.M)
        if found is None:
            failures.append(f'version string not found in: {label}')
        else:
            values[label] = found.group(1)
    if len(set(values.values())) > 1:
        failures.append(f'version strings disagree: {values}')


def check_fences(failures):
    for path in md_files():
        text = read(path, failures)
        if text is None:
            continue
        markers = len(re.findall(r'^```', text, re.M))
        if markers % 2:
            failures.append(f"{path}: unbalanced code fences ({markers} markers)")


def check_links(failures):
    anchors = {}
    for path in md_files():
        raw = read(path, failures)
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
            elif (anchor and target.endswith('.md')
                  and anchor not in anchors_of(target, anchors, failures)):
                failures.append(f"{path}: broken anchor {link}")


def check_lens_table(failures):
    readme = read('README.md', failures)
    if readme is None or read('PROMPT.md', failures) is None:
        return
    normative = check_review.normative_lens_rows('PROMPT.md', failures)
    if not normative:
        return
    # Escape-aware, like every other table parse here (cycle-6 VAR-3).
    reproduced = [(check_review.unescape(cells[1]), cells[2].replace('\\|', '|'))
                  for cells in check_review.table_rows(readme)
                  if len(cells) == 3 and re.match(r'^\d+$', cells[0])]
    if normative != reproduced:
        failures.append(f'README lens table drifted from PROMPT.md: {set(normative) ^ set(reproduced)}')


def prose_vocabulary(prompt):
    """Every list the spec block carries, read back out of PROMPT.md's prose.

    These are the parsers the scripts used before issue #51, kept here and
    nowhere else: the scripts read the block, and this reads the prose only so
    the release can fail when the two disagree. Each list is read at the site
    that defines it. A list whose site is not found reads as empty, and the
    comparison then fails on it.
    """
    lines = prompt.split('\n')
    live = check_review.outside_fences(lines)
    prose = ' '.join(line.strip() for line, keep in zip(lines, live) if keep)
    plain = check_review.plain
    vocab = {}

    listed = re.search(r'#### The 10 Lenses.*?#### W5H1', prompt, re.S)
    vocab['lens_rows'] = ([(plain(n), q.strip()) for n, q in
                           re.findall(r'^\d+\. (.+?) — (.+)$', listed.group(0), re.M)]
                          if listed else [])

    table = re.search(r'\*\*Verdict\*\* is one of .*?\n\n((?:\|.*\n)+)', prompt)
    vocab['verdicts'] = ([check_review.unescape(cells[0])
                          for cells in check_review.table_rows(table.group(1))
                          if check_review.unescape(cells[0]) != 'Verdict']
                         if table else [])

    for key, term in (('severities', 'Severity'), ('confidences', 'Confidence')):
        paragraph = re.search(r'^\*\*' + term + r'\*\* is .*?(?=\n\n)', prompt, re.S | re.M)
        vocab[key] = (re.findall(r'\*\*(\w+)\*\* —', paragraph.group(0))
                      if paragraph else [])

    vocab['tags'] = sorted({re.sub(r'\s+', ' ', t)
                            for t in re.findall(r'`(\[[^`\]]+\])`', prose)})

    keys = re.search(r'defined keys — (.*?`)\.\s', prose)
    vocab['config_keys'] = re.findall(r'`(\w+)`', keys.group(1)) if keys else []
    values, defaults, ranges = {}, {}, {}
    permitted = re.search(r'Permitted values: (.*?)\. An out-of-range', prose)
    for clause in (permitted.group(1).split(';') if permitted else []):
        named = re.match(r'\s*`(\w+)` is (.*)', clause)
        if not named:
            continue
        key, rest = named.groups()
        listed_values = rest.split(' — ')[0]
        span = re.search(r'range (\d+)[–-](\d+)', listed_values)
        if span:
            ranges[key] = (int(span.group(1)), int(span.group(2)))
            continue
        values[key] = re.findall(r'`([^`]+)`', re.sub(r'\([^)]*\)', '', listed_values))
        if 'the last is the PLAN default' in rest and values[key]:
            defaults[key] = values[key][-1]
    vocab['config_values'], vocab['config_defaults'] = values, defaults
    vocab['config_ranges'] = ranges

    named = re.search(r'The abbreviations are \*\*([A-Z0-9, ]+)\*\* for the ten '
                      r'lenses in order, and \*\*([A-Z0-9]+)\*\* for W5H1', prose)
    names = [n.split(None, 1)[-1] for n, _ in vocab['lens_rows']]
    vocab['id_prefixes'] = {}
    if named and len(named.group(1).split(', ')) == len(names):
        vocab['id_prefixes'] = dict(zip(names, named.group(1).split(', ')))
        vocab['id_prefixes']['W5H1'] = named.group(2)

    # The literal text of the two lens-output templates: what lies outside
    # their brackets. Text both carry is required of every lens section; text
    # only Output B carries, of a lens that found nothing.
    def literals(label):
        block = re.search(label + r'.*?\n```markdown\n(.*?)```', prompt, re.S)
        if not block:
            return []
        text = re.sub(r'\[[^\]]*\]', '\n', block.group(1))
        return [part.strip() for part in text.split('\n')
                if not part.lstrip().startswith(('#', '|')) and len(part.strip()) > 1]
    found_some, found_none = literals('Output A'), literals('Output B')
    vocab['literals_always'] = [x for x in found_none if x in found_some]
    vocab['literals_nothing_found'] = [x for x in found_none if x not in found_some]

    template = re.search(r'### Scorecard\n\| Metric \| Value \|\n.*?```', prompt, re.S)
    rows = (re.findall(r'^\| ([^|]+?) \| ([^|]*?) \|$', template.group(0), re.M)
            if template else [])
    vocab['scorecard_rows'] = [plain(k) for k, _ in rows if plain(k) != 'Metric']
    # The template's `Lenses run` value, up to its first non-count word:
    # `X of 10 — [...]` reads as `X of 10`.
    run = [v for k, v in rows if plain(k) == 'Lenses run']
    form = re.match(r'(X\D*?\d+)', run[0]) if run else None
    vocab['lenses_run_form'] = form.group(1).replace('X', '{run}', 1) if form else ''

    # The traces: "carries the step's name: A, B, ..., and — where a
    # Low-Confidence finding exists — C. A name mentioned in passing ..."
    traces = re.search(r"carries the step's name: (.*?)\. A name mentioned", prose)
    split = traces and re.match(r'(.*), and — where an? (\w+)-Confidence finding '
                                r'exists — (.*)$', traces.group(1))
    vocab['traces_mandated'] = split.group(1).split(', ') if split else []
    vocab['traces_conditional'] = ([(n, split.group(2)) for n in split.group(3).split(', ')]
                                   if split else [])
    return vocab


def check_spec_agreement(failures):
    """PROMPT.md's prose and its machine-readable spec block say the same thing.

    The scripts read every closed list from the block (issue #51); a reviewer
    reads the prose, where the reasons are. Each is only as good as its
    agreement with the other, so this reads every list out of the prose at
    its defining site and fails the release on any difference — the block
    cannot gain a value the prose does not define, nor the prose one the
    scripts do not enforce. This replaces the gate that held one table of
    trace names, kept in check_review.py, against PROMPT.md by phrase search.

    It also holds the block to the scripts: every Scorecard row the scripts
    derive from the index is a row the block lists, and every lens and W5H1
    has its own ID abbreviation.
    """
    prompt = read('PROMPT.md', failures)
    if prompt is None:
        return
    found = []
    vocab = check_review.normative_vocabulary('PROMPT.md', found)
    lens_rows = check_review.normative_lens_rows('PROMPT.md', found)
    rows = check_review.normative_scorecard_rows('PROMPT.md', found)
    failures.extend(found)
    if found:
        return
    block = dict(vocab, lens_rows=lens_rows, scorecard_rows=rows,
                 config_ranges={k: tuple(v) for k, v in vocab['config_ranges'].items()},
                 lenses_run_form=vocab['lenses_run_form'].replace(
                     str(len(lens_rows)), '{total}', 1),
                 traces_mandated=[n for n, _ in vocab['traces_mandated']],
                 traces_conditional=[(n, w) for n, _, w in vocab['traces_conditional']])
    prose = prose_vocabulary(prompt)
    prose['lenses_run_form'] = prose['lenses_run_form'].replace(
        str(len(prose['lens_rows'])), '{total}', 1)
    for key, site in (
            ('lens_rows', 'the 10 Lenses list'),
            ('id_prefixes', 'the finding ID abbreviations'),
            ('verdicts', 'the Verdict table'),
            ('severities', 'the Severity paragraph'),
            ('confidences', 'the Confidence paragraph'),
            ('tags', 'the inline tag strings'),
            ('config_keys', 'the diffract.yaml key list'),
            ('config_values', 'the diffract.yaml permitted values'),
            ('config_defaults', 'the diffract.yaml default'),
            ('config_ranges', 'the diffract.yaml ranges'),
            ('literals_always', 'the Output A and B templates'),
            ('literals_nothing_found', 'the Output B template'),
            ('scorecard_rows', 'the Scorecard template'),
            ('lenses_run_form', "the Scorecard template's Lenses run value"),
            ('traces_mandated', 'the CHECK trace list'),
            ('traces_conditional', 'the CHECK trace list (conditional)')):
        if prose[key] != block[key]:
            failures.append(
                f'PROMPT.md: the spec block disagrees with {site}: '
                f'block {block[key]!r}, prose {prose[key]!r}')

    for key in sorted(set(check_review.derived_counts([])) - set(rows)):
        failures.append(f'PROMPT.md: check_review.py derives a {key!r} Scorecard row '
                        f'the spec block does not list')
    prefixes = list(vocab['id_prefixes'].values())
    if len(set(prefixes)) != len(prefixes):
        failures.append(f'PROMPT.md: the spec block reuses an ID abbreviation: {prefixes}')
    for key, default in vocab['config_defaults'].items():
        if default not in vocab['config_values'].get(key, []):
            failures.append(f'PROMPT.md: the spec block\'s {key} default {default!r} '
                            f'is not one of its permitted values')


# Files the vocabulary-drift check leaves alone. CHANGELOG.md quotes
# superseded definitions on purpose; the two reviews are hash-pinned and
# quote-checkable, frozen at the instrument version that produced them, and
# never re-synced (CONTRIBUTING.md, Release Gates).
DRIFT_EXEMPT = (
    'CHANGELOG.md',
    os.path.join('examples', 'semver-2.0.0-review.md'),
    os.path.join('calibration', 'semver-2.0.0-seeded-review.md'),
)
CONFIG_EXAMPLE = os.path.join('examples', 'diffract.yaml')


def drift_files():
    """Every Markdown and YAML file outside the exempt set, PROMPT.md included."""
    found = list(md_files()) + sorted(glob.glob('**/*.y*ml', recursive=True))
    return [p for p in found if p not in DRIFT_EXEMPT
            and not any(part in p.split(os.sep) for part in SKIP_DIRS)]


def tag_pattern(tag):
    """A regex for one PROMPT.md tag string, its `<...>` parts as wildcards."""
    parts = re.split(r'<[^>]+>', tag)
    return re.compile('^' + '.+'.join(re.escape(p) for p in parts) + '$')


def check_vocabulary_drift(failures):
    """Every restatement of a closed vocabulary agrees with PROMPT.md.

    PROMPT.md is normative for its verdicts, severities, Confidence bins, tag
    strings, and diffract.yaml keys and values, and other files may point at
    them but not restate them differently. That was checked by eye, and eye
    checking let a README restatement drop a clause in the release that added
    it (issue #39). This gate reads each vocabulary out of PROMPT.md and fails
    any other file whose text uses a value outside it: a verdict-shaped
    string, a tag-shaped string, a slash list of severities or Confidence
    bins, a `key: value` config mention, and the example config's keys,
    values, and `# Options:` blocks. It catches a wrong or missing value, not
    a paraphrase of a definition — that is still a reviewer's job.
    """
    if read('PROMPT.md', failures) is None:
        return
    vocab = check_review.normative_vocabulary('PROMPT.md', failures)
    tags = [tag_pattern(t) for t in vocab['tags']]
    heads = {re.match(r'\[(\w+)', t).group(1) for t in vocab['tags']}
    values = vocab['config_values']
    for path in drift_files():
        text = read(path, failures)
        if text is None:
            continue

        def at(match):
            return f'{path}:{text.count(chr(10), 0, match.start()) + 1}'

        for m in re.finditer(r'\b(?:Skip|Discard):[A-Za-z]+', text):
            if m.group(0) not in vocab['verdicts']:
                failures.append(f'{at(m)}: {m.group(0)!r} is not a PROMPT.md verdict')
        # A tag is a bracketed string whose first word heads a PROMPT.md tag;
        # a Markdown link or reference ([text](url), [text][ref]) is not one.
        for m in re.finditer(r'\[(\w+)\b[^\]\n]*(?:\n[^\]\n]*)?\](?![(\[])', text):
            tag = re.sub(r'\s+', ' ', m.group(0))
            if m.group(1) in heads and not any(t.match(tag) for t in tags):
                failures.append(f'{at(m)}: tag {tag!r} matches no PROMPT.md tag string')
        for key in ('severities', 'confidences'):
            words = '|'.join(vocab[key])
            for m in re.finditer(rf'\b(?:{words})(?:/(?:{words}))+\b', text):
                if m.group(0).split('/') != vocab[key]:
                    failures.append(f'{at(m)}: {m.group(0)!r} is not PROMPT.md\'s '
                                    f'{"/".join(vocab[key])}')
        for m in re.finditer(r'`(\w+): ([^`\s]+)`', text):
            key, value = m.groups()
            if key in values and value not in values[key]:
                failures.append(f'{at(m)}: {key}: {value!r} is not a permitted value '
                                f'({", ".join(values[key])})')
    check_config_example(vocab, failures)


def check_config_example(vocab, failures):
    """examples/diffract.yaml sets only PROMPT.md's keys, to permitted values,
    and each of its `# Options:` comments lists exactly the permitted values
    and marks no default PROMPT.md does not name. The example is the one
    config file a user copies, so a wrong option list in it is a wrong
    config in theirs (found in the 2026-10-05 triage: it named a weaker
    Integrity bar as the default)."""
    text = read(CONFIG_EXAMPLE, failures)
    if text is None:
        return
    lines = text.split('\n')
    options = None
    for number, line in enumerate(lines, 1):
        where = f'{CONFIG_EXAMPLE}:{number}'
        opened = re.match(r'^#\s*Options:(.*)$', line)
        if opened:
            options = (number, [opened.group(1)])
            continue
        if options and re.match(r'^#\s{2,}\S', line):
            options[1].append(line[1:])
            continue
        setting = re.match(r'^(\w+):\s*(.*?)\s*(?:#.*)?$', line)
        if setting:
            key, value = setting.group(1), setting.group(2).strip('"\'')
            if key not in vocab['config_keys']:
                failures.append(f'{where}: {key!r} is not a PROMPT.md config key')
            elif key in vocab['config_values'] and value not in vocab['config_values'][key]:
                failures.append(f'{where}: {key}: {value!r} is not a permitted value')
            elif key in vocab['config_ranges']:
                low, high = vocab['config_ranges'][key]
                if not (value.isdigit() and low <= int(value) <= high):
                    failures.append(f'{where}: {key}: {value!r} is outside {low}–{high}')
            if options:
                check_options(options, key, vocab, failures)
        if not line.startswith('#'):
            options = None


def check_options(options, key, vocab, failures):
    number, block = options
    where = f'{CONFIG_EXAMPLE}:{number}'
    listed, default = [], None
    for part in block:
        part = part.split(' — ')[0]
        for token, note in re.findall(r'([a-z][\w-]*)\s*(\([^)]*\))?', part):
            listed.append(token)
            if 'default' in note:
                default = token
    permitted = vocab['config_values'].get(key)
    if permitted is None:
        failures.append(f'{where}: Options listed for {key!r}, which has no permitted values')
        return
    if listed != permitted:
        failures.append(f'{where}: Options for {key} list {" | ".join(listed)}; '
                        f'PROMPT.md permits {" | ".join(permitted)}')
    if default and default != vocab['config_defaults'].get(key):
        failures.append(f'{where}: marks {default!r} as the {key} default; PROMPT.md '
                        f'names {vocab["config_defaults"].get(key, "none")}')


MANIFEST = os.path.join('scripts', 'MANIFEST')


def script_files():
    """Every file the manifest covers: scripts/ itself, minus the manifest."""
    return sorted(name for name in os.listdir('scripts')
                  if name != 'MANIFEST' and not name.startswith('.')
                  and os.path.isfile(os.path.join('scripts', name)))


def sha256_of(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def write_manifest():
    with open(MANIFEST, 'w') as handle:
        for name in script_files():
            handle.write(f'{sha256_of(os.path.join("scripts", name))}  {name}\n')


def check_manifest(failures):
    """Every script matches its scripts/MANIFEST hash, and the set is complete.

    The scripts carried no version marker, so a blind reviewer handed
    `scripts/` could not say which implementation it reviewed, nor whether the
    checkout it was given was complete (issue #46). The manifest is in
    `sha256sum -c` format, so it can be verified without this script.
    """
    text = read(MANIFEST, failures)
    if text is None:
        return
    listed = {}
    for number, line in enumerate(text.splitlines(), 1):
        m = re.match(r'^([0-9a-f]{64})  (\S+)$', line)
        if not m:
            failures.append(f'{MANIFEST}:{number}: not "<sha256>  <file>": {line!r}')
            continue
        listed[m.group(2)] = m.group(1)
    present = set(script_files())
    for name, digest in sorted(listed.items()):
        if name not in present:
            failures.append(f'{MANIFEST} lists {name}, which is not in scripts/')
        elif sha256_of(os.path.join('scripts', name)) != digest:
            failures.append(f'scripts/{name} does not match its {MANIFEST} hash; '
                            f'regenerate with --write-manifest if the change is intended')
    for name in sorted(present - set(listed)):
        failures.append(f'scripts/{name} is not in {MANIFEST}')


def main():
    if not at_root():
        print('FAIL: run from a Diffract checkout: no PROMPT.md and README.md here')
        return 1
    if sys.argv[1:] == ['--write-manifest']:
        write_manifest()
        print(f'wrote {MANIFEST}')
        return 0
    if sys.argv[1:]:
        print('usage: check.py [--write-manifest]')
        return 2
    # Passed to every check rather than held at module level (issue #47).
    failures = []
    check_versions(failures)
    check_fences(failures)
    check_links(failures)
    check_lens_table(failures)
    check_spec_agreement(failures)
    check_vocabulary_drift(failures)
    check_manifest(failures)
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print('all checks pass')
    return 0


if __name__ == '__main__':
    sys.exit(main())
