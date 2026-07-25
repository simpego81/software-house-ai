# Communication Protocol

**Version:** 1.0

---

## Overview

Communication between agents in the Software House AI is **file-based and asynchronous**. All inter-agent communication is recorded in the cycle record (`cycles/current.md`). There is no real-time messaging channel — the cycle document is the shared workspace.

This design ensures:
- Every agent contribution is logged and attributable
- The conversation is reproducible and auditable
- Any agent that can read and write Markdown can participate

---

## Primary channel: the cycle record

All agent outputs during a cycle are written to `cycles/current.md` under the corresponding step heading.

Each agent reads all previous steps before producing its output. This is the only synchronization mechanism.

**Sequential order is enforced.** An agent may not skip ahead or write to a step that is not yet its turn.

---

## Inter-step references

An agent may reference a previous step's output using the step number:

> "As identified in Step 3 (Architect), the proposed module boundary creates a coupling risk."

Do not copy-paste large blocks from previous steps — reference them by step number.

---

## Proposals and counter-proposals

When an agent disagrees with a previous step's output, it must:

1. Acknowledge the previous proposal explicitly
2. State what it disagrees with and why
3. Offer a concrete alternative or improvement

An agent may not simply reject a proposal without offering an alternative (Article 4 — Constructive Criticism).

---

## Confidence and assumption labeling

Every agent output must include:

- **Confidence:** High | Medium | Low
- **Assumptions:** a list of assumptions the output rests on

Format:

```
**Confidence:** Medium
**Assumptions:**
- The system will handle at most 1000 concurrent users
- The database schema is finalized (not verified)
```

---

## Fact vs. hypothesis labeling

Agents must distinguish:

- **FACT:** verifiable, cited, or measured
- **HYPOTHESIS:** reasonable assumption not yet verified
- **OPINION:** judgment that depends on values or priorities

Example:

> - FACT: The current implementation has O(n²) complexity (measured in Step 9)
> - HYPOTHESIS: This will become a bottleneck above 10,000 records
> - OPINION: This trade-off is acceptable for the current project phase

---

## Escalation

An agent may escalate any issue to Owner by adding an `ESCALATION` block to its step:

```markdown
---
**ESCALATION**
**Reason:** [why Owner input is required]
**Question:** [specific decision requested]
**Blocking:** yes | no
---
```

A blocking escalation pauses the cycle until Owner responds. A non-blocking escalation is logged and the cycle continues.

---

## Out-of-cycle communication

Some communication occurs outside the 12-step cycle:

| Type | Location | Format |
|------|----------|--------|
| Memory queries | `memory/` | Read existing files |
| Reputation votes | `reputation/history/` | Per-cycle YAML |
| Process improvement proposals | `cycles/current.md` Step 11 | Protocol section |
| Constitutional amendment proposals | Dedicated cycle, flagged | Cycle record with `type: constitutional-amendment` |

---

## Git history protection

The `.swhouse/` directory is the organizational memory. Its git history is the audit trail for all decisions made by the ecosystem.

**Rule:** Commits that touch `.swhouse/` must never be rewritten. Specifically:
- No `git push --force` on any branch containing `.swhouse/` commits
- No `git rebase` that removes or rewrites `.swhouse/` commits
- No `git commit --amend` on commits that include `.swhouse/` changes

This rule is grounded in Article 6 (Transparency) and Article 7 (Memory) of the Constitution. Violation invalidates the audit trail and is treated as a protocol breach. Decided in Cycle 001.

Exception: the Owner may explicitly authorize a rewrite to correct a security incident (e.g., accidental commit of credentials). Any such exception must be documented in a new memory entry.

---

## Communication between instances on different machines

When multiple operators work on the same project from different machines, coordination happens through git:

1. Before opening a cycle: `git pull` to sync latest state
2. Only one cycle may be open at a time — check `cycles/current.md` exists before opening
3. After closing a cycle: `git push` immediately to prevent conflicts
4. If two operators open cycles simultaneously (conflict): escalate to Owner to decide which cycle takes precedence; the other is archived as SUPERSEDED

---

## Formatting rules

All cycle record entries must follow these conventions:

- Use Markdown headers (`##`) for each step
- Bold labels for metadata fields: `**Confidence:**`, `**Decision:**`
- Horizontal rules (`---`) to separate major sections within a step
- No HTML — Markdown only
- Code blocks for all code, configuration, and schema fragments
