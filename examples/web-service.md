# Example: Web Service Review

> Written against [Diffract v0.4.0](../PROMPT.md).

This is an anonymized example of a full Diffract cycle applied to a
web service (Go) that calls third-party APIs, sends outbound mail,
and renders its pages on the server. Prose is condensed, file
paths are fictionalized, and per-lens "Checked" lines are shortened — but
the findings are complete, so every count reconciles with the
[FINDINGS INDEX](#findings-index) at the end.

## PLAN

Entry checks ran first: `go build ./...`, `go test ./...`, `go vet ./...`
— all pass.

```
Diffract: 0.4.0
🧭 Compass: "Is this code ready to be extracted as a reusable library?"
🐍 Cobra:   Cautious — library-grade bar; skip only where fixing breaks a published contract.
⚖️ Integrity: file:line evidence per lens. Cognitive anchoring required.
```

> **Reviewer:** Do these governors match your intent?
> **User:** Yes — confirmed. Proceed.

## DO

**Cold-Start Calibration** — invariants this system must satisfy,
independent of the code as written:

1. PII never leaves the system except to its owner (not to logs, not to third parties).
2. Every outbound call has a bounded timeout and a defined failure path.
3. A session must expire; nothing authenticated lives forever.

### 🗑️ Subtract
Checked: all registered middleware, exported symbols, struct fields.
| ID | File | Finding | Line | Severity | Confidence |
|---|------|---------|------|----------|------------|
| SUB-1 | internal/web/accesslog.go | Dead access-log middleware — defined but never mounted | 17 | Minor | High |
| SUB-2 | internal/catalog/item.go | Unused `ArchivedTags` struct field — never read or written | 31 | Minor | High |

### ✂️ Simplify
Checked: all function signatures, interface definitions, configuration layers.
A finding would look like: a function doing two things that could be split,
an interface with a single implementation that a concrete type would serve,
or a config layer that only forwards values unchanged.
No findings matching this pattern.

### 🏷️ Name
Checked: package names, exported identifiers, comments against behavior.
| ID | File | Finding | Line | Severity | Confidence |
|---|------|---------|------|----------|------------|
| NAM-1 | internal/forecast/client.go | Comment says "Weather client" but package was renamed to "forecast" | 9 | Minor | High |

### 📌 Truth
Checked: constants, stored fields, and configuration for duplicated knowledge.
| ID | File | Finding | Line | Severity | Confidence |
|---|------|---------|------|----------|------------|
| TRU-1 | internal/catalog/item.go | Price stored both in cents and as a formatted string — single source of truth violated | 15 | Major | High |
| TRU-2 | cmd/api/main.go | Timeout constants duplicated across two binaries (also cmd/jobs/main.go:26) | 38 | Minor | High |

### 🧱 Boundary
Checked: import graph between delivery, domain, and template packages.
| ID | File | Finding | Line | Severity | Confidence |
|---|------|---------|------|----------|------------|
| BOU-1 | internal/mailer/send.go | Mail sender imports domain and template packages — should accept a rendered message | 11 | Major | High |

### 🛡️ Shield
Checked: session handling, logging of request data, public endpoint protections.
| ID | File | Finding | Line | Severity | Confidence |
|---|------|---------|------|----------|------------|
| SHI-1 | internal/web/signup.go | Phone number logged in full when form validation fails | 72 | Major | High |
| SHI-2 | internal/auth/cookie.go | Login cookie has no Max-Age — lives until browser closes | 31 | Major | High |
| SHI-3 | cmd/api/main.go | No rate limiting on public endpoints | 64 | Major | High |

### 🔗 Provenance
Checked: go.mod, go.sum, lockfile integrity, and dependency publication dates.
A finding would look like: a dependency with no go.sum entry, or a module
whose path closely resembles a more popular one (typosquat).
No findings matching this pattern.

### 🎯 Variety
Checked: status-code handling in all upstream clients.
| ID | File | Finding | Line | Severity | Confidence |
|---|------|---------|------|----------|------------|
| VAR-1 | internal/upstream/http.go | No 503 handling in any upstream client — all fall to default branch | 96 | Major | High |

### 🔍 Observability
Checked: error paths, panic handlers, background-job logging.
| ID | File | Finding | Line | Severity | Confidence |
|---|------|---------|------|----------|------------|
| OBS-1 | internal/quota/check.go | Error silently swallowed after refactor — no logging when the quota check fails | 44 | Major | High |
| OBS-2 | internal/web/panic.go | Panic handler catches panics without logging any context | 19 | Major | High |
| OBS-3 | internal/jobs/runner.go | Job log lines carry no run ID — one run's lines cannot be grouped | 52 | Minor | High |

### ⚡ Efficiency
Checked: all HTTP clients, template rendering, JSON encoding.
A finding would look like: an unbounded read of a response body, or a
nested loop producing O(n²) where O(n) is achievable.
No findings matching this pattern.

### W5H1
Checked: Why — rationale for non-obvious constants and fallbacks; When — expiry and timeouts.
| ID | File | Finding | Line | Severity | Confidence |
|----|------|---------|------|----------|------------|
| W5H-1 | cmd/api/main.go | Why: no comment explaining 25s idle timeout | 42 | Minor | Medium |
| W5H-2 | internal/upstream/decode.go | Why: no comment explaining why two date layouts are accepted | 58 | Minor | Medium |

When: login cookie expiry — already raised as SHI-2, not counted again.

## CHECK

| Finding | Confidence | ⚖️ Integrity | 🧭 Compass | 🐍 Cobra | Verdict |
|---------|-----------|-------------|-----------|---------|---------|
| SUB-1: Dead middleware | High | grep confirms zero references | Dead code blocks clean extraction | Removal is safe | Fix |
| SUB-2: Unused field | High | grep confirms never read/written | Same | Removal is safe | Fix |
| NAM-1: Stale comment | High | Read line 9; package name differs | Wrong docs mislead library users | None | Fix |
| TRU-1: Duplicated price | High | Read both fields; values can diverge | Data-integrity risk for consumers | None | Fix |
| TRU-2: Duplicated timeouts | High | Read both binaries; values identical today | In scope | Binaries serve different workloads; values may legitimately diverge — unifying couples them | Skip:Cobra |
| BOU-1: Mail sender boundary | High | Import graph verified | Central to extraction goal | Composition layer contains the change | Fix |
| SHI-1: Phone number in logs | High | Read log call; field named | Violates invariant 1 | None | Fix |
| SHI-2: Cookie no expiry | High | Read cookie construction; no Max-Age | Violates invariant 3 | 12-hour Max-Age is uncontroversial | Fix |
| SHI-3: No rate limiting | High | Confirmed no limiter in serve path | Deployment/edge concern — outside "extractable library" goal | — | Skip:Compass |
| VAR-1: No 503 handling | High | Read switch; 503 hits default | Library consumers need retryable errors | Additive sentinel error | Fix |
| OBS-1: Swallowed error | High | Read call site; err discarded | Violates invariant 2 | None | Fix |
| OBS-2: No context in panic log | High | Read handler; logs message only | Debuggability for consumers | Additive | Fix |
| OBS-3: No job run ID | High | Confirmed no run identifier in the job logger | Traceable jobs expected of a service library | Additive log field | Fix |
| W5H-1: Timeout comment | Medium | Read line; constant uncommented | Rationale must travel with the library | None | Fix |
| W5H-2: Date-layout comment | Medium | Read line; second layout uncommented | Same | None | Fix |

### Scope and Nothing-Found Verification

**Form check:** All ten lens sections are present, in order. The three
nothing-found lenses (Simplify, Provenance, Efficiency) each contain an
*"A finding would look like:"* line. All stated counts were recounted
against the FINDINGS INDEX: 15 rows, matching the Scorecard.

Per lens in scope — would the process have caught a deliberate bug?
(Where a lens has DO-time anchoring, the example differs from it.)

- 🗑️ **Subtract:** an exported helper constant no caller references — the
  exported-symbol sweep reads every declaration, so yes.
- ✂️ **Simplify:** a wrapper type that delegates every method unchanged to
  its embedded field — the interface pass lists each type's method set,
  so yes.
- 🏷️ **Name:** a `MustLoad` function that returns an error instead of
  panicking — the comments-against-behavior pass reads each exported
  function under its name, so yes.
- 📌 **Truth:** the upstream base URL hard-coded in both the client and its
  test fixtures — the constants sweep covers every literal, so yes.
- 🧱 **Boundary:** a template helper importing the store package for
  display data — the import-graph walk covers every package edge, so yes.
- 🛡️ **Shield:** a query parameter passed unvalidated into an outbound
  search request — the endpoint sweep traces each input to its sinks, so yes.
- 🔗 **Provenance:** a `replace` directive in go.mod silently redirecting
  a module to a local path — the go.mod read covers every directive,
  so yes.
- 🎯 **Variety:** an upstream error body whose JSON shape differs by endpoint
  but is decoded by one struct — the client sweep reads every decode
  site, so yes.
- 🔍 **Observability:** a background job that retries and then gives up
  without logging — the error-path sweep reads every goroutine, so yes.
- ⚡ **Efficiency:** a template re-parsed from disk on every request — the
  rendering sweep reads each handler's setup, so yes.

Treated as a prompt to re-look, not proof of cleanliness: the three
nothing-found lenses were each re-skimmed once; no new findings.

**Stockholm & Hammer Audit:** TRU-2 was the closest call — the author's
"different workloads" rationale was accepted, but only after confirming the
binaries genuinely have different latency profiles (Cobra, not empathy).
No framework or dependency was accepted on familiarity alone.

## LEARN

### Fixes Applied

All 13 Fix verdicts applied in one pass — dead code removed (SUB-1, SUB-2),
comment corrected (NAM-1), formatted price derived from cents (TRU-1),
composition layer created so the mail sender accepts a rendered message
(BOU-1), phone number masked in logs (SHI-1), 12-hour Max-Age added (SHI-2),
retryable sentinel error added to all 3 upstream clients (VAR-1), error
logged (OBS-1), method and path added to panic logging (OBS-2), run ID added
to job log lines (OBS-3), rationale comments added (W5H-1, W5H-2).

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

Counts below are derived from the [FINDINGS INDEX](#findings-index).

| Metric | Value |
|--------|-------|
| Reviewer | anonymized (AI reviewer; configuration withheld with the project details) |
| Artifact | anonymized web service repository (identifying details withheld; no public hash) |
| Instrument | Diffract 0.4.0 |
| Governors | 🧭 "Is this code ready to be extracted as a reusable library?" · 🐍 Library/Framework · ⚖️ file:line + anchoring |
| Entry checks | `go build ./...`, `go test ./...`, `go vet ./...` — all pass |
| Findings raised | 15 |
| Major findings raised | 8 |
| Fix verdicts | 13 |
| Fixes applied | 13 |
| Cobra-skipped | 1 |
| Compass-skipped | 1 |
| Integrity-discarded | 0 |
| PDCA cycles run | 2 — converged: yes |
| Lenses run | 10 of 10 — none omitted |
| W5H1 run | yes |
| Most productive lens | 🔍 Observability and 🛡️ Shield (3 findings each) |
| Estimated remaining Majors | ≈1 — basis: historical per-lens yield (Observability has yielded one further Major on re-review in comparable services) |
| Calibration | not tested |
| Tags | none |

### Gap Analysis

| Gap | Reason | Recommendation |
|-----|--------|---------------|
| Upstream API behavior under real 503s | No sandbox access — VAR-1 verified against recorded fixtures only | Add contract tests before extraction |
| Page templates | Declared sample: 4 of 14 templates reviewed | Review the remaining 10 before extraction |
| Load characteristics | No profiling data available to the reviewer | Profile under production-shaped load; re-run ⚡ Efficiency with the data |

### Defect Prevention

| Major(s) | Upstream cause | Process change |
|----------|----------------|----------------|
| OBS-1, OBS-2 | Errors dropped during a refactor; no lint gate on discarded errors | Add `errcheck` to CI |
| SHI-1, SHI-2, SHI-3 | No secure-defaults checklist when scaffolding the service | Add session-expiry, log-field-allowlist, and rate-limit items to the service template |
| TRU-1, BOU-1, VAR-1 | Structure grew ad hoc; no design note stating the single-source and boundary rules | One-page package-boundary note in the repo, checked at PR review |

## FINDINGS INDEX

| ID | Lens | Cycle | Line(s) | Severity | Verdict | Claim (one sentence) | Confidence |
|----|------|-------|---------|----------|---------|----------------------|------------|
| SUB-1 | 🗑️ Subtract | 1 | accesslog.go:17 | Minor | Fix | Access-log middleware is defined but never mounted. | High |
| SUB-2 | 🗑️ Subtract | 1 | item.go:31 | Minor | Fix | `ArchivedTags` is never read or written. | High |
| NAM-1 | 🏷️ Name | 1 | client.go:9 | Minor | Fix | Comment names the old "Weather client" package. | High |
| TRU-1 | 📌 Truth | 1 | item.go:15 | Major | Fix | Price is stored twice, as cents and as a formatted string. | High |
| TRU-2 | 📌 Truth | 1 | main.go:38 | Minor | Skip:Cobra | Timeout constants are duplicated across two binaries. | High |
| BOU-1 | 🧱 Boundary | 1 | send.go:11 | Major | Fix | Mail sender imports domain and template packages. | High |
| SHI-1 | 🛡️ Shield | 1 | signup.go:72 | Major | Fix | A failed signup logs the phone number in full. | High |
| SHI-2 | 🛡️ Shield | 1 | cookie.go:31 | Major | Fix | Login cookie is set without expiry. | High |
| SHI-3 | 🛡️ Shield | 1 | main.go:64 | Major | Skip:Compass | Public endpoints have no rate limiting. | High |
| VAR-1 | 🎯 Variety | 1 | http.go:96 | Major | Fix | 503 responses fall to the default branch in every upstream client. | High |
| OBS-1 | 🔍 Observability | 1 | check.go:44 | Major | Fix | A quota-check failure is discarded without logging. | High |
| OBS-2 | 🔍 Observability | 1 | panic.go:19 | Major | Fix | Panic handler logs no request context. | High |
| OBS-3 | 🔍 Observability | 1 | runner.go:52 | Minor | Fix | Job log lines carry no run ID. | High |
| W5H-1 | W5H1 | 1 | main.go:42 | Minor | Fix | The 25s idle timeout has no stated rationale. | Medium |
| W5H-2 | W5H1 | 1 | decode.go:58 | Minor | Fix | Accepting a second date layout has no stated rationale. | Medium |
