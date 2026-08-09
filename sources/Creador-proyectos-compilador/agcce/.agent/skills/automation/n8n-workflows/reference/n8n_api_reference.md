# n8n API Reference

## n8n REST API

### Autenticación

```bash
# Header de autorización
Authorization: Bearer <api-key>

# Crear API key
# Settings → API → Generate API Key
```

### Base URLs

| Instalación | URL |
|-------------|-----|
| Self-hosted | `http://localhost:5678/api/v1` |
| n8n Cloud | `https://<instance>.app.n8n.cloud/api/v1` |

---

## Workflows API

### Listar Workflows

```bash
GET /workflows

# Query params
?active=true          # Solo activos
?tags=production      # Por tag
?limit=50            # Paginación
?cursor=abc123       # Cursor para siguiente página
```

### Obtener Workflow

```bash
GET /workflows/{id}

# Response
{
  "id": "workflow-id",
  "name": "My Workflow",
  "active": true,
  "nodes": [...],
  "connections": {...},
  "settings": {...},
  "staticData": {...},
  "tags": [...]
}
```

### Crear Workflow

```bash
POST /workflows
Content-Type: application/json

{
  "name": "New Workflow",
  "nodes": [
    {
      "parameters": {},
      "name": "Start",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ],
  "connections": {},
  "settings": {
    "saveExecutionProgress": true,
    "saveManualExecutions": true,
    "saveDataErrorExecution": "all"
  }
}
```

### Actualizar Workflow

```bash
PUT /workflows/{id}
Content-Type: application/json

# Body: workflow completo actualizado
```

### Activar/Desactivar

```bash
# Activar
POST /workflows/{id}/activate

# Desactivar
POST /workflows/{id}/deactivate
```

### Eliminar Workflow

```bash
DELETE /workflows/{id}
```

---

## Executions API

### Listar Ejecuciones

```bash
GET /executions

# Query params
?workflowId=abc       # Filtrar por workflow
?status=success       # success, error, waiting
?limit=100
?cursor=xyz
```

### Obtener Ejecución

```bash
GET /executions/{id}

# Response incluye data de cada nodo
{
  "id": "execution-id",
  "finished": true,
  "mode": "manual",
  "startedAt": "2025-01-15T10:00:00.000Z",
  "stoppedAt": "2025-01-15T10:00:05.000Z",
  "workflowId": "workflow-id",
  "data": {
    "resultData": {
      "runData": {
        "Node Name": [{
          "startTime": 1234567890,
          "executionTime": 150,
          "data": { "main": [[{ "json": {...} }]] }
        }]
      }
    }
  },
  "status": "success"
}
```

### Eliminar Ejecuciones

```bash
# Eliminar una
DELETE /executions/{id}

# Eliminar múltiples
POST /executions/delete
{
  "ids": ["id1", "id2", "id3"]
}
```

### Retry Ejecución

```bash
POST /executions/{id}/retry
```

---

## Credentials API

### Listar Credenciales

```bash
GET /credentials

# Response
{
  "data": [
    {
      "id": "cred-id",
      "name": "My API Key",
      "type": "httpHeaderAuth",
      "createdAt": "...",
      "updatedAt": "..."
    }
  ]
}
```

### Crear Credencial

```bash
POST /credentials
Content-Type: application/json

{
  "name": "New API Key",
  "type": "httpHeaderAuth",
  "data": {
    "name": "Authorization",
    "value": "Bearer abc123"
  }
}
```

### Actualizar Credencial

```bash
PUT /credentials/{id}
{
  "name": "Updated Name",
  "data": {
    "name": "Authorization",
    "value": "Bearer new-value"
  }
}
```

### Eliminar Credencial

```bash
DELETE /credentials/{id}
```

---

## Webhooks

### Webhook URL Format

```
# Production (workflow activo)
POST https://<n8n-url>/webhook/<webhook-path>

# Test (workflow inactivo)
POST https://<n8n-url>/webhook-test/<webhook-path>
```

### Webhook Node Configuration

| Parámetro | Descripción |
|-----------|-------------|
| HTTP Method | GET, POST, etc. |
| Path | Ruta personalizada (`my-webhook`) |
| Response Mode | `onReceived`, `lastNode`, `responseNode` |
| Response Code | Código HTTP a devolver |
| Response Data | `allEntries`, `firstEntryJson`, `noData` |

### Response Modes

#### onReceived
Responde inmediatamente, workflow continúa async.

