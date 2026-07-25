# Software House AI

**An open framework for building evolutionary, multi-agent software organizations.**

> "Ideas compete. Knowledge cooperates. The ecosystem evolves."

---

## What this is

Software House AI is a framework for organizing AI agents into a **collaborative, self-improving software organization**. It defines:

- A **Constitution** — immutable principles governing how the organization operates
- **12 founding agent roles** — with distinct cognitive profiles and responsibilities
- An **operational protocol** — a structured cycle for processing any problem
- A **versioned state schema** — so organizational memory evolves alongside your code

The framework is **agent-agnostic**. An instance may run on Claude, DeepSeek, Gemini, Manus, or any future agent that can read and write files. Each deployment adapts the roles to the agents available.

## What this is not

- A coding framework or library
- A specific AI agent or model
- A fixed team topology — roles and workflows can evolve

## Core concepts

| Concept | Description |
|---------|-------------|
| **Framework** | This repository. The "genome" of the organization. |
| **Instance** | A deployment on a specific machine with specific agents. |
| **Project** | A software product the instance is working on. |
| **Cycle** | One complete execution of the 12-step operational protocol. |
| **`.swhouse/`** | The versioned state directory committed inside each project repo. |

## Architecture

```
software-house-ai/        ← this repo (the framework)
    CONSTITUTION.md
    ECOSYSTEM.md
    protocols/
    schemas/
    agents/
    instances/            ← agent-specific adapters

[your-project-repo]/      ← your software project
    .swhouse/             ← versioned instance state (committed to git)
        instance.yaml     ← which agents are available on this machine
        memory/
        reputation/
        cycles/
    CLAUDE.md             ← or equivalent for your agent
```

The `.swhouse/` directory travels with the project. Different contributors on different machines may have different agents — `instance.yaml` declares what is available locally. Shared state (memory, decisions, reputation) is synchronized through git.

## Quick start

See [INSTALL.md](INSTALL.md).

## Founding documents

- [CONSTITUTION.md](CONSTITUTION.md) — 15 articles. The immutable principles.
- [ECOSYSTEM.md](ECOSYSTEM.md) — 12 agents. The operational model.

## Protocols

- [protocols/operational-cycle.md](protocols/operational-cycle.md) — The 12-step cycle
- [protocols/communication.md](protocols/communication.md) — How agents exchange information
- [protocols/review.md](protocols/review.md) — How proposals are reviewed
- [protocols/reputation.md](protocols/reputation.md) — How contributions are scored

## Agent definitions

Each agent has a dedicated specification in [agents/](agents/).

## Agent-specific adapters

- [instances/claude-code/](instances/claude-code/) — Reference implementation for Claude Code

## License

MIT — fork it, adapt the constitution, run your own ecosystem.

## Version

`0.1.0` — Bootstrap phase. The organization is building itself.
