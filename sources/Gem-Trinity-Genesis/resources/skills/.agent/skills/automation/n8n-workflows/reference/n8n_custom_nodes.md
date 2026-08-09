# n8n Custom Nodes Development

## Overview

Los nodos personalizados permiten extender n8n con integraciones propias. Se desarrollan en TypeScript y pueden distribuirse como paquetes npm.

---

## Estructura del Proyecto

```
my-n8n-nodes/
├── package.json
├── tsconfig.json
├── nodes/
│   └── MyNode/
│       ├── MyNode.node.ts         # Lógica del nodo
│       ├── MyNode.node.json       # Codex metadata (opcional)
│       └── mynode.svg             # Icono
├── credentials/
│   └── MyApi.credentials.ts       # Tipo de credencial
└── dist/                          # Compilado (generado)
```

---

## Package.json

```json
{
  "name": "n8n-nodes-myservice",
  "version": "1.0.0",
  "description": "n8n nodes for MyService API",
  "keywords": ["n8n", "n8n-community-node-package"],
  "main": "dist/nodes/MyNode/MyNode.node.js",
  "n8n": {
    "n8nNodesApiVersion": 1,
    "credentials": [
      "dist/credentials/MyApi.credentials.js"
    ],
    "nodes": [
      "dist/nodes/MyNode/MyNode.node.js"
    ]
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "lint": "eslint . --ext .ts"
  },
  "dependencies": {
    "n8n-workflow": "^1.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "n8n-core": "^1.0.0"
  },
  "peerDependencies": {
    "n8n-workflow": "*"
  }
}
```

---

## Credential Type

### Estructura Básica

```typescript
// credentials/MyApi.credentials.ts
import {
  IAuthenticateGeneric,
  ICredentialTestRequest,
  ICredentialType,
  INodeProperties,
} from 'n8n-workflow';

export class MyApi implements ICredentialType {
  name = 'myApi';
  displayName = 'My API';
  documentationUrl = 'https://docs.myservice.com/api';
  
  properties: INodeProperties[] = [
    {
      displayName: 'API Key',
      name: 'apiKey',
      type: 'string',
      typeOptions: {
        password: true,
      },
      default: '',
      required: true,
    },
    {
      displayName: 'Environment',
      name: 'environment',
      type: 'options',
      options: [
        { name: 'Production', value: 'production' },
        { name: 'Sandbox', value: 'sandbox' },
      ],
      default: 'production',
    },
  ];

  authenticate: IAuthenticateGeneric = {
    type: 'generic',
    properties: {
      headers: {
        Authorization: '=Bearer {{$credentials.apiKey}}',
      },
    },
  };

  test: ICredentialTestRequest = {
    request: {
      baseURL: '={{$credentials.environment === "production" ? "https://api.myservice.com" : "https://sandbox.myservice.com"}}',
      url: '/v1/auth/verify',
    },
  };
}
```

### OAuth2

```typescript
export class MyApiOAuth2 implements ICredentialType {
  name = 'myApiOAuth2';
  displayName = 'My API OAuth2';
  extends = ['oAuth2Api'];  // Hereda de OAuth2
  
  properties: INodeProperties[] = [
    {
      displayName: 'Grant Type',
      name: 'grantType',
      type: 'hidden',
      default: 'authorizationCode',
    },
    {
      displayName: 'Authorization URL',
      name: 'authUrl',
      type: 'hidden',
      default: 'https://myservice.com/oauth/authorize',
    },
    {
      displayName: 'Access Token URL',
      name: 'accessTokenUrl',
      type: 'hidden',
      default: 'https://myservice.com/oauth/token',
    },
    {
      displayName: 'Scope',
      name: 'scope',
      type: 'hidden',
      default: 'read write',
    },
  ];
}
```

---

## Node Type Description

### Estructura del Nodo

