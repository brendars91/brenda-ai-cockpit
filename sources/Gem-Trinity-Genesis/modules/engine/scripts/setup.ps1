# ============================================
# AGCCE Ultra - Script de Instalación
# ============================================
# Ejecutar: .\scripts\setup.ps1
# Requisitos: PowerShell 5.1+

param(
    [switch]$SkipPython,
    [switch]$SkipDocker,
    [switch]$SkipSnyk,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$script:errors = @()
$script:warnings = @()

# =====================
# FUNCIONES AUXILIARES
# =====================

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "[*] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
    $script:warnings += $Message
}

function Write-Error {
    param([string]$Message)
    Write-Host "[X] $Message" -ForegroundColor Red
    $script:errors += $Message
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# =====================
# VERIFICACIONES
# =====================

Write-Header "AGCCE Ultra - Instalador v2.5"

Write-Host "Este script verificara e instalara los requisitos para AGCCE Ultra."
Write-Host "Presiona Ctrl+C para cancelar en cualquier momento."
Write-Host ""

# --- Python ---
if (-not $SkipPython) {
    Write-Step "Verificando Python..."
    
    if (Test-Command "python") {
        $pythonVersion = python --version 2>&1
        Write-Success "Python encontrado: $pythonVersion"
        
        # Verificar versión mínima (3.10)
        $versionMatch = [regex]::Match($pythonVersion, "(\d+)\.(\d+)")
        if ($versionMatch.Success) {
            $major = [int]$versionMatch.Groups[1].Value
            $minor = [int]$versionMatch.Groups[2].Value
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
                Write-Warning "Se recomienda Python 3.10+. Tu version: $pythonVersion"
            }
        }
    } else {
        Write-Error "Python no encontrado. Instala desde: https://www.python.org/downloads/"
    }
    
    # Verificar pip
    if (Test-Command "pip") {
        Write-Success "pip encontrado"
    } else {
        Write-Warning "pip no encontrado. Ejecuta: python -m ensurepip"
    }
}

# --- Git ---
Write-Step "Verificando Git..."
if (Test-Command "git") {
    $gitVersion = git --version
    Write-Success "Git encontrado: $gitVersion"
} else {
    Write-Error "Git no encontrado. Instala desde: https://git-scm.com/downloads"
}

# --- Docker ---
if (-not $SkipDocker) {
    Write-Step "Verificando Docker..."
    if (Test-Command "docker") {
        try {
            $dockerVersion = docker --version
            Write-Success "Docker encontrado: $dockerVersion"
            
            # Verificar si Docker está corriendo
            $dockerInfo = docker info 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Docker Desktop esta corriendo"
            } else {
                Write-Warning "Docker instalado pero no esta corriendo. Inicia Docker Desktop."
            }
        } catch {
            Write-Warning "Docker instalado pero no responde"
        }
    } else {
        Write-Warning "Docker no encontrado. Opcional pero recomendado."
        Write-Host "    Instala desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Gray
    }
}

# --- Snyk ---
if (-not $SkipSnyk) {
    Write-Step "Verificando Snyk CLI..."
    if (Test-Command "snyk") {
        Write-Success "Snyk CLI encontrado"
        
        # Verificar autenticación
        $snykAuth = snyk auth check 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Snyk autenticado"
        } else {
            Write-Warning "Snyk no autenticado. Ejecuta: snyk auth"
        }
    } else {
        Write-Warning "Snyk CLI no encontrado. Opcional para escaneos de seguridad."
        Write-Host "    Instala con: npm install -g snyk" -ForegroundColor Gray
    }
}

# =====================
# ESTRUCTURA DE CARPETAS
# =====================

Write-Header "Verificando Estructura de Carpetas"

$folders = @(
    "logs",
    "plans",
    "evidence",
    "config",
    "scripts",
    "dashboard",
    "templates",
    "schemas",
    "n8n",
    "documentacion",
    ".agent/rules",
    ".agent/workflows"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Success "Creada carpeta: $folder"
    } else {
        if ($Verbose) {
            Write-Host "    [i] Carpeta existe: $folder" -ForegroundColor Gray
        }
    }
}

Write-Success "Estructura de carpetas verificada"

# =====================
# ENTORNO VIRTUAL
# =====================

Write-Header "Configurando Entorno Python"

$venvPath = ".venv"

if (-not (Test-Path $venvPath)) {
    Write-Step "Creando entorno virtual..."
    python -m venv $venvPath
    Write-Success "Entorno virtual creado: $venvPath"
} else {
    Write-Success "Entorno virtual existe: $venvPath"
}

# Activar entorno virtual
$activateScript = "$venvPath\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Step "Para activar el entorno virtual, ejecuta:"
    Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}

# Instalar dependencias
if (Test-Path "requirements.txt") {
    Write-Step "Instalando dependencias..."
    & "$venvPath\Scripts\pip.exe" install -r requirements.txt -q
    Write-Success "Dependencias instaladas"
}

# =====================
# CONFIGURACIÓN INICIAL
# =====================

Write-Header "Configuracion Inicial"

# Crear bundle.json si no existe
$bundlePath = "config/bundle.json"
$bundleTemplatePath = "config/bundle.template.json"

if (-not (Test-Path $bundlePath)) {
    if (Test-Path $bundleTemplatePath) {
        Copy-Item $bundleTemplatePath $bundlePath
        Write-Success "Creado bundle.json desde template"
    } else {
        Write-Warning "No existe bundle.json. Copia bundle.template.json manualmente."
    }
} else {
    Write-Success "bundle.json existe"
}

# Crear n8n_webhooks.json si no existe
$webhooksPath = "config/n8n_webhooks.json"
if (-not (Test-Path $webhooksPath)) {
    $webhooksTemplate = @{
        "PLAN_VALIDATED" = "https://TU-N8N.com/webhook/plan-validated"
        "EXECUTION_ERROR" = "https://TU-N8N.com/webhook/execution-error"
        "EVIDENCE_READY" = "https://TU-N8N.com/webhook/evidence-ready"
        "SECURITY_BREACH_ATTEMPT" = "https://TU-N8N.com/webhook/security-alert"
        "HEARTBEAT" = "https://TU-N8N.com/webhook/heartbeat"
        "_comment" = "Reemplaza TU-N8N.com con tu instancia de n8n"
    }
    $webhooksTemplate | ConvertTo-Json | Out-File $webhooksPath -Encoding UTF8
    Write-Success "Creado n8n_webhooks.json (edita con tus URLs)"
}

# =====================
# VERIFICACIÓN FINAL
# =====================

Write-Header "Resumen de Instalacion"

if ($script:errors.Count -gt 0) {
    Write-Host "ERRORES ($($script:errors.Count)):" -ForegroundColor Red
    foreach ($error in $script:errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host ""
}

if ($script:warnings.Count -gt 0) {
    Write-Host "ADVERTENCIAS ($($script:warnings.Count)):" -ForegroundColor Yellow
    foreach ($warning in $script:warnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($script:errors.Count -eq 0) {
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "  INSTALACION COMPLETADA EXITOSAMENTE" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximos pasos:" -ForegroundColor Cyan
    Write-Host "  1. Activa el entorno virtual: .\.venv\Scripts\Activate.ps1"
    Write-Host "  2. Inicia el CLI interactivo: python scripts\agcce_cli.py"
    Write-Host "  3. O inicia el dashboard: python scripts\dashboard_server.py"
    Write-Host ""
} else {
    Write-Host "La instalacion tiene errores. Resuelve los problemas indicados arriba." -ForegroundColor Red
}
