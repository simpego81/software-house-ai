# Prova di falsificazione dei due assessment

**Data:** 2026-10-14
**Oggetto:** `2026-10-02-roles-principles-protocols.md` (A1) e `2026-10-09-software-house-ai-evolution-plan.md` (A2)
**Metodo:** ogni affermazione verificabile è stata ricalcolata dalle fonti (`instance_samples/`, clone Linux in `linux-research/linux/linux`, codice e test del runtime). Dove non ho potuto ricalcolare lo dico.

**Verdetto:** la diagnosi regge, le cifre Linux no, e il pilota v2 non ha ancora prodotto l'evidenza che il piano richiede per i gate successivi.

---

## 1. Cosa regge (ricalcolato)

| Affermazione | Verifica | Esito |
|---|---|---|
| Reputation mai usata in Argo | `reputation/scores.yaml` ha `operators: []`; Argo stessa ha una decisione di sospensione | Confermata |
| VALIDATOR mai autore di uno step | 0 su 167 heading `Step N` nei cicli archiviati di tutte le istanze | Confermata |
| Drift di `summary.yaml` | Argo: `total_cycles=17` ma 16 file archiviati; il ciclo 011 non esiste. Memory count non coincide per `decisions` e `errors` | Confermata, e il ciclo mancante non era nel piano |
| Time-sliced violato | Argo ciclo 008 dichiara `session_deviation`; secretary 001 gira 12 step in una sessione | Confermata |
| Il default reale è già Sprint | Argo cicli 012–017: 015 e 016 Track S, 017 Track M, 012–013 di 2 heading. Mediana heading: 12 (tutti), 8 (da 007), 6 (da 012) | Confermata per **un** progetto e **un** operatore |
| Single-model ovunque | Tutte le `instance.yaml` assegnano `claude-sonnet-4-5/4-6` a ogni ruolo | Confermata |
| Type-H è debito | NRC di Argo: 26 righe H, 23 `PENDING`; 19 righe A | Confermata |

## 2. Cosa va corretto

### 2.1 Cifre Linux

A1 usa "metri Linux" per giudicare la house. Le cifre di partenza non sono quelle ricalcolate:

| Dato citato | Ricalcolato | Nota |
|---|---|---|
| 12.199 revert (0,82%) | 6.273 con `This reverts commit` (0,42%); 5.880 con oggetto `Revert ` (0,40%) | 12.199 è `grep Revert` ovunque nel messaggio: include falsi positivi |
| 854 tree git | 854 **righe** `T:`, ma 317 URL distinti | "854 in parallelo" sovrastima di ~2,7 volte |
| 4.374 maintainer | 4.374 righe `M:`, 2.011 email distinte | |
| 3.332 sottosistemi | 3.290 sezioni con `S:` | |
| 142 orphan | 145 | |

La direzione non cambia: `Documentation/process/handling-regressions.rst` dice davvero "Always consider reverting the culprit". Cambia il peso: nessuna di queste cifre dimostra un meccanismo causale.

### 2.2 I "principi" usati come autorità non sono falsificati

Il protocollo di ricerca (§10, §12, §20) chiede evidenza multipla, falsificazione obbligatoria e validazione su altri progetti. Stato reale: `research/falsification/` e `research/cross-project/` sono **vuote**. Il campo "Falsification attempted" di P002 è una riga con due controesempi. Tutti i principi sono tratti da un solo sistema e portano confidenza HIGH.

A1 cita "P049: no design review boards" come argomento per tagliare i passi 3–6. In `P041-P050-quality-batch.md` quella frase è un'affermazione della ricerca stessa ("Contrast"), non un fatto verificato nel kernel. Il taglio resta plausibile per ragioni locali (zero finding di CRITIC prima del codice? non misurato), ma **non è dimostrato da Linux**.

### 2.3 Cosa A1 non ha misurato

- Costo: "13 invocazioni" è dedotto dagli heading, non da token o tempo.
- `[TRIAGE:]` "mai emesso": il testo del ciclo 014 lo dice; non ho ricontrollato i cicli 015–017 (la mia ricerca era troncata).
- Valore di DESTROYER in Argo 001 (path-separator): non riverificato.
- "Zero REJECTED": sulle righe di decisione che ho potuto estrarre non ne ho trovato; non ho letto ogni ciclo per intero.