```typescript
// nodes/MyNode/MyNode.node.ts
import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

export class MyNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'My Service',
    name: 'myService',
    icon: 'file:myservice.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["operation"] + ": " + $parameter["resource"]}}',
    description: 'Interact with My Service API',
    defaults: {
      name: 'My Service',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'myApi',
        required: true,
      },
    ],
    properties: [
      // Resource selector
      {
        displayName: 'Resource',
        name: 'resource',
        type: 'options',
        noDataExpression: true,
        options: [
          { name: 'User', value: 'user' },
          { name: 'Order', value: 'order' },
        ],
        default: 'user',
      },
      // Operations for User
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        displayOptions: {
          show: {
            resource: ['user'],
          },
        },
        options: [
          { name: 'Create', value: 'create', action: 'Create a user' },
          { name: 'Get', value: 'get', action: 'Get a user' },
          { name: 'List', value: 'list', action: 'List users' },
          { name: 'Update', value: 'update', action: 'Update a user' },
          { name: 'Delete', value: 'delete', action: 'Delete a user' },
        ],
        default: 'get',
      },
      // Parameters for specific operation
      {
        displayName: 'User ID',
        name: 'userId',
        type: 'string',
        required: true,
        displayOptions: {
          show: {
            resource: ['user'],
            operation: ['get', 'update', 'delete'],
          },
        },
        default: '',
        description: 'The ID of the user',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    // Implementation
  }
}
```

---

## Execute Method

### Programmatic Style (Recomendado para APIs)

```typescript
async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
  const items = this.getInputData();
  const returnData: INodeExecutionData[] = [];
  
  const resource = this.getNodeParameter('resource', 0) as string;
  const operation = this.getNodeParameter('operation', 0) as string;
  const credentials = await this.getCredentials('myApi');
  
  const baseUrl = credentials.environment === 'production'
    ? 'https://api.myservice.com'
    : 'https://sandbox.myservice.com';

  for (let i = 0; i < items.length; i++) {
    try {
      let responseData;
      
      if (resource === 'user') {
        if (operation === 'get') {
          const userId = this.getNodeParameter('userId', i) as string;
          
          responseData = await this.helpers.httpRequestWithAuthentication.call(
            this,
            'myApi',
            {
              method: 'GET',
              url: `${baseUrl}/v1/users/${userId}`,
              json: true,
            }
          );
        } else if (operation === 'create') {
          const email = this.getNodeParameter('email', i) as string;
          const name = this.getNodeParameter('name', i) as string;
          
          responseData = await this.helpers.httpRequestWithAuthentication.call(
            this,
            'myApi',
            {
              method: 'POST',
              url: `${baseUrl}/v1/users`,
              body: { email, name },
              json: true,
            }
          );
        } else if (operation === 'list') {
          const limit = this.getNodeParameter('limit', i, 50) as number;
          
          responseData = await this.helpers.httpRequestWithAuthentication.call(
            this,
            'myApi',
            {
              method: 'GET',
              url: `${baseUrl}/v1/users`,
              qs: { limit },
              json: true,
            }
          );
          
          // Si devuelve array, expandir a items individuales
          if (Array.isArray(responseData)) {
            for (const item of responseData) {
              returnData.push({ json: item });
            }
            continue;
          }
        }
      }
      
      returnData.push({ json: responseData });
      
    } catch (error) {
      if (this.continueOnFail()) {
        returnData.push({
          json: { error: (error as Error).message },
          pairedItem: { item: i },
        });
        continue;
      }
      throw new NodeOperationError(this.getNode(), error as Error, { itemIndex: i });
    }
  }
  
  return [returnData];
}
```

### HTTP Request Helpers

```typescript
// Sin autenticación
const response = await this.helpers.httpRequest({
  method: 'GET',
  url: 'https://api.example.com/data',
  json: true,
});

// Con autenticación de credenciales
const response = await this.helpers.httpRequestWithAuthentication.call(
  this,
  'credentialTypeName',
  {
    method: 'POST',
    url: 'https://api.example.com/data',
    body: { key: 'value' },
    json: true,
    timeout: 30000,
  }
);

// Con retry automático
const response = await this.helpers.httpRequestWithAuthentication.call(
  this,
  'credentialTypeName',
  {
    method: 'GET',
    url: 'https://api.example.com/data',
    json: true,
    retry: {
      maxRetries: 3,
      retryDelay: 1000,
    },
  }
);
```

---

## Error Handling

