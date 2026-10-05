# ArchiMate Modeling Protocol

**Version:** 1.0
**Owner:** ARCHITECT (content), LIBRARIAN (structure and currency)
**Constitutional basis:** Article 10 (Knowledge Conservation), Article 19 (Visual Communication), Article 20 (Independent Completion Verification)

---

## Purpose

`protocols/documentation.md` says where the ArchiMate source lives and `protocols/documentation-presentation.md` says how it is shown. This protocol says **what goes into the model**. It exists because a model can render perfectly and still be wrong: it can describe the wrong system, list code helpers as architecture, or leave its layers unconnected.

---

## Rule 1 — Model the product, not the organization that builds it

A use-case model describes the system under documentation and its business context: the people and organizations that use it or feed it, the processes they perform, the data they handle, and the technology it runs on.

It never contains the delivery organization: framework roles (Product Owner, Librarian, Architect…), acceptance criteria, cycle artifacts, or "document the results" steps. Those belong in the cycle records, not in the product architecture.

## Rule 2 — Keep only architecturally significant elements

Before adding an element, ask: **would a stakeholder of the product notice if it were missing?** If not, leave it out.

- Internal helpers, adapters and test doubles are not elements; mention them in the `tech` text of the element that owns them.
- A code class becomes an element only when it carries a responsibility a stakeholder would recognize.
- Do not add a motivation element only because a check exists in the code. Add it when the Owner wants that value shown to stakeholders.

## Rule 3 — Every element is connected; every layer is linked to the one above

- **No isolated elements.** An element with no relationship is either missing its relations or not significant (Rule 2).
- **Behaviour accesses passive structure.** A process or service that reads or writes data has an access relation to it.
- **Lower layers realize or serve upper layers.**
  - Application data objects realize the business objects they represent.
  - Application services realize or serve the business processes they support.
  - Technology artifacts realize the application data or components they carry; technology services serve the application or business behaviour that uses them.
  - Business behaviour realizes the motivation goal it pursues.
- A model whose layers are separate islands has failed this rule, however good each layer looks.

Use ArchiMate relation names and directions (realizes, serves, assigned-to, accesses, flows-to, triggers, composes, aggregates, influences, specializes, association), so that the source reads the same way as the diagram.

## Rule 4 — The source is easy for a human to edit

- One file per layer (Motivation, Business, Application, Technology) per use case.
- Each element is a short section with its id, aspect, type, name, role and tech.
- Each relationship is written once, in the file of its `from` element, so cross-layer relations always have a home.
- The published view offers a direct "edit" link from each element to its source file.
- A local preview regenerates the view within seconds of saving.

## Rule 5 — Automated checks block a defective model

The generator (or an equivalent tool) must fail, with messages the Owner can read, when:

- an element has no relationship;
- a layer below the top has no relation to the layer above;
- an element or relation type is not in the vocabulary, or a relation points to an unknown id;
- a file path quoted in an element's `tech` text does not exist in the repository (stale content).

These checks run in CI and are part of the project's Non-Regression Checklist.

## Rule 6 — Content is accepted separately from rendering

For any cycle that produces or changes a model:

- **Step 2:** acceptance criteria cover model correctness (Rules 1–3) separately from visual rendering.
- **Step 9:** a dedicated **model review** checks the model against Rules 1–3 and against the current code. Verifying layout, JavaScript or fidelity to a visual reference does not satisfy this step.
- **Owner walkthrough:** the Owner reviews the content cell by cell before the cycle may be ACCEPTED. Record it as a Type-H item in the Non-Regression Checklist.
- When agents write `role`/`tech` text, they read the code, not only the documentation, because documentation may already be stale.

---

## Universality

This protocol names ArchiMate concepts and a review contract, not a tool. Any generator, editor or publishing pipeline may implement it.
