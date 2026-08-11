# Changelog

All notable changes to the Software House AI framework are documented here.

Format: `[version] — YYYY-MM-DD`

---

## [0.3.0] — 2026-08-11

### Added (constitutional amendment — Article 12)

- **Article 24 — Validation Infrastructure Ownership**: introduces the VALIDATOR role as a standing infrastructure agent. Every instance must maintain a validation matrix covering all deployment targets. No deliverable may be validated only on localhost when real targets exist.
- **AGENT 13 — VALIDATOR** in `ECOSYSTEM.md`: role definition, responsibilities, and invocation points.

### Updated (operational rules — Article 11)

- **Step 1 (COORDINATOR)**: must verify the validation matrix covers all targets affected by the cycle before proceeding to Step 7.
- **Step 9 (SCIENTIST)**: must read from the VALIDATOR matrix; localhost validation does not substitute a real-target entry.
- **Step 10 (LIBRARIAN)**: must update the validation matrix if infrastructure changed during the cycle.
- **Missing Roles table**: added VALIDATOR with High criticality and fallback procedure.

### Motivation

Retrospective from Consilium Cycle 4: a frontend deliverable was validated on localhost only. The Pi target — the only one with real data — was not validated. Root cause: no agent owned the validation configuration. The VALIDATOR role closes this gap at the constitutional level.

---

## [0.2.1] — 2026-07-26

### Added (operational rules — Article 11)

- **Human interface rule**: the human operator always directs requests to the COORDINATOR (Agent 10),
  which is the permanent entry point. Other agents are invoked by the COORDINATOR and their outputs
  are shown directly to the human. Owner retains the right to escalate directly at any time.
- **Explicit role announcement**: during operational cycles, every agent prefixes its output with
  `[ROLE_NAME]:` in the chat or terminal, making agent transitions visible to the human operator.
  Outside formal cycles, no prefix is required.

### Updated

- `ECOSYSTEM.md` — COORDINATOR mission: added "permanent human interface" responsibility;
  Common Rules: added role announcement convention
- `protocols/communication.md` — new "Human Interface" section + "Agent Invocation" section
  with format, rules, and rationale
- `instances/claude-code/CLAUDE.md` — "always start as COORDINATOR" rule; `[ROLE]` prefix
  instructions for Claude Code during cycles

---

## [0.2.0] — 2026-07-26

### Constitutional Amendment (Articles 16–18)

Triggered by incident: Three.js frontend animation delivered blank due to silent CDN failure
and absence of execution-environment validation in any process gate.

- **Article 16 — Executable Validation**: every deliverable must be validated in its native
  execution environment before being declared complete. Code inspection alone is insufficient.
- **Article 17 — Visible Failure**: silent failure is a constitutional violation. Every failure
  mode must produce an observable signal (log, message, or visible fallback). Bare `return null`
  without any signal is incomplete code.
- **Article 18 — Mandatory Process Retrospective**: when a defect reaches delivery that the
  process should have caught, a Process Gap Commission is mandatory within the next cycle.
  The Evolution Master is responsible if no other agent opens it.

### Added

- `protocols/frontend-checklist.md` — mandatory checklist for HTML/JS/WebGL deliverables
  (CDN loading order, browser observation, onerror, WebGL try/catch, graceful fallback)
- `protocols/review.md` — Process Gap Commission section (Article 18 operational implementation)

### Updated

- `protocols/operational-cycle.md` — Step 9: frontend deliverables require browser observation;
  logical inspection alone does not satisfy verification
- `agents/05-builder.md` — frontend CDN loading order rule in interaction rules
- `agents/08-scientist.md` — "Browser observation" added to verification methods table

---

## [0.1.0] — 2026-07-25

### Added

- `CONSTITUTION.md` — 15 foundational articles
- `ECOSYSTEM.md` — 12 founding agent definitions, governance hierarchy, operational protocol, reputation system
- `INSTALL.md` — step-by-step bootstrapping guide
- `protocols/operational-cycle.md` — 12-step cycle with escalation and missing-role handling
- `protocols/communication.md` — file-based, asynchronous communication protocol
- `protocols/review.md` — review criteria, approval thresholds, veto rules
- `protocols/reputation.md` — voting-based reputation system specification
- `schemas/swhouse-structure.md` — `.swhouse/` directory schema and file formats
- `agents/01-architect.md` through `agents/12-arbiter.md` — individual agent specifications
- `instances/claude-code/CLAUDE.md` — Claude Code reference adapter
- `instances/claude-code/skills/` — four Claude Code skills: open-cycle, close-cycle, vote, query-memory
- `instances/claude-code/.swhouse-template/` — ready-to-copy instance state template

### Status

Bootstrap phase. The organization is building itself.
The 10 objectives of the First Mission (defined in `ECOSYSTEM.md`) are in progress.
