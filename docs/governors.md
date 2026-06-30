# Governors

Governors are meta-level principles that govern the review process itself.
They do not examine the artifact — they vet the findings produced by lenses.

Governors are set **before** analysis begins (in the PLAN phase) and must be
explicitly agreed upon by all reviewers.

## 🧭 Compass

**Root principle:** Goal-seeking (cybernetics) + Bounded Rationality (Kahneman)

**Questions:**
- *Is this finding relevant to our stated goal?*
- *Do I have the context to judge this?*

**Prevents:** Scope drift, uninformed judgment

**Calibration:** The Compass is the most powerful lever in Diffract. Same code,
same lenses, different Compass → different outcomes. A review targeting
"production readiness" will fix things that a review targeting "prototype
validation" will skip.

Always state the Compass as a single sentence:
```
🧭 Compass: "Is this code ready to ship to customers?"
```

### Example Compass Values

| Compass | When to Use |
|---------|-------------|
| "Is this code ready for production?" | Pre-release review |
| "Is this code ready to extract as a library?" | Ascension / reuse review |
| "Can someone use this in 5 minutes?" | Actionability review |
| "Would a senior engineer trust this?" | Credibility review |
| "Is this safe to publish?" | Open-source / compliance review |
| "Could a junior developer onboard from this in one day?" | Readability review |
| "If the author left tomorrow, could someone else maintain this?" | Bus factor review |
| "If this were accidentally open-sourced, would we be embarrassed?" | Quality / secrets review |
| "Does this code respect the user's time, data, and attention?" | Ethics / UX review |
| "Would this survive a 10x traffic spike at 3am?" | Resilience review |
| "If we rewrote this from scratch, would we write the same thing?" | Essence review |
| "Does this code tell a story a future archaeologist could follow?" | Documentation review |
| "Can any LLM follow this prompt equally well?" | Portability review |
| "Would a newcomer feel welcomed or intimidated?" | Approachability review |
| "Are all ideas properly attributed to their sources?" | Intellectual honesty review |

### Bounded Rationality

The Compass includes a self-awareness check: *"Do I have the context to
judge this?"* A reviewer who doesn't understand the domain, the constraints,
or the history of a decision should not override it. This prevents "ivory
tower" reviews where theoretically perfect solutions are demanded without
understanding the real-world tradeoffs.

---

## 🐍 Cobra

**Root principle:** Second-order effects (Donella Meadows, "Thinking in Systems")

**Questions:**
- *Does fixing this cause a new problem?*
- *Is the cure worse than the disease?*

**Prevents:** Overreaction, over-engineering, cascading breakage

**Calibration:** Context-dependent.

```
🐍 Cobra levels:
- Prototype: Skip findings that require >30 minutes to fix OR introduce new abstractions.
  Ask: "Will fixing this slow down learning what works?"
- Production: Skip findings only if fixing requires architectural changes AND current code
  passes all tests. Ask: "Is the cure worse than the disease?"
- Library/Framework: Skip findings only if fixing would break the published API contract.
  Ask: "Will downstream consumers need to change their code?"
```

### The Cobra Effect

Named after the historical policy in colonial Delhi where a bounty on cobras
led people to breed cobras for the reward, making the problem worse. In code
review, this manifests as "fixing" something by adding complexity that
introduces new vulnerabilities.

---

## ⚖️ Integrity

**Root principle:** Falsifiability (Popper) + Calibration (Metrology)

**Questions:**
- *Did I actually look, or did I rush?*
- *Is my finding grounded in an objective criterion, or is it opinion?*
- *Would an independent reviewer with the same input reach the same conclusion?*

**Prevents:** Laziness, bikeshedding, reviewer bias, manipulation

**Calibration:**
```
⚖️ Integrity: Show file:line evidence per lens. Cognitive anchoring required.
```

### Three Sub-Principles

1. **Evidence** — Every lens must produce proof of observation
2. **Falsifiability** — Findings must be objective ("this variable is never
   read" is falsifiable; "this variable name feels wrong" is not)
3. **Calibration** — Different reviewers should reach the same conclusion
   from the same evidence (reproducibility)

---

## Calibration Template

Before every review, state all three:

```
Diffract: v0.1.0
🧭 Compass: [one sentence goal]
🐍 Cobra:   [prototype | production | library/framework] (see Cobra levels above)
⚖️ Integrity: [evidence rules]
```
