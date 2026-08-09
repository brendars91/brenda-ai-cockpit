# Semgrep MCP Usage Rules

Scans AI-generated code for security vulnerabilities using Semgrep Code, Supply Chain, and Secrets.

## Features

Semgrep MCP runs three security products:
- **Semgrep Code** - Static analysis for security vulnerabilities
- **Semgrep Supply Chain** - Dependency vulnerability scanning
- **Semgrep Secrets** - Hardcoded secrets detection

## Prerequisites

- Python 3.10 or later
- Semgrep installed (`pip install semgrep` or `brew install semgrep`)
- Semgrep account (optional, for advanced features)

## Available Tools

| Tool | Description |
|------|-------------|
| `scan` | Scan code for security vulnerabilities |

## When to Use

**Trigger:** After generating or modifying code, especially in security-sensitive areas.

**Action:**
- Scan generated code before committing
- Re-generate code if vulnerabilities found
- Use with Snyk for comprehensive security analysis

## Workflow

```
1. Generate code with LLM
2. Semgrep MCP scans for vulnerabilities
3. If findings → LLM re-generates secure code
4. Repeat until no vulnerabilities
```

## Comparison with Snyk

| Feature | Semgrep | Snyk |
|---------|---------|------|
| SAST | ✅ Code | ✅ snyk_code_scan |
| SCA | ✅ Supply Chain | ✅ snyk_sca_scan |
| Secrets | ✅ Secrets | ❌ |
| Container | ❌ | ✅ snyk_container_scan |
| IaC | ❌ | ✅ snyk_iac_scan |

**Recommendation:** Use both for comprehensive coverage.

## Best Practices

1. **Scan early** - Check code before complex refactoring
2. **Review findings** - Understand why code is flagged
3. **Don't ignore** - Security issues should be fixed, not suppressed
4. **Combine tools** - Use with Snyk for full security coverage

## Supported Languages

Go, Java, JavaScript, TypeScript, Python, Ruby, PHP, C, C++, Rust, Kotlin, Swift, Scala, and more.
