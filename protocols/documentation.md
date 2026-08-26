# Documentation Protocol

**Version:** 1.0

Every project operating under the Software House AI framework must maintain living documentation that any contributor — human or agent — can navigate, update, and verify without prior context.

---

## Core principle

Documentation that cannot be found is not documentation. Documentation that cannot be verified is assumption. Documentation that duplicates information is a maintenance liability.

These three failures share one root cause: no defined structure and no currency obligation.

---

## Structure — the three-domain tree

Every project maintains a `docs/` directory with this fixed structure:

```
docs/
  MAP.md               ← mandatory: index of all documents (see below)
  architecture/        ← what the system is and how it works
  decisions/           ← why it is built this way (ADRs)
  operations/          ← how to run, build, test, deploy
```

**Maximum depth: 2 levels.** `docs/domain/document.md`. No subdirectories inside domains.

**Domain assignment rule (single question per document):**

| The document answers… | Domain |
|---|---|
| "What does X do?" or "How does X connect to Y?" | `architecture/` |
| "Why X and not Y?" or "Why was this decision made?" | `decisions/` |
| "How do I do X?" or "What command runs X?" | `operations/` |

A document that answers more than one question must be split. A document with no clear domain has not been scoped correctly.

---

## MAP.md — the mandatory index

`docs/MAP.md` is the single entry point for all documentation. It must be:

- **Read first** by any agent before consulting specific documents
- **Updated** by the LIBRARIAN at every cycle that adds, removes, or invalidates documentation
- **Self-describing**: a new contributor reading only MAP.md must know where to find any information

Minimum required content:

```markdown
# Documentation Map

last_verified: YYYY-MM-DD

| File | Domain | One-line topic | Last verified |
|------|--------|----------------|--------------|
| architecture/overview.md | architecture | ... | YYYY-MM-DD |
| decisions/ADR-001.md | decisions | ... | YYYY-MM-DD |
| operations/development.md | operations | ... | YYYY-MM-DD |
```

A document not listed in MAP.md does not exist as far as the framework is concerned.

---

## Freshness signal — `last_verified` field

Every document must contain a `last_verified: YYYY-MM-DD` field (frontmatter or first line after the title). This is not the date the document was written — it is the date someone confirmed it reflects the current state of the system.

An agent reading a document whose `last_verified` is older than the last significant cycle affecting that domain must treat the document as **presumed stale**: verify claims before acting on them, and flag the staleness to the LIBRARIAN.

There is no automatic expiry. The LIBRARIAN is responsible for updating `last_verified` when content is confirmed current, not just when content changes.

---

## Diagrams — as code, not as images

Every architecture diagram must be expressed as a **diagram-as-code** block embedded in the relevant `architecture/` document. Accepted formats: Mermaid, PlantUML, D3 (with source in the document).

Rationale: a rendered image cannot be diffed, cannot signal staleness, and cannot be verified without running it. A diagram-as-code block can be read, modified, and compared to the code it describes.

Rendered images (PNG, SVG exports) are permitted as supplements — for stakeholder communication artifacts defined in `protocols/stakeholder-animation.md` — but the authoritative source is always the code block.

A diagram that exists only as an image is not a maintained diagram — it is a snapshot. Snapshots are not documentation.

---

## Cross-references — typed links, no copies

When a document needs to reference content from another domain, it uses a typed link. It does not copy the content.

Typed link format:

```
[architecture: how MetricsOverlay connects → architecture/overlay.md#load-order]
[decision: why side-channel over injection → decisions/ADR-metrics-overlay.md]
[operations: how to run CMetrics → operations/development.md#cmetrics]
```

**Never duplicate content across documents.** If content needs to appear in two places, one of them is wrong — either the content belongs in one domain and is linked from the other, or it should be extracted into its own document and linked from both.

---

## Ownership and update triggers

The **LIBRARIAN** (Step 10 of every cycle) is responsible for documentation currency. The LIBRARIAN's close checklist (see `operational-cycle.md`) includes:

- [ ] `docs/MAP.md` updated to reflect any documents added, removed, or known-stale as a result of this cycle
- [ ] Any document in `architecture/` that describes components changed in this cycle: `last_verified` updated or flagged as stale in MAP.md
- [ ] Any new decision made in this cycle: captured as an ADR in `decisions/`
- [ ] Any new command, procedure, or environment change: reflected in `operations/`

The LIBRARIAN does not need to write complete documentation for everything that changed — but must record in MAP.md what is now stale and who owns the update.

**Any contributor** (human or agent) may update a document at any time, as long as:
1. The document remains within its domain (one question, one document)
2. MAP.md is updated to reflect the change (including `last_verified`)
3. No content is duplicated — cross-references replace copies

---

## Applying this protocol to a project

When adopting this protocol for the first time in a project:

1. Run a documentation audit: list all existing documentation files.
2. Classify each file by domain (architecture / decisions / operations) or mark for deletion if obsolete.
3. Move files to the `docs/` tree structure.
4. Create `docs/MAP.md` with all existing files listed.
5. Set `last_verified` to the audit date for files that were reviewed and confirmed current; leave blank (or set to the file's last-modified date) for files not yet reviewed.
6. Open a Sprint-track cycle to update the first stale document identified (do not attempt to update all stale documents in one cycle).

The goal of the first application is a complete MAP.md with honest freshness dates — not perfect documentation.
