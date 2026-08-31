# Protocol: Faithful Reproduction

**Version:** 1.0  
**Status:** Active  
**Applies to:** All projects using the Software House AI framework

---

## Purpose

Prevent the "fix at a guess" anti-pattern: implementing a fix without first verifying that the exact failure mode is reproducible and that the fix actually resolves it.

Every user-reported bug must be reproduced faithfully — using data and conditions that match the user's actual scenario — before any fix is attempted.

---

## Trigger

This protocol activates at Step 3 (ANALYZE) of any cycle that includes a bug fix reported by the operator.

It also activates during a Live Debug Session (see `protocols/live-debug-session.md`) whenever the operator reports an anomaly.

---

## The Faithful Reproduction Requirement

A reproduction is **faithful** if it satisfies all three of the following:

1. **Same data class**: uses data of the same type and scale as the operator's scenario (e.g., a real embedded C project with duplicate function names, not a 4-symbol synthetic fixture)
2. **Same failure property**: verifies the exact property the operator observed as broken, not a proxy (e.g., "IP_WIFI_Init must NOT appear in USB_Bulk.c::_Init's caller tree", not "the panel is visible")
3. **Automated**: runs without human interaction so it can be re-executed on every future change

A reproduction that fails any of these three is **incomplete** and cannot serve as the basis for declaring a fix done.

---

## Procedure

### Step R1 — Extract the minimal scenario

From the operator's report, identify:
- The exact input data that triggers the bug (extract a minimal slice from the real project if possible)
- The exact observable property that is wrong
- The exact expected correct behavior

### Step R2 — Write a failing test

Write an automated test (unit or E2E) that:
1. Uses the minimal scenario data from Step R1
2. Asserts the **correct** behavior
3. **Fails** with the current (buggy) code

Run the test. Verify it fails for the right reason. If it does not fail, the scenario does not reproduce the bug — go back to Step R1.

### Step R3 — Implement the fix

Implement the minimal fix. No refactoring beyond scope.

### Step R4 — Verify green

Run the test from Step R2. It must pass. If it does not, the fix is incomplete — go back to Step R3.

### Step R5 — Regression guard

Confirm no previously-passing tests now fail. A regression introduced by the fix is a blocking condition (Article 25).

---

## Fixture quality rules

| Rule | Rationale |
|---|---|
| Prefer slices of real project data over synthetic fixtures | Synthetic data cannot exercise emergent behaviors from scale and real naming conventions |
| If real data cannot be used (privacy, size), construct a minimal synthetic fixture that exercises the exact structural property | "One function named Init in two files" is a structural property — it can be synthetic |
| Document the fixture's origin in a comment | Future developers must know what real scenario it represents |
| Store realistic fixtures in `tests/fixtures/realistic/` | Separate from tiny synthetic fixtures in `tests/fixtures/` |

---

## What this protocol does NOT require

- Full project data in every test (extract the minimal relevant slice)
- Visual screenshot comparison for every bug (only when the bug is visual)
- Running the full pipeline for algorithmic bugs (unit tests are faster and more reliable)

---

## Relationship to other protocols

- `bug-fix.md`: defines the mandatory test-before-fix rule
- `user-feedback-capture.md`: Step 0 of capture now requires faithful reproduction
- `live-debug-session.md`: Step 3 (Analyze) must attempt reproduction before Step 5 (Fix)
