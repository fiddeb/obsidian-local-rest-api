# Project Context

## Purpose

Local REST API for Obsidian provides a secure HTTPS interface to automate interactions with Obsidian notes. This plugin allows external tools, scripts, and browser extensions to:
- Read, create, update, or delete notes
- List notes in the vault
- Create and fetch periodic notes
- Execute Obsidian commands

The API is gated behind API key authentication and provides a complete REST interface for vault automation.

## Tech Stack

- **TypeScript** - Main plugin code
- **Express.js** - REST API server
- **esbuild** - Build tooling
- **Jest** - Testing framework
- **Obsidian Plugin API** - Platform integration
- **OpenAPI/Swagger** - API documentation (via Jsonnet)

## Project Conventions

### Code Style
- TypeScript strict mode enabled
- ESLint with TypeScript parser
- Naming conventions:
  - camelCase for variables and functions
  - PascalCase for classes and types
  - kebab-case for file names (e.g., `request-handler.ts`)

### Architecture Patterns
- **Express middleware pattern** - Request handling pipeline
- **Obsidian plugin lifecycle** - onload/onunload hooks
- **API versioning** - Endpoints follow REST conventions
- **Error handling** - Consistent error responses with appropriate HTTP status codes
- **Security**:
  - HTTPS with self-signed certificates
  - API key authentication for all endpoints
  - CORS support for browser extensions

### Testing Strategy
- Unit tests with Jest
- Supertest for API endpoint testing
- Mock Obsidian API for isolated testing
- Test coverage for request handlers and core logic

### Git Workflow
- Semantic commits (if git-workflow skill is active)
- Feature branches for new functionality
- Version bumping via `version-bump.mjs` script
- Version tracking in `manifest.json` and `versions.json`

## Domain Context

### Obsidian Concepts
- **Vault** - The root folder containing all notes and configuration
- **Note** - Markdown file stored in the vault
- **Frontmatter** - YAML metadata at the top of notes
- **Periodic Notes** - Daily, weekly, monthly notes with special handling
- **Commands** - Obsidian actions that can be triggered via API
- **Plugins** - Extensions that enhance Obsidian functionality

### API Patterns
- REST endpoints follow standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- PATCH supports inserting content at specific locations (headings, blocks, frontmatter)
- Periodic notes have dedicated endpoints with date parameters
- Command execution returns success/failure status

### Security Model
- API key must be provided in request headers
- HTTPS required (self-signed cert generated on first run)
- Local-only by default (localhost binding)
- CORS configurable for specific origins

## Important Constraints

### Platform Constraints
- Must work within Obsidian plugin sandbox
- Node.js APIs available via Electron environment
- File system access limited to vault directory
- Plugin must respect Obsidian's file event system

### API Constraints
- Cannot modify Obsidian settings directly
- Command execution depends on plugin availability
- File operations must maintain vault consistency
- Periodic notes require specific plugin configuration

### Security Constraints
- API key authentication mandatory
- HTTPS enforcement for production use
- No sensitive data in logs
- Rate limiting considerations for automation

## External Dependencies

### Runtime Dependencies
- **express** - HTTP server framework
- **cors** - CORS middleware
- **mime-types** - Content-type detection
- **markdown-patch** - PATCH method implementation
- **glob-to-regexp** - Pattern matching for file searches
- **json-logic-js** - Query filtering logic

### Development Dependencies
- **esbuild** - Fast TypeScript bundler
- **jest** - Testing framework
- **typescript** - Type checking
- **obsidian** - Type definitions for plugin API

### External Services
- **None required** - Fully local operation
- Optional: Browser extensions (e.g., Obsidian Web) may consume the API

### Companion Tools
- **vault-cli** - Python CLI tool for AI agents to interact with vault (in `~/.copilot/tools/`)
- **obsidian-vault skill** - Copilot skill defining token-efficient vault interaction patterns
