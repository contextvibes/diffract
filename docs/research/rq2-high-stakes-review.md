# Research: High-Stakes Review Patterns (RQ2)

## Research Question

> How do high-stakes industries (aviation, medicine, nuclear, law) structure
> their review processes to prevent both omission (failing to find real
> issues) and manipulation (claiming issues don't exist)?

## Key Findings

### 1. Verifying the Act of Observation

| Industry | Mechanism | How It Works |
|----------|-----------|-------------|
| Aviation | RFID / barcode scanning | Inspector must physically scan components at the inspection site — cannot sign off remotely |
| Nuclear | Qualification-linked RFID | Operator scans personal ID + component tag; system verifies certification before work begins |
| Railways | Shisa kanko (pointing & calling) | Operator physically points at indicator and verbally calls out state — engages multiple cognitive channels |
| Legal | Audit trail analytics | System tracks document open duration, scrolling, keystrokes — 2.4 seconds on a 50-page document invalidates "reviewed" claim |

**Adopted in Diffract:** Evidence requirements (mechanism 1), Cognitive Anchoring (mechanism 2)

### 2. Bounding the Scope

| Industry | Mechanism | How It Works |
|----------|-----------|-------------|
| Nuclear | Hold points | Work must stop at defined intervals for independent verification before proceeding |
| Aviation | Sterile Cockpit Rule | Below 10,000 feet, no non-essential conversation — protects cognitive bandwidth during critical phases |
| Nuclear | Geofencing | GPS perimeters enforce spatial boundaries — transport vehicles trigger alerts if they deviate from approved routes |

**Adopted in Diffract:** PLAN checkpoint (hold point before DO), Compass governor (scope bounding)

### 3. Verifying "Nothing Found"

| Industry | Mechanism | How It Works |
|----------|-----------|-------------|
| UXO clearance | Blind seeding | Inert munitions secretly buried before sweep — team that misses a seed must resurvey the entire grid |
| Radiology | Synthetic defect injection | Known abnormal slides mixed into daily screening — missed slides trigger threshold recalibration |
| Legal e-discovery | Control sets | Pre-coded documents seeded into review pool — missed documents force algorithm retraining |

**Adopted in Diffract:** Nothing-Found Verification (mechanism 5)

### 4. Combining Independent Perspectives

| Industry | Mechanism | How It Works |
|----------|-----------|-------------|
| Aviation | Junior First protocol | Junior officer states assessment before captain speaks — prevents anchoring bias |
| Aviation | Challenge-Response checklists | Monitoring pilot reads challenge; flying pilot physically verifies and verbally responds — mutual cross-check |
| Aviation | Required Inspection Items (RII) | Mechanic who performs repair cannot inspect it — independent inspector from separate reporting chain |
| Medicine | Dual-reading | Two radiologists independently read same images — final report requires reconciliation |
| Medicine | Tumor Board | Flat multi-disciplinary panel (surgeon, oncologist, radiologist, pathologist) — no single specialty dominates |

**Adopted in Diffract:** Challenge-Response (mechanism 6), Finder/Decider Separation (mechanism 7)

## Structural Insight

> High-stakes industries survive not because their operators are infallible,
> but because their review structures treat fallibility as an absolute,
> measurable certainty.

The common pattern across all four industries: **assume the reviewer will
fail, then engineer the environment so that failure is trapped.**

Diffract applies the same philosophy to code review.
