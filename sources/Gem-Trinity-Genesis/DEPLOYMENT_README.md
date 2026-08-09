# 🔧 Deployment OCI - Quick Reference

## 📦 Archivos Creados para la Migración

```
.
├── Dockerfile                    # Imagen Docker del backend
├── docker-compose.yml            # Stack completo (backend + n8n + ollama)
├── .dockerignore                # Optimización de build
├── .env.production              # Template de variables de entorno
│
├── deploy-to-oci.ps1            # Script de deployment (Windows)
├── deploy-to-oci.sh             # Script de deployment (Linux/Mac)
│
├── pre-flight-check.ps1         # Verificación pre-deployment (Windows)
├── pre-flight-check.sh          # Verificación pre-deployment (Linux/Mac)
│
├── EXECUTION_PLAN.md            # 📋 Plan paso a paso (EMPEZAR AQUÍ)
├── MIGRATION_GUIDE.md           # 📖 Guía completa de migración
└── FRONTEND_UPDATE.md           # 🎨 Actualizar frontend para OCI
```

---

## 🚀 Quick Start

### 1️⃣ Configurar Variables de Entorno
```powershell
copy .env.production.example .env.production
notepad .env.production
```
Rellena tus API keys reales (Google AI, GitHub, Snyk, Composio, n8n) y el token de Cloudflare Tunnel.

### 2️⃣ Verificar Pre-Requisitos
```powershell
.\pre-flight-check.ps1
```

### 3️⃣ Ejecutar Deployment
```powershell
.\deploy-to-oci.ps1
```

### 4️⃣ Verificar
```powershell
curl http://100.69.240.73:8000/api/status
```

### 5️⃣ Mantenimiento (Ops)
- Ver `ops/README.md` para backups, cron y servicio del tunnel.

---

## 📚 Documentación

- **Empezar aquí**: [`EXECUTION_PLAN.md`](./EXECUTION_PLAN.md) - Plan de ejecución paso a paso
- **Guía completa**: [`MIGRATION_GUIDE.md`](./MIGRATION_GUIDE.md) - Detalles técnicos
- **Frontend**: [`FRONTEND_UPDATE.md`](./FRONTEND_UPDATE.md) - Configurar Vercel

---

## 🔗 Endpoints Post-Deployment

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Backend** | http://100.69.240.73:8000 | API principal |
| **n8n** | http://100.69.240.73:5678 | Automatización |
| **Ollama** | http://100.69.240.73:11434 | LLM local |

---

## 🛟 Ayuda Rápida

**Ver logs**:
```powershell
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose logs -f gem-backend'
```

**Reiniciar**:
```powershell
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose restart gem-backend'
```

**Status**:
```powershell
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose ps'
```

---

## ✅ Checklist

- [ ] `.env.production` configurado
- [ ] Pre-flight check pasado
- [ ] Deployment ejecutado
- [ ] Backend responde
- [ ] Frontend actualizado
- [ ] Tunnel activo (Cloudflare)
- [ ] Backups programados
- [ ] Log rotation configurada
- [ ] Pruebas E2E completadas
- [ ] Railway desactivado

---

**🎯 Siguiente paso**: Lee [`EXECUTION_PLAN.md`](./EXECUTION_PLAN.md)
