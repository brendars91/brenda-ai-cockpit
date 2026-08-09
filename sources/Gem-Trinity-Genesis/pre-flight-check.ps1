# ========================================
# Pre-Flight Check - PowerShell Version
# Verificaciones antes del deployment
# ========================================

param(
    [switch]$SkipRemote = $false
)

Write-Host "🔍 Pre-Flight Check - Gem Trinity Genesis" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ERRORS = 0
$WARNINGS = 0

function Check-Pass {
    param([string]$Message)
    Write-Host "✅ PASS - $Message" -ForegroundColor Green
}

function Check-Warn {
    param([string]$Message)
    Write-Host "⚠️  WARN - $Message" -ForegroundColor Yellow
    $script:WARNINGS++
}

function Check-Fail {
    param([string]$Message)
    Write-Host "❌ FAIL - $Message" -ForegroundColor Red
    $script:ERRORS++
}

# 1. Verificar archivos necesarios
Write-Host "📦 Verificando archivos necesarios..."
if (Test-Path "Dockerfile") { Check-Pass "Dockerfile existe" } else { Check-Fail "Dockerfile no encontrado" }
if (Test-Path "docker-compose.yml") { Check-Pass "docker-compose.yml existe" } else { Check-Fail "docker-compose.yml no encontrado" }
if (Test-Path ".dockerignore") { Check-Pass ".dockerignore existe" } else { Check-Warn ".dockerignore no encontrado" }
if (Test-Path ".env.production") { Check-Pass ".env.production existe" } else { Check-Fail ".env.production no encontrado" }
if (Test-Path "requirements.txt") { Check-Pass "requirements.txt existe" } else { Check-Fail "requirements.txt no encontrado" }

Write-Host ""

# 2. Verificar .env.production
Write-Host "🔑 Verificando variables de entorno..."
if (Test-Path ".env.production") {
    $envContent = Get-Content ".env.production" -Raw
    
    if ($envContent -match "your-.*-here") {
        Check-Fail ".env.production contiene valores placeholder (your-xxx-here)"
    } else {
        Check-Pass ".env.production parece configurado"
    }
    
    if ($envContent -match "GOOGLE_API_KEY=") { Check-Pass "GOOGLE_API_KEY definida" } else { Check-Fail "GOOGLE_API_KEY faltante" }
    if ($envContent -match "GITHUB_TOKEN=") { Check-Pass "GITHUB_TOKEN definida" } else { Check-Warn "GITHUB_TOKEN faltante (opcional)" }
    if ($envContent -match "N8N_ENCRYPTION_KEY=") { Check-Pass "N8N_ENCRYPTION_KEY definida" } else { Check-Warn "N8N_ENCRYPTION_KEY faltante" }
}

Write-Host ""

# 3. Verificar SSH
Write-Host "🔐 Verificando conectividad SSH..."
$SSH_KEY = "$env:USERPROFILE\.ssh\id_rsa"
$REMOTE_HOST = "100.69.240.73"

if (Test-Path $SSH_KEY) {
    Check-Pass "Clave SSH existe: $SSH_KEY"
    
    if (-not $SkipRemote) {
        try {
            $sshTest = ssh -i $SSH_KEY -o ConnectTimeout=5 ubuntu@$REMOTE_HOST "echo OK" 2>$null
            if ($sshTest -eq "OK") {
                Check-Pass "Conexión SSH exitosa a $REMOTE_HOST"
            } else {
                Check-Fail "No se puede conectar vía SSH a $REMOTE_HOST (¿Tailscale activo?)"
            }
        } catch {
            Check-Fail "Error al probar conexión SSH"
        }
    }
} else {
    Check-Fail "Clave SSH no encontrada: $SSH_KEY"
}

Write-Host ""

# 4. Verificar Docker local
Write-Host "🐳 Verificando Docker local..."
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Check-Pass "Docker instalado localmente"
} else {
    Check-Warn "Docker no instalado localmente (no es requisito para deployment remoto)"
}

Write-Host ""

# 5. Verificar estructura de directorios
Write-Host "📁 Verificando estructura de proyecto..."
if (Test-Path "local-watcher" -PathType Container) { Check-Pass "Directorio local-watcher existe" } else { Check-Fail "Directorio local-watcher faltante" }
if (Test-Path "modules" -PathType Container) { Check-Pass "Directorio modules existe" } else { Check-Fail "Directorio modules faltante" }
if (Test-Path "config" -PathType Container) { Check-Pass "Directorio config existe" } else { Check-Warn "Directorio config faltante" }
if (Test-Path "resources" -PathType Container) { Check-Pass "Directorio resources existe" } else { Check-Warn "Directorio resources faltante" }
if (Test-Path "artifacts" -PathType Container) { Check-Pass "Directorio artifacts existe" } else { Check-Warn "Directorio artifacts faltante (se creará)" }

Write-Host ""

# 6. Verificar frontend
Write-Host "🎨 Verificando frontend..."
if (Test-Path "frontend" -PathType Container) {
    Check-Pass "Directorio frontend existe"
    
    if (Test-Path "frontend\.env.production") {
        $frontendEnv = Get-Content "frontend\.env.production" -Raw
        if ($frontendEnv -match "100\.69\.240\.73:8000") {
            Check-Pass "Frontend configurado para backend OCI"
        } else {
            Check-Warn "Frontend NO apunta al backend OCI"
        }
    } else {
        Check-Warn "frontend\.env.production no existe"
    }
} else {
    Check-Warn "Directorio frontend no encontrado"
}

Write-Host ""

# 7. Verificar servidor remoto
if (-not $SkipRemote) {
    Write-Host "🖥️  Verificando servidor remoto..."
    try {
        $dockerCheck = ssh -i $SSH_KEY ubuntu@$REMOTE_HOST "command -v docker" 2>$null
        if ($dockerCheck) {
            Check-Pass "Docker instalado en servidor remoto"
        } else {
            Check-Fail "Docker NO instalado en servidor remoto"
        }
    } catch {
        Check-Warn "No se pudo verificar Docker en servidor remoto"
    }
}

Write-Host ""

# Resumen
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 Resumen del Pre-Flight Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($ERRORS -eq 0 -and $WARNINGS -eq 0) {
    Write-Host "✅ TODO LISTO PARA DEPLOYMENT" -ForegroundColor Green
    Write-Host ""
    Write-Host "Puedes ejecutar:" -ForegroundColor Yellow
    Write-Host "  .\deploy-to-oci.ps1" -ForegroundColor White
    exit 0
} elseif ($ERRORS -eq 0) {
    Write-Host "⚠️  $WARNINGS ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Puedes continuar con deployment, pero revisa las advertencias."
    Write-Host ""
    $response = Read-Host "¿Continuar con deployment? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Ejecutando deployment..." -ForegroundColor Cyan
        & .\deploy-to-oci.ps1
    } else {
        Write-Host "Deployment cancelado." -ForegroundColor Yellow
    }
    exit 0
} else {
    Write-Host "❌ $ERRORS ERRORES CRÍTICOS" -ForegroundColor Red
    Write-Host "⚠️  $WARNINGS ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Resuelve los errores antes de continuar con el deployment." -ForegroundColor Red
    exit 1
}
