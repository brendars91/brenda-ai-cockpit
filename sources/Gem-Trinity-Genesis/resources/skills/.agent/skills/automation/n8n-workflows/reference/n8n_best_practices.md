# n8n Best Practices

## Organización de Workflows

### Nomenclatura

```
[Categoría] Nombre descriptivo (v1.0)

Ejemplos:
[ETL] Sync Customers from Salesforce (v2.1)
[API] Order Processing Webhook (v1.0)
[Cron] Daily Report Generator (v1.5)
[Sub] Email Notification Template (v1.0)
```

### Tags Recomendados

| Tag | Uso |
|-----|-----|
| `production` | Workflows activos en producción |
| `development` | En desarrollo |
| `staging` | Testing pre-producción |
| `deprecated` | Por eliminar |
| `critical` | Alto impacto si falla |
| `manual` | Solo ejecución manual |

### Documentación en Workflow

Usa la descripción del workflow para documentar:
- Propósito y contexto
- Dependencias (otros workflows, APIs)
- Contacto del owner
- Changelog de versiones

---

## Manejo de Errores

### Patrón Try-Catch en Code Node

```javascript
try {
  // Lógica principal
  const result = processData($json);
  return [{ json: { success: true, data: result } }];
} catch (error) {
  // En desarrollo: re-lanzar
  // En producción: capturar y loguear
  console.error('Error processing:', error.message);
  return [{ json: { 
    success: false, 
    error: error.message,
    stack: error.stack,
    originalData: $json 
  }}];
}
```

### Error Workflow Global

```
Error trigger → Extract Metadata → Switch by Severity 
    → Critical → Slack + PagerDuty
    → Warning → Slack
    → Info → Log only
```

### Retry Pattern

```
Webhook → Process → IF Error?
    → Yes → Increment Counter → Wait → Re-call Process (max 3)
    → No → Continue
    → Max retries → Dead Letter Queue
```

### Configurar en cada nodo

- **On Error**: `Continue` (con error output) vs `Stop Workflow`
- **Retry on Fail**: Configurar intentos y delay

---

## Rate Limiting

### Split in Batches

```
Fetch All Items → Split In Batches (size: 10) 
    → Process Batch → Wait (1 second) → Loop
```

### Throttling con Wait

```javascript
// En Code Node después de API call
const currentSecond = new Date().getSeconds();
const delayMs = 1100 - (Date.now() % 1000); // Esperar hasta siguiente segundo
// Usar Wait node después con el delay calculado
```

### Verificar Headers de Rate Limit

```javascript
const remaining = $json.headers['x-ratelimit-remaining'];
const resetTime = $json.headers['x-ratelimit-reset'];

if (remaining < 10) {
  // Activar throttling más agresivo
}
```

---

## Variables y Environments

### Estructura Recomendada

```
# Variables globales (Settings → Variables)
API_BASE_URL = https://api.production.com
ENVIRONMENT = production
SLACK_CHANNEL = #production-alerts
EMAIL_SENDER = noreply@company.com

# Por entorno (gestionar con deployment)
DEV_API_BASE_URL = https://api.dev.com
STAGING_API_BASE_URL = https://api.staging.com
```

### Acceso en Expresiones

```javascript
// URL base dinámica
{{ $vars.API_BASE_URL }}/v1/users

// Condicional por ambiente
{{ $vars.ENVIRONMENT === 'production' ? $vars.PROD_KEY : $vars.DEV_KEY }}
```

### Credenciales por Ambiente

Crear credenciales separadas:
- `My Service (Production)`
- `My Service (Staging)`
- `My Service (Development)`

---

## Seguridad

### Credenciales

❌ **Nunca**:
- Hardcodear API keys en nodos
- Exponer secrets en logs
- Compartir credenciales entre ambientes

✅ **Siempre**:
- Usar sistema de credenciales de n8n
- Rotar credenciales periódicamente
- Limitar permisos al mínimo necesario

### Validación de Webhooks

