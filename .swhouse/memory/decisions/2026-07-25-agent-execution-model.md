---
date: 2026-07-25
cycle: 001
title: Agent execution model — Time-Sliced Asynchronous Execution
status: active
---

## Context

The framework defines 12 agent roles. Before any cycle could run, the framework needed to specify how a single AI provider executes all 12 roles without pre-built subagent infrastructure.

## Decision

**Time-Sliced Asynchronous Execution** is the operational model for v0.1.0.

Each of the 12 steps is executed in a separate AI session. Between steps, the session ends. All state lives in `cycles/current.md`. The next session reads the file, identifies the next incomplete step, and executes it.

Three rules:
1. One step per session.
2. `cycles/current.md` is the single source of truth.
3. `/close-cycle` validates all 12 step headings are present before closing.

Any step may optionally be executed as a subagent (Agent tool call). The protocol is identical — the file is the state carrier. This is an optimization, not a protocol change.

## Rationale

Three alternatives were considered (Approaches A/B/C plus Explorer Alternative 3). The Time-Sliced model was initially the Explorer's proposal. It was adopted because:

- Session breaks eliminate cross-step context contamination (the core independence problem of single-session execution)
- Zero cost overhead vs single-session approach — same per-token cost, no additional infrastructure
- The file-based state protocol is already the framework's foundation; this model is a natural extension

## Consequences

- `/open-cycle` skill must NOT auto-continue to Step 2 (updated in this cycle)
- `.swhouse/` git history must not be rewritten (rule added to communication protocol)
- v0.2.0 target: Approach C hybrid — steps requiring high cognitive divergence (EXPLORER, CRITIC, DESTROYER, SCIENTIST, ARBITER) run as subagents by default

## Confidence

High — core independence guarantee is logically verified. Empirical quality comparison deferred to after first 10 cycles.
