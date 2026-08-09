# Context7 MCP Usage Rules

Up-to-date code documentation directly in your prompts. No more outdated examples or hallucinated APIs.

## Why Context7?

| ❌ Without Context7 | ✅ With Context7 |
|---------------------|------------------|
| Outdated code examples | Up-to-date, version-specific docs |
| Hallucinated APIs | Real APIs from official sources |
| Generic answers | Library-specific guidance |

## Available Tools

| Tool | Description |
|------|-------------|
| `resolve-library-id` | Resolves library name to Context7 ID |
| `query-docs` | Retrieves documentation for a library |

## Tool Arguments

### resolve-library-id
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `query` | string | ✅ | User's question or task |
| `libraryName` | string | ✅ | Name of the library to search |

### query-docs
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `libraryId` | string | ✅ | Context7-compatible library ID (e.g., `/mongodb/docs`) |
| `query` | string | ✅ | Question to get relevant documentation |

## When to Use

**Trigger:** When working with any library, framework, or API.

**Action:**
- Add `use context7` to prompts for automatic invocation
- Use `resolve-library-id` first to find correct library ID
- Use `query-docs` with specific questions for targeted documentation
- Specify version in query when needed (e.g., "Next.js 14")

## Usage Patterns

### Direct Library ID (faster)
If you know the library ID, skip resolve step:
```
use library /supabase/supabase for API and docs
```

### With Version
```
How do I set up Next.js 14 middleware? use context7
```

### Auto-invoke Rule
Add to your agent rules:
```
Always use Context7 MCP when I need library/API documentation, code generation, setup or configuration steps.
```

## Common Library IDs

| Library | ID |
|---------|-----|
| Next.js | `/vercel/next.js` |
| React | `/facebook/react` |
| MongoDB | `/mongodb/docs` |
| Supabase | `/supabase/supabase` |

## Best Practices

1. **Use for code generation** - Always fetch current docs before generating code
2. **Specify versions** - Mention version for version-specific docs
3. **Use direct IDs** - Skip resolve step when you know the library ID
4. **Check updates** - Libraries update frequently, always verify current patterns
