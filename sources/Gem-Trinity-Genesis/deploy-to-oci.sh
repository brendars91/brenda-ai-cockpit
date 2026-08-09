#!/bin/bash

# ========================================
# Deploy Script - Gem Trinity Genesis
# Deployment a Oracle Cloud via Tailscale
# ========================================

set -e  # Exit on error

echo "🚀 Gem Trinity Genesis - Deployment a OCI"
echo "=========================================="

# Variables
REMOTE_USER="ubuntu"
REMOTE_HOST="100.69.240.73"
SSH_KEY="$HOME/.ssh/id_rsa"
REMOTE_DIR="/home/ubuntu/gem-trinity-genesis"
LOCAL_DIR="."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función de log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verificar conexión SSH
log_info "Verificando conexión SSH..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo '✅ Conexión exitosa'" 2>/dev/null; then
    log_error "No se puede conectar al servidor. Verifica Tailscale y SSH."
    exit 1
fi

# 2. Crear directorio remoto
log_info "Creando directorio en servidor..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_DIR"

# 3. Copiar archivos (excluir node_modules, .git, etc.)
log_info "Copiando archivos al servidor..."
rsync -avz --progress \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.next' \
    --exclude 'logs/*.log' \
    --exclude '.env' \
    -e "ssh -i $SSH_KEY" \
    "$LOCAL_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

# 4. Copiar .env.production como .env
log_info "Configurando variables de entorno..."
scp -i "$SSH_KEY" "$LOCAL_DIR/.env.production" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/.env"

log_warn "⚠️  IMPORTANTE: Edita el archivo .env en el servidor con tus API keys reales"
echo "   Ejecuta: ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'nano $REMOTE_DIR/.env'"
echo ""
read -p "¿Has configurado el archivo .env con tus API keys? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warn "Deployment pausado. Configura .env y vuelve a ejecutar este script."
    exit 0
fi

# 5. Detener contenedores existentes (si existen)
log_info "Deteniendo contenedores existentes..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_DIR && docker-compose down" || log_warn "No hay contenedores previos"

# 6. Build y deploy con docker-compose
log_info "Construyendo y levantando servicios..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" << EOF
    cd $REMOTE_DIR
    docker-compose build --no-cache gem-backend
    docker-compose up -d
    
    echo ""
    echo "✅ Servicios levantados:"
    docker-compose ps
EOF

# 7. Verificar health checks
log_info "Esperando health checks (30s)..."
sleep 30

ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" << EOF
    echo ""
    echo "🔍 Estado de servicios:"
    docker-compose ps
    
    echo ""
    echo "📊 Logs recientes del backend:"
    docker-compose logs --tail=20 gem-backend
EOF

# 8. Verificar endpoint
log_info "Verificando endpoint del backend..."
if curl -f http://100.69.240.73:8000/api/status > /dev/null 2>&1; then
    log_info "✅ Backend respondiendo correctamente"
else
    log_error "❌ Backend no responde. Revisa los logs."
fi

echo ""
echo "=========================================="
echo "✅ Deployment completado"
echo "=========================================="
echo ""
echo "📍 URLs de acceso (vía Tailscale):"
echo "   Backend:  http://100.69.240.73:8000"
echo "   n8n:      http://100.69.240.73:5678"
echo "   Ollama:   http://100.69.240.73:11434"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs:       ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker-compose logs -f gem-backend'"
echo "   Reiniciar:      ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker-compose restart gem-backend'"
echo "   Detener todo:   ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker-compose down'"
echo ""
