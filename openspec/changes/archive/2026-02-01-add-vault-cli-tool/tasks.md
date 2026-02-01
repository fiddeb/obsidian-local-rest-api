# Implementation Tasks

## 1. CLI Tool Core
- [x] 1.1 Create vault-cli.py with argument parsing
- [x] 1.2 Implement API client with SSL handling
- [x] 1.3 Add authentication via environment variable

## 2. Commands
- [x] 2.1 Implement `search` command (simple text search)
- [x] 2.2 Implement `get` command (read note content/metadata)
- [x] 2.3 Implement `create` command (create new note)
- [x] 2.4 Implement `append` command (append to note)
- [x] 2.5 Implement `patch` command (insert at heading/block/frontmatter)
- [x] 2.6 Implement `daily` command (append to daily note)
- [x] 2.7 Implement `delete` command (delete note)
- [x] 2.8 Implement `list` command (list directory contents)

## 3. Token Efficiency
- [x] 3.1 Add `--max-results` flag for search
- [x] 3.2 Add `--context-length` flag for search
- [x] 3.3 Add `--metadata-only` flag for get
- [x] 3.4 Trim long content with `--max-chars` flag

## 4. Installation
- [x] 4.1 Make script executable
- [x] 4.2 Add to PATH or create alias
- [x] 4.3 Update skill documentation

## 5. Testing
- [x] 5.1 Test all commands work correctly
- [x] 5.2 Verify Unicode handling
- [x] 5.3 Test error handling
