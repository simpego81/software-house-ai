# Software House AI — Claude Code Adapter (v2 preview)

Use this file instead of `CLAUDE.md` **only** in a project that ran `swhouse adopt --apply`. Otherwise keep `CLAUDE.md`.

The agent does not simulate the runtime. It calls it.

## Before any task

1. Run `swhouse doctor`. Fix new errors before starting. Known drift listed in `.swhouse/doctor-baseline.yaml` is shown as `KNOWN` and is not yours to fix unless asked.
2. Run `swhouse status`. If a cycle is open, resume it. If `.swhouse/cycles/current.md` exists, a v1 cycle is open: finish it under v1 first.

## Deciding whether to open a cycle

- Typo, formatting, a question, analysis with no artifact: do the work, show the diff, **no cycle**.
- Anything else: declare the risk honestly, then ask the runtime for the profile.

```bash
swhouse route --risk reversible=true --risk native_verification_available=true --risk blast_radius=low
swhouse start "<problem>" --profile SPRINT --criterion "<observable outcome>" --risk reversible=true ...
```

Do not pick a lighter profile than `route` recommends. If you think the risk is lower than the trigger says, ask the Owner; do not edit the cycle file.

## During the cycle

```bash
swhouse set-change "commit:<sha>"        # or working-tree:<name>
swhouse run-check <id>                   # runs the command declared in validation.yaml
swhouse criterion AC-01 met              # only after you saw the evidence
swhouse record-challenge logical --reviewer-context <ctx> --artifact "review:<path>" --findings N
swhouse add-pending H-1 "<what a human must verify>" --owner <name>
swhouse close                            # dry run: read every line it prints
swhouse close --apply
```

Rules:

1. Never edit files under `.swhouse/cycles/` or `.swhouse/evidence/` by hand. The close policy checks digests; a hand edit is a failed close, and in review it looks like fabrication.
2. Never run `swhouse approve` or `swhouse observe judge` / `skip-judgement` / `defect`. Approval and the verdict on the work belong to the Owner or Operator, who passes `--ref` for approvals, pointing at something outside this session. You may run `swhouse observe friction` when the process got in your way.
3. Set `--reviewer-context same-model` when you reviewed your own work. Do not claim `fresh-context` unless a separate session with no access to your reasoning did the review.
4. If a check cannot run here, add a pending-human item. Do not mark the criterion met and do not describe logical inspection as verification.
5. A regression with a known commit is a REVERT cycle: `swhouse prepare-revert <commit> --reason "<why>"`, then `apply-revert` (dry run first), then re-run the checks.

## Role prefixes

Not required. Name the responsibility in the chat only when it helps the operator follow what is happening.

## Memory

Follow `protocols/operational-cycle-v2.md`, section Memory. Do not write a memory file to satisfy a count.

## Escalate to the Owner when

- the policy blocks and you cannot satisfy it without changing a rule;
- a GUARDED trigger applies;
- a check you need does not exist in `validation.yaml`;
- the Owner's decision would be needed to waive a human check.

State the question and what is blocked. Do not reword the risk to avoid the escalation.
