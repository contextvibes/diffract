# The 9 Lenses

Each lens is grounded in a first principle from a domain **outside** software
engineering. This grounding ensures the lenses are universal — they apply to
any programming language, paradigm, or architecture style.

## Ordering Rationale

The lenses are ordered from most destructive to most constructive:

1-2: **Remove/reduce** before examining what remains
3-4: **Clarity** — is what remains well-named and non-duplicated?
5-6: **Structure** — are the walls right and defended?
7-8: **Completeness** — does it handle all states and report them?
9: **Performance** — is it proportional?

---

## 1. 🗑️ Subtract

**Root domain:** Philosophy — Via Negativa (Nassim Nicholas Taleb)
**The question:** *Can I remove this entirely?*

The most productive lens. Dead code, unused fields, unnecessary abstractions,
vestigial features — all are real findings that are never Cobra-skipped.
Subtraction improves the system by reducing the surface area for bugs.

**Evidence format:**
```
### 🗑️ Subtract
Checked: all modules, all exported types, all configuration fields
| # | File | Finding | Line |
|---|------|---------|------|
| S1 | user_service.py | `OtherDetails` field is never read or written | 34 |
```

**Maps to:** YAGNI (Kent Beck, Extreme Programming)

---

## 2. ✂️ Simplify

**Root domain:** Philosophy — Occam's Razor
**The question:** *Can this be simpler without losing capability?*

Complexity that serves no purpose is entropy. This lens catches over-abstraction,
unnecessary indirection, and cleverness masquerading as elegance.

**Evidence format:**
```
### ✂️ Simplify
Checked: all function signatures, class hierarchies, configuration layers
A finding would look like: a function accepting 10 parameters that could
accept a structured object, or an inheritance chain 5 levels deep where 2 suffice.
No findings matching this pattern.
```

**Maps to:** Principle of Least Surprise

---

## 3. 🏷️ Name

**Root domain:** Linguistics — Sapir-Whorf Hypothesis, Ubiquitous Language (Eric Evans)
**The question:** *Does the name match the thing?*

Names shape understanding. A misnamed function misleads every future reader.
This lens catches stale comments, misleading variable names, and inconsistent
terminology across the codebase.

**Evidence format:**
```
### 🏷️ Name
Checked: all exported names, comments, error messages
| # | File | Finding | Line |
|---|------|---------|------|
| N1 | geocoder.rs | Comment says "Maps client" but package is "geocoder" | 37 |
```

**Maps to:** Ubiquitous Language (DDD)

---

## 4. 📌 Truth

**Root domain:** Physics — Information Entropy (Shannon)
**The question:** *Is this knowledge in exactly one place?*

When the same fact exists in two places, they will diverge. This lens catches
duplicated configuration, copy-pasted logic, and identifiers that duplicate
their container's key.

**Evidence format:**
```
### 📌 Truth
Checked: configuration files, constants, entity definitions
| # | File | Finding | Line |
|---|------|---------|------|
| T1 | config.yaml + constants.ts | Default timeout defined in both places | 12, 45 |
```

**Maps to:** DRY — Don't Repeat Yourself (Andy Hunt & Dave Thomas, *The Pragmatic Programmer*)

---

## 5. 🧱 Boundary

**Root domain:** Systems Theory — Conway's Law, Interface Segregation
**The question:** *Can an isolated change in desired behavior be implemented
by modifying only a single boundary?*

Boundaries exist to contain change. When a boundary is wrong, a single
requirement change forces edits across multiple modules. This lens catches
tight coupling, misplaced responsibilities, and import cycles.

**Evidence format:**
```
### 🧱 Boundary
Checked: import/dependency graph across all modules
| # | File | Finding | Line |
|---|------|---------|------|
| B1 | email_sender.py | Imports user_config for tenant resolution — should accept resolved data | 14 |
```

**Maps to:** Clean Architecture, Dependency Inversion (Robert C. Martin)

---

## 6. 🛡️ Shield

**Root domain:** Biology — Membrane Permeability (Cellular Immunology)
**The question:** *Does the artifact neutralize all external inputs that
violate its internal invariants?*

A cell survives only if its membrane selectively blocks pathogens. Code
survives only if it validates, sanitizes, or rejects hostile input. This lens
catches missing input validation, exposed PII, insecure defaults, and
missing authentication.

