# Implementation Tasks

## 1. Skill Definition
- [x] 1.1 Create skill file structure at `~/.copilot/skills/obsidian-vault/SKILL.md`
- [x] 1.2 Define skill metadata (name, description, triggers)
- [x] 1.3 Document API connection requirements (host, port, bearer token, TLS)

## 2. Core Tools Implementation
- [x] 2.1 Define `search_vault` tool with query and contextLength parameters
- [x] 2.2 Define `get_note_metadata` tool for frontmatter/tags/stat retrieval
- [x] 2.3 Define `get_note_content` tool for full content retrieval
- [x] 2.4 Define `create_note` tool with path and content parameters
- [x] 2.5 Define `append_to_note` tool for appending content
- [x] 2.6 Define `patch_note` tool for targeted insertions (heading/block/frontmatter)
- [x] 2.7 Define `daily_note_append` tool for quick daily note access

## 3. Token Efficiency Patterns
- [x] 3.1 Document search-then-fetch pattern
- [x] 3.2 Specify response trimming rules (max results, context length)
- [x] 3.3 Define output normalization schema
- [x] 3.4 Document caching strategy with mtime invalidation

## 4. Usage Examples
- [x] 4.1 Add example: Search for related notes before creating
- [x] 4.2 Add example: Append work session summary to daily note
- [x] 4.3 Add example: Update frontmatter on existing note
- [x] 4.4 Add example: Document a conversation or solution

## 5. Error Handling
- [x] 5.1 Document common error scenarios (404, auth, connection)
- [x] 5.2 Define graceful fallback behaviors
