#!/usr/bin/env bash
# Diffract — Subtract Lens (🗑️)
# Runs dead code detectors against the target path.
# Usage: subtract.sh <path>
# Output: Tab-separated findings, one per line.
#   FINDING	subtract	<id>	<file>	<line>	<description>

set -euo pipefail

TARGET="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COUNTER=0

# Helper: emit a finding
finding() {
  COUNTER=$((COUNTER + 1))
  local id
  id=$(printf "S%d" "$COUNTER")
  printf "FINDING\tsubtract\t%s\t%s\t%s\t%s\n" "$id" "$1" "$2" "$3"
}

# Helper: check if a binary exists (check PATH then Nix store)
resolve_bin() {
  local bin="$1"
  if command -v "$bin" &>/dev/null; then
    command -v "$bin"
    return 0
  fi
  local nix_bin
  nix_bin=$(find /nix/store -maxdepth 4 -name "$bin" -type f -perm +111 2>/dev/null | head -1)
  if [[ -n "${nix_bin:-}" ]]; then
    echo "$nix_bin"
    return 0
  fi
  return 1
}

# Detect project language
detect_language() {
  if [[ -f "$TARGET/go.mod" ]] || ls "$TARGET"/*.go &>/dev/null 2>&1; then
    echo "go"
  elif [[ -f "$TARGET/requirements.txt" ]] || [[ -f "$TARGET/pyproject.toml" ]] || [[ -f "$TARGET/setup.py" ]]; then
    echo "python"
  elif [[ -f "$TARGET/package.json" ]] || [[ -f "$TARGET/tsconfig.json" ]]; then
    echo "typescript"
  else
    echo "unknown"
  fi
}

LANG=$(detect_language)
FOUND_TOOL=false

# Go: deadcode
if [[ "$LANG" == "go" ]]; then
  DEADCODE=$(resolve_bin deadcode 2>/dev/null || true)
  if [[ -n "$DEADCODE" ]]; then
    FOUND_TOOL=true
    while IFS= read -r line; do
      # deadcode output format: <package>: <function> is unused
      # or: <file>:<line>:<col>: unreachable func
      if [[ "$line" =~ ^(.+):([0-9]+):[0-9]+:\ (.+)$ ]]; then
        finding "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "${BASH_REMATCH[3]}"
      elif [[ "$line" =~ ^(.+):\ (.+)$ ]]; then
        finding "${BASH_REMATCH[1]}" "-" "${BASH_REMATCH[2]}"
      fi
    done < <("$DEADCODE" "$TARGET/..." 2>&1 || true)
  fi
fi

# Python: vulture
if [[ "$LANG" == "python" ]]; then
  VULTURE=$(resolve_bin vulture 2>/dev/null || true)
  if [[ -n "$VULTURE" ]]; then
    FOUND_TOOL=true
    while IFS= read -r line; do
      # vulture output: <file>:<line>: unused <type> '<name>' (NN% confidence)
      if [[ "$line" =~ ^(.+):([0-9]+):\ (.+)$ ]]; then
        finding "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "${BASH_REMATCH[3]}"
      fi
    done < <("$VULTURE" "$TARGET" 2>&1 || true)
  fi
fi

# TypeScript/JavaScript: ts-prune
if [[ "$LANG" == "typescript" ]]; then
  TS_PRUNE=$(resolve_bin ts-prune 2>/dev/null || true)
  if [[ -n "$TS_PRUNE" ]]; then
    FOUND_TOOL=true
    while IFS= read -r line; do
      # ts-prune output: <file>:<line> - <export>
      if [[ "$line" =~ ^(.+):([0-9]+)\ -\ (.+)$ ]]; then
        finding "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "Unused export: ${BASH_REMATCH[3]}"
      fi
    done < <(cd "$TARGET" && "$TS_PRUNE" 2>&1 || true)
  fi
fi

if ! $FOUND_TOOL; then
  echo "NO_TOOLS	subtract	No dead code detector found for language: $LANG" >&2
  exit 0
fi

if [[ $COUNTER -eq 0 ]]; then
  echo "CLEAN	subtract	No dead code found"
fi
