---
name: builder-self-test-mandatory
description: Self-Test Log è output obbligatorio del BUILDER — reasoning != testing, servono comandi eseguiti e output osservato
metadata:
  type: decision
  date: 2026-08-27
  triggered_by: "Consegna ripetuta di codice non testato (cmake file API, ↺ Target button)"
---

# Decisione: Self-Test Log obbligatorio nel BUILDER

## Contesto

In più sessioni consecutive il BUILDER ha consegnato codice non testato, dichiarando "confidence: high" basandosi solo sulla lettura del codice. Il difetto sistematico è che **reasoning about code ≠ testing code**.

## Regola adottata

Il BUILDER non può emettere output (Step 7) senza un Self-Test Log che contenga:
- Componente modificato
- Comando o azione eseguita (non pianificata, ESEGUITA)
- Output effettivo osservato
- Risultato: PASS / FAIL

Senza questo log, il Step 7 è invalidato dal COORDINATOR e rinviato al BUILDER.

**Why:** Tre episodi di regressione in sessioni consecutive. In ogni caso il BUILDER aveva dichiarato alta confidenza basandosi su code review, non su esecuzione. L'utente ha dovuto ripetere le stesse segnalazioni.

**How to apply:** Ogni volta che si modifica un endpoint server, una funzione UI, o un CLI: eseguire il test, catturare l'output, allegarlo al log. Se il test è fisicamente impossibile nell'ambiente corrente, dichiarare SKIPPED con rischio e mitigazione espliciti.

## Anti-pattern bloccati

- "Ho letto il codice e sembra corretto" → NON è un self-test
- "Compila senza errori" → NON è un self-test
- "È simile a codice precedente che funzionava" → NON è un self-test
- "Il SCIENTIST verificherà" (senza SKIPPED esplicito) → NON è accettabile
