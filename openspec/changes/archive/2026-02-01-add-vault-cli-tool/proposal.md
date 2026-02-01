# Change: Add Vault CLI Tool for AI Agents

## Why

Using curl directly in the terminal causes problems:
- Shell escaping issues with quotes, special characters, and multi-line content
- Verbose commands that are error-prone
- No built-in response trimming for token efficiency

A dedicated CLI tool eliminates these problems and provides a clean interface for AI agents to interact with Obsidian vaults.

## What Changes

- **NEW**: Create `vault-cli.py` - a Python CLI tool in `~/.copilot/tools/`
- **UPDATE**: Update the Obsidian Vault skill to reference the CLI tool instead of curl

## Impact

- Affected specs: vault-skill (minor update to tool usage)
- New files: `~/.copilot/tools/vault-cli.py`

## Design Decisions

1. **Python** - Available on macOS, handles Unicode well, easy JSON parsing
2. **Single file** - No dependencies beyond stdlib (uses urllib, json, ssl)
3. **Subcommands** - `search`, `get`, `create`, `append`, `patch`, `daily`, `delete`
4. **Environment variable** - `OBSIDIAN_API_KEY` for authentication
5. **JSON output** - Consistent, parseable output for all commands
6. **Response trimming** - Built-in limits for token efficiency
