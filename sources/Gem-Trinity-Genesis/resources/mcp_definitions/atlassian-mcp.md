# Atlassian MCP Server Usage Rules

Remote MCP Server that connects Jira, Confluence, and Compass with your LLM and IDE.

## Features

- **Jira** - Search, create, update issues
- **Confluence** - Summarize, create, navigate pages
- **Compass** - Manage service components and dependencies
- **OAuth 2.1** - Secure authorization respecting user permissions

## Prerequisites

- Atlassian Cloud site with Jira/Confluence/Compass
- Node.js v18+ (for mcp-remote proxy)
- Modern browser for OAuth login

## Available Tools

### Jira
| Action | Example |
|--------|---------|
| Search | "Find all open bugs in Project Alpha" |
| Create | "Create a story titled 'Redesign onboarding'" |
| Bulk create | "Make five Jira issues from these notes" |
| Update | "Change status of PROJ-123 to Done" |

### Confluence
| Action | Example |
|--------|---------|
| Summarize | "Summarize the Q2 planning page" |
| Create | "Create a page titled 'Team Goals Q3'" |
| Navigate | "What spaces do I have access to?" |
| Link | "Link these tickets to the Release Plan page" |

### Compass
| Action | Example |
|--------|---------|
| Create | "Create a service component for this repository" |
| Query | "What depends on the api-gateway service?" |
| Import | "Import components from this CSV/JSON" |

## When to Use

**Trigger:** When working with Atlassian products (Jira, Confluence, Compass).

**Action:**
- Create Jira issues from code comments or meeting notes
- Search and summarize Confluence documentation
- Track service dependencies in Compass
- Link code to related Jira issues

## First-Time Setup

1. Run any Atlassian command
2. Browser opens for OAuth login
3. Authorize the connection
4. Subsequent requests use saved credentials

## Best Practices

1. **Use natural language** - Commands can be conversational
2. **Specify project keys** - Be explicit about Jira projects
3. **Check permissions** - Actions respect your Atlassian access level
4. **Combine workflows** - Link Jira issues to Confluence pages automatically
