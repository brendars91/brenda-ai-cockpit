# n8n MCP Usage Rules

Tienes **dos MCPs de n8n** configurados para máxima eficiencia:

## n8n-native (Servidor nativo)
Servidor MCP integrado en n8n via supergateway.
- **Uso:** Ejecutar workflows existentes
- Herramientas limitadas

## n8n-mcp ⭐ (czlonkowski - RECOMENDADO)
MCP avanzado con **20 herramientas** para desarrollo completo de workflows.

### Core Tools (7)
| Tool | Descripción |
|------|-------------|
| `search_nodes` | Buscar entre 1,084 nodos |
| `get_node` | Obtener docs de cualquier nodo |
| `validate_node` | Validar configuración de nodo |
| `validate_workflow` | Validar workflow completo |
| `search_templates` | Buscar templates de n8n.io |
| `get_template` | Obtener JSON de template |
| `tools_documentation` | Documentación de herramientas |

### Workflow Management (10)
| Tool | Descripción |
|------|-------------|
| `n8n_create_workflow` | Crear workflows |
| `n8n_get_workflow` | Obtener workflow |
| `n8n_update_full_workflow` | Actualizar completo |
| `n8n_update_partial_workflow` | Actualizar parcialmente |
| `n8n_delete_workflow` | Eliminar workflow |
| `n8n_list_workflows` | Listar workflows |
| `n8n_validate_workflow` | Validar en n8n |
| `n8n_autofix_workflow` | Corregir errores automáticamente |
| `n8n_workflow_versions` | Gestionar versiones |
| `n8n_deploy_template` | Desplegar template de n8n.io |

### Execution (2)
| Tool | Descripción |
|------|-------------|
| `n8n_test_workflow` | Ejecutar/probar workflow |
| `n8n_executions` | Gestionar ejecuciones |

### System (1)
| Tool | Descripción |
|------|-------------|
| `n8n_health_check` | Verificar conectividad |

## Cuándo usar cada uno

| Tarea | MCP Recomendado |
|-------|-----------------|
| Ejecutar workflow existente | n8n-native |
| Crear nuevo workflow | **n8n-mcp** |
| Buscar nodos/documentación | **n8n-mcp** |
| Validar/corregir errores | **n8n-mcp** |
| Gestionar versiones | **n8n-mcp** |
| Desplegar templates | **n8n-mcp** |
