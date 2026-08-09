---
name: code-fixer
description: Metodología sistemática para identificar, diagnosticar y corregir errores en código. Integra debugging paso a paso, análisis con Snyk/Semgrep, y patrones de fix por tipo de error. Usar cuando hay bugs, errores de runtime, o código que no funciona como esperado.
---

# Code Fixer Skill

> **Propósito**: Transformar código roto en código funcional de manera sistemática y reproducible.

---

## 🎯 Cuándo Usar Esta Skill

| Situación | Acción |
|-----------|--------|
| Error de runtime (Exception, crash) | Usar flujo de **Diagnóstico Rápido** |
| Tests fallando | Usar flujo de **Análisis de Tests** |
| Comportamiento inesperado | Usar flujo de **Debugging Lógico** |
| Vulnerabilidad detectada | Usar flujo de **Security Fix** |
| Error de sintaxis/tipos | Usar flujo de **Static Analysis** |

---

## 🔴 Flujo Principal: Red-to-Green

```
ERROR DETECTADO → DIAGNÓSTICO → HIPÓTESIS → FIX → VERIFICACIÓN → DOCUMENTACIÓN
```

### Paso 1: Capturar el Error

```markdown
## Error Report
- **Tipo**: [Runtime | Test | Logic | Security | Syntax]
- **Mensaje**: [Copiar mensaje exacto]
- **Ubicación**: [archivo:línea]
- **Reproducible**: [Sí/No + pasos]
- **Contexto**: [Qué se estaba haciendo]
```

### Paso 2: Diagnóstico Sistemático

#### 2.1 Para Errores de Runtime

```bash
# Ver traceback completo
python -m traceback script.py

# Ejecutar con verbose
python -v script.py 2>&1 | tail -50
```

**Checklist de Diagnóstico:**
- [ ] ¿El error es en MI código o en una dependencia?
- [ ] ¿El error ocurre siempre o intermitente?
- [ ] ¿Cuál es el estado de las variables al momento del error?
- [ ] ¿Hay recursos externos involucrados (file, network, DB)?

#### 2.2 Para Tests Fallando

```bash
# Ejecutar test específico con máximo detalle
pytest path/to/test.py::test_function -vvs --tb=long

# Ver qué assertion falló
pytest --tb=short -q
```

**Checklist:**
- [ ] ¿El test está bien escrito o el bug está en el test?
- [ ] ¿Qué valor esperado vs valor obtenido?
- [ ] ¿Hay side effects entre tests (fixtures mal aisladas)?

#### 2.3 Para Problemas Lógicos

```python
# Añadir logging temporal estratégico
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# En puntos críticos:
logger.debug(f"Estado: {variable=}, {otra_variable=}")
```

### Paso 3: Formular Hipótesis

Antes de tocar código, escribir:

```markdown
## Hipótesis de Causa Raíz
1. [Hipótesis más probable] - Probabilidad: X%
2. [Segunda hipótesis] - Probabilidad: Y%
3. [Tercera hipótesis] - Probabilidad: Z%

## Plan de Verificación
- Para H1: [Qué probar]
- Para H2: [Qué probar]
```

### Paso 4: Aplicar Fix

#### Reglas de Oro para Fixes

1. **Un fix = Un problema** - No arreglar múltiples cosas a la vez
2. **Mínima invasión** - Cambiar lo menos posible
3. **Mantener compatibilidad** - No romper lo que funcionaba
4. **Documentar el cambio** - Comentario explicando el "por qué"

#### Patrones de Fix Comunes

| Error | Patrón de Fix |
|-------|---------------|
| `NoneType has no attribute X` | Añadir guard clause: `if obj is not None:` |
| `KeyError` | Usar `.get(key, default)` o verificar existencia |
| `IndexError` | Verificar bounds antes de acceder |
| `TypeError: expected X got Y` | Validar tipos en entrada o convertir |
| `FileNotFoundError` | Verificar existencia con `Path.exists()` |
| `ImportError` | Verificar instalación, rutas, __init__.py |
| Race condition | Usar locks o hacer operación atómica |
| Memory leak | Verificar referencias, usar context managers |

