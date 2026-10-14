# Software House AI v2: sintesi dell'evoluzione

**Stato:** anteprima opt-in. Il protocollo ufficiale (v1.1) e la Costituzione non sono cambiati.
**Dettagli:** [protocollo](../protocols/operational-cycle-v2.md) · [migrazione](migration/v1-to-v2.md) · [ADR 0002](decisions/0002-v2-opt-in-preview.md)

## Il cambiamento in una riga

Da *"tredici ruoli recitati in sequenza, con la conformità affidata alla memoria del modello"* a *"un rischio dichiarato, un profilo, evidenza eseguibile, una policy che chiude"*.

```text
v1:  task → 12 step, un ruolo ciascuno → verdetto narrativo → aggiornamento manuale dei file
v2:  task → rischio → profilo → lavoro → check eseguiti e hashati → policy → esito
```

## Perché

Il framework scriveva una regola ogni volta che un difetto sfuggiva, e la regola dipendeva dalla disciplina dello stesso modello che voleva chiudere il task. Nell'istanza più matura (Argo, 17 cicli) questo ha prodotto: reputation con zero voti, VALIDATOR mai autore di uno step, `summary.yaml` fuori sincronia, `[TRIAGE:]` ignorato dopo essere stato introdotto. La linea guida presa da Linux è **spostare gli obblighi dalla memoria dell'agente a meccanismi che falliscono da soli**: revert di prima classe, test eseguiti, esiti visibili.

## Cosa cambia

| Area | v1 | v2 |
|---|---|---|
| Struttura | 12 step e 13 ruoli | 6 profili; ogni profilo definisce **evidenze richieste**, non agenti da invocare |
| Scelta del processo | Il COORDINATOR sceglie il track | `swhouse route` ricava il profilo minimo dal rischio; i trigger GUARDED non sono negoziabili dall'autore |
| Verifica | Narrativa del SCIENTIST | Comandi dichiarati in `validation.yaml`, output conservato con SHA-256 |
| Chiusura | Decisione dell'ARBITER, spesso `ACCEPTED WITH CONDITIONS` | Policy sull'evidenza; le condizioni diventano check, voci pending o DEFERRED |
| Verifica umana | `PENDING_HUMAN` in prosa, senza scadenza | Voci con owner; si chiudono per conferma, conversione in test o waiver **con scadenza** |
| Errori | "Ogni fallimento in `memory/errors/`" | Output e exit code conservati come evidenza; nota durevole solo per eventi inattesi o ricorrenti |
| Correzione | Ripercorrere gli step | Profilo REVERT: prepara, applica (dry run prima), verifica il ripristino |
| Indipendenza | Dichiarata | Registrata: `same-model` è marcato non indipendente e non viene mai promosso |
| Stato e metriche | Markdown aggiornato a mano | YAML leggibile da macchina; le metriche sono derivate |
| Adozione | Riscrittura | `swhouse adopt`: aggiunge file accanto allo stato legacy; rollback con hash |

## Benefici

### Misurati su questo lavoro

- **Meno falsi allarmi su un'istanza reale.** Su una copia di Argo `doctor` passava da 14 errori `FRONTMATTER` falsi (non leggeva il formato `**Status:**`) a 5 errori reali e 6 warning, tra cui il ciclo 011 mancante e tre cicli archiviati "IN PROGRESS".
- **Otto difetti del runtime chiusi, ciascuno riprodotto prima e coperto da un test dopo.** Il più grave: con `validation.yaml` vuoto, `python -c pass` chiudeva un ciclo `enforced`. Test del repository: da 15 a 41, tutti verdi.
- **Migrazione reversibile provata.** Su copie delle quattro istanze campione, `adopt --apply` seguito da `adopt --rollback --apply` ha lasciato ogni file byte-identico.
- **Nessun rischio per chi non migra.** Constitution, ECOSYSTEM, `agents/` e `operational-cycle.md` sono intatti.

### Attesi, non ancora misurati

Sono ipotesi da verificare sul lavoro reale, non risultati.

- **Meno overhead per le modifiche piccole.** Nei cicli recenti di Argo la mediana degli heading `Step` è già 6 (contro 12 nell'intero corpus), quindi v2 formalizza una pratica esistente. Il runtime però non registra token né invocazioni: il "−40%" del piano **non è verificabile** con gli strumenti attuali.
- **Meno drift documentale.** Gli indici derivati non possono andare fuori sincronia, ma lo si vedrà solo dopo diversi cicli.
- **Recupero più rapido dalle regressioni.** REVERT ha un test end-to-end su un repository Git di prova. Serve una regressione reale per misurare la latenza.
- **Debito Type-H sotto controllo.** In Argo 23 voci H su 26 sono pending; le scadenze obbligatorie impediscono che restino aperte per sempre, ma la riduzione effettiva non è ancora osservata.

## Cosa v2 non risolve

- **Il rischio è dichiarato dall'agente che vuole chiudere.** Il runtime rifiuta chiavi sconosciute e valori non validi, non una dichiarazione falsa ma ben formata.
- **Evidenza e approvazione hanno un limite di fiducia.** Lo SHA-256 rileva modifiche dopo l'esecuzione, non blocca chi riscrive log e ciclo insieme. L'approvazione dell'Owner richiede un riferimento esterno ma il runtime non può verificarlo.
- **Un esito verde significa "evidenza completa", non "il lavoro è corretto".** Criteri e test sbagliati passano.
- **Pilota non ancora probante.** I quattro cicli del pilota riguardano il runtime stesso, sono stati chiusi in pochi minuti e usano solo challenge `same-model`. I gate per il cutover (5 cicli reali) e per la Costituzione (10) non sono soddisfatti.
- **Le cifre Linux dei due assessment vanno ricalcolate.** Per esempio 6.273 commit con `This reverts commit` (0,42%) e non 12.199 (0,82%); 317 URL di tree distinti e non 854. La direzione resta valida, il peso come prova no. Vedi `self-assessment/2026-10-14-stress-test-of-assessments.md`.

## Come procedere

1. Provare `swhouse adopt` su **un** progetto attivo, in modalità `shadow`.
2. Confrontare, ciclo per ciclo, l'esito v2 con il giudizio v1 e annotare i disaccordi.
3. Passare a `enforced` solo con i criteri della guida di migrazione, sezione 7.
4. Valutare la modifica della Costituzione solo dopo almeno dieci cicli reali.

Se il costo supera il beneficio: `swhouse adopt --rollback --apply` e si continua con v1.
