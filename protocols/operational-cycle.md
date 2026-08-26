# Operational Cycle Protocol

**Version:** 1.1

The operational cycle is the fundamental unit of work in the Software House AI. Every problem, feature, decision, or investigation is processed through this protocol.

---

## Overview

A cycle consists of 12 sequential steps, each owned by one of the founding agents. The cycle produces a documented decision and updates the organizational memory.

**One cycle is open at a time.** Concurrent cycles are not permitted in the current version.

---

## Cycle Tracks

The COORDINATOR selects a track at Step 1 and records it in the cycle header (`**Track:**`).

| Track | Steps executed | When to use |
|-------|---------------|-------------|
| S — Sprint | 1 · 7 · 9 · 12 | Hotfixes, single-component changes where design is already settled |
| M — Standard | 1 · 2 · 3 · 5 · 7 · 8 · 9 · 10 · 11 · 12 | Feature work with design to be decided |
| F — Full | All 12 | Architectural decisions, new modules, cross-cutting changes, self-assessment |

In Track S, skipped steps are not present in `current.md` — they are out of scope by design, not bypassed.  
In Track M, Steps 4 (Explorer) and 6 (Destroyer) are optional: include them if the problem space is novel or adversarial risk is relevant.  
In all tracks, Steps 10 (Librarian) and 11 (Evolution Master) are required.

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
- Track selection: **S | M | F** with one-line justification
- Clear statement of the problem
- Why it is being addressed now
- Scope boundaries (what is in and out of scope)
- Estimated complexity: Low | Medium | High
- **Context check:**
  - Memory lookup: list any `memory/` entries consulted relevant to this cycle's domain (or state "no prior entries in this domain")
  - Validation matrix: if the cycle involves a deployment or a user-facing deliverable, confirm the VALIDATOR matrix covers all affected targets; if missing, invoke VALIDATOR before Step 7

The Coordinator does not propose solutions. It frames the problem.

---

### Step 2 — PRODUCT OWNER: Define the Value

**Output required:**
- Who has this problem? (user, system, organization)
- What is the measurable value of solving it?
- What is the cost of not solving it?
- Acceptance criteria: how will we know the solution is good enough?
- **UX Coherence Check** (if cycle involves any user-facing feature or input): run the checklist in [protocols/ux-coherence.md](ux-coherence.md) and include the `### UX Coherence Check` block. Each finding becomes an acceptance criterion.

If the Product Owner cannot articulate the value, the cycle is paused and returned to the Coordinator for reframing.

---

### Step 3 — ARCHITECT: Propose Structure

**Output required:**
- Decomposition of the problem into components
- Proposed interfaces and dependencies
- At least two structural approaches (with trade-offs)
- Recommended approach with rationale
- **Input Surface Audit** (if cycle involves any user-facing feature or input): run the checklist in [protocols/ux-coherence.md](ux-coherence.md) and include the `### UX Coherence Check` block before the structural proposals. A structure that preserves a P1/P2/P3 violation is not a valid option.

The Architect reduces complexity. If a proposal adds complexity without clear justification, it is returned for revision.

---

### Step 4 — EXPLORER: Generate Alternatives

**Output required:**
- At least three alternative approaches (divergent thinking)
- At least one approach that challenges the Architect's recommendation
- One approach that starts from a different first principle than the Architect's — a genuinely different framing of the problem, not a variation of the same solution
- Brief rationale for each

The Explorer must not self-censor. Unconventional ideas are explicitly welcome.

---

### Step 5 — CRITIC: Analyze Weaknesses

**Output required:**
- Critique of each approach proposed in Steps 3 and 4
- Identified edge cases, inconsistencies, and technical debt risks
- Ranking of approaches by risk (highest to lowest)
- Explicit statement: which approaches are unacceptable and why
- **UX Coherence standing check** (if cycle involves any UI or user input): Q3 ("can the user reach an inconsistent state?") and Q5 ("will wrong input produce silently wrong output?") from [protocols/ux-coherence.md](ux-coherence.md) are mandatory findings — address even if prior steps already raised them. If Steps 2 or 3 omitted the `### UX Coherence Check` block, raise it as a process finding (severity: High).

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

**Production deployment targets**: for any cycle that includes a deployment, the Scientist must read the VALIDATOR matrix and produce one entry per target listed in it:

```
Target: <name>
Reachable by automation: YES / NO
Verification method: <how confirmed — from VALIDATOR matrix>
Status: VERIFIED | PENDING_HUMAN | SKIPPED_JUSTIFIED
```

- `VERIFIED`: automation confirmed the running artifact matches the expected commit/version.
- `PENDING_HUMAN`: target is unreachable by automation. The Scientist has produced exact verification commands and expected output (see VALIDATOR matrix and project `CLAUDE.md` for per-target procedures). Status becomes `VERIFIED` only after the named human operator confirms.
- `SKIPPED_JUSTIFIED`: deployment was explicitly out of scope for this cycle; justification required.

**The SCIENTIST must not substitute localhost validation for a real-target entry.** A target listed in the VALIDATOR matrix that is validated only on localhost produces a SKIPPED entry, not VERIFIED.

Any `PENDING_HUMAN` entry makes the deliverable **provisional** (Article 16). The Arbiter may not issue ACCEPTED until it is resolved (see Step 12).

