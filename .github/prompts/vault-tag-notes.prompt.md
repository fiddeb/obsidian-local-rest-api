---
description: Auto-tag and update tags for notes in a vault folder based on content
---

$ARGUMENTS

You are helping the user tag or update tags for notes in their Obsidian vault.

## Step 1: List files in folder

First, list all markdown files in the folder:

```bash
vault-cli list "<FOLDER FROM ARGUMENTS>"
```

## Step 2: Analyze each file

**⚠️ IMPORTANT: Skip Excalidraw files** - Files with `excalidraw-plugin: parsed` in frontmatter should NOT be tagged as patching their frontmatter can corrupt the drawing data.

For each markdown file found:

1. **Read metadata first** to see existing tags:
   ```bash
   vault-cli get "path/to/note.md" --metadata-only
   ```

2. **Analyze the content** if needed (for files without tags or to update existing tags):
   ```bash
   vault-cli get "path/to/note.md" --max-chars 3000
   ```

## Step 3: Update tags using patch

Based on the content analysis, update tags in the frontmatter:

```bash
vault-cli patch "path/to/note.md" --frontmatter "tags" --operation replace --content '["tag1", "tag2", "tag3"]'
```

### Handling files without frontmatter

If a file has no frontmatter section (empty `frontmatter: {}`), the patch operation will fail. In such cases:

1. **Read FULL content** from the file (no --max-chars to avoid truncation):
   ```bash
   vault-cli get "path/to/note.md"
   ```

2. **Create new content** with frontmatter prepended:
   ```bash
   # Read FULL content (no --max-chars parameter!)
   content=$(OBSIDIAN_API_KEY=... vault-cli get "path/to/note.md" | jq -r '.data.content')
   
   # Create new content with frontmatter
   new_content=$(printf -- '---\ntags: ["tag1", "tag2", "tag3"]\n---\n\n%s' "$content")
   
   # Overwrite file using create command
   OBSIDIAN_API_KEY=... vault-cli create "path/to/note.md" --content "$new_content"
   ```

3. **Important**: Do NOT use `--max-chars` when reading content for this operation, as truncated content will lose data

4. **Alternative**: Note the file for manual review if content is very large or sensitive

## Guidelines

- **Be thoughtful**: Analyze content to suggest relevant, specific tags
- **Preserve context**: If a file already has tags, consider keeping useful ones
- **Consistent naming**: Use lowercase, kebab-case for multi-word tags
- **Limit tags**: Aim for 3-5 relevant tags per note
- **Categories to consider**: 
  - Topic/domain (e.g., "python", "ai", "devops")
  - Type (e.g., "tutorial", "reference", "project", "meeting-notes")
  - Status (e.g., "in-progress", "completed", "archived")

## Workflow

1. List all files in the folder
2. For each file:
   - Check existing tags
   - Read content to understand what it's about
   - Suggest appropriate tags based on content
   - Update frontmatter with new/updated tags
3. Summarize changes made

Process files efficiently but thoughtfully. Show progress as you work through the folder.
