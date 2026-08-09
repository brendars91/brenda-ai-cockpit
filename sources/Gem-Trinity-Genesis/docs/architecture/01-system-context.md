# Gem Trinity Genesis - System Context

## System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Usuario Personal                         │
│                   (Brenda - Developer/Owner)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS/SSH
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Gem Trinity Genesis System                   │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐  │
│  │   Frontend Web   │  │   Backend API    │  │  n8n        │  │
│  │   (Next.js)      │◄─►   (FastAPI)      │  │  Workflow   │  │
│  │                  │  │                  │  │  Automation │  │
│  │  Vercel Hosting  │  │  Railway/OCI     │  │             │  │
│  └──────────────────┘  └────────┬─────────┘  └─────────────┘  │
│                                │                                 │
│                                │                                 │
│                         ┌──────▼───────┐                        │
│                         │   Database    │                        │
│                         │   (SQLite)    │                        │
│                         │   Local File  │                        │
│                         └──────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │  Google AI   │  │   Anthropic   │  │   GitHub         │     │
│  │   Gemini     │  │    Claude     │  │   Repository     │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Descripción de Componentes

### Usuario Personal
- **Rol:** Owner, developer, único usuario
- **Acceso:** Panel web, SSH al servidor
- **Propósito:** Orquestar agentes IA, automatizar tareas

### Gem Trinity Genesis System
Sistema autónomo de orquestación de agentes IA para uso personal.

#### Componentes Principales:

**Frontend Web (Next.js)**
- Hosted en: Vercel
- Framework: Next.js 14 + TypeScript
- Propósito: Interfaz de usuario para generar y gestionar agentes
- Acceso: https://app-eta-fawn-42.vercel.app

**Backend API (FastAPI)**
- Hosted en: Railway u Oracle Cloud Infrastructure
- Framework: FastAPI (Python 3.12)
- Propósito: API RESTful para orquestación de agentes
- Características:
  - Circuit breaker para resiliencia LLM
  - Semantic cache para optimización
  - Error tracking y métricas
  - Health checks y monitoreo

**n8n Workflow Automation**
- Propósito: Automatización de tareas personalizadas
- Integraciones: Slack, email, GitHub
- Workflows: Health checks, alertas, mantenimiento

**Database (SQLite)**
- Almacenamiento: Archivo local con backups automáticos
- Propósito: Persistencia de estado, logs, métricas

### External Services

**Google AI Gemini**
- Propósito: Modelo LLM primario para generación de código
- Costo: Bajo costo por token
- Uso: Architect (planificación), Builder (compilación)

**Anthropic Claude**
- Propósito: Modelo LLM alternativo
- Costo: Mayor calidad, mayor costo
- Uso: Tareas complejas que requieren razonamiento superior

**GitHub Repository**
- Propósito: Control de versiones, CI/CD
- Repositorio: github.com/brendars91/Gem-Trinity-Genesis
- CI/CD: GitHub Actions para tests y despliegue

## Data Flows Principales

### 1. Generación de Agente
```
Usuario → Frontend → Backend API → Gemini → Backend → Frontend
                                      ↓
                                  SQLite (persistir)
```

### 2. Health Check
```
Cron Job → Backend API (/api/health) → n8n → Slack/Email (si falla)
```

### 3. CI/CD Pipeline
```
GitHub Push → GitHub Actions (tests) → Vercel (deploy frontend)
                                       ↓
                                  Railway (deploy backend)
```

## Tecnologías Principales

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Frontend | Next.js 14, React, TypeScript | UI web |
| Backend | FastAPI, Python 3.12 | API REST |
| Database | SQLite | Persistencia local |
| Hosting | Vercel (frontend), Railway/OCI (backend) | Infraestructura |
| Automation | n8n | Workflows personalizados |
| CI/CD | GitHub Actions | Tests y deploy |
| Monitoring | Custom health checks, logs | Observabilidad |

## Costo Mensual Estimado

| Servicio | Costo |
|----------|-------|
| Vercel (Hobby) | $0 |
| Railway (Hobby) | $0 |
| OCI Free Tier | $0 |
| GitHub (Free) | $0 |
| **Total** | **$0/mes** |

## Próximos Niveles de Detalle

- [Container Diagram](02-container-diagram.md) - Detalle de contenedores y aplicaciones
- [Component Diagram](03-component-diagram.md) - Detalle de componentes de código
- [Code Diagram](04-code-diagram.md) - Detalle de estructura de código