---

### Step 10 — LIBRARIAN: Update Memory

**Output required:**
- New entries added to `memory/` (decisions, patterns, errors, knowledge)
- Existing entries updated or superseded
- Links between this cycle and related past cycles
- Summary: what is now reusable from this cycle?
- **Validation matrix update:** if the cycle added, removed, or modified any deployment target, credential, or verification procedure, the VALIDATOR matrix must be updated before this step is marked complete.

**Close checklist (required before cycle can archive):**
- [ ] `metrics/summary.yaml` — `total_cycles` incremented, `memory_entries` counts updated, `last_updated` set to today
- [ ] At least one memory entry written or explicitly updated in `memory/`
- [ ] All failures from this cycle confirmed logged in `memory/errors/` (created or noted as reconstructed if post-hoc)
- [ ] If any deployment target was added/removed: validation matrix updated
- [ ] **Documentation (see `protocols/documentation.md`):**
  - [ ] `docs/MAP.md` updated: any document added, removed, or now known-stale listed with reason
  - [ ] Any `architecture/` document describing components changed this cycle: `last_verified` updated or staleness flagged
  - [ ] Any new decision made this cycle: ADR written or planned in `decisions/`
  - [ ] Any new command/procedure/environment change: reflected in `operations/`

The Librarian's work is not optional. A cycle that leaves no memory entry is constitutionally incomplete (Article 10).

---

### Step 11 — EVOLUTION MASTER: Evaluate the Process

**Required in all tracks (minimum output: 2 lines).**

**Output required:**
- **Cycle quality score:** [1–5] — one sentence rationale
  - 1: Protocol was theater — outputs were thin paraphrases, no new insight
  - 2: Protocol produced some value but most steps were mechanical
  - 3: Protocol added clear value — at least one step changed the direction or identified a real risk
  - 4: Protocol was well-suited and efficient for this cycle
  - 5: Exceptional — protocol produced insights that would not have emerged without the structure
- Process observations: bottlenecks or steps that added no value (optional if score ≥ 3)
- Proposed improvements to the protocol (optional; trigger an Article 11 proposal if adopted)

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

**Constraints on ACCEPTED:**
- If Step 9 contains any target with status `PENDING_HUMAN`: the Arbiter **must** issue DEFERRED, not ACCEPTED. The DEFERRED condition must name: the target, the verification commands, the human owner, and the method for recording confirmation.
- If a DEFERRED decision is issued, the condition must include an explicit method for re-opening the cycle (not just "check later"). A DEFERRED without a re-opening mechanism is constitutionally equivalent to abandonment.
- The Step 10 close checklist must be present and complete. The Arbiter may not issue ACCEPTED or ACCEPTED WITH CONDITIONS if the checklist is absent or has unchecked items without justification.

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

### PENDING_HUMAN resolution

When an archived cycle contains a `PENDING_HUMAN` condition and the human operator has performed the verification:

1. Append to the archived cycle file (`cycles/archive/cycle-NNN.md`):

   ```
   ## Human Verification — [YYYY-MM-DD]
   Performed by: [name]
   Target: [target name from condition]
   Result: VERIFIED | FAILED
   Notes: [optional]
   ```

2. If VERIFIED: change the cycle status header to `ACCEPTED`. No new cycle is opened.
3. If FAILED: open a new Sprint-track cycle referencing `cycle-NNN` as context. The failed verification is the problem statement.

---

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
| VALIDATOR | High | Scientist documents targets from CLAUDE.md manually; Coordinator flags matrix as provisional |

---

## Cycle Record Format

See [schemas/swhouse-structure.md](../schemas/swhouse-structure.md#cyclescurrentmd) for the full `cycles/current.md` format.

---

## Cycle Numbering

Cycles are numbered sequentially from 001, zero-padded to 3 digits. The number is global to the project — it does not reset per milestone or version.

`metrics/summary.yaml` is the authoritative source for the last cycle number.

---

## Real-Time Failure Logging Protocol

This is not a cycle step. It is a continuous obligation binding every agent in every session, inside or outside a formal cycle.

### Trigger conditions

Log immediately when any of the following occurs:

- A shell command, network connection, or API call returns an error or unexpected output
- A service, process, or resource is found in a state different from what was expected
- An operation produces no output when output was expected
- An assumption stated earlier in the session is contradicted by observation
- Multiple attempts are made at the same operation (retries signal an unresolved failure)

### What to log

Create or append to `memory/errors/YYYY-MM-DD-descriptive-title.md` (one file per session or per incident cluster).

**Minimum required fields** — completeness is for Step 10; existence is for now:

```
occurred_at: <time or "approx HH:MM">
what was attempted: <one line>
what was observed: <the actual error, output, or state>
cycle: <NNN or "outside cycle">
```

Analysis (`root cause`, `resolution`, `lesson`) may be left as `pending`. A partial entry is better than no entry.

### What this is not

- It is not a replacement for Step 10 (LIBRARIAN). Step 10 enriches and links entries; this protocol creates them.
- It is not optional when a workaround is found quickly. A failure that was immediately resolved is still evidence: it reveals an assumption that was wrong, an environment that differs from expectations, or a gap in pre-conditions.
- It is not deferred because the session is busy. The log entry takes seconds; the lost evidence costs future sessions hours.
