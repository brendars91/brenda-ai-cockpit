# Coding Standards Rules

## Code Style

### Python
- Follow PEP 8
- Use type hints for function signatures
- Max line length: 100 characters
- Docstrings for public functions (Google style)

### JavaScript/TypeScript
- Use ESLint with recommended config
- Prefer `const` over `let`
- Use TypeScript strict mode
- Async/await over raw promises

### General
- Meaningful variable names (no single letters except loops)
- Functions should do one thing
- Max function length: 50 lines
- Max cyclomatic complexity: 10

## Architecture Patterns

### Separation of Concerns
- Business logic separate from I/O
- Data access in dedicated layers
- Configuration externalized

### Error Handling
- Always catch and handle errors appropriately
- Log errors with context
- Never swallow exceptions silently
- Use custom error types for domain errors

### Documentation
- README.md in every module
- Inline comments for non-obvious logic
- API documentation for public interfaces

## Testing Requirements

- Unit tests for business logic
- Integration tests for API endpoints
- Minimum coverage: 70%
- All tests must pass before merge

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