```javascript
// Verificar firma HMAC
const crypto = require('crypto');
const signature = $headers['x-webhook-signature'];
const payload = JSON.stringify($json);
const secret = $credentials.webhookSecret;

const expectedSignature = crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

if (signature !== expectedSignature) {
  throw new Error('Invalid webhook signature');
}
```

### Rate Limiting en Webhooks

- Configurar límites en reverse proxy (nginx, cloudflare)
- Implementar verificación de origen

### Sanitización de Datos

```javascript
// Limpiar datos antes de procesar
const sanitizedEmail = $json.email
  .toLowerCase()
  .trim()
  .replace(/[<>]/g, '');

// Validar formato
if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(sanitizedEmail)) {
  throw new Error('Invalid email format');
}
```

---

## Logging y Debugging

### Logs Estructurados

```javascript
// En Code Node
const logEntry = {
  timestamp: new Date().toISOString(),
  executionId: $execution.id,
  workflowId: $workflow.id,
  event: 'user_processed',
  userId: $json.id,
  status: 'success',
  duration: performance.now() - startTime
};

console.log(JSON.stringify(logEntry));
```

### Debugging Tips

1. **Pin Data**: Fijar output de un nodo para tests consistentes
2. **Execution Preview**: Ver datos en cada paso
3. **Manual Execution**: Testear nodos individuales
4. **Console.log**: En Code nodes, logs van al panel de ejecución

### Monitoreo Externo

Enviar métricas a:
- DataDog, New Relic, Grafana
- Elastic/Kibana para logs
- Custom dashboards

---

## Performance

### Optimizar Data Size

```javascript
// Extraer solo campos necesarios
const lightData = $input.all().map(item => ({
  json: {
    id: item.json.id,
    name: item.json.name
    // Solo lo necesario, no todo el objeto
  }
}));
```

### Paralelización

n8n procesa items secuencialmente por defecto en un nodo. Para paralelizar:
- Usar múltiples branches con Merge
- Dividir en sub-workflows paralelos

### Cacheo

```javascript
// Usar Static Data para cache en memoria
const cache = $workflow.staticData;
const cacheKey = 'users_list';
const cacheTTL = 3600000; // 1 hora

if (cache[cacheKey] && (Date.now() - cache[`${cacheKey}_time`]) < cacheTTL) {
  return cache[cacheKey];
}

// Fetch y cachear
const users = await fetchUsers();
cache[cacheKey] = users;
cache[`${cacheKey}_time`] = Date.now();
```

---

## Modularidad

### Sub-workflows

Crear workflows reutilizables para:
- Notificaciones comunes
- Transformaciones estándar
- Llamadas a APIs compartidas
- Lógica de validación

### Estructura de llamada

```
Main Workflow → Execute Workflow (sub) → Continue
                      ↓
              Sub-workflow returns data
```

### Pasar Parámetros

```javascript
// En Execute Workflow node
// Input: los items del nodo anterior se pasan automáticamente

// En sub-workflow: acceder con $input
const parentData = $input.first().json;
```

---

## Deployment

### Exportación e Importación

```bash
# Exportar workflow como JSON
# En n8n: Workflow → Export

# Importar: Workflow → Import from File/URL
```

### Versionado

- Mantener workflows en Git como JSON
- Usar tags de versión en nombres
- Changelog en descripción

### CI/CD

```yaml
# GitHub Action example
- name: Deploy n8n workflow
  run: |
    curl -X POST $N8N_API_URL/workflows \
      -H "Authorization: Bearer $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d @workflow.json
```

---

## Checklist de Calidad

### Pre-deployment

- [ ] Todas las credenciales configuradas
- [ ] Variables de entorno verificadas
- [ ] Error handling en todos los paths críticos
- [ ] Tests con datos reales
- [ ] Documentación actualizada
- [ ] Tags asignados

### Post-deployment

- [ ] Monitoreo activo
- [ ] Alertas configuradas
- [ ] Logs accesibles
- [ ] Rollback plan definido
