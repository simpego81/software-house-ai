---
date: 2026-07-26
cycle: N/A (constitutional amendment — Art. 12 process)
title: Constitutional amendment — Articles 16, 17, 18
status: active
---

## Context

A Three.js state machine animation was delivered blank because no process gate required validating the frontend output in a browser. Three agents (Developer, Reviewer, Tester) had no rules mandating execution-environment validation for HTML/JS deliverables. The failure was completely silent (`return null` with no log or visible fallback).

The incident exposed three gaps in the Constitution:

1. No article required validating deliverables in their native execution environment
2. No article prohibited silent failure in production-bound code
3. No article mandated a formal retrospective when a bug escaped the process

## Decisions

Three new articles approved by Owner (2026-07-26):

**Article 16 — Executable Validation**: Every deliverable must be validated in its native execution environment before being declared complete. Inspection and logical analysis are necessary but not sufficient.

**Article 17 — Visible Failure**: Silent failure is a violation of Article 6 (Transparency). Every failure mode must produce an observable signal (log, message, fallback state). A bare `return null` without any signal is incomplete code.

**Article 18 — Mandatory Process Retrospective**: When a defect reaches delivery that the process should have caught, a Process Gap Commission is mandatory. The Evolution Master is responsible if no other agent opens it. Output: updated rule + memory entry.

## Rationale

These three articles are generic principles extractable from the specific incident. They apply across all deliverable types — not just frontend:
- Art. 16 applies to Rust, embedded, docs, APIs, UI
- Art. 17 applies to any code that handles errors
- Art. 18 applies to any delivery defect regardless of domain

Each satisfies the Art. 12 test:
1. Limitation demonstrated (the Three.js incident)
2. Better principle proposed (specific, testable rules)
3. Validated on a real case (2026-07-26 incident documented in errors/)
4. Evolutionary capacity not reduced — increased (more validation → less rework)

## Consequences

- All 12 Software House agent files must now apply Art. 16 validation to their deliverables
- Art. 17 means any code review must flag silent failures as CRITICAL findings
- Art. 18 means the next time a bug escapes, opening a commission is not discretionary

## Related

- `memory/errors/2026-07-26-threejs-cdn-silent-failure.md` — the incident that triggered this amendment
- `protocols/frontend-checklist.md` — the operational rule derived from Art. 16 for frontend
- `protocols/review.md` — Process Gap Commission procedure (Art. 18 implementation)
