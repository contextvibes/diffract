#!/usr/bin/env bash
# Diffract — Shield Lens (🛡️)
# Runs security scanners against the target path.
# Usage: shield.sh <path>
# Output: Tab-separated findings, one per line.
#   FINDING	shield	<id>	<file>	<line>	<description>

set -euo pipefail

TARGET="${1:-.}"
COUNTER=0

# Helper: emit a finding
finding() {
  COUNTER=$((COUNTER + 1))
  local id
  id=$(printf "H%d" "$COUNTER")
  printf "FINDING\tshield\t%s\t%s\t%s\t%s\n" "$id" "$1" "$2" "$3"
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

# semgrep (language-agnostic)
SEMGREP=$(resolve_bin semgrep 2>/dev/null || true)
if [[ -n "$SEMGREP" ]]; then
  FOUND_TOOL=true
  while IFS= read -r line; do
    # Parse semgrep JSON output
    local file check_id message sline
    file=$(echo "$line" | grep -o '"path":"[^"]*"' | head -1 | cut -d'"' -f4)
    sline=$(echo "$line" | grep -o '"start":{"line":[0-9]*' | head -1 | grep -o '[0-9]*$')
    message=$(echo "$line" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [[ -n "${file:-}" ]] && [[ -n "${message:-}" ]]; then
      finding "$file" "${sline:-0}" "$message"
    fi
  done < <("$SEMGREP" scan --config auto --json "$TARGET" 2>/dev/null | \
    python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for r in data.get('results', []):
        print(json.dumps({
            'path': r.get('path', ''),
            'start': r.get('start', {}),
            'message': r.get('extra', {}).get('message', '')
        }))
except: pass
" 2>/dev/null || true)
fi

# gosec (Go-specific)
GOSEC=$(resolve_bin gosec 2>/dev/null || true)
if [[ -n "$GOSEC" ]] && [[ -f "$TARGET/go.mod" ]]; then
  FOUND_TOOL=true
  while IFS= read -r line; do
    # gosec text output: [<file>:<line>] - <rule> (CWE-NNN): <description> (Confidence: ...)
    if [[ "$line" =~ ^\[(.+):([0-9]+)\]\ -\ (.+)$ ]]; then
      finding "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "${BASH_REMATCH[3]}"
    fi
  done < <("$GOSEC" -quiet "$TARGET/..." 2>&1 || true)
fi

# bandit (Python-specific)
BANDIT=$(resolve_bin bandit 2>/dev/null || true)
if [[ -n "$BANDIT" ]] && { [[ -f "$TARGET/requirements.txt" ]] || [[ -f "$TARGET/pyproject.toml" ]]; }; then
  FOUND_TOOL=true
  while IFS= read -r line; do
    # bandit output: >> Issue: [<id>:<severity>] <message>
    #                    Location: <file>:<line>:<col>
    if [[ "$line" =~ ^>\>\ Issue:\ (.+)$ ]]; then
      local issue="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]+Location:\ (.+):([0-9]+) ]] && [[ -n "${issue:-}" ]]; then
      finding "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "$issue"
      unset issue
    fi
  done < <("$BANDIT" -r "$TARGET" 2>&1 || true)
fi

if ! $FOUND_TOOL; then
  echo "NO_TOOLS	shield	No security scanner found" >&2
  exit 0
fi

if [[ $COUNTER -eq 0 ]]; then
  echo "CLEAN	shield	No security findings"
fi
