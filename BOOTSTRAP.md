# Software House AI — Project Bootstrap

This file defines the minimal CLAUDE.md block required to activate the Software House AI framework in any project.

Copy the block below verbatim into the project's `CLAUDE.md`. Replace `[path/to/software-house-ai]` with the actual relative path to the framework submodule (e.g., `../software-house-ai`).

Do not paraphrase, split, or expand this block inside CLAUDE.md. Project-specific rules belong in sections above or below it, never inside it.

---

## Bootstrap block (copy into project CLAUDE.md)

```markdown
## Software House AI

This project operates under the **Software House AI** framework.

- Framework: `[path/to/software-house-ai]/`
- Constitution: binding on all agents — `[path/to/software-house-ai]/CONSTITUTION.md`
- Session startup: `[path/to/software-house-ai]/protocols/session.md`
- Cycle protocol: `[path/to/software-house-ai]/protocols/operational-cycle.md`
- Instance config: `.swhouse/instance.yaml`

### Session startup — mandatory

At the start of every session, follow `protocols/session.md` exactly:
1. Read `.swhouse/instance.yaml`
2. Check `.swhouse/cycles/current.md` — if present, resume the open cycle
3. Read `.swhouse/metrics/summary.yaml`
4. Scan `.swhouse/memory/decisions/` and `.swhouse/memory/patterns/` if relevant
5. Announce as COORDINATOR: `[COORDINATOR]: Session resumed. [one-line status.]`
```

---

## What goes where

| Content | Location |
|---|---|
| Framework principles (universal) | `software-house-ai/CONSTITUTION.md` |
| Framework protocols (universal) | `software-house-ai/protocols/` |
| Agent fleet configuration | `.swhouse/instance.yaml` |
| Cycle state | `.swhouse/cycles/current.md` |
| Organizational memory | `.swhouse/memory/` |
| Project-specific rules | Project `CLAUDE.md` (outside the bootstrap block) |
| Technology, architecture, commands | Project `CLAUDE.md` |

Framework rules must pass the **Universality Test** (Article 21): would this rule make sense in a project with a completely different technology stack, deployment target, and domain? If no, it belongs in the project's `CLAUDE.md`, not in the framework.
