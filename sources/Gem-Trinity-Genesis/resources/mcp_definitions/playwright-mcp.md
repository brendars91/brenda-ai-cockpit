# Playwright MCP Usage Rules

Browser automation using Playwright's accessibility tree - no screenshots or vision models needed.

## Key Features

- **Fast & lightweight** - Uses accessibility tree, not pixels
- **LLM-friendly** - Operates on structured data
- **Deterministic** - Avoids screenshot ambiguity

## Available Tools

### Navigation
| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to URL |
| `browser_go_back` | Go back in history |
| `browser_go_forward` | Go forward in history |
| `browser_wait` | Wait for page to load |

### Interaction
| Tool | Description |
|------|-------------|
| `browser_click` | Click on element |
| `browser_type` | Type text into element |
| `browser_select_option` | Select dropdown option |
| `browser_drag` | Drag and drop |
| `browser_hover` | Hover over element |
| `browser_press_key` | Press keyboard key |

### Page State
| Tool | Description |
|------|-------------|
| `browser_snapshot` | Get accessibility snapshot |
| `browser_take_screenshot` | Capture screenshot |
| `browser_console_messages` | Get console logs |
| `browser_network_requests` | Get network activity |

### Advanced
| Tool | Description |
|------|-------------|
| `browser_evaluate` | Execute JavaScript |
| `browser_file_upload` | Upload files |
| `browser_pdf_save` | Save page as PDF |
| `browser_close` | Close browser |
| `browser_resize` | Resize viewport |

## When to Use

**Trigger:** Web automation, testing, scraping, or interactive web tasks.

**Action:**
- Use `browser_navigate` to open URLs
- Use `browser_snapshot` to understand page structure
- Use `ref` parameter from snapshot for precise element targeting
- Use `browser_click` and `browser_type` for interaction

## Element Targeting

Elements are referenced by `ref` from the accessibility snapshot:
```
1. browser_snapshot → Get page structure with refs
2. browser_click(ref="button[3]") → Click specific element
```

## Best Practices

1. **Always snapshot first** - Get page structure before interacting
2. **Use refs, not selectors** - Refs from snapshot are more reliable
3. **Wait for navigation** - Use `browser_wait` after page changes
4. **Check console** - Use `browser_console_messages` for debugging
5. **Handle forms** - Use `browser_type` then `browser_click` for submit

## Common Patterns

### Login Flow
```
1. browser_navigate(url)
2. browser_snapshot()
3. browser_type(ref="username-field", text="user")
4. browser_type(ref="password-field", text="pass")
5. browser_click(ref="login-button")
6. browser_wait()
```

### Data Extraction
```
1. browser_navigate(url)
2. browser_snapshot() → Parse structured data
3. browser_evaluate(function="...") → Extract specific data
```
