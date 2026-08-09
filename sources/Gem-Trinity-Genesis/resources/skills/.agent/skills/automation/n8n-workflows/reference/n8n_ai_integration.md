# n8n AI Integration Guide

## Overview

n8n ofrece integración nativa con los principales LLMs y frameworks de AI, permitiendo crear workflows de automatización inteligente, agentes autónomos y pipelines de procesamiento de datos con IA.

---

## Nodos AI Disponibles

| Nodo | Uso |
|------|-----|
| **OpenAI** | GPT-4, GPT-3.5, embeddings, images |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) |
| **Google AI** | Gemini Pro, Gemini Flash |
| **Azure OpenAI** | GPT en infraestructura Azure |
| **Ollama** | Modelos locales (Llama, Mistral) |
| **AI Agent** | Agentes autónomos con tools |
| **LangChain** | Chains y retrieval patterns |
| **Vector Store** | Pinecone, Qdrant, Weaviate |

---

## Patrón Básico: LLM Simple

```
Trigger → Prepare Context → LLM Node → Parse Response → Action
```

### Ejemplo con OpenAI

```javascript
// Preparar context (Code Node)
const context = $input.all().map(item => ({
  json: {
    messages: [
      { role: 'system', content: 'Eres un asistente experto en análisis de datos.' },
      { role: 'user', content: `Analiza este texto: ${item.json.text}` }
    ]
  }
}));
return context;
```

### Configuración OpenAI Node

| Parámetro | Valor |
|-----------|-------|
| Resource | Chat |
| Model | gpt-4-turbo |
| Messages | `{{ $json.messages }}` |
| Max Tokens | 1024 |
| Temperature | 0.7 |

---

## Patrón RAG (Retrieval Augmented Generation)

```
Query → Embed Query → Vector Search → Retrieve Docs 
    → Build Context → LLM with Context → Response
```

### Paso 1: Embeddings

```javascript
// Generar embedding de la query
// Usar OpenAI Node → Embeddings
{
  "model": "text-embedding-3-small",
  "input": "{{ $json.query }}"
}
```

### Paso 2: Vector Search

```javascript
// Buscar en Pinecone
{
  "namespace": "documents",
  "vector": "{{ $json.embedding }}",
  "topK": 5,
  "includeMetadata": true
}
```

### Paso 3: Construir Context

```javascript
// Code Node
const relevantDocs = $('Vector Search').all()
  .map(item => item.json.metadata.text)
  .join('\n\n---\n\n');

const prompt = `Usa el siguiente contexto para responder:

CONTEXTO:
${relevantDocs}

PREGUNTA:
${$json.query}

RESPUESTA:`;

return [{ json: { prompt } }];
```

---

## AI Agent (Agente Autónomo)

### Conceptos

- **Agent**: LLM que decide qué herramientas usar
- **Tools**: Acciones disponibles (API calls, search, code execution)
- **Memory**: Contexto de conversación persistente

### Configuración AI Agent Node

```yaml
Agent Type: Conversational Agent
LLM: OpenAI GPT-4
Tools:
  - HTTP Request Tool
  - Code Execution Tool
  - Calculator Tool
Memory: Window Buffer Memory (últimos 10 mensajes)
```

### Definir Tools Personalizadas

```javascript
// En el nodo "AI Agent"
Tools → Add Tool → Workflow Tool

// El workflow tool puede ser otro workflow n8n que el agente puede invocar
```

### Ejemplo: Agente de Soporte

```
User Message → AI Agent
    ↓
    Agent decide:
    - Search KB (workflow tool → vector search)
    - Create Ticket (workflow tool → Zendesk)
    - Escalate (workflow tool → Slack notify)
    ↓
Agent Response → Send to User
```

---

## LangChain en n8n

### Chain Básico

```javascript
// LangChain Code Node
const { ChatOpenAI } = require("@langchain/openai");
const { ChatPromptTemplate } = require("@langchain/core/prompts");

const model = new ChatOpenAI({ 
  modelName: "gpt-4",
  temperature: 0.7,
  openAIApiKey: $credentials.openAiApiKey
});

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "Eres un experto en {domain}."],
  ["human", "{question}"]
]);

const chain = prompt.pipe(model);
const response = await chain.invoke({
  domain: $json.domain,
  question: $json.question
});

return [{ json: { response: response.content } }];
```

### Retrieval Chain

```javascript
const { OpenAIEmbeddings } = require("@langchain/openai");
const { PineconeStore } = require("@langchain/pinecone");
const { RetrievalQAChain } = require("langchain/chains");

// Inicializar retriever
const embeddings = new OpenAIEmbeddings();
const vectorStore = await PineconeStore.fromExistingIndex(embeddings, {
  pineconeIndex: index,
  namespace: "documents"
});

const retriever = vectorStore.asRetriever({ k: 5 });

// Chain con retrieval
const chain = RetrievalQAChain.fromLLM(model, retriever);
const response = await chain.invoke({ query: $json.query });
```

