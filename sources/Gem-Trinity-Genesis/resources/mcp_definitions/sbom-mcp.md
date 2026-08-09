# SBOM MCP Server Usage Rules

Generates Software Bill of Materials (SBOM) in CycloneDX format using Trivy.

## What is SBOM?

A **Software Bill of Materials (SBOM)** is a complete inventory of all software components, libraries, and dependencies in a project. Essential for:
- **Supply chain security**
- **Vulnerability tracking**
- **License compliance**
- **Regulatory requirements** (e.g., Executive Order 14028)

## Prerequisites

1. **uv** - Python package manager: https://github.com/astral-sh/uv
2. **Trivy** - Security scanner: https://github.com/aquasecurity/trivy
3. **Node.js** - JavaScript runtime

## Available Tools

| Tool | Description |
|------|-------------|
| `generate_sbom` | Scan project and produce SBOM in CycloneDX format |

## When to Use

**Trigger:** When you need a complete inventory of software components.

**Action:**
- Generate SBOM for compliance requirements
- Track dependencies for vulnerability management
- Document software components for audits
- Analyze third-party libraries

## SBOM Output Format

Output is in **CycloneDX** format - an industry-standard SBOM format that includes:
- Component names and versions
- License information
- Dependency relationships
- Vulnerability references

## Example Usage

```
Generate an SBOM for this project
```

```
Create a software bill of materials for the current directory
```

## Relationship with Other MCPs

| Task | Recommended MCP |
|------|-----------------|
| Generate SBOM | **SBOM MCP** |
| Analyze SBOM vulnerabilities | Snyk, Trivy |
| Container scanning | Trivy |
| Code security | Semgrep, Snyk |

## Best Practices

1. **Generate regularly** - Include SBOM generation in CI/CD pipeline
2. **Version control** - Store SBOMs with releases
3. **Combine with scanning** - Use Trivy/Snyk to analyze SBOM for vulnerabilities
4. **Compliance tracking** - Maintain SBOMs for regulatory compliance
