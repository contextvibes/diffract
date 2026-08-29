#!/usr/bin/env python3
"""Diffract — Tool Discovery.

Auto-detects available linters, scanners, and analysis tools on the current
system and maps them to Diffract lenses.  Outputs a JSON manifest.

Checks PATH first, then the Nix store (only when /nix/store exists).
Includes version strings where tools support ``--version``.

Exit codes:
    0 — always (output is valid JSON even when no tools are found).

Usage:
    python3 scripts/discover.py            # discover all
    python3 scripts/discover.py --pretty   # pretty-print output
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Lens → tool mapping
# ---------------------------------------------------------------------------
# Each entry: (tool_binary, *extra_names_to_search_in_nix)
# The first element is used as the canonical name.

LENS_TOOLS: Dict[str, List[str]] = {
    "subtract": ["deadcode", "vulture", "ts-prune"],
    "truth": ["jscpd", "simian"],
    "shield": ["semgrep", "gosec", "bandit"],
    "boundary": ["go", "madge"],
    "variety": ["go"],
    "observability": ["errcheck"],
    "efficiency": ["go"],
}

# Display names for tools that are invoked with subcommands.
TOOL_DISPLAY: Dict[str, Dict[str, str]] = {
    "boundary": {"go": "go vet"},
    "variety": {"go": "go vet"},
    "efficiency": {"go": "go test -bench"},
}


# ---------------------------------------------------------------------------
# Resolution helpers
# ---------------------------------------------------------------------------

def _find_in_nix_store(binary: str) -> Optional[str]:
    """Search /nix/store for *binary* if the store exists.

    Returns the absolute path to the first executable match, or ``None``.
    """
    nix_store = Path("/nix/store")
    if not nix_store.is_dir():
        return None
    try:
        result = subprocess.run(
            ["find", str(nix_store), "-maxdepth", "4",
             "-name", binary, "-type", "f", "-perm", "+111"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            candidate = line.strip()
            if candidate:
                return candidate
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


def resolve_binary(name: str) -> Optional[str]:
    """Resolve a tool binary — PATH first, then Nix store."""
    path = shutil.which(name)
    if path:
        return path
    return _find_in_nix_store(name)


def detect_version(binary_path: str, name: str) -> Optional[str]:
    """Try to extract a version string from ``<tool> --version``.

    Returns the first version-like substring, or ``None``.
    """
    try:
        result = subprocess.run(
            [binary_path, "--version"],
            capture_output=True, text=True, timeout=5,
        )
        output = (result.stdout + result.stderr).strip()
        # Grab the first semver-ish token (e.g. "1.23.4", "v0.6.0").
        match = re.search(r"v?(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z0-9_.+-]*))", output)
        if match:
            return match.group(0)
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover() -> Dict[str, Any]:
    """Discover available tools and return a JSON-serialisable manifest.

    Top-level keys are lens names.  Each value is a list of tool-name
    strings (backward-compatible) **or**, when ``--detail`` is passed,
    a list of objects with ``name``, ``path``, and ``version``.
    """
    detailed = "--detail" in sys.argv

    manifest: Dict[str, Any] = {}

    for lens, tools in LENS_TOOLS.items():
        found: List[Any] = []
        seen: set[str] = set()

        for tool_name in tools:
            if tool_name in seen:
                continue
            seen.add(tool_name)

            binary_path = resolve_binary(tool_name)
            if binary_path is None:
                continue

            display = TOOL_DISPLAY.get(lens, {}).get(tool_name, tool_name)

            if detailed:
                version = detect_version(binary_path, tool_name)
                entry: Dict[str, Any] = {
                    "name": display,
                    "path": binary_path,
                }
                if version:
                    entry["version"] = version
                found.append(entry)
            else:
                found.append(display)

        manifest[lens] = found

    return manifest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    pretty = "--pretty" in sys.argv
    try:
        manifest = discover()
    except Exception:
        # Never crash — output empty manifest on unexpected errors.
        manifest = {lens: [] for lens in LENS_TOOLS}

    indent = 2 if pretty else None
    json.dump(manifest, sys.stdout, indent=indent)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
