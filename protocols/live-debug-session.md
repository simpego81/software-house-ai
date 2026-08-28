# Protocol: Live Debug Session

**Version:** 1.0  
**Status:** Active  
**Applies to:** All projects using the Software House AI framework

---

## Purpose

Collaborative mode in which the operator plays with the running application while the COORDINATOR
stands ready to analyze, triage, and fix issues in real time. Every operator report is treated as a
first-class signal; learnings propagate to the NRC and, when systemic, to software-house protocols.

---

## Activation

Triggered when the operator uses one of these phrases (or equivalent intent):
- "entra in modalità debug" / "live debug session" / "let's debug" / "monitora mentre gioco"

COORDINATOR response:
1. Confirm activation in one sentence.
2. Start dev server if not running.
3. Read `memory/validation/non_regression_checklist.md` — announce ⚠ PENDING H-type items relevant to the current domain.
4. Declare readiness: "Server at [URL]. Inizia — segnala qualsiasi cosa sembri strana."

---

## During the Session

### When the operator is silent
Do nothing. Do not interrupt.

### When the operator reports an anomaly — 6-step response

**Step 1 — Acknowledge** (1 sentence)

**Step 2 — Triage** (1 word + 1 sentence)  
BUG | REGRESSION | UX | PERF

**Step 3 — Analyze**  
Read relevant source files directly. If one targeted question is needed: ask it, wait.

**Step 4 — Root Cause** (1 sentence before any code change)

**Step 5 — Fix**  
Minimal fix. No cleanup, no refactoring beyond scope.

**Step 6 — Capture**  
Follow `protocols/user-feedback-capture.md` (NRC + error log if systemic).  
If the bug reveals a process gap: propose a protocol update — operator decides.

---

## Response Format

| Situation | Format |
|---|---|
| Acknowledgment | 1 sentence |
| Triage | 1 word + 1 sentence |
| Root cause | 1 sentence |
| Fix applied | file:lines changed + 1 sentence |
| NRC item | "NRC: NR-[AREA]-[NN] aggiunto" |
| Question | Max 1 per round |

---

## Session End

1. Summary: bugs fixed (N), NRC items added (N).
2. List ⚠ PENDING H-type items still needing verification.
3. List any protocol-update proposals for operator approval.

---

## Anti-patterns

| Anti-pattern | Correct behavior |
|---|---|
| Interrompere l'operatore durante il play | Silent until operator reports |
| Lunghe spiegazioni mentre l'operatore gioca | Signal-only messages |
| Fix senza NRC | NRC first, then fix |
| Dichiarare fixed senza verifica | Almeno ispezionare il path nel source; altrimenti PROVISIONAL |
| Più domande in una risposta | One question, wait for answer |
