---
cycle: 002
type: rule-evolution
status: closed
closed: 2026-08-02
decision: ACCEPTED — Article 20 added to CONSTITUTION.md (Owner approved)
opened: 2026-08-02
trigger: article-18
problem: "Which process gate failed to intercept missing tooltips on delivered animation, and why?"
---

*Note on execution model: this PGC is executed within a single session, with all 6 roles framed sequentially. The independence trade-off is acknowledged — the operator (Owner) acts as the external check via approval gate at Step 5.*

---

## PGC Step 1 — COORDINATOR: Open the Problem

**Agent:** claude-sonnet-4-6

### Trigger

Article 18 is activated. A delivered animation artifact was declared DONE with interactive elements lacking tooltips. The defect was discovered by the Owner post-delivery.

### Which gate was supposed to catch this?

**Article 16 — Executable Validation** was the applicable gate. The animation was opened in the browser (native execution environment). It ran without console errors. The implementer declared it DONE.

**Article 16 did not catch the defect** because:
1. The validator was the implementer — same cognitive context, same blind spots
2. Art. 16 asks "does it run?" not "does it communicate everything it should to someone who has never seen it before?"
3. No rule required a second, independent agent to perform the validation

### Scope

**In scope:** The gap between "validated in native environment" (Art. 16) and "independently verified as complete"  
**In scope:** Whether the fix is an operational rule (Art. 11) or a constitutional principle (Art. 12)  
**Out of scope:** The specific animation implementation, tooltip design, or UI conventions  
**Out of scope:** Changes to Art. 16 itself (it remains valid; the gap is additive)

### Complexity: Medium

---

## PGC Step 2 — CRITIC: Identify the Failing Gate

**Agent:** claude-sonnet-4-6

### Gate failure analysis

| Layer | What existed | What was missing | Severity |
|-------|-------------|-----------------|----------|
| Art. 16 (Execution) | "Validate in native environment" | Requirement that the validator be independent of the implementer | High |
| Art. 16 (Scope) | Focus on correctness (does it run?) | Coverage of completeness (does it communicate without external context?) | High |
| Art. 16 examples | Documentation: "read by at least one agent other than the author" | Same independence requirement extended to interactive/UI deliverables | Medium |
| Operational cycle | SCIENTIST (Step 9) performs verification | No mandatory trigger to apply Step 9 at task-level DONE, not only design-level | Medium |

### Root cause (single sentence)

Art. 16 mandates execution-environment validation but does not require the validator to be independent of the implementer — enabling self-certification with structural blind spots.

### The Documentation Anomaly

Notably, Art. 16 already states that documentation must be "read by at least one agent other than the author." This independence requirement exists for docs but is absent for every other deliverable type. The gap is an **inconsistency** within Art. 16, not only an absence.

### Verdict

The failing gate is **Article 16**, through two compounding omissions:
1. No independence requirement for non-documentation deliverables
2. No mandate to verify experiential completeness (not just execution correctness)

---

## PGC Step 3 — EVOLUTION MASTER: Propose the Rule

**Agent:** claude-sonnet-4-6

### Option A — Article 11 (Operational Rule)

Add to `protocols/completion-checklist.md`: "Before marking any deliverable DONE, at least one agent who did not produce it must perform an adversarial review with the mandate: 'What would a first-time user or integrator NOT understand or be unable to do?' This applies to any deliverable with an interactive, communicative, or integration surface."

**Scope:** Operational — applies to task completion workflow  
**Durability:** Can be modified by standard Art. 11 process  
**Limitation:** Does not fix the inconsistency in Art. 16; a future operator could remove the rule without constitutional protection

### Option B — Article 12 (Constitutional Amendment)

Add Article 20 — Independent Completion Verification:

> Every deliverable must be verified by an agent who did not produce it before being declared complete.
>
> The verifier's mandate is adversarial: find what is missing or unclear to someone with no prior context — not what is present and functioning.
>
> The verification method is domain-specific:
> - **Interactive/UI**: outsider-perspective completeness review — "what does this element mean to someone who has never seen it?"
> - **Compiled software**: integration test driven by a verifier other than the developer
> - **Embedded**: hardware-in-loop or equivalent simulation driven by a verifier other than the firmware author
> - **Documentation**: comprehension check by a reader who was not involved in writing it
> - **Protocols/APIs**: integration attempt by a consumer who did not design the interface
>
> If no domain-specific verification method is defined for the deliverable type, the verifier must state: "verification method undefined — deliverable is PROVISIONAL, not DONE." A PROVISIONAL deliverable may not be declared DONE until a verification method is agreed.

**Scope:** Constitutional — applies universally, across all projects, all domains, resistant to waiver  
**Durability:** Requires Art. 12 process to change (Owner approval + full cycle)  
**Strength:** Resolves the Art. 16 documentation inconsistency by making independence universal

### Recommendation