### Paso 5: Verificar Fix

```bash
# 1. El test específico pasa
pytest path/to/test.py -v

# 2. No se rompió nada más
pytest tests/ -v

# 3. Análisis de seguridad
# (Si tienes Snyk MCP disponible, usarlo aquí)
```

### Paso 6: Documentar

```markdown
## Fix Applied
- **Causa raíz**: [Qué causaba el error]
- **Solución**: [Qué se cambió]
- **Archivos modificados**: [Lista]
- **Tests añadidos/modificados**: [Lista]
- **Riesgo de regresión**: [Bajo/Medio/Alto]
```

---

## 🔒 Flujo de Security Fix

Cuando el error es una vulnerabilidad de seguridad:

### Usando Snyk MCP

```
1. Ejecutar snyk_code_scan en el archivo afectado
2. Revisar findings con severity high/critical
3. Para cada finding:
   a. Entender el vector de ataque
   b. Buscar fix recomendado por Snyk
   c. Aplicar fix
   d. Re-escanear para verificar
```

### Patrones de Security Fix

| Vulnerabilidad | Fix Pattern |
|----------------|-------------|
| SQL Injection | Usar queries parametrizadas, NUNCA concatenar |
| XSS | Escapar output, usar CSP headers |
| Path Traversal | Validar y normalizar paths, usar allowlist |
| Command Injection | Evitar shell=True, usar listas de args |
| Hardcoded Secrets | Mover a env vars, usar secret manager |
| SSRF | Validar URLs, usar allowlist de dominios |
| IDOR | Verificar ownership en cada request |

---

## 🔧 Herramientas de Diagnóstico

### Python

```bash
# Type checking
mypy script.py --strict

# Linting
ruff check script.py
# o
pylint script.py

# Formateo (detecta syntax errors)
black --check script.py
```

### JavaScript/TypeScript

```bash
# Type checking
tsc --noEmit

# Linting
eslint src/

# Tests
npm test -- --verbose
```

### General

```bash
# Buscar el error en el codebase
grep -rn "ErrorMessage" .

# Ver cambios recientes (el bug suele estar ahí)
git log --oneline -10
git diff HEAD~3
```

---

## 📋 Checklist Pre-Fix

Antes de modificar código:

- [ ] Entiendo completamente el error
- [ ] Puedo reproducir el error
- [ ] Tengo una hipótesis clara de la causa
- [ ] Sé cómo verificar que el fix funciona
- [ ] El fix no introduce nuevos problemas
- [ ] Hay tests que cubren el caso

---

## 📋 Checklist Post-Fix

Después de aplicar el fix:

- [ ] El error original ya no ocurre
- [ ] Todos los tests pasan
- [ ] No hay nuevos warnings/errors
- [ ] El código sigue las convenciones del proyecto
- [ ] La documentación está actualizada si aplica
- [ ] El cambio está listo para commit

---

## 🚨 Errores Comunes al Fixear

| Anti-pattern | Por qué es malo | Mejor práctica |
|--------------|-----------------|----------------|
| Silenciar exception con `except: pass` | Oculta el problema | Log el error, manejar específicamente |
| Fix sin test | El bug volverá | Añadir test que reproduzca el bug |
| Cambiar múltiples cosas | No sabrás qué funcionó | Un cambio a la vez |
| Copiar fix de StackOverflow sin entender | Puede introducir bugs nuevos | Entender primero, adaptar después |
| Asumir la causa sin verificar | Perder tiempo en fix equivocado | Siempre verificar hipótesis |

---

## 📚 Referencias

- [Python Debugging Guide](https://docs.python.org/3/library/pdb.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Snyk Learn - Security Fixes](https://learn.snyk.io/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
