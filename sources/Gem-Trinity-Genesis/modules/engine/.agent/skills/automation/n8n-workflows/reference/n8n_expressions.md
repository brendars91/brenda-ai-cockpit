# n8n Expressions - Guía Completa

## Sintaxis Básica

Las expresiones en n8n se escriben entre doble llave `{{ }}` y soportan JavaScript completo.

```javascript
// Sintaxis básica
{{ expression }}

// Multi-línea
{{
  const value = $json.field;
  return value.toUpperCase();
}}
```

---

## Acceso a Datos

### Item Actual

```javascript
// JSON del item actual
{{ $json }}
{{ $json.fieldName }}
{{ $json["field-with-dashes"] }}
{{ $json.nested.deep.value }}

// Acceso seguro (optional chaining)
{{ $json.nested?.optional?.field ?? 'default' }}

// Datos binarios
{{ $binary }}
{{ $binary.data.mimeType }}
```

### Todos los Items del Input

```javascript
// Array completo
{{ $input.all() }}

// Primer item
{{ $input.first() }}

// Último item  
{{ $input.last() }}

// Item por índice
{{ $input.item }}  // Mismo índice que item actual

// Contar items
{{ $input.all().length }}
```

### Datos de Otros Nodos

```javascript
// Por nombre de nodo
{{ $('HTTP Request').item.json.data }}
{{ $('HTTP Request').first().json }}
{{ $('HTTP Request').all() }}

// Último item de un nodo
{{ $('Previous Node').last().json }}

// Iterar sobre items de otro nodo
{{ $('Node').all().map(item => item.json.id) }}
```

---

## Variables del Sistema

### Workflow y Ejecución

```javascript
// Información del workflow
{{ $workflow.id }}
{{ $workflow.name }}
{{ $workflow.active }}

// Información de ejecución
{{ $execution.id }}
{{ $execution.mode }}          // 'test' o 'production'
{{ $execution.resumeUrl }}     // Para Wait nodes

// Variables de entorno (Settings → Variables)
{{ $vars.API_URL }}
{{ $vars.ENVIRONMENT }}

// Posición del item actual
{{ $itemIndex }}
{{ $runIndex }}
```

### Credenciales

```javascript
// Acceso en expresiones (solo campos permitidos)
{{ $credentials.apiKey }}
{{ $credentials.password }}

// En HTTP Request header
{
  "Authorization": "Bearer {{ $credentials.token }}"
}
```

---

## Manipulación de Strings

```javascript
// Métodos básicos
{{ $json.name.toLowerCase() }}
{{ $json.name.toUpperCase() }}
{{ $json.name.trim() }}
{{ $json.text.replace('old', 'new') }}
{{ $json.text.replaceAll('old', 'new') }}

// Substring y split
{{ $json.email.split('@')[1] }}           // Dominio
{{ $json.text.substring(0, 50) }}         // Primeros 50 chars
{{ $json.path.split('/').pop() }}         // Último segmento

// Template literals
{{ `Hello, ${$json.firstName} ${$json.lastName}!` }}

// Regex
{{ $json.phone.replace(/[^0-9]/g, '') }}  // Solo números
{{ /^test/.test($json.email) }}           // Empieza con "test"

// Codificación
{{ encodeURIComponent($json.query) }}
{{ decodeURIComponent($json.encoded) }}
{{ btoa($json.text) }}                    // Base64 encode
{{ atob($json.base64) }}                  // Base64 decode
```

---

## Manipulación de Arrays

```javascript
// Filtrar
{{ $json.items.filter(item => item.active) }}
{{ $json.users.filter(u => u.age >= 18) }}

// Mapear
{{ $json.items.map(item => item.id) }}
{{ $json.users.map(u => ({ name: u.name, email: u.email })) }}

// Reducir
{{ $json.items.reduce((sum, item) => sum + item.price, 0) }}

// Encontrar
{{ $json.items.find(item => item.id === 123) }}
{{ $json.items.findIndex(item => item.id === 123) }}

// Ordenar
{{ $json.items.sort((a, b) => a.date.localeCompare(b.date)) }}
{{ $json.items.sort((a, b) => b.price - a.price) }}  // Descendente

// Otros
{{ $json.items.length }}
{{ $json.items.includes('value') }}
{{ $json.items.join(', ') }}
{{ $json.items.slice(0, 10) }}                        // Primeros 10
{{ [...new Set($json.items)] }}                       // Únicos
```

---

## Manipulación de Objetos

```javascript
// Acceso a propiedades
{{ Object.keys($json) }}
{{ Object.values($json) }}
{{ Object.entries($json) }}

// Spread y merge
{{ { ...$json, newField: 'value' } }}
{{ { ...$json.data, ...$json.metadata } }}

// Eliminar propiedades
{{
  const { password, ...rest } = $json;
  return rest;
}}

// Verificar propiedades
{{ 'fieldName' in $json }}
{{ $json.hasOwnProperty('field') }}
{{ $json.field !== undefined }}
```

---

## Fechas con Luxon

n8n incluye Luxon como biblioteca de fechas. Las variables `$now` y `$today` son objetos Luxon DateTime.

### Acceso Rápido

