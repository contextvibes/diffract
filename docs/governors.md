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
| "Would someone choose this over the alternative?" | Value / differentiation review |
| "Is this safe to publish?" | Open-source / compliance review |
| "Can someone find this and understand it in 10 seconds?" | Discoverability review |

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
- **Prototype:** Aggressive — skip marginal findings
- **Production:** Cautious — fix more, skip less
- **Library/Framework:** Very cautious — downstream users depend on stability

```
🐍 Cobra: Production — cautious. Fix more, skip less.
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
🧭 Compass: [one sentence goal] + [what context do I have/lack?]
🐍 Cobra:   [prototype = aggressive | production = cautious]
⚖️ Integrity: [evidence rules]
```
