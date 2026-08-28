# Protocol: Input Triage

**Version:** 1.0  
**Status:** Active  
**Applies to:** All projects using the Software House AI framework

---

## Purpose

Every operator message is evaluated by the COORDINATOR before any action is taken.
The triage classifies the request and determines the correct routing.
It is mandatory, fast, and visible.

---

## Trigger

Apply this protocol to every operator message that contains a substantive request.
Skip for: one-word confirmations ("ok", "procedi", "sì"), pure acknowledgments,
greetings with no request attached.

---

## Classification

For each substantive request, the COORDINATOR answers two questions:

**Q1 — Does this request reveal a gap in the software-house-ai framework?**  
A gap = a missing protocol, an inadequate rule, a process that consistently fails.  
Answer: YES | NO | MAYBE

**Q2 — Does this request require changes to the project (code, config, docs)?**  
Answer: YES | NO | MAYBE

| Q1 | Q2 | Classification |
|----|----|----------------|
| NO | YES | `project-work` |
| YES | NO | `framework-evolution` |
| YES | YES | `both` |
| MAYBE | * | `both` (safe default) |
| NO | NO | `meta` (question, conversation, no action needed) |

---

## Output Format

Emit exactly one line at the start of the response, before any action:

```
[TRIAGE: <classification> | <one-sentence routing decision>]
```

Examples:
- `[TRIAGE: project-work | proceeding with implementation]`
- `[TRIAGE: framework-evolution | proposing Cycle 011 before acting]`
- `[TRIAGE: both | opening cycle for protocol gap; applying trivial fix immediately]`
- `[TRIAGE: meta | answering directly]`

---

## Routing Rules

### `project-work`
Act immediately. Apply the appropriate workflow from CLAUDE.md (solo / cycle / worktree).

### `framework-evolution`
Before acting: propose opening a formal cycle. State the gap in one sentence.  
If a cycle is already open: propose accodamento — operator decides priority.

### `both`
Evaluate if the project-work part is trivial (< 5 min, < 10 lines):
- Trivial: apply the fix immediately, then propose a cycle for the framework gap.
- Non-trivial: propose a cycle that covers both dimensions.

### `meta`
Answer directly. No cycle, no action.

---

## Co-evolution Rule

Any cycle that modifies this protocol must also update the reference in `session.md`.
The LIBRARIAN step of that cycle must verify both files are consistent.
