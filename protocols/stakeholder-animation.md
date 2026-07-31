# Stakeholder Animation Standard

**Owner:** LIBRARIAN (Agent 07)  
**Version:** 1.0  
**Constitutional basis:** Article 19 — Visual Communication for Stakeholders  
**Template:** [`../templates/milestone-animation.html`](../templates/milestone-animation.html)

---

## Purpose

Every Software House AI project must maintain a `milestone-animation.html` file that explains the project visually to non-technical stakeholders. This file is a self-contained HTML presentation: no server, no build step, open in any browser.

The standard defines what the artifact must contain, when it is created and updated, who owns each step, and how to produce it from the reusable template.

---

## What the artifact must contain

### Per milestone: one scene

Each milestone maps to exactly one scene. A scene contains:

| Element | Requirement |
|---|---|
| Diagram type | Must match the nature of the milestone (see Diagram Type Matrix below) |
| All physical and logical actors | Derived from primary sources — hardware matrix, deployment diagram, protocol specs |
| Data flows | Animated along connection lines — the viewer sees data moving |
| Per-element annotations | One annotation per significant element; appears near the element; navigated by the viewer |

### Navigation UX (non-negotiable)

- No auto-advance. The viewer controls the pace.
- `→` advances to the next annotation; when the scene is exhausted, advances to the next scene.
- `←` goes back one annotation or one scene.
- Keyboard arrows and on-screen buttons both work.
- An indicator shows current position: `nota 2 / 5`.

### Visual rules

- Diagram fills ≥ 80% of viewport — no wasted margin.
- UML notation: stereotypes (`«device»`, `«component»`), node boxes, artifact boxes, cylinders for databases.
- Color coding: consistent per layer or per node type across all scenes.
- Annotations: positioned in a reserved column or near the target element with a pointer line. Solid background so they are readable over the diagram. Previous annotation disappears before the next one appears.
- No bullet-point lists in the diagram area. Text only in annotations, kept under 4 lines.

---

## Diagram Type Matrix

Choose the diagram type that best matches what the milestone delivers:

| Milestone nature | Diagram type | Example |
|---|---|---|
| Repository / module structure | Component Dependency Graph | M0 Foundations |
| Physical deployment and hardware | UML Deployment Diagram | M1 MVP Backbone |
| Process loop or state transitions | UML State Machine | M2 Basic Evolution |
| Agent interaction and messaging | UML Communication Diagram | M3 Cooperative Ecology |
| Software stack and interfaces | UML Component Diagram | M4 Full Observatory |
| Data processing pipeline | UML Activity Diagram | M5 Production Signals |
| Multiple systems combined | Combined diagram with swimlanes | Cross-cutting milestones |

---

## Lifecycle

### When to create

The Librarian issues a Documentation Work Order to create `milestone-animation.html` when:
- The first milestone is formally defined in `state/roadmap.yaml`

### When to update

The Librarian issues a DWO to update the animation when:
- A new milestone is added or removed
- A milestone's hardware topology changes (new node, removed node, protocol change)
- A milestone's status changes to COMPLETED (scene visual should reflect completion)
- An architectural decision (ADR) changes the structure of an existing scene

### When NOT to update

- Task-level progress within a milestone does not require an animation update
- Documentation fixes and typos do not require an update
- Changes in agent assignments do not require an update

---

## How to produce it (Builder instructions)

### Step 1 — Read primary sources first

Before touching the animation, read (in this order):
1. `specs/hardware_function_matrix.md` — all hardware nodes and their roles
2. `specs/node-software-map.md` — software running on each node
3. `diagrams/node-deployment.*` — physical topology
4. `diagrams/per-device/` — per-device views
5. `state/roadmap.yaml` — milestones, their status, and dependencies

Do NOT build scenes from task queues, dashboards, or implementation logs. Those are derived sources.

### Step 2 — Fork the template

Copy `software-house-ai/templates/milestone-animation.html` into your project's `docs/` directory. The template contains the full engine (CSS, helper functions, navigation logic). You only fill in the `SCENES` array.

### Step 3 — Define SCENES

Each scene object requires:

```js
{
  ms:         'M1',                    // milestone ID
  title:      'MVP BACKBONE — 57%',   // display title
  pill:       'pa',                    // 'pd' done · 'pa' active · 'pp' planned
  badge:      '⚡ IN CORSO',           // status badge text
  annotCount: 6,                       // number of annotation groups in the SVG
  svg() {                              // returns SVG string
    return `<svg viewBox="0 0 1000 530" preserveAspectRatio="xMidYMid meet">
      <!-- diagram elements here -->
      <!-- annotations: <g id="ann-{sceneIdx}-{annotIdx}" class="ann" opacity="0"> -->
    </svg>`;
  }
}
```

