# Filesystem MCP Usage Rules

You have access to the **Filesystem MCP Server** for file system operations.

## Available Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read complete file contents |
| `read_multiple_files` | Read multiple files at once |
| `write_file` | Create or overwrite files |
| `edit_file` | Make line-based edits with diff preview |
| `create_directory` | Create directories recursively |
| `list_directory` | List directory contents |
| `directory_tree` | Get recursive tree view |
| `move_file` | Move or rename files/directories |
| `search_files` | Regex search in files |
| `get_file_info` | Get file metadata |
| `list_allowed_directories` | Show accessible directories |

## When to Use

**Trigger:** When performing bulk file operations, recursive directory operations, or file management tasks.

**Action:**
- Use `list_directory` or `directory_tree` for exploring project structure
- Use `read_multiple_files` for batch file reading
- Use `search_files` for regex-based content search across files
- Use `create_directory` when creating nested folder structures

## Best Practices

1. **Always verify paths** before write operations
2. **Use `list_allowed_directories`** if unsure about access
3. **Prefer `edit_file`** over `write_file` for modifications to preserve history
4. **Use relative paths** when possible within allowed directories
