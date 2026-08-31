# Protocol: Bug Fix

**Version:** 1.0  
**Status:** Active  
**Applies to:** All projects using the Software House AI framework

---

## Purpose

Enforce a mandatory test-before-fix discipline. A fix implemented without a failing test is not a fix — it is a guess. Guesses cannot be verified, cannot be regressed against, and do not generate knowledge (Article 7, Article 10).

---

## The Rule

**No fix is implemented until a test exists that:**
1. Reproduces the exact failure (see `protocols/debug-faithful.md`)
2. Fails with the current code
3. Passes after the fix

A fix that lacks this test is PROVISIONAL (Article 16) regardless of how obvious the cause appears.

---

## Mandatory sequence

```
1. Receive bug report
2. Write reproduction test  → must FAIL (red)
3. Implement fix
4. Run test               → must PASS (green)
5. Run full regression    → no new failures
6. Add NRC entry (see protocols/user-feedback-capture.md)
7. Declare fix DONE
```

Skipping step 2 is not permitted. If the test cannot be written before the fix (e.g., requires framework scaffolding not yet in place), declare the fix PROVISIONAL and open a follow-up task for the test.

---

## Test type selection

| Bug category | Preferred test type |
|---|---|
| Algorithmic (wrong computation, wrong data structure) | Unit test (Vitest / Node.js) — milliseconds, no browser |
| UI behavior (panel not shown, button not responding) | Playwright E2E — headless Chrome |
| Visual appearance (wrong color, wrong size) | Playwright E2E with canvas pixel sampling |
| Performance regression | Benchmark test with threshold assertion |
| Data corruption (wrong state after operations) | Unit test on the relevant engine |

---

## What makes a test faithful (summary)

- Uses data of the same structural class as the real scenario
- Asserts the specific property that was broken, not a proxy
- Is deterministic and re-runnable without human interaction

---

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| "The fix is obvious, no test needed" | Obvious fixes have the highest regression rate — they skip edge cases |
| Writing the test AFTER the fix | The test cannot prove the fix works if it was never red |
| Using a 4-symbol fixture for a bug that only appears at real project scale | The test will always pass regardless of the fix |
| Testing "panel is visible" when the bug is "wrong caller in the tree" | Wrong property — the fix may be wrong even if the test passes |

---

## Urgency exception

If the operator requests an emergency fix without waiting for a test:
- Apply the fix immediately (operator's right)
- Open a follow-up NRC item marked `PENDING_TEST`
- The LIBRARIAN (Step 10) must not close the cycle until the `PENDING_TEST` items are resolved or explicitly deferred by the operator

Urgency does not eliminate the test — it defers it with a tracked obligation.
