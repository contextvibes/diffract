# Example: Web Service Review

This is an anonymized example of a full Diffract cycle applied to a
production web service with vendor API integrations, email notifications,
and a server-rendered frontend.

## PLAN

```
🧭 Compass: "Is this code ready to be extracted as a reusable library?"
🐍 Cobra:   Cautious — library-grade bar.
⚖️ Integrity: file:line evidence per lens. Cognitive anchoring required.
```

## DO — Selected Findings

### 🗑️ Subtract
| # | Finding |
|---|---------|
| S1 | Dead logging middleware — defined but never used |
| S2 | Unused `OtherDetails` struct field — never read or written |

### 🏷️ Name
| # | Finding |
|---|---------|
| N1 | Comment says "Maps client" but package was renamed to "geocoder" |

### 📌 Truth
| # | Finding |
|---|---------|
| T1 | Entity ID field duplicates the map key — single source of truth violated |
| T2 | Timeout constants duplicated across two binaries |

### 🧱 Boundary
| # | Finding |
|---|---------|
| B1 | Email delivery client imports domain and template packages — should accept raw HTML |

### 🛡️ Shield
| # | Finding |
|---|---------|
| H1 | PII (name, email) logged in structured output |
| H2 | Session cookie has no expiry — lives until browser closes |

### 🎯 Variety
| # | Finding |
|---|---------|
| V1 | No 503 handling in any vendor client — all fall to default branch |

### 🔍 Observability
| # | Finding |
|---|---------|
| O1 | Error silently swallowed after refactor — no logging on license lookup failure |
| O2 | Recovery handler catches exceptions without logging any context |
| O3 | No correlation IDs for request tracing |

### ✂️ Simplify
Checked: all function signatures, class hierarchies, configuration layers.
A finding would look like: a function doing two things that could be split,
or a class hierarchy 5 levels deep where 2 suffice.
No findings matching this pattern.

### ⚡ Efficiency
Checked: all HTTP clients, template rendering, JSON encoding.
A finding would look like: an unbounded read of a response body, or a
nested loop producing O(n²) where O(n) is achievable.
No findings matching this pattern.

### W5H1
| Q | Finding |
|---|---------|
| Why | No comment explaining 35s write timeout |
| Why | No comment explaining backward-compat field name fallback |
| When | Session cookie expiry (same as H2) |

## CHECK

| Finding | Verdict |
|---------|---------|
| S1 Dead middleware | ✅ Fix |
| S2 Unused field | ✅ Fix |
| N1 Stale comment | ✅ Fix |
| T1 Duplicated ID | ✅ Fix |
| T2 Duplicated timeouts | 🐍 Skip — binaries serve different workloads, values may diverge |
| B1 Email client boundary | ✅ Fix — created composition layer, made delivery client pure |
| H1 PII in logs | ✅ Fix |
| H2 Cookie no expiry | ✅ Fix — added 4-hour MaxAge |
| V1 No 503 handling | ✅ Fix — added retryable sentinel error to all 3 clients |
| O1 Swallowed error | ✅ Fix |
| O2 No context in recovery | ✅ Fix — added method, path, request ID |
| O3 No correlation ID | ✅ Fix — added request ID middleware |
| W1 Timeout comment | ✅ Fix — added "accounts for upstream vendor latency" |
| W2 Fallback comment | ✅ Fix — added "backward compat with legacy systems" |

## LEARN

### Patterns Observed

1. 🔍 **Observability is the most commonly missed** — silent failures are
   invisible to tests and linters
2. 🗑️ **Subtract is the most productive** — dead code is always a real finding
3. **Compass calibration is the most powerful lever** — same code reviewed
   as "prototype" vs "library" produced different outcomes
4. **Fixing during analysis breaks the cycle** — collect all, then fix all
5. **W5H1 uniquely catches "Why" and "When"** — no lens asks these

### Scorecard

| Metric | Value |
|--------|-------|
| Total findings | 15 |
| Fixed | 13 |
| Cobra-skipped | 1 |
| Compass-skipped | 1 |
| Integrity-discarded | 0 |
| PDCA cycles to converge | 3 |
| Most productive lens | 🔍 Observability (3 findings) |
| Calibration | not tested |

