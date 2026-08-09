# 02. Guía de Instalación

## 📋 Requisitos Previos

### Software Requerido

| Software | Versión Mínima | Propósito |
|----------|----------------|-----------|
| **Python** | 3.7+ | Runtime de scripts |
| **Git** | 2.0+ | Control de versiones |
| **Snyk CLI** | 1.0+ | Análisis de seguridad |
| **n8n** | 1.0+ | Automatización (opcional) |

### Verificar Instalaciones

```powershell
# Python
python --version

# Git
git --version

# Snyk (si está instalado)
snyk --version
```

---

## 🚀 Instalación Paso a Paso

### 1. Clonar o Descargar el Proyecto

```powershell
# Si tienes Git configurado
git clone <url-del-repositorio>

# O descarga el ZIP y extrae en tu ubicación deseada
```

### 2. Inicializar Repositorio Git

```powershell
cd "Agente Copilot Engine"
git init
git add .
git commit -m "Initial commit"
```

### 3. Instalar Hook de Pre-Commit

```powershell
python scripts/pre_commit_hook.py --install
```

Esto crea `.git/hooks/pre-commit` que ejecutará validaciones automáticas.

### 4. Configurar Snyk (Opcional pero Recomendado)

```powershell
# Autenticar con Snyk
snyk auth

# O usar el CLI existente
# El proyecto busca Snyk en: C:\Users\ASUS\AppData\Local\snyk\vscode-cli\snyk-win.exe
```

### 5. Verificar Instalación

```powershell
# Validar un plan de ejemplo
python scripts/validate_plan.py examples/example_plan_auth_fix.json

# Ver estado del RAG indexer
python scripts/rag_indexer.py --status

# Ver estado de webhooks
python scripts/event_dispatcher.py status
```

---

## ⚙️ Configuración

### Archivo Principal: `config/bundle.json`

```json
{
  "bundle_id": "BNDL-AGCCE-ULTRA-V2-FINAL",
  "version": "2.0.0-ULTRA-FINAL",
  "governance": {
    "hitl": "mandatory_on_write",
    "security_gate": "Snyk_Hard_Block"
  }
}
```

### Configurar Webhooks n8n: `config/n8n_webhooks.json`

```json
{
  "PLAN_VALIDATED": "https://tu-n8n.com/webhook/agcce-plan-validated",
  "EXECUTION_ERROR": "https://tu-n8n.com/webhook/agcce-execution-error",
  "EVIDENCE_READY": "https://tu-n8n.com/webhook/agcce-evidence-ready"
}
```

O usar el configurador interactivo:

```powershell
python scripts/event_dispatcher.py configure
```

---

## 📦 Importar Workflows n8n

### 1. Abrir tu instancia n8n

### 2. Importar cada workflow desde `n8n/`

- `evidence_report_sender.json`
- `execution_error_handler.json`
- `security_alert_handler.json`

### 3. Activar los workflows

### 4. Copiar las URLs de webhook a `config/n8n_webhooks.json`

### 5. Verificar conexión

```powershell
python scripts/event_dispatcher.py healthcheck
```

---

## 🖥️ Iniciar Dashboard

```powershell
python scripts/dashboard_server.py --port 8888
```

Abrir en navegador: `http://localhost:8888`

---

## ✅ Verificación Final

```powershell
# 1. Indexar codebase
python scripts/rag_indexer.py

# 2. Generar plan de prueba
python scripts/plan_generator.py --objective "Plan de prueba"

# 3. Validar plan generado
python scripts/validate_plan.py plans/PLAN-XXXXXXXX.json

# 4. Iniciar dashboard
python scripts/dashboard_server.py --port 8888
```

Si todos los comandos funcionan sin errores, la instalación está completa.
