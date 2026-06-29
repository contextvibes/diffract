#!/usr/bin/env bash
# Diffract — Tool Discovery
# Detects available linters/scanners and maps them to Diffract lenses.
# Output: JSON manifest of available tools per lens.

set -euo pipefail

# Helper: check if a binary exists
has() { command -v "$1" &>/dev/null; }

# Helper: find binary in Nix store if not in PATH
nix_find() {
  local bin="$1"
  if has "$bin"; then
    echo "$bin"
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

# Collect tools per lens
subtract_tools=()
truth_tools=()
shield_tools=()
boundary_tools=()
variety_tools=()
observability_tools=()
efficiency_tools=()

# 🗑️ Subtract — dead code detectors
nix_find deadcode &>/dev/null && subtract_tools+=("deadcode")
nix_find vulture &>/dev/null && subtract_tools+=("vulture")
nix_find ts-prune &>/dev/null && subtract_tools+=("ts-prune")

# 📌 Truth — duplication detectors
nix_find jscpd &>/dev/null && truth_tools+=("jscpd")
nix_find simian &>/dev/null && truth_tools+=("simian")

# 🛡️ Shield — security scanners
nix_find semgrep &>/dev/null && shield_tools+=("semgrep")
nix_find gosec &>/dev/null && shield_tools+=("gosec")
nix_find bandit &>/dev/null && shield_tools+=("bandit")

# 🧱 Boundary — dependency analysis
has "go" && boundary_tools+=("go vet")
nix_find madge &>/dev/null && boundary_tools+=("madge")

# 🎯 Variety — exhaustiveness
has "go" && variety_tools+=("go vet")

# 🔍 Observability — error handling linters
nix_find errcheck &>/dev/null && observability_tools+=("errcheck")

# ⚡ Efficiency — profilers, benchmarks
has "go" && efficiency_tools+=("go test -bench")

# Output JSON
to_json_array() {
  local arr=("$@")
  if [[ ${#arr[@]} -eq 0 ]]; then
    echo "[]"
    return
  fi
  local json="["
  local first=true
  for item in "${arr[@]}"; do
    if $first; then
      first=false
    else
      json+=","
    fi
    json+="\"$item\""
  done
  json+="]"
  echo "$json"
}

cat <<EOF
{
  "subtract": $(to_json_array "${subtract_tools[@]+"${subtract_tools[@]}"}"),
  "truth": $(to_json_array "${truth_tools[@]+"${truth_tools[@]}"}"),
  "shield": $(to_json_array "${shield_tools[@]+"${shield_tools[@]}"}"),
  "boundary": $(to_json_array "${boundary_tools[@]+"${boundary_tools[@]}"}"),
  "variety": $(to_json_array "${variety_tools[@]+"${variety_tools[@]}"}"),
  "observability": $(to_json_array "${observability_tools[@]+"${observability_tools[@]}"}"),
  "efficiency": $(to_json_array "${efficiency_tools[@]+"${efficiency_tools[@]}"}")
}
EOF
