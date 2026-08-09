# AGCCE Ultra - Instrucciones para Compartir

Este documento explica cómo preparar el proyecto para compartirlo en GitHub de forma segura.

## 📋 Checklist Antes de Compartir

### 1. Archivos a EXCLUIR (ya en .gitignore)
- [ ] `logs/*.jsonl` - Contienen tu telemetría
- [ ] `config/n8n_webhooks.json` - Contiene tus URLs de webhook
- [ ] `.env` - Variables de entorno con secretos
- [ ] `evidence/` - Evidencia de tus ejecuciones
- [ ] `.venv/` o `venv/` - Entorno virtual

### 2. Archivos a REVISAR antes de commit
- [ ] `config/bundle.json` - Verificar que no tenga API keys
- [ ] Cualquier archivo `.json` de configuración

### 3. Archivos INCLUIDOS para compartir
- [x] Todos los scripts en `scripts/`
- [x] Templates en `templates/`
- [x] Schemas en `schemas/`
- [x] Dashboard en `dashboard/`
- [x] Documentación en `documentacion/`
- [x] Workflows en `.agent/workflows/`
- [x] Workflows n8n en `n8n/`

## 🚀 Pasos para Subir a GitHub

```powershell
# 1. Verificar que .gitignore está correcto
Get-Content .gitignore

# 2. Ver qué archivos se van a subir
git status

# 3. Si todo está bien, crear repositorio en GitHub y subir
git remote add origin https://github.com/TU_USUARIO/agcce-ultra.git
git branch -M main
git push -u origin main
```

## 📝 Descripción Sugerida para GitHub

```
AGCCE Ultra v2.5 - Antigravity Core Copilot Engine

Un motor de copiloto de IA determinístico con:
- 🔍 RAG Semántico con indexación incremental
- 🤖 Self-Correction Loop (auto-corrección)
- 🛡️ Gate Snyk + Secrets Detector
- 📊 Dashboard de observabilidad
- 🔔 Integración n8n (webhooks)
- 📋 Audit Trail inmutable
- 🎯 CLI Interactivo

Requisitos: Python 3.10+, Git, Snyk CLI (opcional), n8n (opcional)
```

## 🏷️ Tags Sugeridos

```
ai, copilot, rag, semantic-search, automation, security, observability, n8n
```
