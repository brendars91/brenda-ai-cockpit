# Snyk MCP Usage Rules

You have access to the **Snyk MCP Server** for security analysis.

## Available Tools

### Code Security (SAST)
| Tool | Description |
|------|-------------|
| `snyk_code_scan` | Static Application Security Testing |
| `snyk_sca_scan` | Open-source dependency vulnerability scan |
| `snyk_container_scan` | Container image vulnerability scan |
| `snyk_iac_scan` | Infrastructure as Code security scan |
| `snyk_sbom_scan` | SBOM vulnerability analysis |

### Utility
| Tool | Description |
|------|-------------|
| `snyk_auth` | Authenticate with Snyk |
| `snyk_logout` | Clear authentication |
| `snyk_version` | Check Snyk CLI version |
| `snyk_trust` | Trust a folder for scanning |
| `snyk_send_feedback` | Report fixed/prevented issues |

## When to Use

**Trigger:** After generating or modifying code, especially in security-sensitive areas.

**MANDATORY Actions:**
- **ALWAYS** run `snyk_code_scan` for new first-party code
- **ALWAYS** run `snyk_sca_scan` when adding dependencies
- **FIX** any security issues found using Snyk context
- **RESCAN** after fixes until no new issues found

## Scan Selection Guide

| Scenario | Tool to Use |
|----------|-------------|
| New/modified source code | `snyk_code_scan` |
| Adding npm/pip/maven packages | `snyk_sca_scan` |
| Dockerfile changes | `snyk_container_scan` |
| Terraform/K8s/CloudFormation | `snyk_iac_scan` |
| Third-party SBOM analysis | `snyk_sbom_scan` |

## Best Practices

1. **Use absolute paths** - All path arguments must be absolute
2. **Set severity threshold** - Use `severity_threshold: "high"` to focus on critical issues
3. **Include ignores** - Use `include_ignores: true` to see all issues
4. **For Python** - Always specify `command: "python"` or `command: "python3"`
5. **Trust folders** - Run `snyk_trust` only when instructed

## Supported Languages

Apex, C/C++, Dart, Elixir, Go, Groovy, Java, Kotlin, JavaScript, .NET, PHP, Python, Ruby, Rust, Scala, Swift, Objective-C, TypeScript, VB.NET