```javascript
// Ahora
{{ $now }}                                    // DateTime completo
{{ $now.toISO() }}                           // ISO string
{{ $now.toFormat('yyyy-MM-dd') }}            // Formato custom

// Hoy a medianoche
{{ $today }}
{{ $today.toFormat('yyyy-MM-dd') }}
```

### Operaciones con Fechas

```javascript
// Sumar/restar tiempo
{{ $now.plus({ days: 7 }) }}
{{ $now.minus({ hours: 2 }) }}
{{ $now.plus({ months: 1, days: 15 }) }}

// Inicio/fin de período
{{ $now.startOf('month') }}
{{ $now.endOf('week') }}
{{ $now.startOf('day') }}

// Establecer valores
{{ $now.set({ hour: 9, minute: 0 }) }}
```

### Formateo

```javascript
// Formatos predefinidos
{{ $now.toISO() }}              // 2025-01-15T19:30:00.000+01:00
{{ $now.toISODate() }}          // 2025-01-15
{{ $now.toISOTime() }}          // 19:30:00.000+01:00
{{ $now.toHTTP() }}             // Wed, 15 Jan 2025 18:30:00 GMT

// Formato personalizado
{{ $now.toFormat('dd/MM/yyyy') }}           // 15/01/2025
{{ $now.toFormat('MMMM d, yyyy') }}         // January 15, 2025
{{ $now.toFormat('HH:mm:ss') }}             // 19:30:00
{{ $now.toFormat("yyyy-MM-dd'T'HH:mm:ss") }} // 2025-01-15T19:30:00

// Tokens de formato comunes
// yyyy - Año (2025)
// MM   - Mes con cero (01)
// M    - Mes sin cero (1)
// MMMM - Mes nombre (January)
// dd   - Día con cero (15)
// d    - Día sin cero (15)
// HH   - Hora 24h (19)
// hh   - Hora 12h (07)
// mm   - Minutos (30)
// ss   - Segundos (00)
// a    - AM/PM
```

### Parsing y Comparación

```javascript
// Parsear string a DateTime
{{ DateTime.fromISO($json.dateString) }}
{{ DateTime.fromFormat($json.date, 'dd/MM/yyyy') }}
{{ DateTime.fromMillis($json.timestamp) }}

// Comparar fechas
{{ $now > DateTime.fromISO($json.deadline) }}
{{ $now.diff(DateTime.fromISO($json.createdAt), 'days').days }}

// Zona horaria
{{ $now.setZone('America/New_York') }}
{{ $now.toUTC() }}
{{ $now.zoneName }}
```

---

## Condicionales y Lógica

```javascript
// Ternario
{{ $json.status === 'active' ? 'Activo' : 'Inactivo' }}

// Nullish coalescing
{{ $json.optionalField ?? 'default value' }}

// OR lógico (cuidado con falsy values)
{{ $json.name || 'Sin nombre' }}

// AND lógico
{{ $json.enabled && $json.validated }}

// Condicional complejo
{{
  if ($json.type === 'A') {
    return 'Tipo A';
  } else if ($json.type === 'B') {
    return 'Tipo B';
  }
  return 'Otro';
}}
```

---

## JSON y Serialización

```javascript
// Stringify
{{ JSON.stringify($json) }}
{{ JSON.stringify($json, null, 2) }}        // Pretty print

// Parse
{{ JSON.parse($json.jsonString) }}

// Deep clone
{{ JSON.parse(JSON.stringify($json)) }}
```

---

## Funciones Útiles Integradas

```javascript
// Números
{{ Math.round($json.value) }}
{{ Math.floor($json.price) }}
{{ Math.ceil($json.amount) }}
{{ Math.max(...$json.numbers) }}
{{ Math.min(...$json.numbers) }}
{{ parseFloat($json.stringNumber) }}
{{ parseInt($json.stringInt, 10) }}

// UUID
{{ $execution.id }}                         // Usar como ID único

// Random
{{ Math.random() }}
{{ Math.floor(Math.random() * 100) }}       // 0-99
```

---

## Patrones Comunes

### Transformar Array de Objetos

```javascript
{{
  $json.users.map(user => ({
    id: user.id,
    fullName: `${user.firstName} ${user.lastName}`,
    email: user.email.toLowerCase(),
    createdAt: DateTime.fromISO(user.created).toFormat('yyyy-MM-dd')
  }))
}}
```

### Agrupar por Campo

```javascript
{{
  $input.all().reduce((groups, item) => {
    const key = item.json.category;
    if (!groups[key]) groups[key] = [];
    groups[key].push(item.json);
    return groups;
  }, {})
}}
```

### Filtrar y Contar

```javascript
// Contar activos
{{ $json.items.filter(i => i.status === 'active').length }}

// Sumar precios
{{ $json.items.reduce((sum, i) => sum + i.price, 0) }}
```

### Fechas Relativas

```javascript
// Hace 7 días
{{ $now.minus({ days: 7 }).toISO() }}

// Inicio del mes actual
{{ $now.startOf('month').toISO() }}

// Próximo lunes
{{ $now.plus({ weeks: 1 }).startOf('week').toISO() }}
```
