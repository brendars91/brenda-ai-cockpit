# Trivy MCP Usage Rules

Security scanning for filesystems, container images, and remote repositories via Model Context Protocol.

## Features

- **Natural Language Scanning** - Ask security questions in plain language
- **Multiple Scan Types:**
  - Filesystem scanning for local projects
  - Container image vulnerability scanning
  - Remote repository security analysis
- **Aqua Platform Integration** - Optional enhanced scanning with assurance policies
- **Flexible Transport** - Supports stdio, HTTP, and SSE

## Prerequisites

1. Install Trivy: https://trivy.dev/docs/getting-started/installation/
2. Install MCP plugin:
```bash
trivy plugin install mcp
```

## Available Tools

| Tool | Description |
|------|-------------|
| `scan_filesystem` | Scan local project files |
| `scan_image` | Scan container images |
| `scan_repository` | Scan remote git repos |

## When to Use

**Trigger:** Security scanning for containers, IaC, or comprehensive vulnerability analysis.

**Action:**
- Use for **container images** before deployment
- Use for **Kubernetes/IaC** configurations
- Use for **remote repository** security audits
- Ask natural language questions about security

## Example Queries

```
Are there any vulnerabilities or misconfigurations in this project?
```

```
Scan the nginx:latest image for vulnerabilities
```

```
Check this Dockerfile for security issues
```

## Comparison with Other Security MCPs

| Feature | Trivy | Snyk | Semgrep |
|---------|-------|------|---------|
| Container Images | ✅ | ✅ | ❌ |
| Filesystem | ✅ | ✅ | ✅ |
| IaC (K8s, Terraform) | ✅ | ✅ | ❌ |
| SBOM | ✅ | ✅ | ❌ |
| Secrets | ✅ | ❌ | ✅ |
| SAST | ❌ | ✅ | ✅ |

**Recommendation:** Use Trivy for container/IaC security, Semgrep/Snyk for code analysis.

## Best Practices

1. **Scan images before push** - Check container images before registry push
2. **Include IaC** - Scan Kubernetes manifests and Terraform files
3. **Check dependencies** - Use for SBOM generation and analysis
4. **Combine with CI/CD** - Integrate security scans in pipeline
