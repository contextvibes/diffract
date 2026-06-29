#!/usr/bin/env bash
# Diffract — Boundary Lens (🧱)
# Detects boundary violations: import cycles, tight coupling, misplaced deps.
# Usage: boundary.sh <path>
# Output: Tab-separated findings, one per line.
#   FINDING	boundary	<id>	<file>	<line>	<description>

set -euo pipefail

TARGET="${1:-.}"
COUNTER=0

# Helper: emit a finding
finding() {
  COUNTER=$((COUNTER + 1))
  local id
  id=$(printf "B%d" "$COUNTER")
  printf "FINDING\tboundary\t%s\t%s\t%s\t%s\n" "$id" "$1" "$2" "$3"
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

# Go: import cycle detection via go vet
if [[ -f "$TARGET/go.mod" ]] && command -v go &>/dev/null; then
  FOUND_TOOL=true

  # Check for import cycles
  while IFS= read -r line; do
    if [[ "$line" =~ import\ cycle ]]; then
      finding "go.mod" "-" "$line"
    fi
  done < <(cd "$TARGET" && go vet ./... 2>&1 || true)

  # Check for internal package boundary violations
  # (packages importing another package's internal/ directory)
  while IFS= read -r line; do
    if [[ "$line" =~ use\ of\ internal\ package ]]; then
      file=$(echo "$line" | cut -d: -f1)
      lineno=$(echo "$line" | cut -d: -f2)
      finding "$file" "$lineno" "Internal package boundary violation"
    fi
  done < <(cd "$TARGET" && go build ./... 2>&1 || true)
fi

# JavaScript/TypeScript: madge for circular dependencies
MADGE=$(resolve_bin madge 2>/dev/null || true)
if [[ -n "$MADGE" ]] && { [[ -f "$TARGET/package.json" ]] || [[ -f "$TARGET/tsconfig.json" ]]; }; then
  FOUND_TOOL=true
  while IFS= read -r line; do
    # madge --circular output: file.ts → dep.ts → file.ts
    if [[ -n "$line" ]] && [[ "$line" != "No circular"* ]]; then
      first_file=$(echo "$line" | cut -d' ' -f1)
      finding "$first_file" "-" "Circular dependency: $line"
    fi
  done < <("$MADGE" --circular "$TARGET" 2>&1 || true)
fi

# Fallback: basic import analysis for any language
if ! $FOUND_TOOL; then
  FOUND_TOOL=true

  # Python: look for circular imports (rough heuristic)
  if [[ -f "$TARGET/requirements.txt" ]] || [[ -f "$TARGET/pyproject.toml" ]]; then
    # Find files that import each other
    find "$TARGET" -name "*.py" -not -path "*/venv/*" -not -path "*/.venv/*" 2>/dev/null | while read -r pyfile; do
      module=$(basename "$pyfile" .py)
      dir=$(dirname "$pyfile")
      # Check if this module imports something that imports it back
      grep -l "import.*${module}" "$dir"/*.py 2>/dev/null | while read -r importer; do
        imp_module=$(basename "$importer" .py)
        if grep -q "import.*${imp_module}" "$pyfile" 2>/dev/null; then
          finding "$pyfile" "-" "Potential circular import with $(basename "$importer")"
        fi
      done
    done
  fi
fi

if [[ $COUNTER -eq 0 ]]; then
  echo "CLEAN	boundary	No boundary violations found"
fi
