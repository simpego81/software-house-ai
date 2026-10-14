# ADR 0002 — Release the v2 operating model as an opt-in preview

**Date:** 2026-10-14
**Status:** accepted
**Supersedes in part:** the "no new protocol" freeze of [ADR 0001](0001-executable-runtime-pilot.md), for the v2 files listed below only

## Context

A falsification pass over the two assessments (`self-assessment/2026-10-14-stress-test-of-assessments.md` in the knowledge repository) found that:

- the diagnosis of the legacy process holds on the evidence available (one mature instance, one operator);
- the pilot cycles 003–006 only developed the runtime, were closed within minutes and used same-model challenges, so the pilot gates for cutover (five real v2 cycles) and for constitutional amendment (ten) are **not** met;
- the runtime had reproducible gaps that let an `enforced` cycle close without a real check.

## Decision

1. Fix the runtime gaps and keep their regression tests (`tests/test_hardening.py`).
2. Add `swhouse adopt` so existing v1 instances can opt in without losing or rewriting any legacy file, and roll back byte-for-byte.
3. Publish the v2 operating model as an **opt-in preview**: `protocols/operational-cycle-v2.md`, `instances/claude-code/CLAUDE-v2.md`, `docs/migration/v1-to-v2.md`.
4. Do **not** change `CONSTITUTION.md`, `ECOSYSTEM.md`, `agents/` or `protocols/operational-cycle.md`. Instances that do nothing keep the v1 behaviour.

## Consequences

- Both models coexist. An instance is v2 only after running `swhouse adopt --apply`.
- Evidence for cutover must come from real work on real instances, recorded in shadow mode first.
- Constitutional alignment stays blocked on the gates in `docs/roadmap/evolution-v2.md`.

## Rollback

`swhouse adopt --rollback --apply` removes what `adopt` created. Remove the preview documents from this branch to return to the 0.5.0 documentation set; the tag `pre-v2-cutover` marks the starting point.
