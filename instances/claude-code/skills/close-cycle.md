# Skill: /close-cycle

Closes the current operational cycle, updates reputation, and archives the record.

## Usage

```
/close-cycle
```

## Prerequisites

- `.swhouse/cycles/current.md` must exist with status `open`
- Step 12 (Arbiter) must have been executed and the decision recorded

## What this skill does

1. Verifies the cycle is ready to close (Step 12 present and decided)
2. Sets cycle status to `closed` in `current.md`
3. Moves the file to `cycles/archive/cycle-NNN.md`
4. Updates `reputation/scores.yaml` with votes from Step 11
5. Creates `reputation/history/cycle-NNN.yaml`
6. Increments `total_cycles` in `metrics/summary.yaml`
7. Deletes `cycles/current.md`

## Instructions for Claude Code

When `/close-cycle` is invoked:

1. Read `.swhouse/cycles/current.md`. If it does not exist, respond:
   > "No open cycle found."

2. Check that Step 12 is present and contains a decision (ACCEPTED/REJECTED/DEFERRED/ESCALATED). If not:
   > "Step 12 (Arbiter) has not been completed. Complete all 12 steps before closing."

3. Update the frontmatter of `current.md`:
   ```yaml
   status: closed
   closed: [YYYY-MM-DD]
   ```

4. Determine the cycle number N from the frontmatter.

5. Write the file to `.swhouse/cycles/archive/cycle-[NNN].md`.

6. Read reputation nominations from Step 11 of the cycle. For each nomination:
   - Execute the voting process: prompt 3 other agents to vote (excluding the operator)
   - Compute the aggregate score
   - Write to `.swhouse/reputation/history/cycle-NNN.yaml`
   - Update operator's entry in `.swhouse/reputation/scores.yaml`

7. Update `.swhouse/metrics/summary.yaml`:
   - Increment `total_cycles`
   - Update `cycles_by_status` based on Arbiter's decision
   - Update `memory_entries` counts

8. Delete `.swhouse/cycles/current.md`.

9. Confirm to the user:
   > "Cycle [NNN] closed. Decision: [ARBITER DECISION]. Archive: `.swhouse/cycles/archive/cycle-NNN.md`"
   > "Commit the updated `.swhouse/` to git to share organizational state."
