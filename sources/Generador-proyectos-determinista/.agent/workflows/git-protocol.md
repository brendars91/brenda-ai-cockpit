---
description: # Pre-Flight Check Workflow  Validaciones obligatorias antes de proponer cualquier caso
---

# Git Protocol Workflow

Protocolo para gestión de control de versiones usando comandos git locales.

## Pre-Requisito: Antes de Emitir Plan JSON

// turbo
```powershell
git status
```

### Interpretación de Resultados:

| Estado | Acción |
|--------|--------|
| `nothing to commit, working tree clean` | ✅ Continuar |
| `Changes not staged for commit` | ⚠️ Notificar usuario |
| `Untracked files` | ⚠️ Evaluar si interfieren |

### Si hay cambios pendientes:
1. Notificar al usuario con lista de archivos
2. Proponer: stash, commit, o descartar
3. Esperar confirmación antes de continuar

---

## Post-Requisito: Al Completar Tarea Exitosa

### 1. Ver cambios realizados
// turbo
```powershell
git diff --stat
```

### 2. Preparar archivos
```powershell
git add <archivos_modificados>
```

### 3. Crear commit
```powershell
git commit -m "<tipo>(<scope>): <descripción>"
```

---

## Conventional Commits

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `refactor` | Código sin cambio funcional |
| `test` | Añadir/modificar tests |
| `chore` | Mantenimiento, deps |
| `style` | Formato, sin cambio de código |
| `perf` | Mejoras de rendimiento |

### Ejemplos:
```
feat(auth): add JWT token validation
fix(api): resolve null pointer in user service
docs(readme): update installation instructions
refactor(core): extract validation logic to separate module
```

---

## Comandos Útiles

### Ver historial reciente
// turbo
```powershell
git log -n 5 --oneline
```

### Ver branches
// turbo
```powershell
git branch -a
```

### Crear branch de feature
```powershell
git checkout -b feature/<nombre>
```

### Sincronizar con remoto
```powershell
git pull origin main
git push origin <branch>
```