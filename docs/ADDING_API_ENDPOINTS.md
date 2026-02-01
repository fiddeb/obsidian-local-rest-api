# Adding New API Endpoints

This guide walks through adding new endpoints to the Obsidian Local REST API. We'll use the `/tags/` endpoint as an example.

## Overview

Adding a new API endpoint has five steps:
1. Understand the existing architecture
2. Write tests (TDD approach)
3. Implement the functionality
4. Document the API
5. Verify the implementation

## Step 1: Understand the Existing Architecture

### Files You'll Work With

- `src/requestHandler.ts` - Where all endpoints are implemented
- `src/requestHandler.test.ts` - Test suite for endpoints
- `mocks/obsidian.ts` - Mock implementations of Obsidian API for testing
- `docs/openapi.yaml` - OpenAPI specification for API documentation
- `src/types.ts` - TypeScript type definitions
- `src/api.ts` - Public API for extensions

### Explore Existing Endpoints

Look at similar endpoints first:

```bash
# Find how GET endpoints are implemented
grep -n "Get(req: express.Request" src/requestHandler.ts

# Find how routes are registered
grep -n "this.api.route" src/requestHandler.ts

# Look at test patterns
grep -n "describe\|test(" src/requestHandler.test.ts | head -20
```

### Check Available Obsidian APIs

```bash
# Search for relevant functions in Obsidian's type definitions
grep -i "getAllTags\|metadataCache" node_modules/obsidian/obsidian.d.ts
```

For the `/tags/` endpoint:
```typescript
// Found in node_modules/obsidian/obsidian.d.ts
export function getAllTags(cache: CachedMetadata): string[] | null;
```

## Step 2: Write Tests (TDD Approach)

### 2.1 Update Mock Implementations

If your endpoint uses Obsidian API functions, implement them in the mock first.

In `mocks/obsidian.ts`:

```typescript
export function getAllTags(cache: CachedMetadata): string[] | null {
  if (!cache) return null;
  
  const tags: string[] = [];
  
  // In-line tags (with #)
  if (cache.tags) {
    for (const tagObj of cache.tags) {
      if (tagObj.tag) {
        tags.push(tagObj.tag);
      }
    }
  }
  
  // Frontmatter tags
  if (cache.frontmatter?.tags) {
    const fmTags = cache.frontmatter.tags as string[];
    if (Array.isArray(fmTags)) {
      for (const tag of fmTags) {
        tags.push(tag.startsWith('#') ? tag : `#${tag}`);
      }
    }
  }
  
  return tags.length > 0 ? tags : null;
}
```

### 2.2 Write Tests

In `src/requestHandler.test.ts`:

Cover these cases:
- Authentication (unauthorized access)
- Edge cases (empty data)
- Main functionality
- Special cases (sorting, filtering, etc.)

```typescript
describe("tagsGet", () => {
  test("unauthorized", async () => {
    await request(server).get("/tags/").expect(401);
  });

  test("empty vault returns empty tags", async () => {
    app.vault._markdownFiles = [];

    const result = await request(server)
      .get("/tags/")
      .set("Authorization", `Bearer ${API_KEY}`)
      .expect(200);

    expect(result.body.tags).toEqual([]);
    expect(result.body.totalTags).toEqual(0);
    expect(result.body.totalOccurrences).toEqual(0);
  });

  test("returns tags with counts sorted by count descending", async () => {
    const file1 = new TFile();
    file1.path = "note1.md";
    const file2 = new TFile();
    file2.path = "note2.md";
    
    app.vault._markdownFiles = [file1, file2];

    // Set up mock data
    const cacheMock = new Map<string, CachedMetadata>();
    const cache1 = new CachedMetadata();
    cache1.tags = [{ tag: "#grafana" }, { tag: "#loki" }];
    cacheMock.set("note1.md", cache1);

    app.metadataCache.getFileCache = (file: TFile) => 
      cacheMock.get(file.path) || new CachedMetadata();

    const result = await request(server)
      .get("/tags/")
      .set("Authorization", `Bearer ${API_KEY}`)
      .expect(200);

    expect(result.body.tags).toEqual([
      { tag: "grafana", count: 1 },
      { tag: "loki", count: 1 },
    ]);
  });
});
```

### 2.3 Verify Tests Fail Initially

```bash
npm test -- --testNamePattern="tagsGet"
# Tests should fail - endpoint not implemented yet
```

## Step 3: Implement the Functionality

### 3.1 Import Required Dependencies

**File: `src/requestHandler.ts`**

```typescript
import {
  apiVersion,
  App,
  CachedMetadata,
  Command,
  getAllTags,  // <-- Add new import
  PluginManifest,
  prepareSimpleSearch,
  TFile,
} from "obsidian";
```

### 3.2 Implement the Endpoint Method

Add your method in `src/requestHandler.ts`. Put it near similar endpoints.

```typescript
/**
 * GET /tags/
 * Returns all tags in the vault with their counts
 */