---

## Patrones Avanzados

### Patrón: Clasificación + Routing

```
Input → LLM Classifier → Switch by Category
    → Category A → Process A
    → Category B → Process B
    → Default → Generic Process
```

```javascript
// Prompt de clasificación
const classificationPrompt = `Clasifica el siguiente texto en una de estas categorías:
- URGENT: Requiere atención inmediata
- SUPPORT: Pregunta de soporte técnico
- SALES: Consulta comercial
- OTHER: No encaja en las anteriores

Texto: ${$json.text}

Responde SOLO con la categoría en mayúsculas.`;
```

### Patrón: Validación con LLM

```
Input → LLM Validator → IF Valid?
    → Yes → Continue Processing
    → No → Reject with Reason
```

```javascript
// Prompt de validación
const validationPrompt = `Analiza si el siguiente contenido es apropiado para publicar:
- No contenga información personal sensible
- No sea spam o publicidad
- Sea relevante para el tema

Contenido: ${$json.content}

Responde en JSON:
{
  "valid": true/false,
  "reason": "explicación si no es válido"
}`;
```

### Patrón: Summarization en Lotes

```
Large Document → Split into Chunks → Map: Summarize Each
    → Reduce: Combine Summaries → Final Summary
```

```javascript
// Chunk splitting
const chunkSize = 2000;
const document = $json.fullText;
const chunks = [];

for (let i = 0; i < document.length; i += chunkSize) {
  chunks.push({
    json: { 
      chunk: document.slice(i, i + chunkSize),
      chunkIndex: Math.floor(i / chunkSize)
    }
  });
}

return chunks;
```

---

## Prompt Engineering en n8n

### Templates con Variables

```javascript
// Code Node para construir prompts
const systemPrompt = `Eres ${$json.personality}.
Tu objetivo es ${$json.objective}.
Sigue estas reglas:
${$json.rules.map((r, i) => `${i+1}. ${r}`).join('\n')}`;

const userPrompt = $json.userMessage;

return [{
  json: {
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ]
  }
}];
```

### Few-shot Examples

```javascript
const fewShotExamples = [
  { input: "Hola", output: "¡Hola! ¿En qué puedo ayudarte?" },
  { input: "Precio de X", output: "El producto X cuesta $99. ¿Te gustaría más información?" }
];

const promptWithExamples = `Responde como un asistente de ventas.

Ejemplos:
${fewShotExamples.map(e => `Usuario: ${e.input}\nAsistente: ${e.output}`).join('\n\n')}

Usuario: ${$json.userMessage}
Asistente:`;
```

---

## Manejo de Respuestas

### Parsing JSON

```javascript
// El LLM devuelve JSON stringificado
try {
  const parsed = JSON.parse($json.response);
  return [{ json: parsed }];
} catch (e) {
  // Intentar extraer JSON del texto
  const jsonMatch = $json.response.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    return [{ json: JSON.parse(jsonMatch[0]) }];
  }
  throw new Error('Failed to parse LLM response as JSON');
}
```

### Structured Output (OpenAI)

```javascript
// Configurar en OpenAI node
{
  "response_format": { "type": "json_object" }
}

// En el prompt, especificar formato esperado
```

---

## Consideraciones de Costo

### Rate Limiting

```
Input Items → Split In Batches (5) → LLM → Wait (1s) → Loop
```

### Caching de Embeddings

```javascript
// Guardar embeddings en DB para no recalcular
const cachedEmbedding = await getFromCache($json.textHash);
if (cachedEmbedding) {
  return [{ json: { embedding: cachedEmbedding } }];
}
// Si no existe, generar y guardar
```

### Selección de Modelo

| Tarea | Modelo Recomendado | Costo |
|-------|-------------------|-------|
| Clasificación simple | GPT-3.5 / Claude Haiku | Bajo |
| Análisis complejo | GPT-4 / Claude Sonnet | Medio |
| Razonamiento avanzado | GPT-4-turbo / Claude Opus | Alto |
| Embeddings | text-embedding-3-small | Muy bajo |

---

## Debugging AI Workflows

1. **Log prompts y responses**: Guardar para análisis
2. **Temperature = 0**: Para reproducibilidad en tests
3. **Execution history**: Revisar outputs de cada paso
4. **Token counting**: Monitorear uso

```javascript
// Logging estructurado
console.log(JSON.stringify({
  timestamp: new Date().toISOString(),
  prompt: $json.prompt.substring(0, 200),
  responseLength: $json.response.length,
  model: 'gpt-4',
  tokens: $json.usage
}, null, 2));
```
