# Research: First Principles Validation (RQ1)

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
| Information Entropy | Physics | Can an isolated change be made in one boundary? |
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
| 🔍 Observability | Research ensures all states are handled (Variety); Observability ensures they are reported |
