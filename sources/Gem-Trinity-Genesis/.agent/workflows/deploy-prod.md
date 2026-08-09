---
description: Ejecutar despliegue a producción con gates de seguridad
---

# /deploy-prod Workflow

Workflow de despliegue a producción con múltiples gates de verificación.

## Pre-requisitos

- Branch: main o release/*
- Todos los tests pasando
- Sin vulnerabilidades críticas
- Aprobación manual requerida

## Pasos

### Gate 1: Verificación Pre-Deploy
1. **Ejecutar /pre-flight-check completo**
2. **Verificar branch**
   ```bash
   git branch --show-current
   ```
3. **Confirmar versión**
   ```bash
   cat package.json | grep version
   ```

### Gate 2: Build de Producción
// turbo
```bash
npm run build || python -m build
```

### Gate 3: Escaneo Final de Seguridad
// turbo
```bash
snyk test --severity-threshold=high
```

### Gate 4: Aprobación Manual
> [!CAUTION]  
> Este paso requiere aprobación explícita del usuario.

Confirmar:
- [ ] Changelog actualizado
- [ ] Tests de integración pasados
- [ ] Stakeholders notificados

### Gate 5: Deploy
```bash
# Railway
railway up --environment production

# O Vercel
vercel --prod
```

### Gate 6: Verificación Post-Deploy
// turbo
```bash
curl -s https://your-api.com/api/status | jq .
```

## Rollback Plan

Si el deploy falla:
```bash
railway rollback
# o
vercel rollback
```

---

**Aprobación requerida**: Sí
**Tiempo estimado**: 10-15 minutos