### Step 4 — Annotations

Each annotation is an SVG `<g>` with `id="ann-{sceneIdx}-{annotIdx}"` and `class="ann" opacity="0"`. The engine toggles visibility. Structure:

```svg
<g id="ann-1-0" class="ann" opacity="0">
  <!-- pointer line from callout to element -->
  <line x1="720" y1="89" x2="165" y2="86"
    stroke="#3b82f6" stroke-width="1" stroke-dasharray="5 3" opacity=".7"/>
  <circle cx="165" cy="86" r="3" fill="#3b82f6" opacity=".8"/>
  <!-- callout box (always in right column x≥720) -->
  <rect x="720" y="50" width="265" height="80" rx="5"
    fill="#060e1c" stroke="#3b82f6" stroke-width="1.4"/>
  <rect x="720" y="50" width="265" height="16" rx="5" fill="#3b82f618"/>
  <rect x="720" y="63" width="265" height="3" fill="#3b82f618"/>
  <!-- title -->
  <text x="730" y="61" font-size="7.5" fill="#3b82f6" font-weight="700" letter-spacing=".1em">
    ELEMENT NAME
  </text>
  <!-- body lines (max 4, 12px line-height) -->
  <text x="730" y="80" font-size="8" fill="#7a8fa8">Line 1 of description.</text>
  <text x="730" y="92" font-size="8" fill="#7a8fa8">Line 2 of description.</text>
  <text x="730" y="104" font-size="8" fill="#7a8fa8">Line 3 of description.</text>
</g>
```

### Step 5 — Annotation column rule

Reserve `x: 720–995` in the 1000×530 viewBox as the annotation column. All callout boxes go here. Diagram elements fit in `x: 0–710`. The pointer line connects the callout left edge to the target element.

---

## DWO template for this artifact

```
─────────────────────────────────────────────────────
DOCUMENTATION WORK ORDER
─────────────────────────────────────────────────────
ID:          DWO-<YYYY-MM-DD>-ANI-<NNN>
Issued by:   LIBRARIAN
Assigned to: BUILDER
Priority:    MEDIUM (HIGH if stakeholder review is imminent)
─────────────────────────────────────────────────────

TASK CONTEXT
Task:        Milestone animation — <project name>
Trigger:     <new milestone defined | milestone N status changed | hardware topology changed>

─────────────────────────────────────────────────────

ACTION
File:        docs/milestone-animation.html
Action:      CREATE | UPDATE

If CREATE: fork software-house-ai/templates/milestone-animation.html
If UPDATE: modify only the affected SCENES entries

─────────────────────────────────────────────────────

CONTENT SPECIFICATION
Primary sources to read BEFORE writing:
  - specs/hardware_function_matrix.md
  - specs/node-software-map.md
  - diagrams/node-deployment.*
  - diagrams/per-device/
  - state/roadmap.yaml (milestones section)

Scenes to create/update: <list milestone IDs>
Diagram types: <see Diagram Type Matrix in this document>
Annotation count per scene: ≥ 3, ≤ 8

─────────────────────────────────────────────────────

VERIFICATION
The LIBRARIAN will verify:
  - [ ] All hardware nodes from hardware_function_matrix.md are visible
  - [ ] Navigation is user-controlled (no auto-advance)
  - [ ] Each scene uses the correct diagram type for its nature
  - [ ] Annotations positioned near their elements, not in a separate panel
  - [ ] File opens in browser without server (self-contained HTML)
  - [ ] Viewable on screen without scrolling (≥80% viewport fill)

Status: OPEN
─────────────────────────────────────────────────────
```

---

## Quality checklist (Scientist verification)

Before marking the DWO as DONE, the Scientist runs this checklist:

- [ ] Open the file in a browser. Can a non-technical person understand the system without reading any text in the diagram area?
- [ ] Navigate through all annotations. Does each one appear near its target element?
- [ ] Verify that all hardware nodes listed in `hardware_function_matrix.md` appear in at least one scene.
- [ ] Verify that no scene was built from TASK_QUEUE.md or DASHBOARD.md as the primary source.
- [ ] Resize the window. Does the diagram still fill ≥ 80% without overflow?
