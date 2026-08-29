#!/usr/bin/env python3
"""Diffract — Finding Normalizer.

Reads raw linter / scanner output and normalizes it to the unified Diffract
finding schema (see ``schema.json``).  Supports multiple tools; each has a
dedicated parser.

Supported tools:
    deadcode   — Go dead-code detector
    vulture    — Python dead-code detector
    gosec      — Go security scanner (text output)
    bandit     — Python security scanner (text output)
    semgrep    — Multi-language SAST scanner (JSON output with ``--json``)
    jscpd      — Copy-paste detector (JSON report file)
    go-vet     — ``go vet`` diagnostics (text output)

Usage:
    deadcode ./... 2>&1       | python3 scripts/normalize.py --tool deadcode
    vulture src/              | python3 scripts/normalize.py --tool vulture
    semgrep scan --json ./    | python3 scripts/normalize.py --tool semgrep
    cat jscpd-report.json     | python3 scripts/normalize.py --tool jscpd
    gosec -quiet ./...  2>&1  | python3 scripts/normalize.py --tool gosec
    bandit -r src/      2>&1  | python3 scripts/normalize.py --tool bandit
    go vet ./...        2>&1  | python3 scripts/normalize.py --tool go-vet

    # Read from a file instead of stdin:
    python3 scripts/normalize.py --tool semgrep --file results.json

    # Override the lens (defaults to the tool's canonical lens):
    python3 scripts/normalize.py --tool deadcode --lens subtract

    # Pretty-print:
    python3 scripts/normalize.py --tool deadcode --pretty

Exit codes:
    0 — always (output is valid JSON even on parse errors).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, TextIO

# ---------------------------------------------------------------------------
# Canonical lens for each tool
# ---------------------------------------------------------------------------

TOOL_LENS: Dict[str, str] = {
    "deadcode": "subtract",
    "vulture": "subtract",
    "gosec": "shield",
    "bandit": "shield",
    "semgrep": "shield",
    "jscpd": "truth",
    "go-vet": "boundary",
}

# Finding ID prefixes per lens
LENS_PREFIX: Dict[str, str] = {
    "subtract": "S",
    "simplify": "SI",
    "name": "N",
    "truth": "T",
    "boundary": "B",
    "shield": "SH",
    "variety": "V",
    "observability": "O",
    "efficiency": "E",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FindingCollector:
    """Accumulates findings and assigns sequential IDs."""

    def __init__(self, lens: str, tool: str) -> None:
        self.lens = lens
        self.tool = tool
        self.prefix = LENS_PREFIX.get(lens, "F")
        self.counter = 0
        self.findings: List[Dict[str, Any]] = []

    def add(
        self,
        file: str,
        line: int,
        description: str,
        severity: str = "warning",
    ) -> None:
        self.counter += 1
        self.findings.append({
            "lens": self.lens,
            "id": f"{self.prefix}{self.counter}",
            "file": file,
            "line": max(line, 0),
            "description": description,
            "severity": severity,
            "tool": self.tool,
        })

    def result(self) -> Dict[str, Any]:
        return {"findings": self.findings}


def _safe_int(value: Optional[str], default: int = 0) -> int:
    """Parse an integer, returning *default* on failure."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# ---------------------------------------------------------------------------
# Tool parsers
# ---------------------------------------------------------------------------

def parse_deadcode(text: str, collector: FindingCollector) -> None:
    """Parse ``deadcode`` output.

    Formats:
        file.go:42:10: unreachable func Foo
        package: function Foo is unused
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # file:line:col: message
        m = re.match(r"^(.+?):(\d+):\d+:\s+(.+)$", line)
        if m:
            collector.add(m.group(1), int(m.group(2)), m.group(3))
            continue
        # package: message
        m = re.match(r"^(.+?):\s+(.+)$", line)
        if m:
            collector.add(m.group(1), 0, m.group(2), severity="info")


def parse_vulture(text: str, collector: FindingCollector) -> None:
    """Parse ``vulture`` output.

    Format:  file.py:42: unused function 'foo' (60% confidence)
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(.+?):(\d+):\s+(.+)$", line)
        if m:
            collector.add(m.group(1), int(m.group(2)), m.group(3))


