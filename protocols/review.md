# Review Protocol

**Version:** 1.0

---

## Overview

The review protocol governs how proposals are evaluated, challenged, and accepted within a cycle. It is implemented through Steps 5 (Critic), 6 (Destroyer), and 12 (Arbiter) of the operational cycle, with escalation paths for blocked cases.

---

## Reviewable artifacts

Any artifact produced during a cycle is subject to review:

- Architectural proposals (Step 3)
- Alternative approaches (Step 4)
- Implementation plans (Step 7)
- Optimized solutions (Step 8)
- Verification results (Step 9)
- The protocol itself (Step 11)

---

## Review criteria

Every review must address these dimensions:

| Dimension | Question |
|-----------|----------|
| Correctness | Does this solve the stated problem? |
| Completeness | Does it address all acceptance criteria from Step 2? |
| Risk | What can fail, and how likely is it? |
| Evidence | Is the solution backed by data, benchmarks, or verifiable reasoning? |
| Simplicity | Is there a simpler solution with equivalent value? |
| Reusability | Does this increase the collective knowledge base? |

Not every dimension applies to every artifact. Irrelevant dimensions must be explicitly dismissed, not silently skipped.

---

## Approval thresholds

### Accepted by consensus

A solution is accepted when:
- Critic finds no issues rated Critical or High
- Destroyer finds no exploitable vulnerabilities rated Critical or High
- Scientist's confidence is Medium or above
- Arbiter issues an ACCEPTED decision

### Accepted with conditions

A solution is accepted with conditions when:
- Minor issues exist but are explicitly tracked as follow-up tasks
- Conditions are recorded in `memory/decisions/` with a clear resolution path

### Rejected

A solution is rejected when:
- A Critical or High issue has no proposed mitigation
- Confidence is Low and no path to verification exists
- The Builder's proposal does not address Step 5 or 6 findings

A rejection returns the cycle to Step 4 (maximum 2 re-activations).

### Deferred

A solution is deferred when:
- A decision requires information not currently available
- The condition for re-evaluation is specific and time-bound

### Escalated to Owner

A solution is escalated when:
- Two re-activations have not produced an acceptable solution
- A Critical security or constitutional issue is found
- Agents are deadlocked with no convergence path

---

## Veto and counter-proposal rule

Any agent may issue a veto on a proposal during its designated review step.

A veto is valid only if it:
1. Names the specific problem
2. Rates the severity: Critical | High | Medium | Low
3. Proposes an alternative or mitigation

A veto without alternative or mitigation is logged but treated as a Medium-severity concern, not a blocking veto.

---

## Constitutional reviews

Proposals that modify the Constitution or operational rules follow an extended review:

1. A dedicated cycle is opened with `type: rule-evolution` (Article 11) or `type: constitutional-amendment` (Article 12)
2. All 12 steps are executed
3. The Evolution Master assesses the proposal's impact on the ecosystem's evolutionary capacity
4. The Arbiter's decision requires explicit Owner approval to take effect
5. The change is recorded in `memory/decisions/` with full provenance

---

## Process Gap Commission (Article 18)

A Process Gap Commission is opened when a defect reaches delivery that the process should have intercepted. It is mandatory, not optional.

### Trigger (any one is sufficient)

- A bug is found in a delivered artifact that a process gate should have caught
- Any agent identifies a systematic process gap during a cycle
- The Evolution Master finds the same class of defect recurring
- The PQM audit finds >3 HIGH findings in a single audit

### Flow

| Step | Agent | Action |
|------|-------|--------|
| 1 | COORDINATOR | Opens a `type: rule-evolution` cycle. Problem statement: "Which gate failed and why?" |
| 2 | CRITIC | Identifies the specific gate that failed. Quotes the rule (or its absence) that permitted the bug through. |
| 3 | EVOLUTION MASTER | Proposes the rule(s) that would have closed the gap. References the failing case as validation. |
| 4 | SCIENTIST | Verifies: would the proposed rule have actually caught this specific bug? |
| 5 | ARBITER | Decides: operational rule (Article 11) or constitutional amendment (Article 12)? |
| 6 | LIBRARIAN | Creates entry in `memory/errors/` with root cause + rule proposed + outcome. |

### Output

- Updated rule in `protocols/` or `agents/` (if operational)
- Updated `CONSTITUTION.md` (if constitutional, after Owner approval)
- Memory entry in `.swhouse/memory/errors/YYYY-MM-DD-title.md`

### Responsibility

If no agent opens the commission within the next cycle after a delivery defect is identified, the Evolution Master is responsible for opening it. The commission cannot be silently skipped.

---

## Review of the review protocol

This protocol may be revised through the standard rule evolution process (Article 11). The Evolution Master flags review bottlenecks during Step 11 of each cycle. Proposals for change are evaluated in a dedicated `type: rule-evolution` cycle.
