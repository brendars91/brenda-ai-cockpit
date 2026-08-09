#!/bin/bash

# ========================================
# Pre-Flight Check - Gem Trinity Genesis
# Verificaciones antes del deployment
# ========================================

echo "🔍 Pre-Flight Check - Gem Trinity Genesis"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✅ PASS${NC} - $1"
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC} - $1"
    ((WARNINGS++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC} - $1"
    ((ERRORS++))
}

# 1. Verificar archivos necesarios
echo "📦 Verificando archivos necesarios..."
[ -f "Dockerfile" ] && check_pass "Dockerfile existe" || check_fail "Dockerfile no encontrado"
[ -f "docker-compose.yml" ] && check_pass "docker-compose.yml existe" || check_fail "docker-compose.yml no encontrado"
[ -f ".dockerignore" ] && check_pass ".dockerignore existe" || check_warn ".dockerignore no encontrado"
[ -f ".env.production" ] && check_pass ".env.production existe" || check_fail ".env.production no encontrado"
[ -f "requirements.txt" ] && check_pass "requirements.txt existe" || check_fail "requirements.txt no encontrado"

echo ""

# 2. Verificar .env.production tiene valores reales
echo "🔑 Verificando variables de entorno..."
if [ -f ".env.production" ]; then
    if grep -q "your-.*-here" .env.production; then
        check_fail ".env.production contiene valores placeholder (your-xxx-here)"
    else
        check_pass ".env.production parece configurado"
    fi
    
    # Verificar claves importantes
    grep -q "GOOGLE_API_KEY=" .env.production && check_pass "GOOGLE_API_KEY definida" || check_fail "GOOGLE_API_KEY faltante"
    grep -q "GITHUB_TOKEN=" .env.production && check_pass "GITHUB_TOKEN definida" || check_warn "GITHUB_TOKEN faltante (opcional)"
    grep -q "N8N_ENCRYPTION_KEY=" .env.production && check_pass "N8N_ENCRYPTION_KEY definida" || check_warn "N8N_ENCRYPTION_KEY faltante"
fi

echo ""

# 3. Verificar SSH
echo "🔐 Verificando conectividad SSH..."
SSH_KEY="$HOME/.ssh/id_rsa"
REMOTE_HOST="100.69.240.73"

if [ -f "$SSH_KEY" ]; then
    check_pass "Clave SSH existe: $SSH_KEY"
    
    # Test conexión
    if ssh -i "$SSH_KEY" -o ConnectTimeout=5 ubuntu@$REMOTE_HOST "echo OK" 2>/dev/null | grep -q "OK"; then
        check_pass "Conexión SSH exitosa a $REMOTE_HOST"
    else
        check_fail "No se puede conectar vía SSH a $REMOTE_HOST (¿Tailscale activo?)"
    fi
else
    check_fail "Clave SSH no encontrada: $SSH_KEY"
fi

echo ""

# 4. Verificar Docker local (opcional)
echo "🐳 Verificando Docker local..."
if command -v docker &> /dev/null; then
    check_pass "Docker instalado localmente"
    
    # Test build local (dry-run)
    if docker build --dry-run -f Dockerfile . &> /dev/null 2>&1; then
        check_pass "Dockerfile sintácticamente válido"
    else
        check_warn "No se pudo verificar sintaxis de Dockerfile (¿BuildKit disponible?)"
    fi
else
    check_warn "Docker no instalado localmente (no es requisito para deployment remoto)"
fi

echo ""

# 5. Verificar estructura de directorios
echo "📁 Verificando estructura de proyecto..."
[ -d "local-watcher" ] && check_pass "Directorio local-watcher existe" || check_fail "Directorio local-watcher faltante"
[ -d "modules" ] && check_pass "Directorio modules existe" || check_fail "Directorio modules faltante"
[ -d "config" ] && check_pass "Directorio config existe" || check_warn "Directorio config faltante"
[ -d "resources" ] && check_pass "Directorio resources existe" || check_warn "Directorio resources faltante"
[ -d "artifacts" ] && check_pass "Directorio artifacts existe" || check_warn "Directorio artifacts faltante (se creará automáticamente)"

echo ""

# 6. Verificar frontend (si aplica)
echo "🎨 Verificando frontend..."
if [ -d "frontend" ]; then
    check_pass "Directorio frontend existe"
    
    if [ -f "frontend/.env.production" ]; then
        if grep -q "100.69.240.73:8000" frontend/.env.production; then
            check_pass "Frontend configurado para backend OCI"
        else
            check_warn "Frontend NO apunta al backend OCI (revisar frontend/.env.production)"
        fi
    else
        check_warn "frontend/.env.production no existe"
    fi
else
    check_warn "Directorio frontend no encontrado (frontend separado?)"
fi

echo ""

# 7. Verificar servidor remoto (Docker instalado)
echo "🖥️  Verificando servidor remoto..."
if ssh -i "$SSH_KEY" ubuntu@$REMOTE_HOST "command -v docker" &> /dev/null; then
    check_pass "Docker instalado en servidor remoto"
else
    check_fail "Docker NO instalado en servidor remoto"
fi

if ssh -i "$SSH_KEY" ubuntu@$REMOTE_HOST "command -v docker-compose" &> /dev/null; then
    check_pass "docker-compose instalado en servidor remoto"
else
    check_warn "docker-compose NO instalado (se intentará con 'docker compose')"
fi

echo ""

# Resumen
echo "=========================================="
echo "📊 Resumen del Pre-Flight Check"
echo "=========================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ TODO LISTO PARA DEPLOYMENT${NC}"
    echo ""
    echo "Puedes ejecutar:"
    echo "  ./deploy-to-oci.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS ADVERTENCIAS${NC}"
    echo ""
    echo "Puedes continuar con deployment, pero revisa las advertencias."
    echo ""
    read -p "¿Continuar con deployment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Ejecutando deployment..."
        ./deploy-to-oci.sh
    else
        echo "Deployment cancelado."
    fi
    exit 0
else
    echo -e "${RED}❌ $ERRORS ERRORES CRÍTICOS${NC}"
    echo -e "${YELLOW}⚠️  $WARNINGS ADVERTENCIAS${NC}"
    echo ""
    echo "Resuelve los errores antes de continuar con el deployment."
    exit 1
fi
