---
description: Configurar hooks de CI/CD con Gate Snyk
---

# CI/CD Hooks Workflow

Configura hooks de Git con verificaciones automaticas y Gate de Snyk.

## Instalar Pre-Commit Hook
```powershell
python scripts/pre_commit_hook.py --install
```

## Verificar Manualmente
// turbo
```powershell
python scripts/pre_commit_hook.py
```

## Checks del Pre-Commit

| Check | Bloqueante | Descripcion |
|-------|------------|-------------|
| Lint | Si | Errores de sintaxis |
| Type | No | Warnings de tipos |
| Snyk | **SI** | Critical/High vulnerabilities |

## Gate de Snyk

**REGLA CRITICA**: El commit se bloquea si Snyk detecta:
- Vulnerabilidades **Critical**
- Vulnerabilidades **High**

Para ver detalles:
```powershell
snyk code test .
```

## Bypass (NO RECOMENDADO)

Solo en emergencias:
```powershell
git commit --no-verify -m "mensaje"
```

> [!WARNING]
> Usar --no-verify viola las directivas de seguridad AGCCE.

## Desinstalar Hook

```powershell
Remove-Item .git/hooks/pre-commit
```
