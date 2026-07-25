# Skill: /vote

Records a reputation vote for a specific intervention in the current or a recently closed cycle.

## Usage

```
/vote [operator-id] [step-number] [score] "[rationale]"
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `operator-id` | The identifier of the operator being voted on | `claude-sonnet-4-6` |
| `step-number` | Which cycle step the intervention occurred in | `3` |
| `score` | Integer from 1 to 10 | `8` |
| `rationale` | One sentence explaining the score | `"The Architect's decomposition reduced complexity by eliminating 3 unnecessary modules"` |

## Instructions for Claude Code

When `/vote` is invoked:

1. Parse all four parameters. If any are missing or invalid, prompt for them:
   > "Please provide: operator-id, step number (1-12), score (1-10), and a one-sentence rationale."

2. Validate the score is between 1 and 10.

3. Validate the rationale is non-empty (votes without rationale are not counted per the reputation protocol).

4. Determine the current cycle number from `cycles/current.md` (if open) or from the most recent archive.

5. Read the current `reputation/history/cycle-NNN.yaml` (create it if it does not exist).

6. Append the vote:
   ```yaml
   - operator: [operator-id]
     step: [step-number]
     role: [role name for that step]
     votes:
       - voter: [current agent role]
         score: [score]
         rationale: "[rationale]"
   ```

7. Recompute the `aggregate_score` for this intervention (mean of all votes).

8. Confirm:
   > "Vote recorded: [operator-id] Step [N] — Score [score]/10. Current aggregate: [aggregate]/10 ([N] votes)."

## Notes

- An operator cannot vote on their own intervention.
- Votes can be added at any time during or after a cycle (before the cycle state is archived beyond the current session).
- Use `/close-cycle` to finalize all votes and update cumulative reputation scores.
