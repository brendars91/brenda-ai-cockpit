# Fetch MCP Usage Rules

A server that provides web content fetching capabilities, converting HTML to markdown.

> [!CAUTION]
> This server can access local/internal IP addresses. Exercise caution to avoid exposing sensitive data.

## Available Tools

| Tool | Description |
|------|-------------|
| `fetch` | Fetches a URL and extracts contents as markdown |

## Tool Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | URL to fetch |
| `max_length` | integer | ❌ | 5000 | Maximum characters to return |
| `start_index` | integer | ❌ | 0 | Start content from this character index |
| `raw` | boolean | ❌ | false | Get raw content without markdown conversion |

## When to Use

**Trigger:** When needing to fetch and read web content.

**Action:**
- Use `fetch` to retrieve webpage content as markdown
- Use `start_index` to paginate through long documents
- Use `raw: true` for non-HTML content (JSON, plain text)

## Pagination Pattern

For long webpages, use `start_index` to read in chunks:

```
1. fetch(url, max_length: 5000, start_index: 0)    → First 5000 chars
2. fetch(url, max_length: 5000, start_index: 5000) → Next 5000 chars
3. Continue until desired content found
```

## Best Practices

1. **Start with default max_length** (5000) - increase only if needed
2. **Use pagination** for long pages rather than fetching everything
3. **Prefer markdown conversion** - only use `raw: true` for APIs or structured data
4. **Respect rate limits** - don't fetch the same URL repeatedly
5. **Check robots.txt compliance** - server respects robots.txt by default

## Use Cases

- Reading documentation pages
- Extracting article content
- Fetching API responses (with `raw: true`)
- Researching web content for context
