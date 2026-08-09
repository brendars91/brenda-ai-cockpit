---
description: Indexar codebase para busqueda semantica con RAG
---

# RAG Index Workflow

Indexa el proyecto para habilitar busqueda semantica de codigo.

## Comando Rapido
// turbo
```powershell
python scripts/rag_indexer.py
```

## Verificar Estado
// turbo
```powershell
python scripts/rag_indexer.py --status
```

## Forzar Re-indexacion
```powershell
python scripts/rag_indexer.py --reindex
```

## Busqueda Semantica

Despues de indexar, usa smart-coding-mcp para buscar:

```
Tool: mcp_smart-coding-mcp_a_semantic_search
Params:
  query: "tu pregunta sobre el codigo"
  maxResults: 5
```

## Cuando Usar

1. **Inicio de proyecto** - Indexar todo el codebase
2. **Despues de cambios grandes** - Re-indexar con --reindex
3. **Antes de generar planes** - Asegurar indice actualizado
