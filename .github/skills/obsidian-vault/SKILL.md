# Obsidian Vault Skill

Token-efficient tools for reading, searching, creating, and editing notes in Obsidian vaults via the Local REST API.

## Quick Start - Using vault-cli

The `vault-cli` tool handles all API communication, SSL, and authentication automatically.

```bash
# Set API key (add to ~/.zshrc for persistence)
export OBSIDIAN_API_KEY='your-key-here'

# Search
vault-cli search "topic" --max-results 5

# Read note
vault-cli get "path/to/note.md"
vault-cli get "path/to/note.md" --metadata-only

# Create note
vault-cli create "path/to/note.md" --content "# Title\n\nContent"

# Append to note
vault-cli append "path/to/note.md" --content "New content"

# Daily note
vault-cli daily --content "## Log entry\n\nDetails..."

# Patch (insert at specific location)
vault-cli patch "note.md" --heading "Notes" --operation append --content "New item"
```

## Connection Details

- **CLI Tool**: `~/.copilot/skills/obsidian-vault/vault-cli.py` (alias: `vault-cli`)
- **Base URL**: `https://127.0.0.1:27124` (configurable via `OBSIDIAN_API_URL`)
- **Authentication**: `OBSIDIAN_API_KEY` environment variable
- **API Token**: Find in Obsidian Settings → Local REST API

## Key Principles

1. **Search first, fetch later**: Use search to find candidates, then fetch only what you need
2. **Metadata before content**: Check if frontmatter/tags suffice before reading full content
3. **Snippets over dumps**: Request minimal context length in searches
4. **Top-N results**: Never return more than 10 results without explicit need
5. **Structured output**: All responses are JSON for easy parsing

---

## Commands Reference

### search - Find notes

```bash
vault-cli search "query" [--max-results N] [--context-length N]
```

**Example**:
```bash
vault-cli search "opentelemetry" --max-results 5 --context-length 80
```

**Output**: JSON with paths, scores, and snippets for each match.

---

### get - Read note

```bash
vault-cli get "path/to/note.md" [--metadata-only] [--max-chars N]
```

**Examples**:
```bash
# Full note with content
vault-cli get "Projects/Alpha.md"

# Metadata only (frontmatter, tags, stats)
vault-cli get "Projects/Alpha.md" --metadata-only

# Truncate long content
vault-cli get "Projects/Alpha.md" --max-chars 2000
```

---

### list - List directory

```bash
vault-cli list [path]
```

**Examples**:
```bash
vault-cli list              # Root of vault
vault-cli list "Projects/"  # Specific directory
```

---

### create - Create new note

```bash
vault-cli create "path/to/note.md" --content "content"
vault-cli create "path/to/note.md" --stdin
vault-cli create "path/to/note.md" --file /path/to/file.md
```

**Example with frontmatter**:
```bash
vault-cli create "Dev/New Project.md" --content "---
title: New Project
created: 2026-02-01
tags: [project, dev]
---

# New Project

Description here..."
```

---

### append - Add to note

```bash
vault-cli append "path/to/note.md" --content "content to add"
vault-cli append "path/to/note.md" --stdin
```

**Example**:
```bash
vault-cli append "Projects/Alpha.md" --content "

## Update - 2026-02-01

New information added..."
```

---

### patch - Insert at specific location

```bash
vault-cli patch "note.md" --heading "Target" --operation append --content "text"
vault-cli patch "note.md" --frontmatter "field" --operation replace --content "value"
vault-cli patch "note.md" --block "ref123" --operation prepend --content "text"
```

**Operations**: `append`, `prepend`, `replace`

**Examples**:
```bash
# Add under a heading
vault-cli patch "Projects/Alpha.md" --heading "Notes" --operation append --content "- New note item"

# Update frontmatter
vault-cli patch "Projects/Alpha.md" --frontmatter "status" --operation replace --content '"completed"'

# Nested heading (use :: separator)
vault-cli patch "doc.md" --heading "Chapter 1::Section A" --operation append --content "New text"
```

---

### daily - Periodic notes

```bash
vault-cli daily --content "content" [--date YYYY-MM-DD] [--period daily|weekly|monthly]
```

**Examples**:
```bash
# Today's daily note
vault-cli daily --content "## Session Log

- Worked on X
- Fixed Y"

# Specific date
vault-cli daily --date 2026-02-01 --content "Entry for that date"

# Weekly note
vault-cli daily --period weekly --content "Week summary"
```

---

### delete - Remove note

```bash
vault-cli delete "path/to/note.md"
```

---

## Workflow Examples

### Document a Solution

1. **Search for existing notes**:
   ```bash
   vault-cli search "topic name" --max-results 5
   ```

2. **Decide**: Create new or append to existing?

3. **Create new**:
   ```bash
   vault-cli create "Dev/Solution - Topic.md" --content "---
   title: Solution - Topic
   created: 2026-02-01
   tags: [solution, topic]
   ---
   
   # Solution - Topic
   
   ## Problem
   Description...
   
   ## Solution
   How we fixed it..."
   ```

4. **Or append to existing**:
   ```bash
   vault-cli append "existing-note.md" --content "
   
   ## Additional Notes - 2026-02-01
   
   New findings..."
   ```

### Log Work Session

```bash
vault-cli daily --content "## Work Session - 14:30

**Topic**: What was worked on
**Outcome**: What was achieved

### Key Points
- Point 1
- Point 2"
```

### Update Project Status

```bash
# Update frontmatter
vault-cli patch "Projects/Alpha.md" --frontmatter "status" --operation replace --content '"completed"'

# Add history entry
vault-cli patch "Projects/Alpha.md" --heading "History" --operation append --content "
- **2026-02-01**: Project completed"
```

---

## Error Handling

All commands return JSON with `ok` field:

**Success**:
```json
{"ok": true, "data": {...}}
```

**Error**:
```json
{"ok": false, "error": "Error message", "code": 404}
```

Common errors:
- `OBSIDIAN_API_KEY environment variable not set` - Set the API key
- `Connection failed` - Obsidian not running or plugin disabled
- `code: 404` - Note doesn't exist
- `code: 401` - Invalid API key

