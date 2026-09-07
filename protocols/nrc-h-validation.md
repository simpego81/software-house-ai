# Protocol: NRC H-Validation Lifecycle

**Version:** 1.0  
**Status:** Active  
**Applies to:** All projects using the Software House AI framework

---

## Purpose

The Non-Regression Checklist (NRC) contains two types of items:
- **Type-A:** automated — must pass on every `npm run test:e2e` (or equivalent).
- **Type-H:** human-validated — require an interactive session with the running application.

Type-H items accumulate debt when not verified. This protocol defines when and how they must be resolved, and provides a path from H→A (automation preferred).

---

## Triggers for H-validation

A validation session (see below) must be executed when **any** of these conditions is met:

1. **Module trigger:** the current cycle modifies a module listed in the NRC header. All Type-H items whose "Procedure" involves that module must be run.
2. **Age trigger:** any Type-H item has been PENDING for **5 or more cycles** since it was first added, regardless of which module the current cycle touches.
3. **Explicit trigger:** the operator requests a validation session.

The COORDINATOR checks both triggers at Step 1. The check must be explicit — the COORDINATOR must list which H-items are triggered and why, or state "no H-items triggered this cycle".

### Gaming prevention

The module trigger cannot be self-declared. The COORDINATOR must verify by diffing the cycle's changed files against the NRC module list. "This cycle did not touch NRC modules" requires listing the actual files changed and the NRC module list side-by-side.

---

## Validation session format

A validation session is a **Sprint-track cycle** (Steps 1, 7, 9, 10, 11, 12) whose sole purpose is executing H-items.

**Step 7 output:** the BUILDER lists each H-item to be verified with the exact procedure from the NRC.

**Step 9 output:** for each H-item, the SCIENTIST records:
```
NRC-ID: <id>
Procedure: <summary of what was done>
Observed: <what the app showed>
Result: VERIFIED | FAILED
Notes: <optional>
```

**Step 10:** the LIBRARIAN updates the NRC — `VERIFIED` items get status ✅; `FAILED` items get status ❌ and a new Sprint cycle is opened for the failing bug.

---

## Harness Validation Protocol

When a validation session uses an **automated harness** (e.g., Playwright script, CLI tool) to execute H-items, follow this protocol to prevent multi-iteration debugging of the harness itself on expensive real-dataset runs.

### Smoke-test before real-dataset

Before executing the full NRC H-validation session on real-dataset (e.g., SWDC AS-CX06_Main — 30 min run):

1. **Minimal fixture smoke-test:**
   - Run harness on minimal fixture (≤10 symbols, ≤5 files)
   - Expected duration: <5 min
   - Verify: selectors resolve, timing logic correct, no crashes

2. **Failure interpretation:**
   - Harness **fails minimal fixture** → **tool bug** (debug harness, re-run minimal)
   - Harness **passes minimal but fails real-dataset** → **scale-dependent issue** (LOD, performance, fixture assumptions like cmake scope, symbol availability)

3. **Proceed to real-dataset only after minimal fixture PASS.**

A harness that requires >2 iterations on real-dataset without prior minimal smoke-test has violated this protocol. The EVOLUTION MASTER (Step 11) must flag it and propose a harness improvement or smoke-test fixture definition.

**Rationale (Art. 11 evidence):**
- Evidence: Cycle 015 (Argo) required 5 iterations × 15-30 min = 75-150 min overhead debugging harness on SWDC (selectors, timing, indent formula, cmake scope)
- Impact: Smoke-test cost 5 min. Iteration cost saved 60-120 min. ROI 12:1 minimum.
- All 5 bugs would have been caught by minimal fixture.

---

## H→A conversion (preferred path)

Before executing a validation session, the LIBRARIAN (or COORDINATOR at Step 1) must review each H-item and assess:

> *"Can this be detected by a Playwright test or Vitest unit test?"*

If YES: convert H→A. Write the test first (failing). The item transitions to Type-A before the validation session. The test itself becomes the verification.

If NO: retain as H. Document why automation is not feasible in the NRC item row.

**Priority:** an H-item that can be automated MUST be automated before the next cycle that touches its module. Converting H→A is preferred over running H manually.

---

## Age limit enforcement

| Age (cycles since item was added) | Required action |
|---|---|
| 1–4 | No action required unless module trigger fires |
| 5 | Validation session required. The cycle that triggers age-5 cannot be ACCEPTED until the session is complete (or until the item is converted H→A). |
| >5 | Escalate to operator: item is blocking new cycles in its domain. |

The ARBITER (Step 12) may not issue ACCEPTED to a cycle that triggered the age-5 condition without evidence that all triggered H-items have been run.

---

## NRC item lifecycle

```
ADDED (PENDING)
    │
    ├─ H→A conversion? ──YES──► Type-A item ──► automated every test run
    │
    NO
    │
    ▼
PENDING (age 1–4: no action)
    │
    ▼
PENDING (age 5: validation session required)
    │
    ├─ VERIFIED ──► ✅ in NRC; remains as H-item; re-checked after next major change
    │
    └─ FAILED ──► ❌ in NRC; open Sprint cycle for bug; convert to A after fix
```

---

## Relationship to other protocols

- `protocols/operational-cycle.md` Step 1: COORDINATOR checks triggers (module + age).
- `protocols/operational-cycle.md` Step 10: LIBRARIAN updates NRC status after session.
- `memory/validation/non_regression_checklist.md`: authoritative NRC per project instance.
- `memory/validation/validation_matrix.md`: maps NRC items to validation targets (runbooks).

---

## Co-evolution rule

Any cycle that adds a new NRC Type-H item must also update `validation_matrix.md` with a target that covers that item. A Type-H item with no corresponding matrix target is unverifiable and must be treated as Type-A until a runbook is written.
