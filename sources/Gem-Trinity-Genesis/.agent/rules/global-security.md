# Global Security Rules (Priority 9999)

## Mandatory Security Checks

### 1. Secret Detection
- **NEVER** commit API keys, tokens, or passwords to code
- Scan all code changes for patterns: `API_KEY`, `SECRET`, `PASSWORD`, `TOKEN`, `BEGIN PRIVATE KEY`, `AKIA[0-9A-Z]{16}`
- Use environment variables for all secrets

### 2. Input Validation
- Validate ALL user inputs before processing
- Sanitize data to prevent injection attacks (SQL, XSS, Command)
- Use parameterized queries for database operations

### 3. Dependency Security
- Run `npm audit` / `pip-audit` before deployment
- No dependencies with known critical vulnerabilities
- Lock dependency versions in production

### 4. Code Review Gates
- All code must pass linting before commit
- Security-sensitive changes require HITL (Human-in-the-Loop) approval
- Production deployments require manual approval

### 5. File System Security
- Never write outside designated directories
- Validate file paths to prevent path traversal
- Restrict file permissions appropriately

### 6. API Security
- Implement rate limiting on all endpoints
- Validate authentication tokens on every request
- Log security-relevant events

---

## Enforcement

These rules are enforced automatically:
- Pre-commit hooks validate secret patterns
- CI/CD pipeline runs security scans
- Snyk integration blocks vulnerable dependencies

**Priority: 9999** - These rules override all other configuration.
