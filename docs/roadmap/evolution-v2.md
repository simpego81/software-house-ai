# Software House AI v2 roadmap

**Status:** implementation pilot; opt-in preview published (see [ADR 0002](../decisions/0002-v2-opt-in-preview.md))
**Target:** evolve from a sequential role simulation to a risk- and evidence-driven organizational runtime

> **Gate status (2026-10-14).** Pilot cycles 003–006 developed the runtime itself, closed within minutes and used only `same-model` challenges. They do not count toward the "five real v2 cycles" gate of phase 2 or the "ten cycles" gate of phase 4. Those gates restart on real work in an adopted instance.

## Target model

The runtime recognizes responsibilities rather than permanent personae:

- `ROUTE`: frame value, scope and risk;
- `BUILD`: produce the change and self-test it;
- `CHALLENGE`: review the diff or artifact using an explicit context;
- `VERIFY`: execute configured checks and preserve evidence;
- `GOVERN`: apply deterministic policy and route exceptions to the Owner;
- `CURATE` and `EVOLVE`: triggered knowledge and process work, not mandatory cycle steps.

Execution profiles are `DIRECT`, `SPRINT`, `STANDARD`, `GUARDED`, `REVERT`, and `EXPERIMENT`. A profile defines evidence obligations, not a number of agents to invoke.

## Phases and gates

### 0 — Freeze and baseline

- No new constitutional article, permanent role, or protocol during the runtime pilot.
- Legacy state is inspected read-only and known drift remains visible.

### 1 — Executable core

- Machine-readable v2 cycles.
- Configured checks with retained evidence.
- Deterministic routing and close policy.
- Generated metrics and CI.
- At least three shadow cycles before changing the official operating model.

### 2 — Routing and catalog cutover

- Requires five v2 pilot cycles with complete verification evidence.
- Rewrite the official operational model around profiles and responsibilities.
- Keep legacy archive readers and provide a reversible migration.

### 3 — Reversibility and visibility

- First-class, tested REVERT path.
- Detection and recovery latency.
- CI/reporting provides visibility without creating another approver.

### 4 — Constitutional alignment

- Requires at least ten v2 cycles and a pilot review.
- Amend rules only to describe mechanisms already shown to work.
- Revisit mandatory memory, universal independent-agent claims, failure logging, VALIDATOR ownership, and NRC retirement.

### 5 — Scale experiments

- Domains and concurrent cycles require observed lock contention and genuinely independent work.
- Trust-scaled review requires stable identities and enough outcomes to support a meaningful baseline.

## Adoption decision

After the pilot, the Owner chooses one explicit outcome:

- `ADOPT`: gates met without observed quality regression;
- `REVISE`: direction retained, bounded correction required;
- `ROLLBACK`: runtime cost or reliability is worse than the legacy baseline.

Writing or implementing v2 does not predetermine adoption.
