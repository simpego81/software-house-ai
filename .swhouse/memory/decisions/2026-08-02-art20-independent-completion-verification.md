---
date: 2026-08-02
cycle: 002
title: Article 20 — Independent Completion Verification
status: active
---

## Context

A delivered animation was declared DONE while missing tooltips on interactive elements. Article 16 (Executable Validation) was satisfied — the artifact ran in its native environment — but the implementer validated their own work and had a blind spot for what they had not included. No rule required independent validation.

Process Gap Commission (Cycle 002) identified the failing gate as Article 16's absence of an independence requirement. The Art. 16 documentation example ("read by at least one agent other than the author") already implied independence for docs but did not generalize it.

## Decision

Add **Article 20 — Independent Completion Verification** to CONSTITUTION.md.

Core principle: every deliverable must be verified by an agent who did not produce it, with an adversarial mandate (find what is missing, not what works), using domain-specific methods.

If no domain method is defined → deliverable is PROVISIONAL, not DONE.

## Rationale

Classified as Article 12 (constitutional), not Article 11 (operational rule), because:
- Independence is a fundamental quality guarantee, not a workflow preference
- Operational rules can be silently waived under time pressure; constitutional articles cannot
- The principle must apply across all domains — including domains not yet encountered
- The PROVISIONAL fallback (Art. 17 alignment) prevents silent skipping when no method exists

## Consequences

- Every DONE declaration now requires evidence that a non-author verified the deliverable
- The SCIENTIST is the natural verifier in most design-cycle contexts
- Domain playbooks in `protocols/` specify verifier and method per deliverable type (follow-up item)
- Deliverables without a defined verification method are explicitly PROVISIONAL — visible, not silent

## Confidence

High — Scientist confirmed the rule would have caught the specific incident (tooltip gap). Cross-domain applicability confirmed for embedded (hardware-in-loop) and documentation (comprehension check).

## Related

- `errors/2026-08-02-animation-tooltip-gap.md` — the incident that triggered this amendment
- `decisions/2026-07-26-constitutional-amendment-16-17-18.md` — precedent (Art. 16/17/18 via Three.js incident)
