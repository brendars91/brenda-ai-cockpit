# ========================================
# Deploy Script - Gem Trinity Genesis (PowerShell)
# Deployment a Oracle Cloud via Tailscale
# ========================================

param(
    [switch]$SkipEnvCheck = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Gem Trinity Genesis - Deployment a OCI" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Variables
$REMOTE_USER = "ubuntu"
$REMOTE_HOST = "100.69.240.73"
$SSH_KEY = "$env:USERPROFILE\.ssh\id_rsa"
$REMOTE_DIR = "/home/ubuntu/gem-trinity-genesis"
$LOCAL_DIR = "."

# Función de log
function Log-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Log-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Log-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 1. Verificar conexión SSH
Log-Info "Verificando conexión SSH..."
try {
    $testConnection = ssh -i $SSH_KEY -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo 'OK'" 2>$null
    if ($testConnection -eq "OK") {
        Log-Info "✅ Conexión SSH exitosa"
    } else {
        throw "Conexión fallida"
    }
} catch {
    Log-Error "No se puede conectar al servidor. Verifica Tailscale y SSH."
    exit 1
}

# 2. Crear directorio remoto
Log-Info "Creando directorio en servidor..."
ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_DIR"

# 3. Verificar archivo .env.production
if (-not (Test-Path ".env.production")) {
    Log-Error "No se encuentra .env.production. Créalo primero."
    exit 1
}

# 4. Copiar archivos con SCP (PowerShell alternativa a rsync)
Log-Info "Copiando archivos al servidor..."

# Lista de archivos/directorios a copiar
$itemsToCopy = @(
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    ".env.production",
    "requirements.txt",
    "Procfile",
    "runtime.txt",
    "pyproject.toml",
    "local-watcher",
    "modules",
    "config",
    "resources",
    "static",
    "artifacts"
)

foreach ($item in $itemsToCopy) {
    if (Test-Path $item) {
        Log-Info "Copiando: $item"
        scp -i $SSH_KEY -r $item "$REMOTE_USER@${REMOTE_HOST}:$REMOTE_DIR/" 2>$null
    } else {
        Log-Warn "Item no encontrado (omitido): $item"
    }
}

# 5. Copiar .env.production como .env
Log-Info "Configurando variables de entorno..."
scp -i $SSH_KEY ".env.production" "$REMOTE_USER@${REMOTE_HOST}:$REMOTE_DIR/.env"

if (-not $SkipEnvCheck) {
    Log-Warn "⚠️  IMPORTANTE: Debes editar el archivo .env en el servidor con tus API keys reales"
    Write-Host "   Ejecuta: ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'nano $REMOTE_DIR/.env'" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "¿Has configurado el archivo .env con tus API keys? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        Log-Warn "Deployment pausado. Configura .env y vuelve a ejecutar con -SkipEnvCheck"
        exit 0
    }
}

# 6. Detener contenedores existentes
Log-Info "Deteniendo contenedores existentes..."
ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_DIR && docker-compose down" 2>$null
if ($LASTEXITCODE -ne 0) {
    Log-Warn "No hay contenedores previos o docker-compose no disponible"
}

# 7. Build y deploy
Log-Info "Construyendo y levantando servicios..."
$deployScript = @"
cd $REMOTE_DIR
docker-compose build --no-cache gem-backend
docker-compose up -d

echo ''
echo '✅ Servicios levantados:'
docker-compose ps
"@

ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" $deployScript

# 8. Esperar health checks
Log-Info "Esperando health checks (30s)..."
Start-Sleep -Seconds 30

# 9. Status final
$statusScript = @"
cd $REMOTE_DIR
echo ''
echo '🔍 Estado de servicios:'
docker-compose ps

echo ''
echo '📊 Logs recientes del backend:'
docker-compose logs --tail=20 gem-backend
"@

ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" $statusScript

# 10. Verificar endpoint
Log-Info "Verificando endpoint del backend..."
try {
    $response = Invoke-WebRequest -Uri "http://100.69.240.73:8000/api/status" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Log-Info "✅ Backend respondiendo correctamente"
    }
} catch {
    Log-Error "❌ Backend no responde. Revisa los logs."
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Deployment completado" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 URLs de acceso (vía Tailscale):" -ForegroundColor Yellow
Write-Host "   Backend:  http://100.69.240.73:8000"
Write-Host "   n8n:      http://100.69.240.73:5678"
Write-Host "   Ollama:   http://100.69.240.73:11434"
Write-Host ""
Write-Host "📝 Comandos útiles:" -ForegroundColor Yellow
Write-Host "   Ver logs:       ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker-compose logs -f gem-backend'"
Write-Host "   Reiniciar:      ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker-compose restart gem-backend'"
Write-Host "   Detener todo:   ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker-compose down'"
Write-Host ""