**Evidence format:**
```
### 🛡️ Shield
Checked: all external inputs (HTTP, file I/O, env vars), all auth boundaries
| # | File | Finding | Line |
|---|------|---------|------|
| H1 | middleware.ts | Session cookie has no expiry — lives until browser closes | 20 |
```

**Maps to:** Input Validation, Zero Trust

---

## 7. 🎯 Variety

**Root domain:** Cybernetics — Ashby's Law of Requisite Variety
**The question:** *Does every possible input state map to a defined,
intentional output state?*

"Only variety can destroy variety." For a system to be stable, it must handle
at least as many states as its environment presents. This lens catches
unhandled exceptions, missing error branches, partial functions, and implicit
fallthrough in switch/match statements.

**Shield vs. Variety:** Shield asks "does it block bad input?" Variety asks
"does it handle ALL input — including valid but unexpected states?"

**Evidence format:**
```
### 🎯 Variety
Checked: all switch/match statements on external status codes
| # | File | Finding | Line |
|---|------|---------|------|
| V1 | http_client.rb | No case for 503 Service Unavailable (retryable) | 74 |
```

**Maps to:** Error Handling, Exhaustive Pattern Matching

---

## 8. 🔍 Observability

**Root domain:** Control Theory — Kálmán Observability (1960)
**The question:** *Can I determine the internal state of the system from its
external outputs?*

A system that fails silently is worse than one that crashes loudly. This lens
catches swallowed errors, missing log statements, and the absence of
correlation IDs for distributed tracing.

**Evidence format:**
```
### 🔍 Observability
Checked: all error handling paths, all log statements, recovery/exception handlers
| # | File | Finding | Line |
|---|------|---------|------|
| O1 | error_handler.java | Exception caught and ignored — no logging | 67 |
```

**Maps to:** Logging, Metrics, Distributed Tracing

---

## 9. ⚡ Efficiency

**Root domain:** Physics — Thermodynamic Efficiency
**The question:** *Is the consumption of resources proportional to the
theoretical minimum required to complete the work?*

An optimal system converts input to output with minimal waste. This lens
catches N+1 queries, unbounded reads, quadratic algorithms where linear
suffices, and memory leaks.

**Context-dependent:** Skip for cold paths and prototypes. Apply rigorously
for hot paths and production systems.

**Evidence format:**
```
### ⚡ Efficiency
Checked: all database queries, all loop structures, all memory allocations
A finding would look like: an unbounded read of a response body, or a nested
loop producing O(n²) where O(n) is achievable.
No findings matching this pattern.
```

**Maps to:** Performance Optimization, Algorithmic Complexity

---

## Software Pattern Mapping

| Pattern | Derived From |
|---------|-------------|
| DRY | 📌 Truth |
| YAGNI | 🗑️ Subtract |
| Least Surprise | ✂️ Simplify |
| Ubiquitous Language | 🏷️ Name |
| Clean Architecture | 🧱 Boundary |
| Input Validation | 🛡️ Shield |
| Error Handling | 🎯 Variety |
| Logging / Metrics | 🔍 Observability |
| Performance | ⚡ Efficiency |
| Over-engineering | 🐍 Cobra |
| Scope creep | 🧭 Compass |
| Bikeshedding | ⚖️ Integrity |

---

## Automation: Tools First

Use deterministic tools before applying judgment. A tool finding is more
reliable than an AI finding — and more reproducible.

| Lens | Deterministic Tools | AI Adds |
|------|--------------------:|---------|
| 🗑️ Subtract | Dead code analyzers, `grep` for unreferenced exports | Unused abstractions, vestigial features |
| ✂️ Simplify | Complexity linters (cyclomatic, cognitive) | Over-abstraction, unnecessary indirection |
| 🏷️ Name | — (judgment required) | Semantic accuracy, misleading comments |
| 📌 Truth | Duplicate detectors, `grep` for duplicate constants | Conceptual duplication, diverging configs |
| 🧱 Boundary | Import/dependency analysis | Misplaced responsibilities, coupling |
| 🛡️ Shield | SAST scanners (semgrep, language-specific security linters) | Missing validation logic, insecure defaults |
| 🎯 Variety | Exhaustiveness checkers, compiler warnings | Unhandled business states, partial functions |
| 🔍 Observability | Error-handling linters, `grep` for swallowed errors | Missing context, missing correlation IDs |
| ⚡ Efficiency | Benchmarks, profilers, query analyzers | Algorithmic inefficiency, unbounded reads |

**If a tool can check it, run the tool.** Reserve AI for the judgment calls
that tools cannot make.