```typescript
import { NodeApiError, NodeOperationError } from 'n8n-workflow';

// Error de API con contexto
try {
  const response = await this.helpers.httpRequestWithAuthentication.call(
    this,
    'myApi',
    options
  );
} catch (error) {
  const errorResponse = error.response?.body;
  
  if (error.response?.statusCode === 404) {
    throw new NodeApiError(this.getNode(), error, {
      message: 'Resource not found',
      description: `The requested resource with ID "${id}" does not exist`,
    });
  }
  
  if (error.response?.statusCode === 429) {
    throw new NodeApiError(this.getNode(), error, {
      message: 'Rate limit exceeded',
      description: 'Please wait before making more requests',
    });
  }
  
  throw new NodeApiError(this.getNode(), error);
}

// Error de operación (configuración incorrecta)
if (!userId) {
  throw new NodeOperationError(
    this.getNode(),
    'User ID is required for this operation',
    { itemIndex: i }
  );
}
```

---

## Trigger Nodes

### Webhook Trigger

```typescript
import {
  IWebhookFunctions,
  IWebhookResponseData,
  INodeType,
  INodeTypeDescription,
} from 'n8n-workflow';

export class MyServiceTrigger implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'My Service Trigger',
    name: 'myServiceTrigger',
    icon: 'file:myservice.svg',
    group: ['trigger'],
    version: 1,
    description: 'Triggers on My Service events',
    defaults: {
      name: 'My Service Trigger',
    },
    inputs: [],
    outputs: ['main'],
    webhooks: [
      {
        name: 'default',
        httpMethod: 'POST',
        responseMode: 'onReceived',
        path: 'webhook',
      },
    ],
    properties: [
      {
        displayName: 'Event Type',
        name: 'eventType',
        type: 'options',
        options: [
          { name: 'User Created', value: 'user.created' },
          { name: 'Order Completed', value: 'order.completed' },
        ],
        default: 'user.created',
      },
    ],
  };

  async webhook(this: IWebhookFunctions): Promise<IWebhookResponseData> {
    const bodyData = this.getBodyData();
    const eventType = this.getNodeParameter('eventType') as string;
    
    // Validar evento
    if (bodyData.type !== eventType) {
      return {
        noWebhookResponse: true,  // No procesar
      };
    }
    
    return {
      workflowData: [
        [{ json: bodyData as object }]
      ],
    };
  }
}
```

### Polling Trigger

```typescript
import {
  IPollFunctions,
  INodeExecutionData,
  INodeType,
} from 'n8n-workflow';

export class MyServicePollingTrigger implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'My Service Polling',
    name: 'myServicePolling',
    group: ['trigger'],
    version: 1,
    polling: true,
    inputs: [],
    outputs: ['main'],
    properties: [
      {
        displayName: 'Poll Interval',
        name: 'pollInterval',
        type: 'number',
        default: 60,
        description: 'How often to poll (in seconds)',
      },
    ],
  };

  async poll(this: IPollFunctions): Promise<INodeExecutionData[][] | null> {
    const lastPollTime = this.getWorkflowStaticData('lastPollTime') as number || 0;
    const now = Date.now();
    
    // Fetch nuevos items desde lastPollTime
    const items = await fetchNewItems(lastPollTime);
    
    // Actualizar estado
    this.setWorkflowStaticData('lastPollTime', now);
    
    if (items.length === 0) {
      return null;  // Sin nuevos items
    }
    
    return [[...items.map(item => ({ json: item }))]];
  }
}
```

---

## Testing

### Instalación Local

```bash
# En el directorio del nodo custom
npm run build
npm link

# En el directorio de n8n
npm link n8n-nodes-myservice

# Reiniciar n8n
n8n start
```

### Con Docker

```dockerfile
FROM n8nio/n8n

# Copiar nodo custom
COPY dist /home/node/.n8n/custom

# O instalar desde npm
RUN npm install -g n8n-nodes-myservice
```

---

## Publicación

1. **Preparar package.json** con keywords correctas
2. **Compilar**: `npm run build`
3. **Publicar**: `npm publish`
4. **Registrar** en n8n community nodes (opcional)

---

## Best Practices

1. **Usar helpers de n8n** para HTTP requests
2. **Manejar paginación** en operaciones list
3. **Incluir `continueOnFail`** support
4. **Documentar parámetros** con descriptions claras
5. **Validar inputs** antes de llamar APIs
6. **Retornar datos estructurados** consistentes
7. **Usar `pairedItem`** para trazabilidad
