# Migrating a project from Software House AI v1 to the v2 preview

**Audience:** an Owner or operator with a project that already has a `.swhouse/` directory created by v1 (framework 0.1.0–0.5.0).
**Status:** opt-in preview. Nothing here is mandatory, and nothing in v1 stops working.
**Time:** about 15 minutes for the mechanical part; the first real cycle is where you learn whether it suits the project.

## 1. Decide whether to migrate

Migrate if the project is active and you recognise at least one of these:

- `summary.yaml` drifts from the archive and nobody trusts it;
- cycles stay `IN PROGRESS` or `open` after they are done;
- most real work already skips steps 2–6 and the ceremony is a tax;
- you want executable evidence behind `ACCEPTED`.

**Do not migrate** a project with no recent cycles (the framework cost is never amortised: `prj_adoplanner` had zero cycles), or one that is about to end. Staying on v1 is a valid, supported choice.

Evidence behind the recommendation is limited: one mature instance, one operator. It is a hypothesis you are testing on your project, not a proven improvement.

## 2. Prerequisites

- Python 3.10+, Git, and a clean commit of `.swhouse/` so rollback has a reference.
- No open v1 cycle: `.swhouse/cycles/current.md` must not exist. Close it under v1 first. The runtime refuses to start a v2 cycle while it exists.
- The framework checkout you want on disk, at the preview branch or tag.
- At least one command that can fail for a real reason (test suite, build, linter). v2 closes cycles on executable evidence; without one, `enforced` mode cannot close anything.

Install the runtime **from the checkout you mean to use**:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1      Linux/macOS: source .venv/bin/activate
python -m pip install -e /path/to/software-house-ai
swhouse --root . doctor
```

An editable install points at the directory you installed from. If you keep several checkouts (for example a branch worktree), verify with `python -c "import swhouse; print(swhouse.__file__)"`.

## 3. Step by step

### 3.1 Look before touching

```bash
swhouse doctor
```

`doctor` is read-only. It reads both v1 layouts (YAML frontmatter and `**Status:**` header). Expect findings about your own history, for example:

| Code | Meaning | Typical cause |
|---|---|---|
| `ARCHIVED_NOT_CLOSED` | An archived cycle says open or in progress | Status never updated at close |
| `STALE_STATUS_HEADER` | Header says open, a later line says closed | Header written at open, never edited |
| `CYCLE_NUMBER_GAP` | A number is missing from the archive | Cycle abandoned or archived under another name |
| `LEGACY_CYCLE_COUNT` | `summary.yaml` disagrees with the archive | Manual counter drift |
| `MEMORY_COUNT` | Memory counts disagree with files | Entries added without updating the summary |

These are observations about the past. Do not rewrite old cycles to silence them.

### 3.2 Dry run

```bash
swhouse adopt --check "tests=python -m pytest"
```

It prints what it would create and writes nothing. `--check` may be repeated. The command is split on spaces, so keep it simple; for anything with quoting, edit `validation.yaml` afterwards.

### 3.3 Adopt

```bash
swhouse adopt --apply --check "tests=python -m pytest"
```

Creates only new paths inside `.swhouse/`:

| Path | Purpose |
|---|---|
| `config.yaml` | `mode: shadow`, `concurrent_cycles: false` |
| `validation.yaml` | The checks you declared. This is the close contract |
| `doctor-baseline.yaml` | Today's known **errors**, so they show as `KNOWN` and new ones fail |
| `adoption.yaml` | Manifest with a SHA-256 for each created file, used by rollback |
| `cycles/open/`, `cycles/archive-v2/`, `evidence/`, `metrics/generated.json` (later) | v2 state, separate from v1 |

It does not read for write or modify: `cycles/archive/`, `cycles/current.md`, `memory/`, `reputation/`, `metrics/summary.yaml`, `instance.yaml`. It refuses to run if `config.yaml` or `validation.yaml` already exist.

Check: `swhouse doctor` now exits 0, errors shown as `KNOWN`, warnings still visible.

### 3.3b What to put in `validation.yaml`

Each check needs `id`, `command` (a list, no shell), `profiles`, `required`, `timeout_seconds`. Add one entry per thing that must pass before work is accepted: tests, type check, lint, build. Pick commands that fail when the work is wrong. A check that always exits 0 satisfies the policy and proves nothing.

### 3.4 Swap the adapter

Replace the framework section of the project's `CLAUDE.md` with the contents of `instances/claude-code/CLAUDE-v2.md`. Keep your project-specific sections. The v2 adapter drops the one-step-per-session rule and the role prefixes, and tells the agent to call `swhouse` instead of editing cycle files.

Other agents (Codex, Cursor, Gemini…) need the same rules in whatever instruction file they read. The runtime is agent-agnostic; only this adapter is Claude-specific.

### 3.5 Run one real cycle in shadow mode

```bash
swhouse route --risk reversible=true --risk native_verification_available=true --risk blast_radius=low
swhouse start "<real task>" --profile SPRINT --criterion "<observable outcome>" \
  --risk reversible=true --risk native_verification_available=true --risk blast_radius=low
