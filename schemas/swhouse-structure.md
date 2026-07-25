# `.swhouse/` Directory Structure

This document defines the structure, schema, and semantics of the `.swhouse/` directory committed inside every project that uses the Software House AI framework.

**The `.swhouse/` directory is the versioned organizational memory of your instance.** It must be committed to git. It must never be ignored.

---

## Top-level structure

```
.swhouse/
  instance.yaml          ← agent configuration for this machine
  memory/
    decisions/
    patterns/
    errors/
    knowledge/
  reputation/
    scores.yaml
    history/
  cycles/
    current.md
    archive/
  metrics/
    summary.yaml
```

---

## `instance.yaml`

Declares which agents are available on the current machine and maps them to the 12 founding roles.

```yaml
framework_version: "0.1.0"
framework_repo: "https://github.com/simpego81/software-house-ai"

instance:
  machine: "string"          # descriptive label for this machine
  operator: "string"         # human operator name or identifier

agents:
  - role: "ROLE_NAME"        # one of the 12 founding roles (uppercase)
    provider: "string"       # e.g. claude, deepseek, gemini, unavailable
    model: "string"          # specific model identifier, optional
```

**Valid role values:** `ARCHITECT`, `EXPLORER`, `CRITIC`, `DESTROYER`, `BUILDER`, `OPTIMIZER`, `LIBRARIAN`, `SCIENTIST`, `PRODUCT_OWNER`, `COORDINATOR`, `EVOLUTION_MASTER`, `ARBITER`

**`provider: unavailable`** marks a role as absent. The operational protocol defines fallback behavior for each role.

Multiple roles may share the same provider. The provider executes each role sequentially with explicit role framing in the prompt.

---

## `memory/decisions/YYYY-MM-DD-title.md`

Records an architectural or process decision that was made during a cycle.

```markdown
---
date: YYYY-MM-DD
cycle: NNN
title: Short decision title
status: active | superseded | deprecated
superseded_by: YYYY-MM-DD-new-title.md   # if status is superseded
---

## Context
What situation prompted this decision.

## Decision
What was decided.

## Rationale
Why this option was chosen over alternatives.

## Consequences
What becomes easier or harder as a result.

## Confidence
High | Medium | Low — and why.
```

---

## `memory/patterns/pattern-name.md`

Documents a reusable solution pattern discovered during the project.

```markdown
---
discovered: YYYY-MM-DD
cycle: NNN
applicability: "brief description of when this applies"
---

## Problem
The recurring situation this pattern addresses.

## Solution
The reusable approach.

## Example
A concrete instance from this project.

## Known limitations
When this pattern does not apply.
```

---

## `memory/errors/YYYY-MM-DD-title.md`

Documents a failure, its cause, and the lesson extracted.

```markdown
---
date: YYYY-MM-DD
cycle: NNN
severity: low | medium | high | critical
---

## What failed
Description of the failure.

## Root cause
Analysis of what caused it.

## How it was detected
At what step and by which agent.

## Resolution
How it was corrected.

## Lesson
The extractable, reusable knowledge.
```

---

## `memory/knowledge/topic-name.md`

General knowledge base entries not tied to a specific decision, pattern, or error.

```markdown
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
---

## Summary
One paragraph overview.

## Details
Full content.

## Sources
- source 1
- source 2
```

---

## `reputation/scores.yaml`

Current cumulative reputation scores for all operators who have participated in cycles.

```yaml
version: 1
last_updated: YYYY-MM-DD
operators:
  - id: "operator-identifier"     # e.g. "claude-sonnet-4-6" or "alice"
    total_interventions: 0
    total_score: 0.0
    average_score: 0.0            # total_score / total_interventions
    last_intervention: null       # YYYY-MM-DD or null
```

Initial state: all operators have zero interventions and score `null`.

---

## `reputation/history/cycle-NNN.yaml`

Per-cycle reputation snapshot. Created when a cycle closes.

```yaml
cycle: NNN
closed: YYYY-MM-DD
interventions:
  - operator: "operator-identifier"
    step: 3                        # which operational step (1-12)
    role: ARCHITECT
    description: "brief description of the intervention"
    votes:
      - voter: CRITIC              # agent role that voted
        score: 7                   # 1-10
        rationale: "one sentence"
      - voter: SCIENTIST
        score: 8
        rationale: "one sentence"
    aggregate_score: 7.5           # mean of votes
    measurable_impact: "what concretely improved"
```

---

## `cycles/current.md`

The active operational cycle. Only one cycle is open at a time.

```markdown
---
cycle: NNN
status: open
opened: YYYY-MM-DD
problem: "Short description of the problem being addressed"
---

## Step 1 — Coordinator
**Agent:** [provider/model]
**Output:** [what the coordinator stated]

## Step 2 — Product Owner
**Agent:** [provider/model]
**Output:** [value definition]

## Step 3 — Architect
...

## Step 12 — Arbiter
**Agent:** [provider/model]
**Decision:** [decision text]
**Rationale:** [reasoning]
**Status:** decided | deferred | escalated-to-owner
```

When the cycle closes, this file is moved to `cycles/archive/cycle-NNN.md` and `current.md` is deleted (or reset).

---

## `cycles/archive/cycle-NNN.md`

Closed cycle records. Identical format to `current.md` with `status: closed` and a `closed` date in the frontmatter.

---

## `metrics/summary.yaml`

Aggregate performance metrics updated after each cycle closes.

```yaml
version: 1
last_updated: YYYY-MM-DD
total_cycles: 0
cycles_by_status:
  decided: 0
  deferred: 0
  escalated: 0
average_cycle_duration_days: null
memory_entries:
  decisions: 0
  patterns: 0
  errors: 0
  knowledge: 0
knowledge_reuse_rate: null        # % of cycles that referenced existing memory
evidence_rate: null               # % of decisions backed by data/experiment
```

---

## Versioning and migration

The schema version is defined in `instance.yaml` under `framework_version`.

When upgrading the framework, check the changelog for schema-breaking changes. Migration scripts (if required) are provided in the framework release notes.

Backward-incompatible schema changes increment the minor version (e.g. `0.1.0` → `0.2.0`). Patch versions (`0.1.1`) are always backward compatible.
