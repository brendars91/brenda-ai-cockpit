---
name: security-red-team
description: Skill de seguridad proactiva - Genera hipótesis de ataque y valida fixes
---

# Security Red Team Skill

> **Rol**: Guardián Autónomo que anticipa riesgos en lugar de solo reaccionar a alertas.

## 🎯 Propósito

Este skill convierte al agente en un investigador de seguridad que:
1. **Genera hipótesis de ataque** antes de cada implementación
2. **Detecta vulnerabilidades lógicas** que Snyk/herramientas estáticas ignoran
3. **Valida fixes** con tests de prueba de concepto (PoC)

---

## 🔴 Protocolo Red-to-Green

### Paso 1: Hipótesis de Ataque
Antes de implementar cualquier feature, pregúntate:

```
¿Cómo podría un atacante abusar de esta funcionalidad?
```

### Checklist de Vectores de Ataque

| Categoría | Preguntas Clave |
|-----------|-----------------|
| **Autenticación** | ¿Se puede bypass? ¿Hay rutas sin proteger? |
| **Autorización (IDOR)** | ¿Puedo acceder a recursos de otros usuarios cambiando un ID? |
| **Inyección** | ¿Hay inputs que llegan a SQL/comandos sin sanitizar? |
| **Race Conditions** | ¿Qué pasa si dos requests llegan simultáneamente? |
| **Logic Flaws** | ¿El flujo puede ser alterado (ej: saltar pasos)? |
| **Data Exposure** | ¿Se exponen datos sensibles en respuestas/logs? |
| **SSRF/CSRF** | ¿Hay requests a URLs controlables por usuario? |
| **Crypto** | ¿Se usa crypto débil o hardcoded secrets? |

### Paso 2: Escribir PoC
Si identificas una vulnerabilidad:

```python
# Ejemplo de test PoC para IDOR
def test_idor_vulnerability():
    """Usuario A no debe acceder a datos de Usuario B."""
    user_a_token = login("user_a", "pass_a")
    user_b_resource_id = 42  # ID de recurso de User B
    
    response = get(f"/api/resource/{user_b_resource_id}", 
                   headers={"Authorization": user_a_token})
    
    # DEBE fallar con 403, no 200
    assert response.status_code == 403, "IDOR VULNERABILITY DETECTED!"
```

### Paso 3: Aplicar Fix
Implementar la corrección siguiendo mejores prácticas:

```python
# Fix: Verificar ownership antes de retornar
@app.get("/api/resource/{resource_id}")
def get_resource(resource_id: int, current_user: User):
    resource = db.get(resource_id)
    if resource.owner_id != current_user.id:
        raise HTTPException(403, "No autorizado")
    return resource
```

### Paso 4: Verificar
Ejecutar el test PoC para confirmar que ahora pasa:

```bash
pytest tests/security/test_idor.py -v
```

---

## 📋 Integración con Plan JSON

Todo Plan JSON debe incluir esta sección:

```json
{
  "security_analysis": {
    "assumptions": [
      "El usuario siempre estará autenticado antes de llegar aquí"
    ],
    "attack_vectors": [
      {
        "type": "IDOR",
        "description": "Cambiar ID en URL para acceder a datos ajenos",
        "likelihood": "high",
        "impact": "critical"
      }
    ],
    "mitigations": [
      "Verificar ownership en cada endpoint de recursos"
    ],
    "validation_tests": [
      "tests/security/test_idor_resource.py"
    ]
  }
}
```

---

## 🔧 Comandos

```bash
# Generar hipótesis de ataque para un archivo
python scripts/security_guardian.py analyze path/to/file.py

# Verificar que todos los tests de seguridad pasan
python scripts/security_guardian.py verify

# Ver estadísticas de vulnerabilidades detectadas
python scripts/security_guardian.py stats
```

---

## 📊 Métricas

El dashboard trackea:
- **Vulnerabilidades Lógicas Detectadas**: Encontradas por razonamiento, no por Snyk
- **Ratio Red-to-Green**: % de vulnerabilidades que fueron verificadas con test
- **Attack Surface Coverage**: % de código analizado con hipótesis de ataque

---

## 🚨 Reglas de Oro

1. **NUNCA** desplegar código sin análisis de seguridad
2. **SIEMPRE** escribir test PoC antes de fix
3. **DOCUMENTAR** cada vulnerabilidad encontrada en el Plan JSON
4. **MEDIR** ratio de vulnerabilidades lógicas vs estáticas
