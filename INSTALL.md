# Installation Guide

This guide walks you through bootstrapping a Software House AI instance inside an existing project repository.

**Time required:** ~30 minutes for the first setup.

---

## Prerequisites

- A git repository for your project
- At least one AI agent available (Claude, DeepSeek, Gemini, Manus, or any agent that can read/write files)
- Basic familiarity with Markdown

---

## Step 1 — Add `.swhouse/` to your project

Copy the template directory into your project root:

```bash
# Clone the framework (or use a specific tag for stability)
git clone https://github.com/simpego81/software-house-ai.git /tmp/swh

# Copy the template into your project
cp -r /tmp/swh/instances/claude-code/.swhouse-template your-project/.swhouse

cd your-project
git add .swhouse/
git commit -m "chore: bootstrap Software House AI instance"
```

The `.swhouse/` directory is **committed to git** — it is the versioned memory of your organization.

Do **not** add `.swhouse/` to `.gitignore`.

---

## Step 2 — Configure `instance.yaml`

Edit `.swhouse/instance.yaml` to declare which agents are available on your machine:

```yaml
# .swhouse/instance.yaml
framework_version: "0.1.0"
framework_repo: "https://github.com/simpego81/software-house-ai"

instance:
  machine: "your-machine-name"   # descriptive label, not enforced
  operator: "your-name"          # human operator identifier

agents:
  - role: ARCHITECT
    provider: claude
    model: claude-sonnet-4-6
  - role: EXPLORER
    provider: claude
    model: claude-sonnet-4-6
  - role: CRITIC
    provider: claude
    model: claude-sonnet-4-6
  - role: DESTROYER
    provider: claude
    model: claude-sonnet-4-6
  - role: BUILDER
    provider: claude
    model: claude-sonnet-4-6
  - role: OPTIMIZER
    provider: claude
    model: claude-sonnet-4-6
  - role: LIBRARIAN
    provider: claude
    model: claude-sonnet-4-6
  - role: SCIENTIST
    provider: claude
    model: claude-sonnet-4-6
  - role: PRODUCT_OWNER
    provider: claude
    model: claude-sonnet-4-6
  - role: COORDINATOR
    provider: claude
    model: claude-sonnet-4-6
  - role: EVOLUTION_MASTER
    provider: claude
    model: claude-sonnet-4-6
  - role: ARBITER
    provider: claude
    model: claude-sonnet-4-6
```

If an agent role has no provider available, set `provider: unavailable`. The operational protocol defines fallback behavior for missing roles (see [protocols/operational-cycle.md](protocols/operational-cycle.md#missing-roles)).

---

## Step 3 — Add agent instructions

### Claude Code

Copy the reference adapter:

```bash
cp /tmp/swh/instances/claude-code/CLAUDE.md your-project/CLAUDE.md
```

Edit the copied `CLAUDE.md` to add your project-specific context below the `## Project Context` section.

Install the skills (optional but recommended):

```bash
mkdir -p your-project/.claude/skills
cp /tmp/swh/instances/claude-code/skills/* your-project/.claude/skills/
```

Available skills after installation:

| Skill | Command | Description |
|-------|---------|-------------|
| Open Cycle | `/open-cycle` | Start a new operational cycle |
| Close Cycle | `/close-cycle` | Close cycle, update reputation, archive |
| Vote | `/vote` | Record a reputation vote for an intervention |
| Query Memory | `/query-memory` | Search organizational memory |

### Other agents

Read [instances/](instances/) for available adapters. If your agent is not listed, use the file-based protocol described in [protocols/communication.md](protocols/communication.md) — any agent that can read Markdown and write files can participate.

---

## Step 4 — Verify your installation

Run this checklist:

- [ ] `.swhouse/instance.yaml` exists and is committed
- [ ] `.swhouse/memory/` directory exists (can be empty)
- [ ] `.swhouse/reputation/scores.yaml` exists with initial zeros
- [ ] `.swhouse/cycles/` directory exists (can be empty)
- [ ] Your agent can read `CONSTITUTION.md` and `ECOSYSTEM.md` from the framework

Open a conversation with your agent and ask:

> "Read the Software House AI constitution and tell me what Article 2 says."

If the agent answers correctly, the installation is complete.

---

## Step 5 — Run your first cycle

Start with a small, well-defined problem. Open a cycle:

```
/open-cycle "Define the format for memory entries in this project"
```

The agent will execute the 12-step operational protocol. The cycle record is written to `.swhouse/cycles/current.md`.

When the cycle closes, the result is archived to `.swhouse/cycles/archive/cycle-001.md` and reputation scores are updated.

---

## Directory structure reference

After installation, your project will contain:

```
your-project/
  .swhouse/
    instance.yaml                    ← agent configuration for this machine
    memory/
      decisions/                     ← architectural and process decisions
        YYYY-MM-DD-title.md
      patterns/                      ← reusable patterns discovered
        pattern-name.md
      errors/                        ← documented failures and lessons
        YYYY-MM-DD-title.md
      knowledge/                     ← general knowledge base entries
        topic-name.md
    reputation/
      scores.yaml                    ← current reputation scores
      history/
        cycle-NNN.yaml               ← per-cycle reputation snapshots
    cycles/
      current.md                     ← active cycle (one at a time)
      archive/
        cycle-001.md
        cycle-002.md
    metrics/
      summary.yaml                   ← aggregate performance metrics
```

For the full schema specification, see [schemas/](schemas/).

---

## Multi-machine collaboration

When multiple contributors work on the same project from different machines:

1. Each machine has its own `instance.yaml` (commit yours, others commit theirs — use git branches or a convention like `.swhouse/instances/machine-name.yaml`)
2. Shared state (memory, reputation, cycles) is synchronized via normal git push/pull
3. Before opening a new cycle, always `git pull` to get the latest shared state
4. After closing a cycle, `git push` to share the updated state

Conflicts in `.swhouse/` are resolved the same way as any other git conflict — manually, with the understanding that organizational memory is as important as code.

---

## Upgrading the framework

To upgrade to a newer version of `software-house-ai`:

1. Check the changelog for breaking schema changes
2. Update `framework_version` in `instance.yaml`
3. Run any migration scripts provided in the release notes
4. Commit the updated `.swhouse/` state

Pinning to a git tag is recommended for stability:

```bash
git clone --branch v0.1.0 https://github.com/simpego81/software-house-ai.git
```

---

## Troubleshooting

**Agent ignores the protocol**
Make sure the agent's instruction file (CLAUDE.md or equivalent) explicitly references both `CONSTITUTION.md` and `ECOSYSTEM.md` at startup.

**`.swhouse/` is growing too large**
Archive old cycle records periodically. The active memory should contain only decisions that are still relevant. Deprecated entries can be moved to `.swhouse/memory/archive/`.

**Two agents disagree on the same cycle**
This is expected and desirable (Article 3 — Cognitive Diversity). The Arbiter role resolves conflicts. If no Arbiter is available, escalate to the human operator.
