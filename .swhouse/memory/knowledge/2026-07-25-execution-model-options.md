---
created: 2026-07-25
updated: 2026-07-25
tags: [agent-architecture, execution-model, protocol]
---

## Summary

Comparative analysis of four execution models for running 12 agent roles with a single AI provider. Produced during Cycle 001.

## Details

### Approach A — Pure Internal Roles (Single Context)
All 12 steps in one session. Fast, zero overhead. Core weakness: structural context bias — the AI that writes Step 3 also writes Step 5 (Critic) and Step 6 (Destroyer). Anchoring bias is structurally possible.

### Approach B — Separate Subagent Processes
Each step is a separate Agent tool call. True cognitive independence. Cost: ~12x API calls per cycle. Provider-extensible (different models per role). Correct for high-stakes cycles; too expensive for routine use.

### Approach C — Hybrid (two-tier)
Lightweight roles (Coordinator, Librarian, Optimizer) run internally; cognitively demanding roles (Explorer, Critic, Destroyer, Scientist, Arbiter) run as subagents. Good balance, but introduces two-tier complexity. Target for v0.2.0.

### Alternative 3 — Time-Sliced Asynchronous (ADOPTED for v0.1.0)
Each step runs in a separate session. Session break = no shared conversation context = structural independence, same as Approach B. Cost = identical to Approach A. No infrastructure required beyond the existing file protocol.

**Key insight:** The session break is equivalent to a fresh subagent context at zero additional cost, because the AI starts each session by reading the file — not by continuing a conversation.

## Sources

- Cycle 001, Steps 3-9 (full comparative analysis)
- `memory/decisions/2026-07-25-agent-execution-model.md`
