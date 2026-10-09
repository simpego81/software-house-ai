# V2 runtime pilot

**Mode:** shadow
**Owner:** repository Owner
**Framework freeze:** no new role, article, or protocol until the pilot review

## Baseline

The initial `swhouse doctor` run is expected to report at least:

- archived `cycle-001.md` has `status: open`;
- closed `cycle-002.md` still says it is awaiting Owner approval;
- `metrics/summary.yaml` reports 3 decision entries while 5 files exist.

These are observations, not automatic repair instructions.

Every v2 record stores `governance_mode`. While it is `shadow`, `outcome` is the result the v2 policy would have produced; it does not replace the official legacy governance decision.

## Setup

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
swhouse doctor --baseline docs/operations/doctor-baseline.yaml
python -m unittest discover -s tests -v
```

The global `--root` option can inspect another project:

```bash
swhouse --root /path/to/project doctor
```

## Minimal SPRINT example

```bash
swhouse start "Small reversible change" --profile SPRINT \
  --criterion "The changed behavior is covered" \
  --risk reversible=true \
  --risk native_verification_available=true \
  --risk blast_radius=low

swhouse set-change "commit:<sha>"
swhouse criterion AC-01 met
swhouse run-check runtime-tests
swhouse close                 # dry-run policy evaluation
swhouse close --apply         # archive only if policy passes
swhouse metrics
```

`run-check` does not invoke a shell: arguments after `--` are passed directly to the process. Its stdout and stderr are stored under `.swhouse/evidence/<cycle>/`. Common token, password and key formats are redacted best-effort; commands must still avoid printing or accepting secrets when possible.

Required commands and timeouts come from `.swhouse/validation.yaml` and are copied into the cycle when it opens. A configured check cannot be replaced at execution time by a different command; this prevents an irrelevant green command from satisfying close policy. Close also verifies that evidence resolves to an existing file inside the project.

STANDARD and GUARDED also require challenge evidence:

```bash
swhouse record-challenge logical \
  --reviewer-context fresh-context \
  --artifact "review:<path-or-id>" \
  --findings 2
```

Using `same-model` is recorded as non-independent and remains visible in policy output; it is never silently promoted to independent verification.

## REVERT flow

REVERT is deliberately two-stage:

```bash
swhouse prepare-revert <bad-commit> --reason "observed regression"
swhouse apply-revert                         # dry run
swhouse apply-revert --apply                 # executes git revert
swhouse run-check runtime-tests
swhouse criterion AC-01 met
swhouse set-rollback "revert the revert commit" --verified
swhouse close --outcome REVERTED --apply
```

`apply-revert` refuses dirty product paths (pilot state below `.swhouse/` is allowed), rejects merge commits until mainline semantics are implemented, and records conflicts as blocking findings instead of silently aborting or claiming recovery.

## Pilot gates

1. Run the CLI against legacy state in read-only mode.
2. Complete three shadow cycles without adopting runtime decisions as official governance.
3. Complete five v2 pilot cycles with no manual update to generated metrics.
4. Review after ten v2 cycles or earlier on an escaped defect/policy override cluster.

## Rollback

Stop using the CLI and remove only pilot-created paths:

- `.swhouse/cycles/open/*.yaml`;
- `.swhouse/cycles/archive-v2/*.yaml`;
- `.swhouse/evidence/<pilot-cycle>/`;
- `.swhouse/metrics/generated.json`.

Do not modify or delete legacy cycle archives as part of rollback.
