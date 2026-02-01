## ADDED Requirements

### Requirement: Vault CLI Tool

The system SHALL provide a Python CLI tool for AI agents to interact with Obsidian vaults without shell escaping issues.

#### Scenario: Agent creates note with special characters
- **WHEN** agent calls `vault-cli create "path/to/note.md" --content "Text with 'quotes' and émojis 🎉"`
- **THEN** note is created successfully without escaping issues

#### Scenario: Agent searches vault
- **WHEN** agent calls `vault-cli search "query" --max-results 5`
- **THEN** returns JSON with top 5 results and snippets

---

### Requirement: Search Command

The CLI SHALL provide a `search` command for finding notes.

#### Scenario: Basic search
- **WHEN** `vault-cli search "opentelemetry"`
- **THEN** returns JSON array of matching notes with paths, scores, and context

#### Scenario: Limited results
- **WHEN** `vault-cli search "topic" --max-results 3 --context-length 50`
- **THEN** returns at most 3 results with 50-char context snippets

---

### Requirement: Get Command

The CLI SHALL provide a `get` command for reading notes.

#### Scenario: Get full note
- **WHEN** `vault-cli get "path/to/note.md"`
- **THEN** returns JSON with content, frontmatter, tags, and stats

#### Scenario: Get metadata only
- **WHEN** `vault-cli get "path/to/note.md" --metadata-only`
- **THEN** returns JSON with frontmatter, tags, and stats but no content

---

### Requirement: Create Command

The CLI SHALL provide a `create` command for making new notes.

#### Scenario: Create with inline content
- **WHEN** `vault-cli create "path/to/note.md" --content "# Title\n\nContent"`
- **THEN** creates note at path with given content

#### Scenario: Create from stdin
- **WHEN** `echo "content" | vault-cli create "path/to/note.md" --stdin`
- **THEN** creates note with content from stdin

---

### Requirement: Append Command

The CLI SHALL provide an `append` command for adding to notes.

#### Scenario: Append content
- **WHEN** `vault-cli append "path/to/note.md" --content "New section"`
- **THEN** appends content to end of note

---

### Requirement: Patch Command

The CLI SHALL provide a `patch` command for targeted insertions.

#### Scenario: Patch under heading
- **WHEN** `vault-cli patch "note.md" --heading "Notes" --operation append --content "New item"`
- **THEN** inserts content under the Notes heading

#### Scenario: Patch frontmatter
- **WHEN** `vault-cli patch "note.md" --frontmatter "status" --operation replace --content "done"`
- **THEN** updates the status frontmatter field

---

### Requirement: Daily Command

The CLI SHALL provide a `daily` command for periodic notes.

#### Scenario: Append to today
- **WHEN** `vault-cli daily --content "Log entry"`
- **THEN** appends to today's daily note (creates if needed)

#### Scenario: Specific date
- **WHEN** `vault-cli daily --date 2026-02-01 --content "Entry"`
- **THEN** appends to that date's daily note

---

### Requirement: Authentication

The CLI SHALL use environment variable for API key.

#### Scenario: Missing API key
- **WHEN** `OBSIDIAN_API_KEY` is not set
- **THEN** prints error message and exits with code 1

---

### Requirement: JSON Output

The CLI SHALL output JSON for all commands.

#### Scenario: Success response
- **WHEN** command succeeds
- **THEN** outputs JSON with `{"ok": true, "data": ...}`

#### Scenario: Error response
- **WHEN** command fails
- **THEN** outputs JSON with `{"ok": false, "error": "message"}`
