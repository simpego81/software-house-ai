# Operational Cycle Protocol

**Version:** 1.0

The operational cycle is the fundamental unit of work in the Software House AI. Every problem, feature, decision, or investigation is processed through this protocol.

---

## Overview

A cycle consists of 12 sequential steps, each owned by one of the founding agents. The cycle produces a documented decision and updates the organizational memory.

**One cycle is open at a time.** Concurrent cycles are not permitted in the current version.

---

## Cycle Lifecycle

```
OPEN → [12 steps] → CLOSE → ARCHIVE
```

- **OPEN:** A new `cycles/current.md` file is created with status `open`.
- **12 steps:** Each step is appended to `current.md` as it completes.
- **CLOSE:** The cycle receives a final Arbiter decision. Status changes to `closed`.
- **ARCHIVE:** `current.md` is moved to `cycles/archive/cycle-NNN.md`. Reputation scores are updated. `metrics/summary.yaml` is updated.

---

## The 12 Steps

### Step 1 — COORDINATOR: Open the Problem

**Output required:**
- Clear statement of the problem
- Why it is being addressed now
- Scope boundaries (what is in and out of scope)
- Estimated complexity: Low | Medium | High

The Coordinator does not propose solutions. It frames the problem.

---

### Step 2 — PRODUCT OWNER: Define the Value

**Output required:**
- Who has this problem? (user, system, organization)
- What is the measurable value of solving it?
- What is the cost of not solving it?
- Acceptance criteria: how will we know the solution is good enough?

If the Product Owner cannot articulate the value, the cycle is paused and returned to the Coordinator for reframing.

---

### Step 3 — ARCHITECT: Propose Structure

**Output required:**
- Decomposition of the problem into components
- Proposed interfaces and dependencies
- At least two structural approaches (with trade-offs)
- Recommended approach with rationale

The Architect reduces complexity. If a proposal adds complexity without clear justification, it is returned for revision.

---

### Step 4 — EXPLORER: Generate Alternatives

**Output required:**
- At least three alternative approaches (divergent thinking)
- At least one approach that challenges the Architect's recommendation
- One approach derived from analogy or biomimicry
- Brief rationale for each

The Explorer must not self-censor. Unconventional ideas are explicitly welcome.

---

### Step 5 — CRITIC: Analyze Weaknesses

**Output required:**
- Critique of each approach proposed in Steps 3 and 4
- Identified edge cases, inconsistencies, and technical debt risks
- Ranking of approaches by risk (highest to lowest)
- Explicit statement: which approaches are unacceptable and why

Every critique must propose a mitigation or clearly state that none exists.

---

### Step 6 — DESTROYER: Attempt Invalidation

**Output required:**
- Security and abuse scenarios for the leading approach(es)
- Failure modes under adversarial conditions
- Fault tolerance gaps
- Verdict: can the leading approach survive a motivated adversary?

The Destroyer's job is to break things. If it cannot find a way to break a solution, that result is itself informative and must be stated explicitly.

---

### Step 7 — BUILDER: Produce a Solution

**Input:** Steps 1–6 outputs  
**Output required:**
- Concrete implementation plan (tasks, specifications, or code)
- Explicit response to each Critic and Destroyer finding
- Unresolved issues clearly flagged (not hidden)
- Confidence level: High | Medium | Low

The Builder does not ignore Step 5 and 6 findings. Every finding must be addressed or explicitly deferred with justification.

---

### Step 8 — OPTIMIZER: Improve the Solution

**Output required:**
- Identified redundancies, over-engineering, or unnecessary complexity
- Simplified or more efficient version of the Builder's solution
- Performance, cost, or maintainability improvements
- Anything that was added but can be safely removed

The Optimizer's output replaces the Builder's solution as the working proposal.

---

### Step 9 — SCIENTIST: Verify

**Output required:**
- Verification method used (benchmark, experiment, simulation, comparison, logical proof, browser observation)
- Results of verification
- Confidence level with explicit reasoning
- Open hypotheses that could not be verified

If verification is not possible at this stage, the Scientist must state why and propose a future verification plan.