```javascript
// Workflow
Webhook → [Respond inmediato] → Proceso largo → ...
```

#### lastNode
Espera a que termine el workflow y responde con output del último nodo.

#### responseNode
Usa un nodo "Respond to Webhook" para respuesta personalizada.

```javascript
// Con Respond to Webhook node
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "X-Custom-Header": "value"
  },
  "body": {
    "success": true,
    "id": "{{ $json.id }}"
  }
}
```

### Webhook Security

```javascript
// Verificar shared secret en header
const expectedSecret = $vars.WEBHOOK_SECRET;
const receivedSecret = $headers['x-webhook-secret'];

if (receivedSecret !== expectedSecret) {
  // En Respond to Webhook:
  return {
    statusCode: 401,
    body: { error: 'Unauthorized' }
  };
}
```

### Webhook con Binary Data

```javascript
// Recibir archivos
Webhook config:
  - Response Mode: lastNode
  - Binary Property: data

// Acceder al archivo
const fileContent = $binary.data.data;  // Base64
const mimeType = $binary.data.mimeType;
const fileName = $binary.data.fileName;
```

---

## Ejecutar Workflow Programáticamente

### Desde otro Workflow

```javascript
// Execute Workflow node
{
  "workflowId": "{{ $json.targetWorkflowId }}",
  "waitForSubWorkflow": true,
  // Los items del input se pasan automáticamente
}
```

### Vía API

```bash
# Ejecutar workflow existente
POST /workflows/{id}/run

# Con datos
POST /workflows/{id}/run
Content-Type: application/json

{
  "data": {
    "customData": "value"
  }
}

# Response
{
  "executionId": "execution-id"
}
```

### Vía Webhook (recomendado)

```bash
# Trigger workflow con webhook
POST https://<n8n-url>/webhook/my-trigger

{
  "action": "process",
  "data": { ... }
}
```

---

## Variables y Static Data

### Workflow Static Data

```javascript
// Acceso en Code Node
const staticData = this.getWorkflowStaticData('global');

// Leer
const lastRun = staticData.lastRun;

// Escribir (persistente entre ejecuciones)
staticData.lastRun = new Date().toISOString();
staticData.counter = (staticData.counter || 0) + 1;
```

### Environment Variables (Settings → Variables)

```javascript
// Acceso en expresiones
{{ $vars.API_KEY }}
{{ $vars.BASE_URL }}
```

---

## Uso desde Llamadas Externas

### cURL Examples

```bash
# Listar workflows
curl -X GET "https://n8n.example.com/api/v1/workflows" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Ejecutar workflow por webhook
curl -X POST "https://n8n.example.com/webhook/process-order" \
  -H "Content-Type: application/json" \
  -d '{"orderId": "12345", "action": "fulfill"}'

# Obtener estado de ejecución
curl -X GET "https://n8n.example.com/api/v1/executions/exec-id" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### JavaScript/Node.js

```javascript
const n8nApi = axios.create({
  baseURL: 'https://n8n.example.com/api/v1',
  headers: {
    'Authorization': `Bearer ${process.env.N8N_API_KEY}`,
    'Content-Type': 'application/json'
  }
});

// Listar workflows
const { data } = await n8nApi.get('/workflows');

// Ejecutar via webhook
const response = await axios.post(
  'https://n8n.example.com/webhook/my-endpoint',
  { data: 'value' }
);
```

### Python

```python
import requests

N8N_URL = "https://n8n.example.com"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Listar workflows
response = requests.get(
    f"{N8N_URL}/api/v1/workflows",
    headers=headers
)
workflows = response.json()

# Trigger webhook
response = requests.post(
    f"{N8N_URL}/webhook/process-data",
    json={"key": "value"}
)
```

---

## Rate Limits

| Endpoint | Límite por defecto |
|----------|-------------------|
| API requests | 5000/hora |
| Webhook requests | Configurable |
| Executions concurrentes | Según plan |

### Headers de respuesta

```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4985
X-RateLimit-Reset: 1673520000
```

---

## Error Responses

```json
// 400 Bad Request
{
  "code": 400,
  "message": "Invalid workflow JSON"
}

// 401 Unauthorized
{
  "code": 401,
  "message": "Invalid API key"
}

// 404 Not Found
{
  "code": 404,
  "message": "Workflow not found"
}

// 500 Internal Error
{
  "code": 500,
  "message": "Internal server error",
  "hint": "Check n8n logs for details"
}
```
