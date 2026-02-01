## ADDED Requirements

### Requirement: Obsidian Vault Skill

The skill SHALL provide AI agents with structured, token-efficient access to Obsidian vaults via the Local REST API.

#### Scenario: Agent documents a conversation
- **WHEN** user asks agent to document a solution or conversation
- **THEN** agent uses skill tools to append or create notes without additional user guidance

#### Scenario: Agent searches for related content
- **WHEN** agent needs context about a topic before responding
- **THEN** agent uses `search_vault` to find relevant notes with minimal token overhead

---

### Requirement: Search Vault Tool

The skill SHALL provide a `search_vault` tool that searches for notes using text queries and returns ranked snippets.

#### Scenario: Simple text search
- **WHEN** agent calls `search_vault` with query "project alpha"
- **THEN** returns up to 10 results with file paths, scores, and context snippets
- **AND** each snippet is limited to configured `contextLength` (default 100 chars)

#### Scenario: Empty results
- **WHEN** search returns no matches
- **THEN** returns empty array with clear message

---

### Requirement: Get Note Metadata Tool

The skill SHALL provide a `get_note_metadata` tool that fetches note metadata without content.

#### Scenario: Fetch metadata for decision making
- **WHEN** agent calls `get_note_metadata` with path "Projects/Alpha.md"
- **THEN** returns frontmatter fields, tags, and file stats (mtime, ctime, size)
- **AND** does NOT include full content

---

### Requirement: Get Note Content Tool

The skill SHALL provide a `get_note_content` tool that fetches full note content.

#### Scenario: Read full note when needed
- **WHEN** agent calls `get_note_content` with path "Projects/Alpha.md"
- **THEN** returns complete markdown content
- **AND** includes frontmatter and tags for context

---

### Requirement: Create Note Tool

The skill SHALL provide a `create_note` tool that creates new notes.

#### Scenario: Create new note with content
- **WHEN** agent calls `create_note` with path and content
- **THEN** creates file at specified path with given content
- **AND** creates parent directories if needed

#### Scenario: Note already exists
- **WHEN** target path already exists
- **THEN** returns error suggesting use of update tools instead

---

### Requirement: Append to Note Tool

The skill SHALL provide an `append_to_note` tool that appends content to existing notes.

#### Scenario: Append to existing note
- **WHEN** agent calls `append_to_note` with path and content
- **THEN** appends content to end of file

#### Scenario: Append to non-existent note
- **WHEN** target note doesn't exist
- **THEN** creates the note with the provided content

---

### Requirement: Patch Note Tool

The skill SHALL provide a `patch_note` tool for targeted content insertion.

#### Scenario: Append under heading
- **WHEN** agent calls `patch_note` with operation="append", targetType="heading", target="Notes"
- **THEN** inserts content after the "Notes" heading

#### Scenario: Update frontmatter field
- **WHEN** agent calls `patch_note` with operation="replace", targetType="frontmatter", target="status"
- **THEN** updates the frontmatter field to new value

---

### Requirement: Daily Note Append Tool

The skill SHALL provide a `daily_note_append` tool for quick daily note access.

#### Scenario: Append to today's daily note
- **WHEN** agent calls `daily_note_append` with content
- **THEN** appends content to today's daily note
- **AND** creates the daily note if it doesn't exist

#### Scenario: Append to specific date
- **WHEN** agent calls `daily_note_append` with content and date (year, month, day)
- **THEN** appends content to that date's daily note

---

### Requirement: Token Efficiency

The skill SHALL implement patterns that minimize context token usage.

#### Scenario: Search returns snippets not full content
- **WHEN** search results are returned
- **THEN** each result contains only path, score, and short context snippet

#### Scenario: Response size limits
- **WHEN** any tool returns results
- **THEN** total response is capped at reasonable size (suggested 20KB)
- **AND** results exceeding limit are truncated with indication

---

### Requirement: Structured Output

The skill SHALL normalize all outputs to consistent JSON schema.

#### Scenario: Consistent result format
- **WHEN** any tool returns successfully
- **THEN** response follows documented schema
- **AND** includes status indicator and relevant data fields