**Frontend deliverables**: for any solution whose output is HTML, JavaScript, WebGL, or a browser-rendered artifact, logical inspection alone does **not** satisfy this step. The required method is **browser observation** — open the deliverable in a browser and directly confirm visual rendering and absence of console errors. See [protocols/frontend-checklist.md](frontend-checklist.md).

---

### Step 10 — LIBRARIAN: Update Memory

**Output required:**
- New entries added to `memory/` (decisions, patterns, errors, knowledge)
- Existing entries updated or superseded
- Links between this cycle and related past cycles
- Summary: what is now reusable from this cycle?

The Librarian's work is not optional. A cycle that leaves no memory entry is constitutionally incomplete (Article 10).

---

### Step 11 — EVOLUTION MASTER: Evaluate the Process

**Output required:**
- Assessment of how well the 12-step protocol served this cycle
- Bottlenecks or steps that added no value
- Proposed improvements to the protocol (if any)
- Reputation vote recommendations (see [protocols/reputation.md](reputation.md))

The Evolution Master does not evaluate the solution — it evaluates the process that produced it.

---

### Step 12 — ARBITER: Decide

**Output required:**
- Final decision: **ACCEPTED** | **REJECTED** | **DEFERRED** | **ESCALATED**
- Rationale (minimum 3 sentences)
- If REJECTED: specific reason and what would make it acceptable
- If DEFERRED: condition that must be met before re-evaluation
- If ESCALATED: why Owner intervention is required

The Arbiter evaluates quality, evidence, and consensus. It does not create or implement.

**The Arbiter's decision closes the cycle.**

---

## Escalation and Deadlock Protocol

### When Critic + Destroyer invalidate all proposals

If Step 5 and Step 6 together make all proposed approaches unacceptable:

1. The Builder (Step 7) must explicitly state: "No viable solution identified in this cycle."
2. The cycle is **not closed** — it is **suspended**.
3. The Explorer is re-activated with the constraint: "Generate approaches that survive the Critic and Destroyer findings."
4. The cycle resumes from Step 4 (maximum 2 re-activations per cycle).
5. If after 2 re-activations no viable solution exists, the cycle is ESCALATED to Owner.

### When the Arbiter cannot decide

If the Arbiter lacks sufficient evidence to decide:

1. The Arbiter requests specific additional evidence from the Scientist (Step 9 re-run, targeted).
2. If evidence cannot be produced, the Arbiter issues a DEFERRED decision with explicit conditions.

### When a step produces no output

If an agent produces no output for its step (failure, unavailability):

- If the role is marked `unavailable` in `instance.yaml`: step is skipped and logged.
- If the role is available but fails: retry once. If it fails again, log and skip.
- If the failed role is COORDINATOR or ARBITER: cycle is paused and Owner is notified.

---

## Missing Roles

If a role listed in the operational protocol is not available:

| Role | Criticality | Fallback |
|------|-------------|---------|
| COORDINATOR | Critical | Pause cycle, notify Owner |
| PRODUCT OWNER | High | Owner provides value statement directly |
| ARCHITECT | High | Builder attempts structure definition |
| EXPLORER | Medium | Architect provides one alternative approach |
| CRITIC | Medium | Destroyer covers critic function partially |
| DESTROYER | Medium | Scientist covers adversarial testing |
| BUILDER | Critical | Pause cycle, notify Owner |
| OPTIMIZER | Low | Builder self-reviews for simplicity |
| SCIENTIST | Medium | Builder provides confidence estimate only |
| LIBRARIAN | High | Builder writes memory entries; Coordinator schedules Librarian catch-up |
| EVOLUTION MASTER | Low | Step 11 is skipped |
| ARBITER | Critical | Pause cycle, notify Owner |

---

## Cycle Record Format

See [schemas/swhouse-structure.md](../schemas/swhouse-structure.md#cyclescurrentmd) for the full `cycles/current.md` format.

---

## Cycle Numbering

Cycles are numbered sequentially from 001, zero-padded to 3 digits. The number is global to the project — it does not reset per milestone or version.

`metrics/summary.yaml` is the authoritative source for the last cycle number.