**Option B (Art. 12).** The user's explicit goal is a general principle applicable across all domains — including cases not yet encountered. A constitutional article is the correct vehicle because:
1. The independence requirement is a fundamental quality guarantee, not a workflow detail
2. Time pressure will create temptation to skip it; constitutional protection makes it harder to waive
3. The domain-specific method table makes it concrete without being prescriptive — new domains can add rows without amending the article

The proposed article deliberately **does not introduce a new role**. Any agent may serve as the independent verifier. The SCIENTIST is the natural choice in most contexts; for embedded, an engineer with debug access; for documentation, the Librarian. The domain playbooks (in `protocols/`) specify who is appropriate per domain.

---

## PGC Step 4 — SCIENTIST: Verify

**Agent:** claude-sonnet-4-6

### Claim 1: The proposed Art. 20 would have caught the tooltip gap

**Method:** Simulation — apply Art. 20 to the specific incident

**Simulation:**
- Deliverable: animation with interactive elements
- Domain: Interactive/UI
- Required verification: outsider-perspective completeness review
- Verifier: an agent who did not build the animation opens it for the first time
- Verifier mandate: "What would a first-time viewer NOT understand?"
- Observable gap: interactive elements with no tooltip → verifier cannot determine what they represent → files finding
- DONE blocked until tooltips added

**Result:** CONFIRMED — Art. 20 would have caught the defect. **Confidence: High.**

### Claim 2: The rule applies to the embedded domain as described by the user

**Method:** Logical extension

**Simulation:**
- Deliverable: embedded firmware for ESP8266
- Domain: Embedded
- Required verification: hardware-in-loop or equivalent simulation, driven by verifier other than firmware author
- Verifier connects to the device via debug session
- Tests the functionality the author claimed was working
- Any gap between claimed and observed behavior → DONE blocked

**Result:** CONFIRMED — the verification method (hardware-in-loop debug) is exactly the mechanism the user described. **Confidence: High.**

### Claim 3: The "PROVISIONAL if no method defined" fallback prevents silent skipping

**Method:** Logical proof

If no domain playbook exists, the rule does not silently pass — it produces a visible state (PROVISIONAL). This satisfies Art. 17 (Visible Failure): the absence of a method is itself an observable signal.

**Result:** CONFIRMED. **Confidence: High.**

### Open hypotheses (not verified)

| Hypothesis | Why not verified | Future verification |
|-----------|-----------------|-------------------|
| Adding a verifier step does not materially slow delivery | No cycle data yet | Measure time-to-DONE before/after in first 5 cycles post-adoption |
| The domain table covers all likely deliverable types | Unknown future domains | Accept: the PROVISIONAL fallback handles unknowns |

### Overall verdict

**Solution is verified.** All three core claims confirmed. Proceed to ARBITER.

---

## PGC Step 5 — ARBITER: Decide

**Agent:** claude-sonnet-4-6

### Classification

**Article 12 (Constitutional Amendment)** — not Article 11 (Operational Rule).

Rationale:
1. The independence requirement for validators is not a workflow detail — it is a fundamental quality guarantee. Operational rules can be silently amended or waived; a constitutional article cannot without explicit Art. 12 process.
2. The Scientist confirmed the rule would have caught the specific incident (real-case validation required by Art. 12, clause 3).
3. The amendment does not reduce evolutionary capacity — it increases it by making deliverables more trustworthy, reducing rework.
4. The Art. 16 documentation inconsistency (independence required only for docs) is resolved: the new article makes independence universal and principled.

### Decision

**ACCEPTED — pending Owner approval**

Per `protocols/review.md` (Constitutional Reviews): *"The Arbiter's decision requires explicit Owner approval to take effect."*

The proposed text for **Article 20 — Independent Completion Verification** (as drafted in PGC Step 3) is the text to be added to `CONSTITUTION.md` upon Owner approval.

The Arbiter notes one follow-up item for a future cycle (not blocking this amendment):
- A `protocols/completion-domains.md` file should be created with the domain-specific verification method table in machine-readable form, enabling agents to look up the appropriate method without reading the full Constitution.

---

## PGC Step 6 — LIBRARIAN: Register Memory

**Agent:** claude-sonnet-4-6

Memory entries to be written upon cycle closure (after Owner approval):

1. `memory/errors/2026-08-02-animation-tooltip-gap.md` — root cause, gate that failed, rule proposed
2. `memory/decisions/2026-08-02-art20-independent-completion-verification.md` — decision record with full provenance

Knowledge graph updates:
- Link new error entry to `memory/decisions/2026-07-26-constitutional-amendment-16-17-18.md` (prior Art. 16/18 incident — same pattern: validation gate existed but was insufficient)
- Link new decision entry to `memory/decisions/2026-07-26-constitutional-amendment-16-17-18.md` (precedent for constitutional amendment via real incident)

Reusability:
- The pattern "validation gate existed but lacked independence requirement" is extractable as a `memory/patterns/` entry for future gap detection

---

*Cycle 002 — awaiting Owner approval to close*
