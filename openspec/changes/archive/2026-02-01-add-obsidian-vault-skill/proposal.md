# Change: Add Obsidian Vault Skill for AI Agents

## Why

AI agents (like GitHub Copilot) need a structured, token-efficient way to interact with Obsidian vaults. Currently, there's no standardized skill that defines how to search, read, create, and update notes while minimizing context pollution and API overhead.

The key insight from preliminary research is that token efficiency comes from:
1. Two-stage retrieval: search first, then fetch only needed files
2. Server-side filtering: use API search capabilities instead of listing/reading entire vault
3. Narrow response surface: return minimal JSON, not raw documents
4. Smart caching: reuse results until file mtime changes

## What Changes

- **NEW**: Create a Copilot skill (`~/.copilot/skills/obsidian-vault/SKILL.md`) that:
  - Defines 5-7 core tools for vault interaction
  - Implements token-efficient retrieval patterns
  - Provides structured output schemas for consistent responses
  - Documents caching and error handling strategies
  - Includes practical usage examples and workflows

## Impact

- Affected specs: None (new capability)
- Affected code: No code changes to the Obsidian plugin itself
- New files: Skill definition file in user's Copilot config directory

## Design Principles

### Core Tools (Minimal Set)

1. **search_vault** - Search for notes using simple text query, returns snippets
2. **get_note_metadata** - Fetch note metadata (frontmatter, tags, stats) without content
3. **get_note_content** - Fetch full note content (only when explicitly needed)
4. **create_note** - Create a new note at specified path
5. **append_to_note** - Append content to an existing note
6. **patch_note** - Insert content at specific location (heading/block/frontmatter)
7. **daily_note** - Quick access to daily/periodic notes (append or replace)

### Token Efficiency Strategy

1. **Search returns snippets only**: Use `contextLength` parameter to limit response size
2. **Metadata before content**: Always check if metadata alone suffices
3. **Top-N filtering**: Never return more than 10 results without explicit request
4. **Structured output**: All responses use consistent JSON schema
5. **No raw dumps**: Never return full vault listings or complete file trees
