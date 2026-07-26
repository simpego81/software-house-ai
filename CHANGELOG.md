# Changelog

All notable changes to the Software House AI framework are documented here.

Format: `[version] — YYYY-MM-DD`

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
