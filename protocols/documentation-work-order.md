# Documentation Work Order (DWO)

**Owner:** LIBRARIAN (Agent 07)  
**Version:** 1.0  
**Used at:** Step 10 of the operational cycle

---

## Purpose

A Documentation Work Order is the unit by which the LIBRARIAN delegates a specific documentation action to the agent with domain knowledge. The agent writes the content; the LIBRARIAN designs the location, format, and cross-references — and verifies the result.

A DWO is not a suggestion. It is a precise instruction with a defined verification criterion. It is closed only when the LIBRARIAN confirms that the output is correctly integrated into the knowledge graph.

---

## DWO Template

```
─────────────────────────────────────────────────────
DOCUMENTATION WORK ORDER
─────────────────────────────────────────────────────
ID:          DWO-<YYYY-MM-DD>-<NNN>
Issued by:   LIBRARIAN
Assigned to: <AGENT NAME>
Priority:    HIGH | MEDIUM | LOW
─────────────────────────────────────────────────────

TASK CONTEXT
Task:        <name of the cycle or task that generated this DWO>
Trigger:     <what output or event requires this documentation>

─────────────────────────────────────────────────────

ACTION
File:        <exact relative path from repo root>
Section:     <exact section heading or anchor, e.g. "## M1-T3 Event Logger">
Action:      ADD | UPDATE | SUPERSEDE | CREATE
             - ADD: insert new content into existing section
             - UPDATE: modify existing content in place
             - SUPERSEDE: replace entire section; mark old version [SUPERSEDED]
             - CREATE: create the file from scratch

─────────────────────────────────────────────────────

CONTENT SPECIFICATION
What to document:
  <describe the type and scope of content — not the actual text>
  Example: "Current implementation status of M1-T3: list what is done,
  what is partial, what is missing. Use factual language, no speculation."

Format reference:
  <template path, e.g. COMMUNICATION/TEMPLATES/impl_log.md §4.2>
  OR inline format:
  <define the exact structure here if no template exists>

─────────────────────────────────────────────────────

CROSS-REFERENCES
After completing this DWO, also update:
  - <path> → <what to change there>
  - <path> → <what to change there>

─────────────────────────────────────────────────────

VERIFICATION
The LIBRARIAN will verify:
  - [ ] Content is in the correct file and section
  - [ ] Format matches the specified template
  - [ ] All cross-references are updated
  - [ ] No contradictions introduced with: <list of related documents>
  - [ ] Document is reachable from: <entry point, e.g. DASHBOARD.md>

Status: OPEN | IN_PROGRESS | DONE | REJECTED
─────────────────────────────────────────────────────
```

---

## Example — M1-T3 implementation log

```
─────────────────────────────────────────────────────
DOCUMENTATION WORK ORDER
─────────────────────────────────────────────────────
ID:          DWO-2026-08-01-001
Issued by:   LIBRARIAN
Assigned to: DEVELOPER (Claude Code)
Priority:    HIGH
─────────────────────────────────────────────────────

TASK CONTEXT
Task:        M1-T3 Event Persistence (PARTIAL)
Trigger:     Implementation partially complete; state documents not updated

─────────────────────────────────────────────────────

ACTION
File:        tr4d3rz-persistence/COMMUNICATION/IMPLEMENTATION_LOG.md
Section:     ## M1-T3 Event Logger
Action:      UPDATE

─────────────────────────────────────────────────────

CONTENT SPECIFICATION
What to document:
  Current status: PARTIAL. List which components exist (event_logger.rs,
  schema.rs, lib.rs) and which are missing (main.rs, config/, systemd/,
  migrations/). State what works and what is blocked.

Format reference:
  tr4d3rz-docs/COMMUNICATION/TEMPLATES/ — impl_log standard section

─────────────────────────────────────────────────────

CROSS-REFERENCES
After completing this DWO, also update:
  - tr4d3rz-docs/COMMUNICATION/TASK_QUEUE.md → M1-T3 row: status IN_PROGRESS (PARTIAL)
  - tr4d3rz-docs/DASHBOARD.md → M1 task table, M1-T3 row: note "Library ✓, binary ✗"
  - tr4d3rz-docs/state/project_state.md → M1 progress entry

─────────────────────────────────────────────────────

VERIFICATION
The LIBRARIAN will verify:
  - [ ] Content is in IMPLEMENTATION_LOG.md under M1-T3 section
  - [ ] TASK_QUEUE.md row is consistent with log
  - [ ] DASHBOARD.md reflects same state
  - [ ] project_state.md does not contradict

Status: OPEN
─────────────────────────────────────────────────────
```

---

## Example — Primary Source Map (pre-cycle)

Issued at Step 0, before any agent begins work:

```
─────────────────────────────────────────────────────
PRIMARY SOURCE MAP
─────────────────────────────────────────────────────
Issued by:   LIBRARIAN
Task:        Build milestone visualization / any system representation
─────────────────────────────────────────────────────

PRIMARY SOURCES — must be read before producing any output:

  specs/hardware_function_matrix.md
    → Canonical inventory of all 13 hardware device classes,
      their roles (Evolution/Optimization/Persistence/Observatory/Gateway/Broker),
      and constraints

  specs/node-software-map.md
    → Software running on each hardware node, with repo origin and tech stack

  diagrams/node-deployment.d2
    → Physical deployment topology: which node connects to which, via which protocol

  diagrams/per-device/*.puml
    → Per-device ArchiMate views (14 files: rpi2, linux, esp, stm32f3, stm32f1,
      mimx, ra8, str, m24lr, tablet, phone, browser, android, php_hosting)

  protocols/MVP_INTERFACE_CONTRACTS.md
    → All payload schemas and topic contracts

  adr/ADR-0001-repository-structure.md through ADR-0004-ohlcv-data-contract.md
    → Accepted architectural decisions that constrain the implementation

DERIVED SOURCES — describe progress, do not define the system:

  COMMUNICATION/TASK_QUEUE.md   → task status, not system definition
  DASHBOARD.md                  → current progress snapshot, not architecture
  COMMUNICATION/IMPLEMENTATION_LOG.md → history, not specification

Navigation note:
  Entry point for hardware context is always hardware_function_matrix.md,
  not DASHBOARD.md or TASK_QUEUE.md.
─────────────────────────────────────────────────────
```

---

## Rules for issuing DWOs

1. **One action per DWO.** Do not bundle unrelated updates.
2. **Exact paths, no ambiguity.** "Update the docs" is not a DWO.
3. **Always specify cross-references.** No document is an island.
4. **Verification criteria must be checkable.** If you cannot verify it, the criterion is too vague.
5. **Retroactive DWOs are valid.** If an agent produced output without a DWO, issue one retroactively before Step 11.
6. **A DWO is closed only by the LIBRARIAN**, not by the executing agent.
