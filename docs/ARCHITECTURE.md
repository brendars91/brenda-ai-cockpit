# Brenda AI Cockpit - Architecture

## System Overview
Brenda AI Cockpit implements a layered microservices architecture with a unified control plane. All components are built as TypeScript/JavaScript packages with Python tooling for security and validation.

## Architecture Layers

### 1. Control Plane API (`apps/control-plane-api`)
- **Purpose**: Central REST/gRPC API for agent orchestration
- **Tech Stack**: Node.js + Express/Fastify
- **Key Features**:
  - Capability registration (`/api/v1/capabilities`)
  - Agent status monitoring (`/api/v1/agents/status`)
  - Task routing and assignment
  - Quota enforcement hooks
- **Dependencies**: `@cockpit/contracts`, `@cockpit/policy`, `@cockpit/quota-governor`

### 2. Agent Runtime Console (`apps/agent-runtime-console`)
- **Purpose**: Backend service for agent lifecycle management
- **Tech Stack**: Python 3.11
- **Key Features**:
  - Agent heartbeat monitoring
  - Task queue management
  - Event logging and tracing
- **Dependencies**: `@cockpit/context-fabric`, `@cockpit/telemetry`

### 3. Cockpit UI (`apps/cockpit-ui`)
- **Purpose**: Frontend dashboard for operational visibility
- **Tech Stack**: React 18 + TypeScript + Vite
- **Key Features**:
  - Real-time agent status dashboard
  - Capability registry viewer
  - Task routing visualization
- **Dependencies**: `@cockpit/contracts` (type definitions)

### 4. Packages Layer

#### `@cockpit/contracts`
- API specification schemas (OpenAPI 3.0)
- Request/response type definitions
- Validation schemas using Zod

#### `@cockpit/policy`
- Security policy engine
- Task routing rules
- Access control policies

#### `@cockpit/context-fabric`
- Event store (SQLite backed)
- Context persistence layer
- Traceability metadata

#### `@cockpit/capability-registry`
- Agent capability indexing
- Capability matching algorithms

#### `@cockpit/quota-governor`
- Per-agent usage limits
- Rate limiting enforcement
- Quota violation alerts

#### `@cockpit/telemetry`
- Metrics collection
- Event logging
- Performance monitoring

#### `@cockpit/adapters`
- Pluggable adapters for:
  - Hermes (native integration)
  - Claude Code (Anthropic API)
  - OpenAI Codex (API integration)
  - Paperclip (local service)

### 5. Tooling Layer

#### Security Tools (`tools/`)
- `secret_scan.py`: Automated secret detection with Neptune token pattern support
- `validate_repo.py`: Source import and documentation validation

#### CI/CD (`deterministic-gates`)
- Runs verification pipeline on every commit
- Blocks merge on any failure
- Enforces code quality standards

## Data Flow

```
[Cockpit UI] ↔ [Control Plane API] ↔ [Policy Engine]
                                    ↓
                          [Quota Governor]
                                    ↓
                     [Capability Registry] ↔ [Agents]
                                    ↓
                    [Context Fabric (Event Store)]
                                    ↓
                            [Telemetry/Metrics]
```

## Deployment Architecture

### Local Development
- All services run on localhost
- SQLite file-based storage
- Vite dev server for UI
- Python tools for validation

### Production
- Docker containerized services
- PostgreSQL for context fabric (SQLite for dev)
- Shared filesystem or object storage for artifacts
- Tailscale/VPN for internal service communication

## Security Model
- Zero hardcoded credentials
- Automated secret scanning in CI
- API authentication via signed JWTs
- Role-based access control (RBAC) in policy engine

## Reliability
- Health check endpoints: `/api/health`
- Graceful degradation when agents are unreachable
- Event-driven architecture with retry logic
- Full traceability of all agent actions