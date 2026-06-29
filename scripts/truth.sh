#!/usr/bin/env bash
# Diffract — Truth Lens (📌)
# Detects duplicated knowledge: code, constants, configuration.
# Usage: truth.sh <path>
# Output: Tab-separated findings, one per line.
#   FINDING	truth	<id>	<file>	<line>	<description>

set -euo pipefail

TARGET="${1:-.}"
COUNTER=0

# Helper: emit a finding
finding() {
  COUNTER=$((COUNTER + 1))
  local id
  id=$(printf "T%d" "$COUNTER")
  printf "FINDING\ttruth\t%s\t%s\t%s\t%s\n" "$id" "$1" "$2" "$3"
}

# Helper: resolve binary from PATH or Nix store
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

FOUND_TOOL=false

# jscpd — copy-paste detection (language-agnostic)
JSCPD=$(resolve_bin jscpd 2>/dev/null || true)
if [[ -n "$JSCPD" ]]; then
  FOUND_TOOL=true
  # Run jscpd with JSON reporter, parse output
  TMPDIR=$(mktemp -d)
  trap 'rm -rf "$TMPDIR"' EXIT
  "$JSCPD" "$TARGET" --reporters json --output "$TMPDIR" --min-lines 5 --min-tokens 50 \
    --ignore "**/vendor/**,**/node_modules/**,**/.git/**" 2>/dev/null || true

  if [[ -f "$TMPDIR/jscpd-report.json" ]]; then
    python3 -c "
import json, sys
try:
    with open('$TMPDIR/jscpd-report.json') as f:
        data = json.load(f)
    for dup in data.get('duplicates', []):
        first = dup.get('firstFile', {})
        second = dup.get('secondFile', {})
        f1 = first.get('name', '?')
        f2 = second.get('name', '?')
        s1 = first.get('startLoc', {}).get('line', 0)
        s2 = second.get('startLoc', {}).get('line', 0)
        lines = dup.get('lines', 0)
        print(f'{f1}\t{s1}\tDuplicated block ({lines} lines) also at {f2}:{s2}')
except: pass
" 2>/dev/null | while IFS=$'\t' read -r file line desc; do
      finding "$file" "$line" "$desc"
    done
  fi
fi

# Fallback: grep for duplicated string constants across source files
if ! $FOUND_TOOL; then
  # Find string constants that appear in multiple files
  # This is a rough heuristic — better than nothing when no tool is available
  FOUND_TOOL=true

  # Look for repeated const/define patterns
  if [[ -f "$TARGET/go.mod" ]]; then
    # Go: find constants defined in multiple packages
    grep -rn 'const\s\+\w\+\s*=' "$TARGET" --include="*.go" 2>/dev/null | \
      awk -F'=' '{gsub(/.*const\s+/, "", $1); split($1, a, " "); print a[1]}' | \
      sort | uniq -d | while read -r name; do
        locations=$(grep -rn "const\s\+${name}\s*=" "$TARGET" --include="*.go" 2>/dev/null | head -5)
        if [[ $(echo "$locations" | wc -l) -ge 2 ]]; then
          first_file=$(echo "$locations" | head -1 | cut -d: -f1)
          first_line=$(echo "$locations" | head -1 | cut -d: -f2)
          count=$(echo "$locations" | wc -l | tr -d ' ')
          finding "$first_file" "$first_line" "Constant '$name' defined in $count places"
        fi
      done
  fi
fi

if [[ $COUNTER -eq 0 ]]; then
  echo "CLEAN	truth	No duplicated knowledge found"
fi
