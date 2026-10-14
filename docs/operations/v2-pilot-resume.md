# v2 preview: where we stopped and how to resume

**Written:** 2026-10-14
**Branch:** `evolution/v2-operating-model` (worktree `software-house-ai-v2/`), based on `master` at `c370e77`; tag `pre-v2-cutover`
**Version:** 0.6.0a2. Nothing pushed.

## State

- v2 is an **opt-in preview**. `CONSTITUTION.md`, `ECOSYSTEM.md`, `agents/` and `protocols/operational-cycle.md` are unchanged.
- Runtime hardened (8 gaps closed), `adopt`/`--rollback`, `route`, `add-pending`/`resolve-pending`, `observe` added. 52 tests pass.
- Migration verified only on **copies** of the four sample instances (`prj_argo`, `prj_secretary`, `prj_personal`, `prj_adoplanner`): legacy state byte-identical after rollback.
- **No real project has run a v2 cycle yet.** The roadmap gates (5 real cycles for cutover, 10 for the Constitution) are not met. Pilot cycles 003–006 do not count.

## Not done

1. Choose the real test command for Argo. `node --test` used in trials was a placeholder.
2. Run `swhouse adopt` on a real project, in `shadow` mode.
3. Run at least 5 real cycles with `swhouse observe` (see `docs/migration/v1-to-v2.md`, section 7b).
4. In at least 2 STANDARD/GUARDED cycles, use a different model as CHALLENGE and record `--reviewer-context different-model`.
5. Decide: `enforced`, keep `shadow` with fixes, or `adopt --rollback --apply`.
6. Second project (`prj_secretary` or `prj_personal`) for cross-project confirmation. `prj_adoplanner` has zero cycles.
7. Merge to `master` has not been decided. The uncommitted changes (5 files) in `software-house-ai-repo/` are unrelated to this branch and were left untouched.

## Failure criteria (fixed before data, in `src/swhouse/observe.py`)

False blocks >= 2; escaped defects >= 1; cycles with manual edits >= 2; median minutes above the v1 baseline. Minimum sample: 5 cycles. Change them only before collecting data.

## Open limits

- Risk is declared by the agent that wants to close; the runtime rejects malformed values, not false ones.
- SHA-256 on evidence and on cycle files detects edits, not a rewrite of log and cycle together. A CI log outside the tree would be needed.
- Owner approval carries a reference the runtime cannot verify.
- `observe judge` is blocked for agents by the adapter prompt only, not by the runtime.
- Minutes are self-reported; no token or invocation counts exist, so the plan's "-40% invocations" is not verifiable.
- The NRC is not migrated automatically (Type-A to a required check, Type-H to pending-human items).
- Constitution Articles 7, 10, 15, 22, 23 were flagged as problematic in the assessment; no amendment was proposed.
- Linux figures in the two assessments need recomputing with a stated method; see `docs/assessments/2026-10-14-stress-test-of-assessments.md`.

## Where to look

| Need | File |
|---|---|
| Summary of the evolution and benefits | `docs/evolution-v2-summary.md` |
| Migrate a project, rollback, pilot procedure | `docs/migration/v1-to-v2.md` |
| Operating model | `protocols/operational-cycle-v2.md` |
| Agent rules | `instances/claude-code/CLAUDE-v2.md` |
| Why the preview is opt-in | `docs/decisions/0002-v2-opt-in-preview.md` |
| Falsification of the two assessments | `docs/assessments/2026-10-14-stress-test-of-assessments.md` |
| Roadmap and gates | `docs/roadmap/evolution-v2.md` |

## First command on return

```bash
git -C software-house-ai-v2 log --oneline -3
set PYTHONPATH=software-house-ai-v2\src          # the editable install points at software-house-ai-repo
python -m swhouse --root <copy-of-argo> doctor
```
