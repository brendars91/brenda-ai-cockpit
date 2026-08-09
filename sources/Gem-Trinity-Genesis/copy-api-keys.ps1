# ========================================
# Copy API Keys Helper
# Copia valores de .env a .env.production
# ========================================

Write-Host "🔑 Copiador de API Keys" -ForegroundColor Cyan
Write-Host "De: .env (local) → A: .env.production" -ForegroundColor Cyan
Write-Host ""

# Verificar que existe .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ No se encontró archivo .env" -ForegroundColor Red
    Write-Host "   Crea primero un .env con tus API keys" -ForegroundColor Yellow
    exit 1
}

# Leer .env
$envContent = Get-Content ".env" -Raw

# Extraer valores (simple regex)
$googleApiKey = ""
$githubToken = ""
$snykToken = ""
$composioKey = ""

if ($envContent -match "GOOGLE_API_KEY=([^\r\n]+)") {
    $googleApiKey = $Matches[1]
}

if ($envContent -match "GITHUB_TOKEN=([^\r\n]+)") {
    $githubToken = $Matches[1]
}

if ($envContent -match "SNYK_TOKEN=([^\r\n]+)") {
    $snykToken = $Matches[1]
}

if ($envContent -match "COMPOSIO_API_KEY=([^\r\n]+)") {
    $composioKey = $Matches[1]
}

# Generar N8N key si no existe
$n8nKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Mostrar valores encontrados
Write-Host "Valores encontrados en .env:" -ForegroundColor Green
Write-Host "  GOOGLE_API_KEY: $(if ($googleApiKey) { '✅ Encontrada' } else { '❌ No encontrada' })"
Write-Host "  GITHUB_TOKEN: $(if ($githubToken) { '✅ Encontrada' } else { '⚠️  No encontrada (opcional)' })"
Write-Host "  SNYK_TOKEN: $(if ($snykToken) { '✅ Encontrada' } else { '⚠️  No encontrada (opcional)' })"
Write-Host "  COMPOSIO_API_KEY: $(if ($composioKey) { '✅ Encontrada' } else { '⚠️  No encontrada (opcional)' })"
Write-Host "  N8N_ENCRYPTION_KEY: 🔐 Generada automáticamente"
Write-Host ""

if (-not $googleApiKey) {
    Write-Host "❌ GOOGLE_API_KEY es obligatoria" -ForegroundColor Red
    exit 1
}

# Crear .env.production
$productionContent = @"
# ========================================
# .env.production - Oracle Cloud Infrastructure
# Generado automáticamente desde .env
# ========================================

# ============ Google AI ============
GOOGLE_API_KEY=$googleApiKey
GOOGLE_MODEL=gemini-2.0-flash-exp

# ============ GitHub ============
GITHUB_TOKEN=$githubToken
GITHUB_REPO=brendars91/Gem-Trinity-Genesis

# ============ Snyk Security ============
SNYK_TOKEN=$snykToken

# ============ Composio/RUBE ============
COMPOSIO_API_KEY=$composioKey

# ============ n8n ============
N8N_ENCRYPTION_KEY=$n8nKey

# ============ Application ============
ENVIRONMENT=production
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# ============ URLs (Tailscale) ============
BACKEND_URL=http://100.69.240.73:8000
FRONTEND_URL=http://100.69.240.73:3000
N8N_URL=http://100.69.240.73:5678
OLLAMA_URL=http://100.69.240.73:11434
"@

# Guardar
Set-Content -Path ".env.production" -Value $productionContent

Write-Host "✅ Archivo .env.production creado exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Revisa el archivo para confirmar:" -ForegroundColor Yellow
Write-Host "   notepad .env.production" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Siguiente paso:" -ForegroundColor Cyan
Write-Host "   .\pre-flight-check.ps1" -ForegroundColor White
