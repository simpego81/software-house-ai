# Session Protocol

**Version:** 1.0

Every session operating under the Software House AI framework follows this startup sequence.

---

## Startup checklist

At the start of every session:

1. Read `instance.yaml` to identify active agents and framework version.
2. Check `cycles/current.md` — if it exists, a cycle is open. Read it and identify the next incomplete step.
3. Read `metrics/summary.yaml` for current project state.
4. If the session involves work in a domain where prior cycles exist: scan `memory/decisions/` and `memory/patterns/` for relevant prior work.
5. **Non-Regression Check:** Read `memory/validation/non_regression_checklist.md`. Count H-type PENDING items. If any relate to the current task domain, announce them explicitly: `[COORDINATOR]: ⚠ [N] NRC items PENDING human validation in this domain: [list IDs]`.
6. Greet as COORDINATOR: `[COORDINATOR]: Session resumed. [state current status in one line.]`

**User Feedback Capture rule (mandatory):** If the operator reports any bug, regression, or UX issue in chat, apply `protocols/user-feedback-capture.md` immediately — capture to NRC before the session ends. No exception.

If no cycle is open, the COORDINATOR receives the operator's request and decides:
- Answer directly (trivial question, no cycle needed)
- Open a cycle and delegate to the appropriate agent sequence
- Route to a specific agent for a focused sub-task

---

## Role announcement

During any formal cycle step, prefix every output with `[ROLE_NAME]:` — both in chat and in `cycles/current.md`.

Outside formal cycles (meta-conversation, quick questions): no prefix required.

---

## Time-sliced execution model

Each cycle step runs in a **separate session**. Between steps, the session ends. All cycle state lives in `cycles/current.md`. The next session reads the file, identifies the next incomplete step, and executes it.

Three rules:
1. One step per session.
2. `cycles/current.md` is the single source of truth.
3. The cycle does not close until the LIBRARIAN close checklist (Step 10) is complete.

---

## Human interface

The orchestrating agent assumes the **COORDINATOR** role by default at session start. Every operator request is received by the COORDINATOR, which decides how to route it.

Before routing, apply [`protocols/input-triage.md`](input-triage.md). The triage line `[TRIAGE: ...]` must appear at the start of every response to a substantive operator request.

The COORDINATOR must prefix all outputs with `[COORDINATOR]:` during formal cycle execution. When a cycle step hands off to another role, that role prefixes its outputs with its own `[ROLE_NAME]:` tag. Outside formal cycles, no prefix is required.

---

See [`operational-cycle.md`](operational-cycle.md) for the full cycle protocol.
