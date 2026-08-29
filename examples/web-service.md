# Example: Web Service Review

> Written against [Diffract v0.2.4](../PROMPT.md).

This is an anonymized example of a full Diffract cycle applied to a
production web service (Go) with vendor API integrations, email
notifications, and a server-rendered frontend. Prose is condensed, file
paths are fictionalized, and per-lens "Checked" lines are shortened — but
the findings are complete, so every count reconciles with the
[FINDINGS INDEX](#findings-index) at the end.

## PLAN

Entry checks ran first: `go build ./...`, `go test ./...`, `go vet ./...`
— all pass.

```
Diffract: 0.2.4
🧭 Compass: "Is this code ready to be extracted as a reusable library?"
🐍 Cobra:   Cautious — library-grade bar; skip only where fixing breaks a published contract.
⚖️ Integrity: file:line evidence per lens. Cognitive anchoring required.
```

> **Reviewer:** Do these governors match your intent?
> **User:** Yes — confirmed. Proceed.

## DO

**Cold-Start Calibration** — invariants this system must satisfy,
independent of the code as written:

1. PII never leaves the system except to its owner (not to logs, not to vendors).
2. Every outbound call has a bounded timeout and a defined failure path.
3. A session must expire; nothing authenticated lives forever.

### 🗑️ Subtract
Checked: all registered middleware, exported symbols, struct fields.
| # | File | Finding | Line | Severity |
|---|------|---------|------|----------|
| S1 | internal/httpserver/middleware.go | Dead logging middleware — defined but never mounted | 41 | Minor |
| S2 | internal/store/entity.go | Unused `OtherDetails` struct field — never read or written | 27 | Minor |

### ✂️ Simplify
Checked: all function signatures, interface definitions, configuration layers.
A finding would look like: a function doing two things that could be split,
an interface with a single implementation that a concrete type would serve,
or a config layer that only forwards values unchanged.
No findings matching this pattern.

### 🏷️ Name
Checked: package names, exported identifiers, comments against behavior.
| # | File | Finding | Line | Severity |
|---|------|---------|------|----------|
| N1 | internal/geocoder/client.go | Comment says "Maps client" but package was renamed to "geocoder" | 12 | Minor |

### 📌 Truth
Checked: constants, IDs, and configuration for duplicated knowledge.
| # | File | Finding | Line | Severity |
|---|------|---------|------|----------|
| T1 | internal/store/entity.go | Entity ID field duplicates the map key — single source of truth violated | 19 | Major |
| T2 | cmd/server/main.go | Timeout constants duplicated across two binaries (also cmd/worker/main.go:29) | 33 | Minor |

### 🧱 Boundary
Checked: import graph between delivery, domain, and template packages.
| # | File | Finding | Line | Severity |
|---|------|---------|------|----------|
| B1 | internal/email/client.go | Email delivery client imports domain and template packages — should accept raw HTML | 8 | Major |

### 🛡️ Shield
Checked: session handling, logging of request data, public endpoint protections.
| # | File | Finding | Line | Severity |
|---|------|---------|------|----------|
| H1 | internal/httpserver/handlers.go | PII (name, email) logged in structured output | 88 | Major |
| H2 | internal/session/session.go | Session cookie has no expiry — lives until browser closes | 54 | Major |
| H3 | cmd/server/main.go | No rate limiting on public endpoints | 61 | Major |

### 🔗 Provenance
Checked: go.mod, go.sum, lockfile integrity, and dependency publication dates.
A finding would look like: a dependency with no go.sum entry, or a module
whose path closely resembles a more popular one (typosquat).
No findings matching this pattern.

### 🎯 Variety
Checked: status-code handling in all vendor clients.
| # | File | Finding | Line | Severity |
|---|------|---------|------|----------|
| V1 | internal/vendors/client.go | No 503 handling in any vendor client — all fall to default branch | 102 | Major |

### 🔍 Observability
Checked: error paths, recovery handlers, request tracing.
| # | File | Finding | Line | Severity |
|---|------|---------|------|----------|
| O1 | internal/license/lookup.go | Error silently swallowed after refactor — no logging on license lookup failure | 47 | Major |
| O2 | internal/httpserver/recover.go | Recovery handler catches panics without logging any context | 22 | Major |
| O3 | internal/httpserver/server.go | No correlation IDs for request tracing | 30 | Minor |

### ⚡ Efficiency
Checked: all HTTP clients, template rendering, JSON encoding.
A finding would look like: an unbounded read of a response body, or a
nested loop producing O(n²) where O(n) is achievable.
No findings matching this pattern.

### W5H1
| Q | # | File | Finding | Line | Severity |
|---|---|------|---------|------|----------|
| Why | W1 | cmd/server/main.go | No comment explaining 35s write timeout | 35 | Minor |
| Why | W2 | internal/vendors/parse.go | No comment explaining backward-compat field name fallback | 74 | Minor |
| When | — | — | Session cookie expiry — already raised as H2, not counted again | — | — |

## CHECK

| Finding | ⚖️ Integrity | 🧭 Compass | 🐍 Cobra | Verdict |
|---------|-------------|-----------|---------|---------|
| S1: Dead middleware | grep confirms zero references | Dead code blocks clean extraction | Removal is safe | Fix |
| S2: Unused field | grep confirms never read/written | Same | Removal is safe | Fix |
| N1: Stale comment | Read line 12; package name differs | Wrong docs mislead library users | None | Fix |
| T1: Duplicated ID | Read both sites; values can diverge | Data-integrity risk for consumers | None | Fix |
| T2: Duplicated timeouts | Read both binaries; values identical today | In scope | Binaries serve different workloads; values may legitimately diverge — unifying couples them | Skip:Cobra |
| B1: Email client boundary | Import graph verified | Central to extraction goal | Composition layer contains the change | Fix |
| H1: PII in logs | Read log call; fields named | Violates invariant 1 | None | Fix |
| H2: Cookie no expiry | Read cookie construction; no MaxAge | Violates invariant 3 | 4-hour MaxAge is uncontroversial | Fix |
| H3: No rate limiting | Confirmed no limiter in serve path | Deployment/edge concern — outside "extractable library" goal | — | Skip:Compass |
| V1: No 503 handling | Read switch; 503 hits default | Library consumers need retryable errors | Additive sentinel error | Fix |
| O1: Swallowed error | Read call site; err discarded | Violates invariant 2 | None | Fix |
| O2: No context in recovery | Read handler; logs message only | Debuggability for consumers | Additive | Fix |
| O3: No correlation ID | Confirmed no request ID anywhere | Tracing expected of a service library | Additive middleware | Fix |
| W1: Timeout comment | Read line; constant uncommented | Rationale must travel with the library | None | Fix |
| W2: Fallback comment | Read line; fallback uncommented | Same | None | Fix |

### Nothing-Found Verification

**Form check:** All ten lens sections are present, in order. The three
nothing-found lenses (Simplify, Provenance, Efficiency) each contain an
*"A finding would look like:"* line. All stated counts were recounted
against the FINDINGS INDEX: 15 rows, matching the Scorecard.

Per nothing-found lens — would the process have caught a deliberate bug?

- ✂️ **Simplify:** a handler that both validates and persists in one
  function — the signature pass walks every function body's
  responsibilities, so yes.
- 🔗 **Provenance:** a go.mod entry pointing at a fork with no go.sum
  pin — the lockfile diff would flag the missing entry, so yes.
- ⚡ **Efficiency:** an `io.ReadAll` on a vendor response with no
  `http.MaxBytesReader` — the client sweep checks every body read, so yes.

Treated as a prompt to re-look, not proof of cleanliness: each of the three
lenses was re-skimmed once; no new findings.

**Stockholm & Hammer Audit:** T2 was the closest call — the author's
"different workloads" rationale was accepted, but only after confirming the
binaries genuinely have different latency profiles (Cobra, not empathy).
No framework or dependency was accepted on familiarity alone.

## LEARN

### Fixes Applied

All 13 Fix verdicts applied in one pass — dead code removed (S1, S2),
comment corrected (N1), ID derived from map key (T1), composition layer
created so the delivery client accepts raw HTML (B1), PII fields dropped
from logs (H1), 4-hour MaxAge added (H2), retryable sentinel error added
to all 3 vendor clients (V1), error logged (O1), method/path/request ID
added to recovery logging (O2), request ID middleware added (O3),
rationale comments added (W1, W2).

**Verification:** `go build ./...`, `go test ./...`, `go vet ./...` — all
pass after fixes.

**Convergence:** cycle 2 re-ran PLAN → DO → CHECK against the fixed
artifact and produced zero new Fix outcomes.

### Patterns Observed

1. 🔍 **Observability is the most commonly missed** — silent failures are
   invisible to tests and linters
2. 🗑️ **Subtract is the most productive for cheap wins** — dead code is
   always a real finding
3. **Compass calibration is the most powerful lever** — same code reviewed
   as "prototype" vs "library" produced different outcomes
4. **Fixing during analysis breaks the cycle** — collect all, then fix all
5. **W5H1 uniquely catches "Why" and "When"** — no lens asks these

### Scorecard

Counts below are derived from the [FINDINGS INDEX](#findings-index);
"Total" and "Major" count findings **raised**.

| Metric | Value |
|--------|-------|
| Total findings | 15 |
| Major findings | 8 |
| Fixed | 13 |
| Cobra-skipped | 1 |
| Compass-skipped | 1 |
| Integrity-discarded | 0 |
| PDCA cycles to converge | 2 |
| Most productive lens | 🔍 Observability (3 findings) |
| Estimated remaining Majors | ≈1 — basis: historical per-lens yield (Observability has yielded one further Major on re-review in comparable services) |
| Calibration | not tested |

### Gap Analysis

| Gap | Reason | Recommendation |
|-----|--------|---------------|
| Vendor API behavior under real 503s | No sandbox access — V1 verified against recorded fixtures only | Add contract tests before extraction |
| Frontend templates | Declared sample: 3 of 11 templates reviewed | Review the remaining 8 before extraction |
| Load characteristics | No profiling data available to the reviewer | Profile under production-shaped load; re-run ⚡ Efficiency with the data |

### Defect Prevention

| Major(s) | Upstream cause | Process change |
|----------|----------------|----------------|
| O1, O2 | Errors dropped during a refactor; no lint gate on discarded errors | Add `errcheck` to CI |
| H1, H2, H3 | No secure-defaults checklist when scaffolding the service | Add session-expiry, log-field-allowlist, and rate-limit items to the service template |
| T1, B1, V1 | Structure grew ad hoc; no design note stating the single-source and boundary rules | One-page package-boundary note in the repo, checked at PR review |

## FINDINGS INDEX

| ID | Lens | Line(s) | Severity | Verdict | Claim (one sentence) | Confidence |
|----|------|---------|----------|---------|----------------------|------------|
| S1 | 🗑️ Subtract | middleware.go:41 | Minor | Fix | Logging middleware is defined but never mounted. | High |
| S2 | 🗑️ Subtract | entity.go:27 | Minor | Fix | `OtherDetails` is never read or written. | High |
| N1 | 🏷️ Name | client.go:12 | Minor | Fix | Comment names the old "Maps client" package. | High |
| T1 | 📌 Truth | entity.go:19 | Major | Fix | Entity ID duplicates the map key. | High |
| T2 | 📌 Truth | main.go:33 | Minor | Skip:Cobra | Timeout constants are duplicated across two binaries. | High |
| B1 | 🧱 Boundary | client.go:8 | Major | Fix | Delivery client imports domain and template packages. | High |
| H1 | 🛡️ Shield | handlers.go:88 | Major | Fix | Name and email are written to structured logs. | High |
| H2 | 🛡️ Shield | session.go:54 | Major | Fix | Session cookie is set without expiry. | High |
| H3 | 🛡️ Shield | main.go:61 | Major | Skip:Compass | Public endpoints have no rate limiting. | High |
| V1 | 🎯 Variety | client.go:102 | Major | Fix | 503 responses fall to the default branch in every vendor client. | High |
| O1 | 🔍 Observability | lookup.go:47 | Major | Fix | License lookup failure is discarded without logging. | High |
| O2 | 🔍 Observability | recover.go:22 | Major | Fix | Recovery handler logs no request context. | High |
| O3 | 🔍 Observability | server.go:30 | Minor | Fix | Requests carry no correlation ID. | High |
| W1 | W5H1 | main.go:35 | Minor | Fix | The 35s write timeout has no stated rationale. | Medium |
| W2 | W5H1 | parse.go:74 | Minor | Fix | The field-name fallback has no stated rationale. | Medium |
