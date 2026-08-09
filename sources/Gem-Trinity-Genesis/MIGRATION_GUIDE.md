# 🚀 Guía de Migración: Railway → Oracle Cloud Infrastructure

## 📋 Resumen

Esta guía te ayudará a migrar tu backend de **Gem Trinity Genesis** desde Railway a tu servidor OCI con Docker Compose, aprovechando Tailscale para seguridad.

---

## ✅ Ventajas de esta Migración

1. **Ahorro de costos**: Sin pagar plan de Railway
2. **Control total**: Tu propia infraestructura
3. **Seguridad**: Red privada con Tailscale
4. **Integración local**: Backend, n8n y Ollama en el mismo stack
5. **Escalabilidad**: Puedes añadir más servicios fácilmente

---

## 📦 Archivos Creados

```
Gem-Trinity-Genesis/
├── Dockerfile                 # Imagen Docker del backend
├── docker-compose.yml         # Orquestación de servicios
├── .dockerignore             # Optimización de build
├── .env.production           # Template de variables de entorno
├── deploy-to-oci.ps1         # Script de deployment (Windows)
└── deploy-to-oci.sh          # Script de deployment (Linux/Mac)
```

---

## 🔧 Configuración Paso a Paso

### 1. Configurar Variables de Entorno

Edita `.env.production` con tus valores reales:

```bash
# Google AI
GOOGLE_API_KEY=tu-api-key-real
GOOGLE_MODEL=gemini-2.0-flash-exp

# GitHub
GITHUB_TOKEN=ghp_tu_token_real
GITHUB_REPO=brendars91/Gem-Trinity-Genesis

# Snyk
SNYK_TOKEN=tu-snyk-token

# Composio/RUBE
COMPOSIO_API_KEY=tu-composio-key

# n8n (generar clave segura)
N8N_ENCRYPTION_KEY=$(openssl rand -hex 16)
```

💡 **Tip**: Puedes obtener tus valores actuales del `.env` local o de Railway.

---

### 2. Ejecutar Deployment

#### Opción A: Windows (PowerShell)

```powershell
# Desde el directorio del proyecto
.\deploy-to-oci.ps1
```

#### Opción B: Linux/Mac (Bash)

```bash
# Dar permisos de ejecución
chmod +x deploy-to-oci.sh

# Ejecutar
./deploy-to-oci.sh
```

El script automáticamente:
- ✅ Verifica conexión SSH
- ✅ Copia archivos al servidor
- ✅ Construye imagen Docker
- ✅ Levanta servicios con docker-compose
- ✅ Verifica health checks
- ✅ Muestra logs y status

---

### 3. Verificar Deployment

Una vez completado, verifica que los servicios estén corriendo:

```bash
# Conectar al servidor
ssh -i C:\Users\ASUS\.ssh\id_rsa ubuntu@100.69.240.73

# Ver estado de contenedores
cd /home/ubuntu/gem-trinity-genesis
docker-compose ps

# Ver logs del backend
docker-compose logs -f gem-backend
```

**Endpoints esperados**:
- Backend API: http://100.69.240.73:8000/api/status
- n8n: http://100.69.240.73:5678
- Ollama: http://100.69.240.73:11434

---

## 🔄 Actualizar Frontend

Necesitas actualizar la URL del backend en tu frontend. Hay dos opciones:

### Opción 1: Frontend Local (Desarrollo)

Edita `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://100.69.240.73:8000
```

### Opción 2: Frontend en Vercel (Producción)

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Añade/edita:
   ```
   NEXT_PUBLIC_API_URL=http://100.69.240.73:8000
   ```
4. Redeploy el frontend

⚠️ **Importante**: Asegúrate de que tu máquina con Vercel pueda acceder a la red Tailscale, o considera exponer el backend con HTTPS (nginx reverse proxy).

---

## 🐳 Stack Docker Compose

Tu stack incluye:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **gem-backend** | 8000 | API FastAPI del orquestador |
| **n8n** | 5678 | Plataforma de automatización |
| **ollama** | 11434 | Servidor LLM local |

Todos conectados en red `gem-network` con volúmenes persistentes.

---

## 🛠️ Comandos Útiles

### Ver logs en tiempo real
```bash
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose logs -f gem-backend'
```

### Reiniciar backend
```bash
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose restart gem-backend'
```

### Rebuild completo (tras cambios de código)
```bash
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose down && docker-compose build --no-cache && docker-compose up -d'
```

### Detener todo
```bash
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose down'
```

### Ver uso de recursos
```bash
ssh ubuntu@100.69.240.73 'docker stats'
```

---

## 🔐 Seguridad

1. **Tailscale**: Todo el tráfico va por red privada (100.69.240.73)
2. **Firewall OCI**: Solo exponer puertos necesarios
3. **Variables de entorno**: Nunca commitear `.env` con valores reales
4. **Health checks**: Monitoreo automático de servicios

---

## 🚨 Troubleshooting

### Backend no responde
```bash
# Ver logs del backend
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose logs gem-backend'

# Verificar que el puerto esté escuchando
ssh ubuntu@100.69.240.73 'netstat -tlnp | grep 8000'
```

### Error de build de Docker
```bash
# Rebuild forzado sin cache
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose build --no-cache gem-backend'
```

### Ollama no tiene modelo
```bash
# Descargar modelo glm-4.7-flash
ssh ubuntu@100.69.240.73 'docker exec ollama ollama pull glm-4.7-flash'
```

### n8n perdió datos
Los datos de n8n están en volumen `n8n_data`. Para respaldarlos:
```bash
ssh ubuntu@100.69.240.73 'docker run --rm -v n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n_backup.tar.gz /data'
```

---

## 📊 Monitoring (Opcional)

Puedes añadir servicios adicionales al `docker-compose.yml`:

### Prometheus + Grafana
```yaml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - gem-network

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - gem-network
```

---

## 🎯 Siguiente Paso: Desactivar Railway

Una vez que verifiques que todo funciona correctamente:

1. Ve a Railway Dashboard
2. Selecciona tu proyecto "Gem Trinity Genesis"
3. Settings → Delete Service
4. Esto detendrá el cobro

⚠️ **Antes de borrar Railway**:
- Asegúrate de tener respaldos de variables de entorno
- Verifica que el frontend funcione con el nuevo backend
- Haz pruebas de los 3 agentes (Architect, Builder, Engine)

---

## ✅ Checklist Final

- [ ] Archivo `.env.production` configurado con API keys reales
- [ ] Script de deployment ejecutado exitosamente
- [ ] Backend responde en http://100.69.240.73:8000/api/status
- [ ] n8n accesible en http://100.69.240.73:5678
- [ ] Ollama funcionando en http://100.69.240.73:11434
- [ ] Frontend actualizado con nueva URL del backend
- [ ] Pruebas E2E de los agentes completadas
- [ ] Railway desactivado

---

## 📞 Soporte

Si encuentras problemas, revisa:
1. Logs del backend: `docker-compose logs gem-backend`
2. Estado de contenedores: `docker-compose ps`
3. Conectividad Tailscale: `tailscale status`

---

**¡Listo para migrar! 🎉**
