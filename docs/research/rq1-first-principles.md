# Research: First Principles Validation (RQ1)

> **Author-graded.** The research was produced by an AI research model. Which
> of its findings Diffract adopted, and how they map onto lenses, was judged by
> the party that authored the instrument. No independent analyst has checked
> that mapping (issue #26).

## Research Question

> What is the minimal complete set of first principles needed to evaluate
> the quality of a software artifact?
>
> For each candidate principle, it must:
> 1. Be grounded in a domain outside software
> 2. Produce unique findings that no other principle catches
> 3. Be expressible as a single yes/no question
>
> Additionally: some principles evaluate the artifact, while others
> evaluate the process of evaluation. Identify which is which.

## Findings

Independent analysis derived 7 principles in two categories:

### Artifact Principles (4)

| Principle | Root Domain | Question |
|-----------|-------------|----------|
| Information Entropy | Physics | Is this knowledge in exactly one place? |
| Membrane Permeability | Biology | Does it neutralize inputs violating invariants? |
| Requisite Variety | Cybernetics | Does every input map to a defined output? |
| Thermodynamic Efficiency | Physics | Is resource use proportional to work? |

### Meta-Evaluation Principles (3)

| Principle | Root Domain | Question |
|-----------|-------------|----------|
| Falsifiability | Philosophy | Is the finding objective or opinion? |
| Bounded Rationality | Economics | Does the evaluator have full context? |
| Calibration | Metrology | Would another reviewer reach the same conclusion? |

## Impact on Diffract

| Research Finding | Diffract Change |
|-----------------|----------------|
| Requisite Variety confirmed as distinct | Added 🎯 Variety lens |
| Thermodynamic Efficiency confirmed as distinct | Added ⚡ Efficiency lens |
| Membrane Permeability sharpened Shield | Upgraded 🛡️ Shield question |
| Falsifiability + Calibration strengthened Integrity | Upgraded ⚖️ Integrity governor |
| Bounded Rationality strengthened Compass | Upgraded 🧭 Compass governor |

## Unique Diffract Additions Not Found in Research

The research model, while rigorous, missed several principles that produce
unique findings in practice:

| Diffract Lens | Why It's Unique |
|---------------|----------------|
| 🗑️ Subtract | Research assumes things should exist; Subtract asks "should this exist at all?" |
| ✂️ Simplify | Research measures structural entropy; Simplify measures unnecessary complexity in ordered systems |
| 🏷️ Name | Research catches structural naming issues; Name catches semantic accuracy |
| 🧱 Boundary | Research folded change-locality into Information Entropy; Boundary makes "can this change stay in one place?" its own test |
| 🔍 Observability | Research ensures all states are handled (Variety); Observability ensures they are reported |

RQ1 ran in February 2026 against the 7-lens set that preceded 0.1.0. It
independently derived 2 of those 7 (📌 Truth, 🛡️ Shield) and added 2 more
(🎯 Variety, ⚡ Efficiency), giving the 9 lenses 0.1.0 shipped. The lenses
above are the 5 it did not derive. 🔗 Provenance was added in 0.2.0
(August 2026) and postdates this research entirely — its absence here is
chronology, not an omission by the research model.