swhouse set-change "commit:<sha>"
swhouse run-check tests
swhouse criterion AC-01 met
swhouse close            # read the output
swhouse close --apply
swhouse metrics
```

In `shadow` mode the recorded outcome is what v2 policy **would** have decided. It does not replace your official v1 decision. Compare the two on every cycle and note disagreements: they are the data you need.

## 4. What happens to each v1 artifact

| v1 artifact | After adoption | Action for you |
|---|---|---|
| `cycles/archive/cycle-NNN.md` | Untouched, still read by `doctor` | None. New v2 numbers continue after the highest v1 number |
| `cycles/current.md` | Blocks `swhouse start` while present | Close the v1 cycle first |
| `metrics/summary.yaml` | Untouched and **no longer updated** | Treat as frozen history. `doctor` will keep warning about its drift until you decide to archive it |
| `metrics/generated.json` | New, derived by `swhouse metrics` | Never edit it |
| `reputation/` | Untouched, dormant | Ignore. v2 has no reputation |
| `memory/decisions`, `errors`, `knowledge`, `patterns` | Untouched, still valid | Keep reading them. Write new entries only under the v2 triggers |
| `memory/validation/validation_matrix.md` | Untouched | Port the **automatable** targets into `validation.yaml`. Targets that need a human become pending-human items |
| `memory/validation/non_regression_checklist.md` (NRC) | Untouched | **Not migrated automatically.** See below |
| `instance.yaml` (13 agents) | Untouched | The v2 runtime ignores the role list |
| `CLAUDE.md` | You change it (3.4) | Revert it to roll back |

### NRC: the known gap

The preview does not import the NRC. Suggested handling:

- **Type-A items:** if one command runs them (for example the whole test suite), make that command a required check in `validation.yaml`. That is the strongest enforcement of Article 25 you can get.
- **Type-H items:** keep the NRC file. When a cycle touches the relevant module, open a pending item (`swhouse add-pending H-7 "<procedure>" --owner <name>`). Each resolves as `verified`, `converted` to an automated check, or `waived` with an expiry and the Owner's decision reference. This gives the long-pending H items a deadline instead of leaving them indefinitely.

In one mature instance, 23 of 26 Type-H items were pending. Expect to spend a session converting or waiving them.

## 5. v1 concepts and their v2 counterparts

| v1 | v2 |
|---|---|
| 12 steps, one role each | Profile (DIRECT, SPRINT, STANDARD, GUARDED, REVERT, EXPERIMENT) with evidence obligations |
| Track S / M / F / SA | SPRINT / STANDARD / GUARDED. `SA` has no equivalent: use STANDARD and a written experiment |
| COORDINATOR picks the track | `swhouse route` computes the minimum profile from declared risk |
| SCIENTIST narrative verdict | `swhouse run-check` with retained, hashed output |
| ARBITER decision | `swhouse close`. The Owner decides exceptions |
| `ACCEPTED WITH CONDITIONS` | Does not exist. Use a check, a pending-human item or DEFERRED |
| `PENDING_HUMAN` in prose | `swhouse add-pending` / `resolve-pending` with owner and deadline |
| VALIDATOR agent | `.swhouse/validation.yaml` |
| LIBRARIAN step 10 checklist | Memory only on triggers; indexes are derived |
| EVOLUTION MASTER every cycle | Triggered review (escaped defect, three overrides, degrading metric, ten new cycles) |
| Reputation, quality score 1–5 | Not in the preview |
| "One cycle at a time" | Still the default. Parallel cycles are off |

## 6. Rollback

```bash
swhouse adopt --rollback            # dry run
swhouse adopt --rollback --apply
```

Removes only what `adopt` created and only if unmodified since (compared by SHA-256). Files you edited are kept and listed. Directories that contain v2 cycles or evidence are kept. Afterwards restore your `CLAUDE.md`.

On copies of the four sample instances (`prj_argo`, `prj_secretary`, `prj_personal`, `prj_adoplanner`) a full `adopt --apply` followed by `adopt --rollback --apply` left every file byte-identical. That result is for those four layouts; keep your own commit as the real safety net.

If you want to keep the v2 cycles you ran, copy `cycles/archive-v2/` and `evidence/` elsewhere before rolling back.

## 7. Gates: when to switch from shadow to enforced

Stay in `shadow` until you have, on real work in this project:

- at least five v2 cycles closed with complete evidence;
- no manual edit of any generated file;
- a note, for each cycle, of whether v2 policy and your v1 judgement agreed, and why not when they did not;
- at least one cycle where a required check failed and stopped something you would otherwise have accepted.

Then change `mode: enforced` in `config.yaml`. In `enforced` mode:

- `validation.yaml` must declare at least one required check for the profile;
- GUARDED needs `swhouse approve <owner> --ref <external proof>` **by the Owner**, and one challenge from a different model, a human or a tool;
- cycle records carry `governance_mode: enforced`, and metrics report them separately.

These thresholds are the framework's own roadmap gates (`docs/roadmap/evolution-v2.md`). They are a starting rule, not a proven standard.

## 7b. Running the pilot: recording observations

The runtime cannot see tokens or invocations, so cost and fit are recorded with `swhouse observe`. Fix the failure criteria **before** the first cycle; they are in `src/swhouse/observe.py` (`THRESHOLDS`, `MIN_SAMPLE`) and change only before data exists.

Per cycle, by the Operator (a person, not the agent):

```bash
swhouse start "<task>" ...
swhouse observe judge accept|conditional|reject --by <you> --reason "<one line>"   # BEFORE the first `close`
swhouse observe session --minutes 25                                                # once per working session
swhouse observe friction "<what slowed you down or what you worked around>"
swhouse close                                                                       # then compare
swhouse observe defect "<what broke later>" --cycle 003                             # works on archived cycles
```

`judge` is rejected once `close` has been evaluated and cannot be changed afterwards, so the comparison is blind. Use `observe skip-judgement` if you did not judge; skipped cycles are counted, not hidden.

The runtime also records, without being asked: check runs and failures, every `close` attempt with its blockers, and whether the cycle file was edited outside the CLI (integrity digest). That last one measures the main risk of v2: an agent that bypasses the CLI.

```bash
swhouse observe report --baseline-minutes 30    # writes .swhouse/metrics/observations.json
```

| Criterion (default) | Meaning if tripped |
|---|---|
| `false_blocks` >= 2 | v2 blocked work you would have accepted: rules or checks too strict |
| `escaped_defects` >= 1 | v2 passed work that later proved defective: evidence is not enough |
| `manual_edit_cycles` >= 2 | The agent bypassed the CLI: the obligation problem moved, not solved |
| median minutes > baseline | No time benefit over v1 for comparable tasks |

`sufficient_sample` is false below 5 cycles; do not decide before it is true. Also compare, for cycles with `different-model` and `same-model` challenges, `challenge_findings_by_reviewer_context`: it shows whether independence found more defects.

Limits: minutes are self-reported; `manual_edits` detects changes to the cycle file, not to the product code; the judgement can be given by the agent if you let it, so run `observe judge` yourself.

## 8. Known limits

- **Declared risk.** The agent that wants to close declares the risk. The runtime rejects unknown keys and bad values, but cannot tell a false `reversible=true` from a true one.
- **Evidence integrity.** A SHA-256 catches editing a log after the check ran. It does not stop someone who can rewrite both the log and the cycle record. For stronger guarantees keep a CI log outside the working tree.
- **Owner approval.** The runtime records a reference; it cannot verify who made it.
- **Semantic correctness.** A green close means the declared evidence is complete. It does not mean the acceptance criteria are right or the tests relevant.
- **Windows and shell.** `--check` splits on spaces. Checks run without a shell, so pipes and redirects need a wrapper script.
- **No cost data.** The runtime does not record tokens or invocation counts yet, so a claim like "fewer invocations" cannot be verified from its output.

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `A legacy v1 cycle is open` | `cycles/current.md` exists | Close it under v1 |
| `CONTRACT_EMPTY` on close | `enforced` with no required check for the profile | Add a check to `validation.yaml` |
| `CONTRACT_CHECK_MISSING` | The cycle was opened before a check was added | Open a new cycle, or run `swhouse run-check <id>` |
| `EVIDENCE_MODIFIED` | The log changed after the run | Re-run the check. Do not edit logs |
| `RISK_UNKNOWN_KEY` | Typo in a risk key | Use one of the keys printed in the message |
| `GUARDED_REQUIRED` | A trigger applies | Use GUARDED, or fix the declared risk if it was wrong |
| `swhouse` imports the wrong checkout | Editable install from another directory | Reinstall from the intended checkout |
| `adopt` refuses | `config.yaml`/`validation.yaml` already exist, or the instance was already adopted | Inspect them; use `--rollback` first if they came from `adopt` |
