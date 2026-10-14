# Operational Cycle Protocol v2 (opt-in preview)

**Status:** preview. Applies only to instances that ran `swhouse adopt --apply`. All other instances keep [`operational-cycle.md`](operational-cycle.md) v1.1 unchanged.
**Decision record:** [ADR 0002](../docs/decisions/0002-v2-opt-in-preview.md)

## What changes in one paragraph

A cycle no longer walks through twelve named roles. It declares a **risk**, receives a **profile**, collects **executable evidence**, and closes when a **policy** says the evidence is complete. Roles survive as responsibilities that a profile may require. A person or a tool can fill them as well as a model.

## Responsibilities

| Responsibility | Purpose | Who can fill it |
|---|---|---|
| ROUTE | Frame problem, scope, risk, profile | Model or Owner |
| BUILD | Change the artifact and self-test it | Model or Owner |
| CHALLENGE | Look for defects in the **diff or artifact**, not in a design essay | Tool, different model, human; same model counts but is recorded as not independent |
| VERIFY | Run configured checks and keep the output | The runtime. A model only orchestrates |
| GOVERN | Apply close policy; route exceptions to the Owner | The runtime and the Owner |
| CURATE | Keep reusable knowledge | On trigger only (see Memory) |
| EVOLVE | Review the process | On trigger only (see Evolution) |

Mapping from v1 names, for reading old cycles: COORDINATOR and PRODUCT OWNER → ROUTE; BUILDER and OPTIMIZER → BUILD; CRITIC and DESTROYER → CHALLENGE (modes `logical`, `adversarial`, `ux`); SCIENTIST → VERIFY; ARBITER → policy plus Owner; LIBRARIAN → CURATE; EVOLUTION MASTER → EVOLVE; VALIDATOR → `.swhouse/validation.yaml`.

The mapping is for reading. v2 does not ask a model to impersonate each name in turn.

## Profiles

The profile is chosen from declared risk. `swhouse route --risk key=value ...` prints the minimum profile.

| Profile | Use | Required evidence |
|---|---|---|
| DIRECT | Typo, formatting, a question, analysis with no artifact | None. Git is the record. No cycle is opened |
| SPRINT | Local, reversible, natively verifiable | Criteria met, change reference, all configured checks passed |
| STANDARD | Feature, non-obvious root cause | SPRINT, plus one completed challenge on the diff, plus a rollback strategy |
| GUARDED | Any escalation trigger below | STANDARD, plus Owner approval; in `enforced` mode the approval needs an external reference and one challenge from a different model, human or tool |
| REVERT | A known regression with a known commit | Prepare, apply, verify restore; root cause is a separate cycle |
| EXPERIMENT | High novelty, bounded blast radius | Baseline, hypothesis, stop condition, `adopt`, `reject` or `continue` |

**GUARDED triggers (not negotiable by the author):** `irreversible`, `data_migration`, `public_contract`, `attack_surface`, `cross_domain`, `blast_radius=high`, `reversible=false`, `native_verification_available=false`.

Risk keys are validated. An unknown key such as a typo is an error, not a silent no-op.

## Close policy

`swhouse close` allows `ACCEPTED` when all of these hold:

- every acceptance criterion is `met`;
- a change reference exists;
- every check required by `.swhouse/validation.yaml` for the profile is present, required, passed, exit code 0, with an evidence file inside the project whose SHA-256 matches the one recorded at run time;
- no `pending_human` item is unresolved or expired;
- no open high or critical finding;
- STANDARD and GUARDED: a completed challenge with an artifact, and a rollback strategy;
- GUARDED: Owner approval.

The contract lives in `validation.yaml`, not in the cycle file. Editing the cycle cannot remove or downgrade a required check. In `enforced` mode the contract must not be empty.

What the policy **cannot** decide: whether the acceptance criteria are right, whether the tests are relevant, whether a declared risk is honest. Those stay with the Owner. A green close means "the declared evidence is complete", not "the change is correct".

### Outcomes

`ACCEPTED`, `PROVISIONAL` (usable, human verification pending), `DEFERRED` (needs a reason and a reopen trigger), `REJECTED`, `REVERTED`. `ACCEPTED WITH CONDITIONS` does not exist in v2: conditions are either checks, pending-human items or a DEFERRED.

## Pending human verification

Some checks are human by nature: a native dialog, a standby resume, a hardware target. The runtime tracks them:

```bash
swhouse add-pending H-1 "Canvas redraws after standby resume" --owner <name>
swhouse resolve-pending H-1 verified
swhouse resolve-pending H-1 converted --ref "test:tests/standby.spec.js"
swhouse resolve-pending H-1 waived --expires 2026-12-31 --ref "owner:decision-id"
```

A pending item blocks `ACCEPTED`. It resolves by human confirmation, by conversion into an automated check, or by a waiver that has an expiry date and a reference to the Owner's decision. An expired waiver blocks again. This replaces open-ended Type-H debt with a deadline.

## Memory

Write a memory entry only when one of these is true: a decision with real alternatives and future consequences; an incident that escaped the checks; a pattern seen at least twice; an operating contract not derivable from the repository; operator feedback that exposes a recurring class of error.

Do not write an entry for routine changes already described by the commit and the tests, for each failed command during exploration, or for a paraphrase of the cycle. Git is the routine record.

Failures have two levels: command output and exit codes are kept automatically as evidence; a durable incident note exists only for unexpected, escaped or recurring failures.

## Operator feedback

A correction changes the current task. It becomes a framework proposal only if it reveals a serious systemic risk, repeats a second time, or shows that an existing check can never apply.

## Evolution

The framework changes by experiment: observed problem and baseline, hypothesis, minimal change, a metric that could falsify it, pilot size, adoption or rollback criterion. An EVOLVE review runs on an escaped defect, three overrides of the same policy, a metric degrading past its baseline, or at least ten new cycles since the last review. It does not run on a calendar.

## Single-model honesty

When author and reviewer are the same model, the cycle record says `same-model` and the policy reports that the challenge is not independent. It is never promoted to independent verification. Independence comes from a different model, a human, or a tool that executes something.

## Concurrency

One v2 cycle at a time by default (`concurrent_cycles: false`). A v1 cycle open in `.swhouse/cycles/current.md` blocks opening a v2 cycle. Concurrent cycles need real parallel work, observed contention and per-path ownership, none of which exist yet.

## Metrics

Derived, never hand-edited: `swhouse metrics` writes `.swhouse/metrics/generated.json` from archived cycles. Current set: cycles closed, outcomes by governance mode, median lead time per profile, verification completeness. A metric is added only with the decision it changes.

## Not in this preview

Reputation, quality scores 1–5, `knowledge_reuse_rate`, trust-scaled review, concurrent cycles, domain files, and any amendment to the Constitution. Each needs evidence from real cycles first.
