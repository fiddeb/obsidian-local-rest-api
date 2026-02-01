# Obsidian Vault Skill

A GitHub Copilot skill that provides token-efficient tools for working with Obsidian vaults via the Local REST API plugin.

## Prerequisites

1. **Obsidian** with the **[Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api)** plugin installed and enabled
2. **Python 3.7+** (for the vault-cli tool)

## Installation

### 1. Copy skill to GitHub Copilot skills directory

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.copilot/skills

# Copy the skill
cp -r .github/skills/obsidian-vault ~/.copilot/skills/
```

### 2. Create vault-cli alias

Add to your `~/.zshrc` (or `~/.bashrc` for bash):

```bash
alias vault-cli='python3 ~/.copilot/skills/obsidian-vault/vault-cli.py'
```

Then reload your shell:

```bash
source ~/.zshrc
```

### 3. Get API key from Obsidian

1. Open Obsidian
2. Go to **Settings** → **Community plugins** → **Local REST API**
3. Copy the **API Key** shown in the settings

### 4. Configure API key

Add to your `~/.zshrc` (or `~/.bashrc`):

```bash
export OBSIDIAN_API_KEY='your-api-key-here'
```

Then reload your shell:

```bash
source ~/.zshrc
```

**Alternative**: Set it temporarily for the current session:

```bash
export OBSIDIAN_API_KEY='your-api-key-here'
```

### 5. Verify installation

```bash
# Test the connection
vault-cli list

# Should return JSON listing your vault's root directory
```

## Configuration

### Environment Variables

- **`OBSIDIAN_API_KEY`** (required): Your Obsidian Local REST API key
- **`OBSIDIAN_API_URL`** (optional): Override the default API URL (default: `https://127.0.0.1:27124`)

## Quick Start

```bash
# Search for notes
vault-cli search "project" --max-results 5

# Read a note
vault-cli get "path/to/note.md"

# Read only metadata (frontmatter, tags)
vault-cli get "path/to/note.md" --metadata-only

# Create a new note
vault-cli create "Projects/New Project.md" --content "# New Project

Description here..."

# Append to daily note
vault-cli daily --content "## Work Log

- Completed task X
- Started task Y"
```

## Usage with GitHub Copilot

Once installed, GitHub Copilot can use this skill to:

- Search your vault for relevant information
- Read notes to get context
- Create new notes with structured content
- Update existing notes
- Manage daily/periodic notes

Just ask Copilot to interact with your Obsidian vault naturally:

- "Search my vault for notes about TOPIC X"
- "Create a new project note for this work"
- "Add today's work to my daily note"
- "What does my note about X say?"

## Documentation

See [SKILL.md](SKILL.md) for complete command reference and workflow examples.

## Troubleshooting

### "OBSIDIAN_API_KEY environment variable not set"

Make sure you've:
1. Added `export OBSIDIAN_API_KEY='...'` to your `~/.zshrc`
2. Reloaded your shell with `source ~/.zshrc`
3. Verify with: `echo $OBSIDIAN_API_KEY`

### "Connection failed" or SSL errors

- Make sure Obsidian is running
- Verify the Local REST API plugin is enabled in Obsidian settings
- Check that the API is listening on `https://127.0.0.1:27124`
- The skill uses certificate verification bypass for localhost (this is safe for local-only connections)

### "code: 401" - Authentication failed

- Your API key is incorrect or has changed
- Get the current API key from Obsidian Settings → Local REST API
- Update your `OBSIDIAN_API_KEY` environment variable

### "code: 404" - Note not found

- Double-check the note path (case-sensitive)
- Use `vault-cli list` to browse your vault structure
- Paths should be relative to vault root, without leading `/`

## License

See [LICENSE.txt](LICENSE.txt)
