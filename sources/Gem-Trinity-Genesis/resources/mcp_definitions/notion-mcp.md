# Notion MCP Server Usage Rules

Official MCP Server for Notion API - manage pages, databases, comments and more.

## Prerequisites

1. Create Notion integration at https://www.notion.so/profile/integrations
2. Get your integration token (`ntn_****`)
3. Connect pages to your integration (Settings > Connections)

## Configuration

⚠️ **Replace `YOUR_NOTION_TOKEN_HERE`** in settings.json with your actual token:
```json
"env": {
  "NOTION_TOKEN": "ntn_xxxx..."
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `search` | Search pages and databases |
| `get_page` | Get page content |
| `create_page` | Create new page |
| `update_page` | Update page properties |
| `get_database` | Get database schema |
| `query_database` | Query database entries |
| `create_comment` | Add comments to pages |

## When to Use

**Trigger:** Working with Notion content, documentation, or project management.

**Action:**
- Search Notion for relevant documentation
- Create pages from code specifications
- Query databases for project tracking
- Add comments for collaboration

## Example Commands

```
Comment "Hello MCP" on page "Getting started"
```

```
Add a page titled "Notion MCP" to page "Development"
```

```
Get the content of page 1a6b35e6e67f802fa7e1d27686f017f2
```

## Security Note

> Create a **read-only** integration if you only need to read content.
> Configure capabilities in your integration settings.

## Best Practices

1. **Connect only needed pages** - Only share necessary content
2. **Use read-only for safety** - Limit write access if not needed
3. **Reference by ID** - Use page IDs for precise operations
4. **Combine with search** - Search first, then operate on results