## 3. Cosa non regge nel piano A2

### 3.1 I cicli del pilota non sono evidenza

Il piano chiede 3 cicli shadow, poi 5 cicli v2 prima del cutover e 10 prima della Costituzione. Il pilota ha 4 cicli archiviati (003–006) con queste proprietà:

- tutti sviluppano il runtime stesso;
- aperti e chiusi in 7 minuti (15:45–15:52 del 2026-10-09);
- lead time mediano 0,007–0,019 ore (25–68 secondi), cioè registrati a lavoro fatto;
- challenge sempre `same-model`, quindi non indipendenti secondo la policy stessa;
- ciclo 004 chiuso con `approval.owner: null`.

Non misurano nulla sul routing, sull'overhead o sui difetti sfuggiti. **Il gate "5 cicli pilota" non è soddisfatto**; vanno ripetuti su lavoro reale di un'istanza reale.

### 3.2 La metrica di successo non è raccolta

La soglia "−40% invocazioni mediane rispetto ai cicli legacy" richiede un campo `invocations`. `metrics.py` non lo legge e lo schema non lo prevede. La baseline legacy "ricostruibile" non è stata prodotta: `docs/operations/` contiene solo `doctor-baseline.yaml`.

### 3.3 Il routing deterministico è deterministico solo sull'input

A2 §3.3 sostituisce il punteggio soggettivo con condizioni booleane. Ma i flag di rischio sono dichiarati dallo stesso agente che vuole chiudere, e il codice li ignorava in silenzio se sbagliati.

### 3.4 Buchi riproducibili nel runtime del piano

Provati con probe su copie temporanee, ora coperti da `tests/test_hardening.py`:

| # | Buco | Effetto |
|---|---|---|
| 1 | Con `validation.yaml` vuoto, `python -c pass` passa come check required | Un ciclo `enforced` chiude senza verifica reale |
| 2 | Il contratto dei check viveva nel file del ciclo | Cancellare i check dal YAML li eludeva |
| 3 | Chiave di rischio sbagliata (`attack_surfce=true`) ignorata | Nessuna escalation a GUARDED |
| 4 | `approve` invocabile dall'agente | L'"Owner approval" era autoasserita |
| 5 | `--optional` dopo l'id veniva eseguito come comando (`exit 127`) | Check opzionali inutilizzabili |
| 6 | Nessun comando per `pending_human` | Il debito Type-H, problema centrale di A1, non era gestibile |
| 7 | Evidenza senza digest | Un log modificabile dopo l'esecuzione |
| 8 | `doctor` non leggeva il formato `**Status:**` | Su Argo 14 errori `FRONTMATTER` falsi che nascondevano i veri |

### 3.5 Limiti che restano

- **Rischio autodichiarato.** Mitigazione futura: derivarlo dal diff (path toccati) invece che dichiararlo. Non implementato.
- **Digest dell'evidenza.** Rileva modifiche dopo l'esecuzione, non impedisce a chi può riscrivere sia log sia ciclo di falsificare entrambi. Serve un log CI esterno.
- **Approvazione Owner.** `--ref` registra un riferimento, ma il runtime non può verificarne l'autenticità. In modo `enforced` è obbligatorio, non verificato.

## 4. Decisioni prese

1. Il runtime viene corretto (§3.4) e i test di regressione restano nel repository.
2. Il modello v2 è rilasciato come **anteprima opt-in**. Il protocollo ufficiale e la Costituzione **non** cambiano: i gate di A2 non sono soddisfatti.
3. La migrazione è reversibile e non tocca lo stato legacy (provato byte-identico su copia di Argo).
4. Cutover e modifiche costituzionali restano condizionati a cicli reali: vedi `docs/migration/v1-to-v2.md` per i criteri.
5. Le cifre Linux di A1/A2 non vanno più citate come evidenza finché non sono ricalcolate con un metodo dichiarato.
