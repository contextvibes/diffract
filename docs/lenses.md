# The 10 Lenses

Each lens is grounded in a first principle from a domain **outside** software
engineering. This grounding ensures the lenses are universal — they apply to
any programming language, paradigm, or architecture style.

## Rules Make Findings Citeable

A finding is strongest when it names the written rule it violates — "no
defect without a rule" is the discipline of software inspection (Tom Gilb &
Dorothy Graham, *Software Inspection*, 1993, after Michael Fagan's IBM
inspections), and it is what makes Rule 4's "findings must be testable"
operational rather than aspirational. The lens remains the question; the
**Example rules** under each lens are answers made falsifiable. They are
starting points, not exhaustive lists — when a finding matches no written
rule, state the invariant it violates (PROMPT.md, Rule 4) and consider
adding the rule here. Because linters are rule engines, these rules are also
the substrate for mapping existing tool output onto lenses
([ROADMAP](../ROADMAP.md) v0.3).

## Ordering Rationale

The lenses are ordered from most destructive to most constructive:

1-2: **Remove/reduce** before examining what remains
3-4: **Clarity** — is what remains well-named and non-duplicated?
5-7: **Structure** — walls (Boundary) → membrane (Shield) → lineage (Provenance)
8-9: **Completeness** — does it handle all states and report them?
10: **Performance** — is it proportional?

---

## 1. 🗑️ Subtract

**Root domain:** Philosophy — Via Negativa (Nassim Nicholas Taleb)
**The question:** *Can I remove this entirely?*

The most productive lens. Dead code, unused fields, unnecessary abstractions,
vestigial features — all are real findings that are never Cobra-skipped.
Subtraction improves the system by reducing the surface area for bugs.

**Example rules:**
- No exported symbol with zero references outside its own tests.
- No configuration field that no code path reads.
- No feature flag whose branches are identical, or that is never toggled.
- No abstraction with exactly one implementation and no concrete second
  consumer.

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

**Example rules:**
- No indirection layer that forwards calls without adding behavior, policy,
  or a boundary.
- No design pattern (factory, registry, observer) serving a single fixed
  case.
- No parameter list a call site cannot fill without reading the signature —
  past roughly five, pass a structured object.
- No conditional logic re-deriving a fact the caller already knew.

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

**Example rules:**
- No name that states a different type, unit, or direction than the value
  holds (`timeoutSeconds` holding milliseconds).
- No comment that contradicts the code it annotates.
- No two names for one concept, and no one name for two concepts, within
  the artifact.
- No boolean whose name does not read as a predicate.

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

**Example rules:**
- No literal value whose meaning is defined in more than one place.
- No copy-pasted block that must change in every copy to stay correct.
- No schema, type, or interface restated by hand where it can be derived or
  imported from the source of truth.
- No documentation restating a detail the code itself declares.

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

**Example rules:**
- No import cycle between modules.
- No module reaching past another's public surface into its internals.
- No plausible single-requirement change that forces edits in more than one
  module (name the change to make the finding testable).
- No domain logic inside an I/O adapter, and no I/O inside domain logic.

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

**Example rules:**
- Every external input (network, file, environment, user) crosses a
  validation before its first use.
- No secret or PII written to logs, error messages, or URLs.
- No security-relevant default that fails open (permissive CORS, no expiry,
  debug enabled).
- Every authentication or authorization check runs on the trusted side of
  the boundary it guards.

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

## 7. 🔗 Provenance

**Root domain:** Epidemiology — Contact Tracing
**The question:** *Can I verify the origin and integrity of every dependency?*

Supply chain attacks exploit trust. This lens catches unvetted dependencies,
missing lockfiles, AI-generated code pasted without review, and phantom or
typosquat packages.

| What it catches | What it doesn't |
|---|---|
| Unvetted dependencies, missing lockfiles | Whether deps are well-written |
| Dependencies with known CVEs | Performance of dependencies |
| AI-generated code pasted without review | Whether AI code is correct |
| Phantom/typosquat packages | Licensing issues |

**Example rules:**
- Every dependency is pinned by a lockfile or checksum.
- No dependency with a known unpatched advisory at the pinned version.
- No dependency whose name near-collides with a popular package without a
  documented reason it was chosen.
- No AI-generated or vendored block merged without a named human having
  read it.

**Evidence format:**
```
### 🔗 Provenance
Checked: go.mod, go.sum, lockfile diff since last release, AI-pasted blocks
| # | File | Finding | Line |
|---|------|---------|------|
| P1 | go.mod | `github.com/unknown/jwt` v0.0.1 — 0 stars, created 2 days ago, name near-collides with `dgrijalva/jwt-go`; possible typosquat | 12 |
```

**Maps to:** Supply Chain Security, SBOM, SLSA

---

## 8. 🎯 Variety

**Root domain:** Cybernetics — Ashby's Law of Requisite Variety
**The question:** *Does every possible input state map to a defined,
intentional output state?*

"Only variety can destroy variety." For a system to be stable, it must handle
at least as many states as its environment presents. This lens catches
unhandled exceptions, missing error branches, partial functions, and implicit
fallthrough in switch/match statements.

**Shield vs. Variety:** Shield asks "does it block bad input?" Variety asks
"does it handle ALL input — including valid but unexpected states?"

**Example rules:**
- No switch/match on an external value without an explicit, handled
  default branch.
- No error return or rejected promise that a caller silently ignores.
- No partial function: every input state the interface admits maps to a
  defined output state.
- No retryable failure handled as fatal, and no fatal failure handled as
  retryable.

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

## 9. 🔍 Observability

**Root domain:** Control Theory — Kálmán Observability (1960)
**The question:** *Can I determine the internal state of the system from its
external outputs?*

A system that fails silently is worse than one that crashes loudly. This lens
catches swallowed errors, missing log statements, and the absence of
correlation IDs for distributed tracing.

**Example rules:**
- No caught exception that is neither handled nor logged.
- Every background job or long-running operation reports start, success,
  and failure distinguishably.
- No user-facing failure whose server-side cause cannot be located from
  emitted outputs alone.
- Every request crossing a service boundary carries a correlation ID.

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

## 10. ⚡ Efficiency

**Root domain:** Physics — Thermodynamic Efficiency
**The question:** *Is the consumption of resources proportional to the
theoretical minimum required to complete the work?*

An optimal system converts input to output with minimal waste. This lens
catches N+1 queries, unbounded reads, quadratic algorithms where linear
suffices, and memory leaks.

**Context-dependent:** Skip for cold paths and prototypes. Apply rigorously
for hot paths and production systems.

**Example rules:**
- No query inside a loop that a batch or join can replace (N+1).
- No unbounded read of external input (response body, file, queue) on a
  hot path.
- No O(n²) pass over unbounded n where a linear or O(n log n) equivalent
  exists.
- No resource acquired without a bounded release path.

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
| Supply Chain Security | 🔗 Provenance |
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
| 🔗 Provenance | `npm audit`, `gh advisory`, lockfile diff, SBOM generators | Typosquats, unvetted AI-pasted code |
| 🎯 Variety | Exhaustiveness checkers, compiler warnings | Unhandled business states, partial functions |
| 🔍 Observability | Error-handling linters, `grep` for swallowed errors | Missing context, missing correlation IDs |
| ⚡ Efficiency | Benchmarks, profilers, query analyzers | Algorithmic inefficiency, unbounded reads |

**If a tool can check it, run the tool.** Reserve AI for the judgment calls
that tools cannot make.

