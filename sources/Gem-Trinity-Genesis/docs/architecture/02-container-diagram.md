# Gem Trinity Genesis - Container Diagram

## Container Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Usuario Personal                            │
│                       (Browser + Terminal)                          │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Frontend    │   │    SSH/Term   │   │   GitHub UI   │
│     Web       │   │               │   │               │
│   (Next.js)   │   │    bash       │   │               │
│               │   │               │   │               │
│  - React UI   │   │  - make       │   │  - View Code  │
│  - Pages      │   │  - pytest     │   │  - CI Status  │
│  - Components │   │  - git        │   │  - Issues     │
│               │   │  - docker     │   │               │
│  Port: 3000   │   │  Port: 22     │   │               │
│  (Vercel)     │   │  (OCI/Railway)│   │               │
└───────┬───────┘   └───────┬───────┘   └───────────────┘
        │                   │
        │ HTTPS/WS          │
        ▼                   │
┌───────────────┐           │
│  Single Page  │           │
│   Application │           │
└───────┬───────┘           │
        │                   │
        │ HTTPS API Calls   │
        ▼                   │
┌─────────────────────────────────────────────────────────────────┐
│                     Backend API Container                        │
│                        (FastAPI)                                 │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │  API Server │  │  Routers    │  │   Services Layer        ││
│  │             │  │             │  │                         ││
│  │  - Uvicorn  │  │  - /architect│  │  - Architect Service    ││
│  │  - CORS     │  │  - /builder  │  │  - Builder Service      ││
│  │  - Auth     │  │  - /engine   │  │  - Engine Service       ││
│  │  - WebSocket│  │  - /admin    │  │  - Cache + Circuit      ││
│  │             │  │  - /health   │  │    Breaker              ││
│  └─────────────┘  └─────────────┘  └─────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Infrastructure Layer                      ││
│  │                                                             ││
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐ ││
│  │  │  SQLite    │  │  File      │  │    Metrics/Logs      │ ││
│  │  │  Database  │  │  System    │  │                      │ ││
│  │  │            │  │  Storage   │  │  - Prometheus format │ ││
│  │  │  - agents  │  │            │  │  - Structured logs   │ ││
│  │  │  - payloads│  │  - logs/   │  │  - Error tracking   │ ││
│  │  │  - metrics │  │  - artifacts│  │                      │ ││
│  │  └────────────┘  └────────────┘  └──────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  Port: 8000  (Railway/OCI)                                       │
└───────────────────────────┬───────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  n8n          │   │  Health Check │   │  CI/CD        │
│  Container    │   │  Script       │   │  Pipelines    │
│               │   │               │   │               │
│  - Workflows  │   │  - Cron       │   │  - GitHub     │
│  - Integrations│   │  - Alerts     │   │    Actions    │
│  - Slack      │   │  - Logs       │   │  - Vercel     │
│  - Email      │   │               │   │  - Railway     │
│               │   │               │   │               │
│  Port: 5678   │   │  bash script  │   │  yaml config  │
│  (Docker)     │   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
        │
        └─────────────────────────────────────┐
                                              │
                    ┌─────────────────────────┼─────────────────────┐
                    │                         │                     │
                    ▼                         ▼                     ▼
        ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
        │  Google AI        │   │   Anthropic       │   │   File System     │
        │   Gemini API      │   │   Claude API      │   │                   │
        │                   │   │                   │   │  - logs/           │
        │  - gemini-pro     │   │  - claude-3       │   │  - artifacts/      │
        │  - gemini-2.0-flash│   │  - sonnet         │   │  - backups/        │
        │                   │   │                   │   │                   │
        │  REST API         │   │  REST API         │   │  Local Storage    │
        └───────────────────┘   └───────────────────┘   └───────────────────┘
```

## Contenedores Desglosados

### 1. Frontend Web Container
**Tecnología:** Next.js 14 + React + TypeScript

**Responsabilidades:**
- Renderizar UI para el usuario
- Manejar estado de la aplicación (hooks)
- Comunicarse con el Backend API
- Desplegar en Vercel con build optimizado

**Interfaces expuestas:**
- HTTP (443): Páginas web estáticas
- WebSocket (WS): Actualizaciones en tiempo real

**Datos almacenados:**
- Ninguno (stateless)

### 2. Backend API Container
**Tecnología:** FastAPI + Python 3.12

**Responsabilidades:**
- API RESTful para orquestación de agentes
- Servicios de negocio (Architect, Builder, Engine)
- Manejo de errores y circuit breaker
- Cache semántico y métricas

**Interfaces expuestas:**
- HTTP (8000): API REST
- WebSocket: Comunicación en tiempo real

**Datos almacenados:**
- SQLite: agentes, payloads, métricas
- File System: logs, artifacts, backups

### 3. n8n Container
**Tecnología:** n8n (Node.js)

**Responsabilidades:**
- Automatización de workflows personalizados
- Health checks y alertas
- Integraciones con servicios externos

**Interfaces expuestas:**
- HTTP (5678): UI de n8n

### 4. Health Check Script
**Tecnología:** Bash script

**Responsabilidades:**
- Verificar salud del backend cada 5 min
- Enviar alertas por email/Slack si falla
- Registrar logs de monitoreo

### 5. External Services Containers
**Google AI Gemini:**
- Propósito: Generación de código y respuestas
- Acceso: REST API
- Costo: Por token

**Anthropic Claude:**
- Propósito: Generación alternativa de alta calidad
- Acceso: REST API
- Costo: Por token (mayor que Gemini)

## Comunicación Entre Contenedores

### Frontend → Backend
```
Protocolo: HTTPS
Formato: JSON
Autenticación: Ninguna (uso personal)
Rate limiting: 600 req/min
```

### Backend → LLM APIs
```
Protocolo: HTTPS
Formato: JSON
Autenticación: API Keys
Resiliencia: Circuit breaker + Cache
```

### Backend → File System
```
Operaciones: Read/Write
Formato: JSON logs, SQLite DB
Backups: Diarios + Semanales
```

## Orquestación

**Despliegue:**
```yaml
Servicios: Docker Compose
Contenedores: 3 (backend, n8n, cloudflared)
Redes: bridge
Volumes: 3 (data, logs, n8n)
```

**Escalabilidad:**
- Frontend: Auto-scaling (Vercel)
- Backend: Manual (Railway/OCI)
- n8n: Single instance (personal use)

**Resiliencia:**
- Restart policies: always
- Health checks: /api/health
- Backups: Automatizados

## Tecnologías por Contenedor

| Contenedor | Tecnologías Principales |
|------------|------------------------|
| Frontend | Next.js, React, TypeScript, Tailwind, Framer Motion |
| Backend | FastAPI, Pydantic, Uvicorn, SQLite, pytest |
| n8n | Node.js, Express, WebSockets |
| Health Check | Bash, curl, mail |