tagsGet(req: express.Request, res: express.Response): void {
  const tagCounts: Record<string, number> = {};

  // Iterate over all markdown files
  const files = this.app.vault.getMarkdownFiles();

  for (const file of files) {
    const cache = this.app.metadataCache.getFileCache(file);
    if (!cache) continue;

    const tags = getAllTags(cache);
    if (!tags) continue;

    for (const tag of tags) {
      // Normalize: remove leading # if present
      const normalizedTag = tag.replace(/^#/, "");
      tagCounts[normalizedTag] = (tagCounts[normalizedTag] || 0) + 1;
    }
  }

  // Sort by count (descending) then alphabetically
  const sortedTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([tag, count]) => ({ tag, count }));

  res.json({
    tags: sortedTags,
    totalTags: sortedTags.length,
    totalOccurrences: Object.values(tagCounts).reduce((a, b) => a + b, 0),
  });
}
```

Patterns to follow:
- Use descriptive method names matching the pattern `{resource}{HttpMethod}`
- Add JSDoc comments explaining what the endpoint does
- Use `this.app` to access Obsidian's API
- Return JSON using `res.json()`
- For errors, use `this.returnCannedResponse(res, { statusCode, errorCode })`

### 3.3 Register the Route

In the `setupRouter()` method, add your route registration:

```typescript
setupRouter(): void {
  // ... existing middleware setup ...

  // Register routes
  this.api.route("/commands/").get(this.commandGet.bind(this));
  this.api.route("/commands/:commandId/").post(this.commandPost.bind(this));

  this.api.route("/tags/").get(this.tagsGet.bind(this));  // <-- Add here

  this.api.route("/search/").post(this.searchQueryPost.bind(this));
  // ... more routes ...
}
```

Route patterns:
- Simple GET: `.get(this.methodName.bind(this))`
- With params: `"/resource/:param/"` 
- Multiple methods: `.route("/path/").get(...).post(...).delete(...)`

### 3.4 Verify Tests Pass

```bash
npm test -- --testNamePattern="tagsGet"
# All tests should pass now
```

## Step 4: Document the API

### 4.1 Add to OpenAPI Specification

**File: `docs/openapi.yaml`**

Find an appropriate location (usually alphabetically or near similar endpoints) and add your endpoint definition:

```yaml
  /tags/:
    get:
      description: |
        Returns all tags used in the vault, along with the count of how many
        notes use each tag. Tags are sorted by count (descending) and then
        alphabetically. Both inline tags (#tag) and frontmatter tags are included.
      responses:
        "200":
          content:
            application/json:
              example:
                tags:
                  - tag: "project"
                    count: 42
                  - tag: "meeting"
                    count: 15
                  - tag: "idea"
                    count: 8
                totalTags: 3
                totalOccurrences: 65
              schema:
                properties:
                  tags:
                    description: "Array of tags with their occurrence counts"
                    items:
                      properties:
                        tag:
                          description: "The tag name (without leading #)"
                          type: "string"
                        count:
                          description: "Number of notes containing this tag"
                          type: "number"
                      type: "object"
                    type: "array"
                  totalTags:
                    description: "Total number of unique tags in the vault"
                    type: "number"
                  totalOccurrences:
                    description: "Total number of tag occurrences across all notes"
                    type: "number"
                type: "object"
          description: "A list of all tags in the vault with counts."
      summary: |
        Get all tags in the vault with occurrence counts.
      tags:
        - "Tags"
```

Include in your OpenAPI documentation:
- Description explaining what the endpoint does
- All possible response codes (200, 400, 401, 404, etc.)
- Example response data
- Schema with descriptions
- Summary (one-line description)
- Tags for grouping in Swagger UI

## Step 5: Build, Deploy, and Verify

### 5.1 Run Full Test Suite

```bash
npm test
# Ensure all tests pass, not just your new ones
```

### 5.2 Build the Plugin

```bash
npm run build
```

### 5.3 Deploy to Obsidian

```bash
# Copy to your vault's plugins directory
cp main.js "<path-to-vault>/.obsidian/plugins/obsidian-local-rest-api/"
```

### 5.4 Test in Production

Reload the plugin in Obsidian, then test:

```bash
# Test the endpoint
curl -k -H "Authorization: Bearer YOUR_API_KEY" \
  https://127.0.0.1:27124/tags/ | jq

# Verify OpenAPI documentation
open http://127.0.0.1:27124/
```

### 5.5 View Documentation

Start a local server to view Swagger UI:

```bash
cd docs
python3 -m http.server 8080
open http://localhost:8080/
```

## Common Patterns

### Authentication

Most endpoints should require authentication:

```typescript
// Authentication is handled by middleware, but verify in tests:
test("unauthorized", async () => {
  await request(server).get("/your-endpoint/").expect(401);
});
```

### Error Handling

Use the error response helper:

```typescript
if (!resource) {
  this.returnCannedResponse(res, { 
    statusCode: 404,
    message: "Resource not found" 
  });
  return;
}
```

### Async Operations

If you need to read files or perform async operations:

```typescript
async myEndpoint(req: express.Request, res: express.Response): Promise<void> {
  const content = await this.app.vault.adapter.read(path);
  // ... process content ...
  res.json({ data: result });
}
```

### Query Parameters

Access query parameters via `req.query`:

```typescript
const limit = parseInt(req.query.limit as string) || 10;
const filter = req.query.filter as string;
```

### Path Parameters

For routes like `/resource/:id/`:

```typescript
const resourceId = req.params.id;
```

### Request Body

For POST/PUT/PATCH requests:

```typescript
const data = req.body;  // Parsed by body-parser middleware
```

## Troubleshooting

### Tests Fail After Implementation

1. Check mock implementations match real Obsidian API
2. Verify test data setup (files, caches, etc.)
3. Run with verbose output: `npm test -- --verbose`

### Endpoint Returns 404

1. Verify route is registered in `setupRouter()`
2. Check route path matches exactly (trailing slashes matter!)
3. Rebuild the plugin: `npm run build`

### TypeScript Compilation Errors

1. Ensure imports are correct
2. Check type definitions in `src/types.ts`
3. Run type check: `npm run build` (includes tsc check)

### Documentation Not Showing

1. Verify OpenAPI YAML is valid (use online validator)
2. Check indentation in YAML (must use spaces, not tabs)
3. Restart the documentation server

## Example Checklist

When adding a new endpoint, use this checklist:

- [ ] Research Obsidian API capabilities
- [ ] Update `mocks/obsidian.ts` with any new mocks needed
- [ ] Import `CachedMetadata` in test file if needed
- [ ] Write test: unauthorized access
- [ ] Write test: edge cases (empty, missing data)
- [ ] Write test: main functionality
- [ ] Write test: special cases (sorting, filtering)
- [ ] Verify tests fail initially
- [ ] Import required Obsidian API functions
- [ ] Implement endpoint method with JSDoc
- [ ] Register route in `setupRouter()`
- [ ] Verify tests pass
- [ ] Add OpenAPI documentation
- [ ] Run full test suite
- [ ] Build plugin
- [ ] Deploy to test vault
- [ ] Test with curl/API client
- [ ] Verify Swagger documentation displays correctly

## Resources

- [Obsidian API Documentation](https://github.com/obsidianmd/obsidian-api)
- [Express.js Documentation](https://expressjs.com/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Jest Testing Framework](https://jestjs.io/)

## Getting Help

- Check existing endpoints in `src/requestHandler.ts` for patterns
- Look at test files for testing examples
- Review OpenAPI spec for documentation examples
- Open an issue on GitHub for complex questions
