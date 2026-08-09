---
description: Verificación previa antes de proponer cambios de código
---

# /pre-flight-check Workflow

Este workflow ejecuta verificaciones previas antes de cualquier cambio de código.

## Pasos

1. **Verificar estado del repositorio**
   ```bash
   git status
   git diff --stat
   ```

2. **Ejecutar linters**
   // turbo
   ```bash
   npm run lint || python -m flake8 . --count
   ```

3. **Ejecutar tests existentes**
   // turbo
   ```bash
   npm test || pytest --tb=short
   ```

4. **Verificar dependencias**
   // turbo
   ```bash
   npm audit --audit-level=high || pip-audit
   ```

5. **Escaneo de seguridad**
   // turbo
   ```bash
   snyk test || echo "Snyk no configurado"
   ```

6. **Generar reporte**
   - Estado: ✅ PASS | ⚠️ WARNINGS | ❌ FAIL
   - Issues encontrados
   - Recomendaciones

## Criterios de Bloqueo

- ❌ Tests fallando
- ❌ Vulnerabilidades críticas en dependencias
- ❌ Secretos detectados en código

## Output

```
Pre-Flight Check Results:
├── Git Status: Clean ✅
├── Linting: 0 errors ✅
├── Tests: 42 passed ✅
├── Dependencies: 0 critical vulns ✅
└── Security: No secrets detected ✅

Status: READY TO PROCEED ✅
```

// turbo-all
