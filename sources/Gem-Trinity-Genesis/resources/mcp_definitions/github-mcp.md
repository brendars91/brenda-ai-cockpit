# GitHub MCP Usage Rules

You have access to the **GitHub MCP Server** for repository and project management.

## Available Tools

### Repository Management
| Tool | Description |
|------|-------------|
| `create_repository` | Create new GitHub repository |
| `fork_repository` | Fork a repository |
| `create_branch` | Create new branch |
| `list_branches` | List repository branches |
| `list_commits` | Get commit history |
| `get_commit` | Get commit details with diff |

### Pull Requests
| Tool | Description |
|------|-------------|
| `create_pull_request` | Create new PR |
| `list_pull_requests` | List PRs in repository |
| `pull_request_read` | Get PR details, diff, status, files, comments |
| `update_pull_request` | Update PR title, body, reviewers |
| `merge_pull_request` | Merge a PR |
| `request_copilot_review` | Request Copilot code review |

### Issues
| Tool | Description |
|------|-------------|
| `issue_write` | Create or update issues |
| `issue_read` | Get issue details, comments, labels |
| `list_issues` | List repository issues |
| `search_issues` | Search issues across repos |
| `add_issue_comment` | Add comment to issue |

### Files & Content
| Tool | Description |
|------|-------------|
| `get_file_contents` | Read file from repository |
| `create_or_update_file` | Push single file changes |
| `push_files` | Push multiple files in one commit |
| `delete_file` | Delete file from repository |

### Search
| Tool | Description |
|------|-------------|
| `search_code` | Search code across GitHub |
| `search_repositories` | Find repositories |
| `search_users` | Find GitHub users |

## When to Use

**Trigger:** When managing GitHub repositories, PRs, issues, or searching code.

**Action:**
- Use `search_code` for finding code patterns across repositories
- Use `pull_request_read` with `method: "get_diff"` for reviewing changes
- Use `push_files` for multi-file commits
- Use `create_pull_request` after pushing changes to a branch

## Best Practices

1. **Always specify owner and repo** for repository operations
2. **Use search tools** before creating duplicate issues
3. **Include meaningful commit messages** in file operations
4. **Request Copilot review** for automated feedback before human review
