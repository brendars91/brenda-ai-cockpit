# Open Policy Agent (OPA) MCP Usage Rules

MCP Server for Open Policy Agent REST API - policy-based control for cloud-native environments.

## What is OPA?

**Open Policy Agent (OPA)** is an open-source policy engine that enables unified policy enforcement across the stack:
- **Authorization** - API access control, RBAC, ABAC
- **Admission Control** - Kubernetes pod policies
- **Configuration** - Terraform, Docker, CI/CD pipelines
- **Data Filtering** - Row-level security, field masking

## Prerequisites

1. **Python 3.9+**
2. **pip** or **uv**
3. Install dependencies:
```bash
cd ~/.gemini/open-policy-agent-opa-rest-api
pip install -e ".[dev]"
```

## Available Tools

| Tool | Description |
|------|-------------|
| `evaluate_policy` | Evaluate a policy against input data |
| `create_policy` | Create or update a policy |
| `get_policy` | Retrieve a policy by ID |
| `delete_policy` | Remove a policy |
| `query_data` | Query the OPA data store |

## When to Use

**Trigger:** Policy-as-code implementation, access control, or compliance enforcement.

**Action:**
- Define authorization policies in Rego language
- Evaluate requests against policies
- Implement RBAC/ABAC for applications
- Enforce compliance rules

## Rego Policy Language

OPA uses **Rego** - a declarative policy language:
```rego
package authz

default allow = false

allow {
    input.method == "GET"
    input.user.role == "admin"
}
```

## Common Use Cases

| Use Case | Example |
|----------|---------|
| API Authorization | Check if user can access endpoint |
| K8s Admission | Validate pod security policies |
| Data Filtering | Row-level access control |
| CI/CD Gates | Enforce deployment policies |

## Integration Pattern

```
1. Define policy in Rego
2. Load policy via create_policy
3. Send request + context to evaluate_policy
4. Receive allow/deny decision with reasons
```

## Best Practices

1. **Version control policies** - Store Rego files in Git
2. **Test policies** - Write unit tests for policies
3. **Use bundles** - Organize policies into bundles
4. **Audit decisions** - Log all policy decisions
5. **Combine with security MCPs** - Use with Trivy/Snyk for comprehensive security
