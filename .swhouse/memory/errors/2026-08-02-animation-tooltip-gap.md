---
date: 2026-08-02
cycle: 002
severity: medium
---

## What failed

An interactive animation deliverable was declared DONE with several elements lacking tooltips. A first-time viewer could not determine what each element represented without external context.

## Root cause

Article 16 (Executable Validation) was satisfied — the animation ran in the browser without errors. However, the implementer validated their own work. The blind spot: they knew what every element represented, so the missing tooltips were invisible to them.

No rule required an independent agent to perform the validation.

## How it was detected

Discovered by the Owner post-delivery during review.

## Resolution

Process Gap Commission (Cycle 002) opened per Article 18. Root cause identified as absence of independence requirement in validation gate. Constitutional amendment proposed and approved by Owner: Article 20 — Independent Completion Verification added to CONSTITUTION.md.

## Lesson

Validation by the implementer is not validation — it is self-certification. The implementer's context collapses the distinction between "correct" and "complete." An independent verifier with an adversarial mandate ("what is missing?") is structurally necessary, not optional.

## Related

- `decisions/2026-07-26-constitutional-amendment-16-17-18.md` — prior Art. 16/18 incident (same pattern: existing gate insufficient)
- `decisions/2026-08-02-art20-independent-completion-verification.md` — the rule that closed this gap
