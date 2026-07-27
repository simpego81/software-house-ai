---
date: 2026-07-26
cycle: N/A (operational rule — Art. 11 process)
title: Human interface rule + explicit role announcement
status: active
---

## Context

The framework lacked two explicit rules about how the human operator interacts with the ecosystem and how agent transitions are made visible.

## Decisions

**Rule 1 — Single human interface (COORDINATOR)**

The human operator always directs requests to the COORDINATOR (Agent 10). The COORDINATOR is the permanent entry point. It delegates to other agents and ensures their outputs are visible to the human. The human retains the right to escalate directly to Owner/Arbiter level at any time — this is the exception, not the default.

**Rule 2 — Explicit role announcement during cycles**

During any operational cycle, every agent prefixes its output with `[ROLE_NAME]:` in the chat or terminal. Example: `[COORDINATOR]:`, `[ARCHITECT]:`, `[CRITIC]:`. Transitions between roles are announced. Outside formal cycles (informal conversation), no prefix is required.

**Transparency model**: output direct (not synthesized). The human sees each agent's output directly as it is produced — the team works visibly, not backstage.

## Rationale

Without a designated interface, the human must track which agent is relevant at any given moment — cognitive overhead. Without explicit role announcements, agent transitions are invisible, making the system opaque. Both rules are consistent with Art. 6 (Transparency) and Art. 9 (Self-Observation).

## Consequences

- `ECOSYSTEM.md`: COORDINATOR mission updated with "human interface" responsibility; Common Rules updated with role announcement convention
- `protocols/communication.md`: new "Human Interface" and "Agent Invocation" sections added
- `instances/claude-code/CLAUDE.md`: COORDINATOR-first session startup; `[ROLE]` prefix instructions for Claude Code

## Confidence

High. Both rules are operationally clear, consistently applicable, and approved by Owner 2026-07-26.
