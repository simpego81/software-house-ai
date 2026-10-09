# ADR 0001 — Validate an executable, evidence-driven runtime

**Date:** 2026-10-09
**Status:** accepted for pilot, not yet adopted as the official protocol

## Context

The current framework encodes most organizational controls in Markdown and asks one model to execute thirteen nominal roles. The empirical assessment that initiated this pilot found repeated drift between declared and actual state, unused roles, manual metrics, and high sequential overhead.

The repository itself provides useful baseline defects: an archived cycle still marked `open`, a closed cycle retaining an “awaiting Owner approval” marker, and memory counts that differ from `metrics/summary.yaml`.

## Decision

Build a provider-agnostic Python runtime in shadow mode before changing the Constitution or official operational protocol. The first increments will:

1. inspect legacy state without modifying it;
2. store new cycles as machine-readable YAML;
3. execute and retain check evidence;
4. apply deterministic routing and close policies;
5. derive metrics from archived events.

The pilot follows the accepted plan summarized in [`../roadmap/evolution-v2.md`](../roadmap/evolution-v2.md).

## Consequences

- Existing archives remain readable and untouched.
- V2 state uses separate `cycles/open/` and `cycles/archive-v2/` directories during the pilot.
- Official role and constitutional documents remain unchanged until the pilot gate is met.
- The runtime can be removed without migrating legacy data.

## Rollback

Remove the v2 runtime and its isolated v2 directories. Continue using the legacy Markdown process. No legacy file is rewritten by the pilot runtime.
