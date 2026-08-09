---
description: Ejecutar comandos Docker sin MCP (alternativa a docker MCP)
---

# Docker Executor Workflow

Este workflow reemplaza el MCP de Docker que no funciona correctamente.

## Prerequisitos
- Docker Desktop instalado y corriendo
- Acceso a terminal PowerShell

## Comandos Disponibles

### 1. Levantar servicios
// turbo
```powershell
docker compose up -d
```

### 2. Ver logs
// turbo
```powershell
docker compose logs --tail=100
```

### 3. Ejecutar tests en contenedor
```powershell
docker compose exec app pytest
```

### 4. Detener servicios
// turbo
```powershell
docker compose down
```

### 5. Ver estado de contenedores
// turbo
```powershell
docker ps -a
```

## Mapeo de Acciones AGCCE

| Acción AGCCE | Comando Docker | Step ID Pattern |
|--------------|----------------|-----------------|
| compose_up | `docker compose up -d` | S*_DOCKER_UP |
| run_tests | `docker compose exec app pytest` | S*_DOCKER_TEST |
| fetch_logs | `docker compose logs --tail=100` | S*_DOCKER_LOGS |

## Notas
- Antes de ejecutar, verificar que el step_id esté mapeado en el Plan JSON
- Los comandos marcados con `// turbo` se auto-ejecutan
