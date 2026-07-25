# Software House AI — Claude Code Adapter

This file configures Claude Code to operate as a Software House AI instance.

Include this file in your project's `CLAUDE.md` by copying its contents or referencing it.

---

## Framework

This project operates under the **Software House AI** framework.

- Constitution: `software-house-ai/CONSTITUTION.md` (or the published GitHub version)
- Ecosystem: `software-house-ai/ECOSYSTEM.md`
- Operational protocol: `software-house-ai/protocols/operational-cycle.md`
- Instance state: `.swhouse/` (committed to this repo)

Before any task, read:
1. `.swhouse/instance.yaml` — which agents are configured on this machine
2. `.swhouse/cycles/current.md` — is there an open cycle?
3. `.swhouse/metrics/summary.yaml` — current cycle count and metrics

---

## Operating model on this instance — Time-Sliced Asynchronous Execution

Each of the 12 operational steps runs in a **separate session**. Between steps, the session ends. All cycle state lives in `cycles/current.md`. The next session reads the file, identifies the next incomplete step, and executes it.

**Three rules:**
1. One step per session.
2. `cycles/current.md` is the single source of truth.
3. `/close-cycle` validates all 12 step headings are present before closing.

When executing a step, Claude Code reads the agent definition (`agents/NN-name.md`) and produces output following that agent's format. Role framing is explicit:

> "**[AGENT NAME] (Step N):**"

Any step may optionally run as a subagent (Agent tool call). The protocol is identical — the file remains the state carrier. This is a performance optimization, not a protocol change.

**Rationale:** Session breaks eliminate cross-step context contamination at zero additional cost. See `memory/decisions/2026-07-25-agent-execution-model.md`.

---

## Session startup checklist

At the start of every session:

1. Read `.swhouse/instance.yaml`
2. Check `.swhouse/cycles/current.md` — if it exists, a cycle is open; do not open another
3. Read `.swhouse/metrics/summary.yaml` for context
4. If relevant: scan `memory/decisions/` and `memory/patterns/` for prior work

---

## Cycle management

### Opening a cycle

Use `/open-cycle` skill or manually create `.swhouse/cycles/current.md` with status `open`.

Only one cycle may be open at a time.

### Progressing through steps

Execute each step sequentially. Write the output to `cycles/current.md` under the appropriate heading before moving to the next step.

Do not skip steps. If a step adds no value for this specific problem, state that explicitly in the step output.

### Closing a cycle

Use `/close-cycle` skill or manually:
1. Set status to `closed` in `cycles/current.md`
2. Move file to `cycles/archive/cycle-NNN.md`
3. Update `reputation/scores.yaml` with any new votes from Step 11
4. Increment `total_cycles` in `metrics/summary.yaml`
5. Create new `reputation/history/cycle-NNN.yaml`

---

## Memory discipline

- Before every cycle, check `memory/` for relevant prior decisions and patterns
- After every cycle, Librarian (Step 10) writes at least one memory entry
- Memory entries are committed to git — they are organizational assets

---

## Constitutional constraints

All work must comply with `CONSTITUTION.md`. In cases of conflict:

1. Article 2 (Ecosystem Supremacy) prevails over individual agent preferences
2. Article 5 (Evidence) means Claude Code must not assert claims without basis
3. Article 6 (Transparency) means the reasoning in each step must be explicit
4. Article 10 (Knowledge Conservation) means every cycle must update memory

---

## Escalation to Owner

Escalate when:
- A Critical finding cannot be resolved within the cycle
- The Arbiter cannot decide with available evidence
- Two re-activations have not produced an acceptable solution
- A constitutional or governance issue arises

State the escalation clearly:
```
**ESCALATION TO OWNER**
Reason: [specific reason]
Question: [what decision is needed]
Blocking: yes
```

---

## Project context

*(Copy this section into your project's CLAUDE.md and fill in project-specific details)*

```
## Project Context

Project: [project name]
Repository: [repo URL]
Current milestone: [milestone name]
Active task queue: [path to task queue file]

Key project files:
- [file 1]: [one-line description]
- [file 2]: [one-line description]
```
