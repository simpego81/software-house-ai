# Protocol: User Feedback Capture

**Version:** 1.0  
**Status:** Active  
**Applies to:** All projects using the Software House AI framework

---

## Purpose

Ensure that every bug, regression, or UX observation reported by the operator in chat is captured as a non-regression checklist item within the same session — eliminating the pattern where the same issue must be reported multiple times across sessions.

---

## Trigger

This protocol activates when the operator reports ANY of the following in a chat message:

- A bug or unexpected behavior
- A regression (something that used to work and no longer does)
- A UX issue or inconsistency
- An incorrect output from an AI-generated feature

---

## Mandatory Actions (same session)

### 1. Acknowledge
The COORDINATOR must explicitly acknowledge the report before proceeding to fixes.

### 2. Capture to NRC
Before the session ends, the COORDINATOR must add at least one item to the project's Non-Regression Checklist (`memory/validation/non_regression_checklist.md`) for each reported issue:

```markdown
| NR-[AREA]-[NN] | [Description matching the user's report] | H | ⚠ PENDING | Procedure: [exact steps to reproduce and verify] |
```

- **Type H** (Human) if visual verification is required.
- **Type A** (Automated) if a Playwright/vitest test can be written.

### 3. Root Cause Note
Add a brief root-cause note to the memory error log (`memory/errors/`) if the bug reveals a systematic failure (not just a one-off typo).

### 4. Fix Protocol
After capturing, proceed to fix. The fix is NOT considered done until:
- Code change is implemented
- NRC item is added
- (For Type A items) Automated test exists or is planned

---

## Verification at Session Start

At every session startup (see `protocols/session.md`), the COORDINATOR must:

1. Read `memory/validation/non_regression_checklist.md`
2. Count and announce H-type PENDING items
3. If any H-type item relates to the current task domain, remind the operator to validate them during the session

---

## Anti-patterns to avoid

| Anti-pattern | Correct behavior |
|---|---|
| "I'll remember the bug" | No — write it to NRC immediately |
| "The fix is obvious, no need for NRC" | No — every fix without a test is a future regression |
| "I'll add NRC items at the end of the session" | No — add them when the bug is reported or fixed |
| "The SCIENTIST verified it on localhost" | No — use the operator's real dataset if specified in CLAUDE.md |

---

## Real Dataset Requirement

When a project specifies a validation dataset in `CLAUDE.md` (e.g., `C:\projects\SWDC\pi3_1\SWDC\AS-CX06_Main` for Argo), any fix affecting the validated functionality MUST be tested against that dataset before being declared complete.

The SCIENTIST step (Step 9) must include:
```
Real-dataset validation: [VERIFIED | PENDING_HUMAN]
Dataset: [path from CLAUDE.md]
Procedure: [exact steps]
```

A fix declared complete without real-dataset validation is considered PROVISIONAL (Article 16).