def parse_gosec(text: str, collector: FindingCollector) -> None:
    """Parse ``gosec -quiet`` text output.

    Format:  [file.go:42] - G104 (CWE-703): Errors unhandled (Confidence: HIGH)
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\[(.+?):(\d+)\]\s*-\s*(.+)$", line)
        if m:
            desc = m.group(3).strip()
            severity = "error" if "HIGH" in desc else "warning"
            collector.add(m.group(1), int(m.group(2)), desc, severity=severity)


def parse_bandit(text: str, collector: FindingCollector) -> None:
    """Parse ``bandit -r`` text output.

    Bandit emits multi-line blocks::

        >> Issue: [B108:hardcoded_tmp_directory] ...
           Severity: Medium   Confidence: High
           Location: path/file.py:42:0
    """
    current_issue: Optional[str] = None
    current_severity = "warning"

    for line in text.splitlines():
        # Issue line
        m = re.match(r"^>{1,2}\s*Issue:\s*(.+)$", line)
        if m:
            current_issue = m.group(1).strip()
            continue

        # Severity line
        m = re.match(r"^\s*Severity:\s*(\w+)", line)
        if m:
            sev = m.group(1).lower()
            if sev == "high":
                current_severity = "error"
            elif sev == "low":
                current_severity = "info"
            else:
                current_severity = "warning"
            continue

        # Location line
        m = re.match(r"^\s*Location:\s*(.+?):(\d+)", line)
        if m and current_issue:
            collector.add(
                m.group(1), int(m.group(2)),
                current_issue, severity=current_severity,
            )
            current_issue = None
            current_severity = "warning"


def parse_semgrep(text: str, collector: FindingCollector) -> None:
    """Parse ``semgrep --json`` output.

    Expects the JSON object with a ``results`` array.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return

    for result in data.get("results", []):
        path = result.get("path", "")
        start = result.get("start", {})
        line = start.get("line", 0)
        extra = result.get("extra", {})
        message = extra.get("message", result.get("check_id", ""))
        severity_raw = extra.get("severity", "WARNING").upper()
        if severity_raw == "ERROR":
            severity = "error"
        elif severity_raw == "INFO":
            severity = "info"
        else:
            severity = "warning"
        if path and message:
            collector.add(path, line, message, severity=severity)


def parse_jscpd(text: str, collector: FindingCollector) -> None:
    """Parse ``jscpd`` JSON report.

    Expects the JSON object with a ``duplicates`` array.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return

    for dup in data.get("duplicates", []):
        first = dup.get("firstFile", {})
        second = dup.get("secondFile", {})
        f1 = first.get("name", "?")
        f2 = second.get("name", "?")
        s1 = first.get("startLoc", {}).get("line", 0)
        s2 = second.get("startLoc", {}).get("line", 0)
        lines = dup.get("lines", 0)
        desc = f"Duplicated block ({lines} lines) also at {f2}:{s2}"
        collector.add(f1, s1, desc, severity="warning")


def parse_go_vet(text: str, collector: FindingCollector) -> None:
    """Parse ``go vet ./...`` output.

    Format:  file.go:42:10: message
    Also catches import-cycle and internal-package diagnostics.
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # import cycle (no file reference)
        if "import cycle" in line:
            collector.add("go.mod", 0, line, severity="error")
            continue

        # use of internal package
        if "use of internal package" in line:
            m = re.match(r"^(.+?):(\d+)", line)
            if m:
                collector.add(
                    m.group(1), int(m.group(2)),
                    "Internal package boundary violation", severity="error",
                )
            else:
                collector.add("unknown", 0, line, severity="error")
            continue

        # Standard file:line:col: message
        m = re.match(r"^(.+?):(\d+):\d+:\s+(.+)$", line)
        if m:
            collector.add(m.group(1), int(m.group(2)), m.group(3))
            continue

        # file:line: message (no column)
        m = re.match(r"^(.+?):(\d+):\s+(.+)$", line)
        if m:
            collector.add(m.group(1), int(m.group(2)), m.group(3))


# ---------------------------------------------------------------------------
# Parser dispatch
# ---------------------------------------------------------------------------

PARSERS = {
    "deadcode": parse_deadcode,
    "vulture": parse_vulture,
    "gosec": parse_gosec,
    "bandit": parse_bandit,
    "semgrep": parse_semgrep,
    "jscpd": parse_jscpd,
    "go-vet": parse_go_vet,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize raw tool output to the Diffract finding schema.",
    )
    parser.add_argument(
        "--tool", required=True, choices=sorted(PARSERS),
        help="Name of the tool whose output is being normalized.",
    )
    parser.add_argument(
        "--lens",
        help="Override the lens (default: tool's canonical lens).",
    )
    parser.add_argument(
        "--file",
        help="Read input from a file instead of stdin.",
    )
    parser.add_argument(
        "--pretty", action="store_true",
        help="Pretty-print the JSON output.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    lens = args.lens or TOOL_LENS.get(args.tool, "shield")
    collector = FindingCollector(lens=lens, tool=args.tool)

    # Read input
    try:
        if args.file:
            with open(args.file, encoding="utf-8", errors="replace") as f:
                text = f.read()
        else:
            text = sys.stdin.read()
    except OSError as exc:
        # Output empty findings on I/O error — never crash.
        print(json.dumps({"findings": [], "error": str(exc)}))
        sys.exit(0)

    # Parse
    parse_fn = PARSERS.get(args.tool)
    if parse_fn:
        try:
            parse_fn(text, collector)
        except Exception:
            # Swallow parse errors — output whatever we collected so far.
            pass

    # Output
    indent = 2 if args.pretty else None
    json.dump(collector.result(), sys.stdout, indent=indent)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
