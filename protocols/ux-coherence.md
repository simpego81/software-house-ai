# UX Coherence Protocol

**Version:** 1.0  
**Applies to:** Any cycle that introduces a user-facing feature, input field, control, or workflow step.

---

## Purpose

Prevent UX regressions caused by design decisions that are individually reasonable but collectively incoherent. The most common failure mode: a new feature adds a user input that could be inconsistent with an existing input, creating a failure mode the user cannot detect until damage is done.

---

## Three Meta-Principles

### P1 — Single Point of Truth for User Inputs (SPOTU)

Every set of inputs that must be mutually consistent should be reducible to a single upstream selection. If a new input is derivable from an existing one, derive it — do not ask the user twice.

**Trigger:** any new feature that requires the user to provide information the system already has, or that must agree with information already provided.

**Correct response:** consolidate upstream, derive downstream.

### P2 — Input Surface Minimization

Before adding a new UI control or input field, ask: "Is this derivable from inputs already present?" If yes, derive it. If no, document why it is orthogonally independent.

**Trigger:** any proposal that adds a new input field, selector, upload control, or configuration option.

**Correct response:** demonstrate derivability or justify independence.

### P3 — UX Regression Test

A feature that introduces a new failure mode for the user (two fields that must agree but might not; a workflow that requires a precondition the user cannot see) is a UX regression, even if it adds net functionality.

**Trigger:** any feature where incorrect user input would produce silently wrong output, or where the user could reach an inconsistent state without a visible error.

**Correct response:** eliminate the inconsistency at the input level (P1/P2), or add a validation gate that surfaces the inconsistency before harm occurs.

---

## Checklist (run at Step 2 and Step 3)

Answer all five questions. A "Yes" answer is a finding — it must be addressed in the current step's output.

| # | Question | Finding if Yes |
|---|----------|---------------|
| Q1 | Does this feature add a new input field or control? | Apply P2: is it derivable from existing inputs? |
| Q2 | Does the new input need to be consistent with any existing input? | Apply P1: consolidate upstream |
| Q3 | Can the user reach an inconsistent state by providing different values to related fields? | Apply P3: add validation gate or eliminate the inconsistency |
| Q4 | Does this feature require the user to re-enter information the system already holds? | Apply P1: derive, don't re-ask |
| Q5 | If the user ignores or misunderstands the new input, will the output be silently wrong? | Apply P3: fail visibly or constrain the input surface |

---

## Output format

When this protocol applies, agents must include in their step output:

```markdown
### UX Coherence Check
**Applies:** Yes
**Trigger:** [which Q# triggered, and why]
**Findings:** [list of findings, one per triggered question]
**Resolution:** [how each finding is addressed]
```

If the cycle has no user-facing component:

```markdown
### UX Coherence Check
**Applies:** No
```

---

## Invocation points in the operational cycle

| Step | Role | Obligation |
|------|------|-----------|
| Step 2 | PRODUCT OWNER | Run checklist before writing acceptance criteria. Each finding becomes an acceptance criterion. |
| Step 3 | ARCHITECT | Run checklist before proposing structure. Each finding constrains the structural options. |
| Step 5 | CRITIC | Q3 and Q5 are standing items in the weakness analysis for any UI-touching feature. |

---

## Motivating example

*CMakeFile directory integration (2026-08):* When asked to add CMakeFile interpretation from a project directory, the correct design was to unify directory selection into a single input from which CTAGS, XRef, and CMake paths are all derived. The original proposal added a separate input for the directory, leaving the user able to specify inconsistent paths across three fields. Applying P1 at Step 3 would have identified the consolidation opportunity before implementation began.
