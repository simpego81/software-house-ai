# Skill: /open-cycle

Opens a new Software House AI operational cycle.

## Usage

```
/open-cycle "Problem statement"
```

## What this skill does

1. Verifies no cycle is currently open (`.swhouse/cycles/current.md` must not exist)
2. Determines the next cycle number from `metrics/summary.yaml`
3. Creates `.swhouse/cycles/current.md` with status `open`
4. Executes **Step 1 (Coordinator)** with the provided problem statement
5. Continues to **Step 2 (Product Owner)** automatically if the problem statement is clear

## Instructions for Claude Code

When `/open-cycle` is invoked:

1. Check if `.swhouse/cycles/current.md` exists. If yes, respond:
   > "A cycle is already open. Close it with `/close-cycle` before opening a new one."
   > Show the current cycle's problem statement.

2. Read `.swhouse/metrics/summary.yaml` and determine `next_cycle = total_cycles + 1`.

3. Create `.swhouse/cycles/current.md`:

```markdown
---
cycle: [NNN]
status: open
opened: [YYYY-MM-DD]
problem: "[problem statement from args]"
---
```

4. Execute Step 1 as the COORDINATOR agent (see `agents/10-coordinator.md` for output format).
   Write the output to `cycles/current.md` under `## Step 1 — Coordinator`.

5. Ask the user:
   > "Step 1 complete. Continue to Step 2 (Product Owner)? [Y/n]"
   
   If yes, proceed to Step 2 automatically.

## Example

```
/open-cycle "Define the format for memory entries in this project"
```
