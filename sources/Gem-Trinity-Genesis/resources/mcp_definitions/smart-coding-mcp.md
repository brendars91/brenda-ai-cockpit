# Smart Coding MCP Usage Rules

You must prioritize using the **Smart Coding MCP** tools for the following tasks.

## Available Tools

| Tool | Description |
|------|-------------|
| `d_check_last_version` | Check latest package versions |
| `a_semantic_search` | Semantic search across codebase |
| `e_set_workspace` | Set/change workspace path |
| `f_get_status` | Get MCP server health and index status |

## 1. Dependency Management

**Trigger:** When checking, adding, or updating package versions (npm, python, go, rust, etc.).

**Action:**
- **MUST** use the `d_check_last_version` tool
- **DO NOT** guess versions or trust internal training data
- **DO NOT** use generic web search unless `d_check_last_version` fails

## 2. Codebase Research

**Trigger:** When asking about "how" something works, finding logic, or understanding architecture.

**Action:**
- **MUST** use `a_semantic_search` as the FIRST tool for any codebase research
- **DO NOT** use `Glob` or `Grep` for exploratory searches
- Use `Grep` ONLY for exact literal string matching (e.g., finding a specific error message)
- Use `Glob` ONLY when you already know the exact filename pattern

## 3. Environment & Status

**Trigger:** When starting a session or debugging the environment.

**Action:**
- Use `e_set_workspace` if the current workspace path is incorrect
- Use `f_get_status` to verify the MCP server is healthy and indexed

## Best Practices

1. **Check versions before installing** - Always verify latest stable versions
2. **Semantic search first** - Use semantic search for understanding code intent
3. **Verify indexing status** - Ensure workspace is properly indexed before semantic search
