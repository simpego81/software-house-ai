# Skill: /query-memory

Searches the organizational memory for entries relevant to a query.

## Usage

```
/query-memory "[query]"
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Natural language description of what to find | `"authentication decisions"` or `"database errors"` |

## Instructions for Claude Code

When `/query-memory` is invoked:

1. Parse the query string.

2. Search all four memory directories for relevant entries:
   - `.swhouse/memory/decisions/`
   - `.swhouse/memory/patterns/`
   - `.swhouse/memory/errors/`
   - `.swhouse/memory/knowledge/`

3. For each matching file, extract:
   - File path
   - Date (from filename or frontmatter)
   - Title (from frontmatter or first heading)
   - One-paragraph summary of the relevant content

4. Return results grouped by type:

```
## Memory query: "[query]"

### Decisions (N results)
- [YYYY-MM-DD] [title] — [one sentence summary]
  Path: memory/decisions/YYYY-MM-DD-title.md

### Patterns (N results)
- [pattern-name] — [one sentence summary]
  Path: memory/patterns/pattern-name.md

### Errors (N results)
- [YYYY-MM-DD] [title] — [one sentence summary]
  Path: memory/errors/YYYY-MM-DD-title.md

### Knowledge (N results)
- [topic-name] — [one sentence summary]
  Path: memory/knowledge/topic-name.md

---
Total: [N] results found
```

5. If no results are found:
   > "No memory entries found for '[query]'. This may be the first time this topic has been addressed."

## Use cases

- Before opening a cycle: find prior decisions on the same topic
- During Step 3 (Architect): find architectural patterns
- During Step 7 (Builder): find reusable implementation patterns
- During Step 10 (Librarian): check for duplicate entries before writing

## Example

```
/query-memory "message queue design"
```

Returns all decisions, patterns, errors, and knowledge entries that mention message queues, MQTT, NATS, queuing, or related concepts.
