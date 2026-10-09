# Documentation Presentation Protocol

**Version:** 1.0
**Owner:** LIBRARIAN (Agent 07)
**Constitutional basis:** Article 19 (Visual Communication for Stakeholders), Article 10 (Knowledge Conservation)

---

## Purpose

`protocols/documentation.md` defines *what* documentation exists and *where* it lives (the three-domain tree). This protocol defines *how it is presented* to stakeholders on a published surface (e.g. a static site). It is technology-neutral: it names the contract, not the engine.

The contract applies whenever project documentation is published for an audience that includes non-technical stakeholders (business angels, product owners, evaluators). It complements — does not replace — `protocols/stakeholder-animation.md` (which governs the per-milestone animation artifact).

---

## Core contract

1. **Diagrams first, text as annotation.** The architecture diagram is the centerpiece of each use-case page; prose is secondary and may be collapsible. A stakeholder must be able to grasp the use case from the diagram alone. (Article 19.)

2. **Viewer-controlled navigation.** No auto-advance. The viewer decides what to look at and for how long. Layer focus, section expansion, and element drill-down are opt-in. (Article 19.)

3. **Responsive by default.** Diagrams and pages must scale to the viewport (≤480px included); no horizontal overflow. A fixed-size diagram that overflows mobile has failed the contract.

4. **Value frame on entry.** The landing page and each use-case page open with a value frame: Who has the problem, what the problem is, the impact of solving it, the impact of NOT solving it. Plain language; no jargon on the landing.

5. **Technical depth available, not forced.** Stakeholders who want technical detail (component interfaces, ADRs, source links) can reach it in one click, but it is not the first thing they see. Collapsible sections and typed cross-references satisfy this.

6. **Scales to many use cases.** Navigation and the use-case page template must be data-driven (a registry of use cases), so adding a use case does not require redesigning the site. The first use case is not special-cased.

7. **One source of truth.** The authoritative documentation stays in the repo's `docs/` tree and the structured diagram source (e.g. `archimate/` layer files). The published site is a *derived view*. A published page that cannot be reproduced from the repo is a snapshot, not documentation (Article 10).

8. **Diagrams-as-code remain authoritative.** Rendered images/SVG are presentation supplements; the fenced code block (PlantUML/Mermaid) or the structured source (layer files) remains the source of truth. If the renderer fails, the code block is still legible (graceful fallback).

9. **Frontend quality bar.** Browser-observed rendering, no console errors, responsive ≤480px, `prefers-reduced-motion` respected, CDN version-pinned with `onerror` fallback, graceful degradation when JS fails. See `protocols/frontend-checklist.md`.

---

## Use-case page template (contract)

Every use-case page MUST present, in this order:

1. **Header** — title, status (done/active/planned), last-verified date.
2. **Value frame** — Who / Problem / Impact of solving / Impact of NOT solving (collapsible).
3. **Architecture diagram** — the centerpiece; responsive; interactive (layer focus, element drill-down to detail); viewer-controlled.
4. **Layer × Aspect matrix** — the derived summary table; non-empty cells link to detail.
5. **Main flow / preconditions / failure paths** — the use-case narrative (collapsible).
6. **Technical depth** — typed cross-references to ADRs, the architecture overview, and source files.

---

## Universality

This protocol is technology-neutral. It does not name Jekyll, Liquid, or any specific static-site engine. A project may implement it with any publishing pipeline that respects the contract. Project-specific implementation patterns (e.g. a Jekyll layout system) are recorded in the project's memory, not in this protocol.

---

## Verification

The LIBRARIAN verifies the published surface against this contract at Step 10, using `protocols/frontend-checklist.md` as the method. A page that fails the responsive, console-error, or reduced-motion check fails this protocol. A page whose diagram does not render (and has no graceful fallback) fails this protocol.

Independent verification (Article 20): a reader who did not write the documentation must confirm that a non-technical stakeholder can understand the use case from the diagram alone, and that a technical stakeholder can reach source-level detail in one click.
