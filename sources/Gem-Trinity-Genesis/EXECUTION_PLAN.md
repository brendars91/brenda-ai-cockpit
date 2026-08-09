# 🎯 Plan de Ejecución - Migración Railway → OCI

## ⏱️ Tiempo estimado: 15-30 minutos

---

## 📋 Checklist Rápida

### Antes de Empezar
- [ ] Tengo acceso SSH al servidor (100.69.240.73)
- [ ] Tailscale está activo en mi máquina
- [ ] Tengo las API keys necesarias

### Paso 1: Configurar Variables de Entorno (5 min)
```powershell
# Editar este archivo con tus API keys reales
notepad .env.production
```

**Valores que DEBES cambiar**:
- `GOOGLE_API_KEY`: Tu API key de Google AI (gemini)
- `GITHUB_TOKEN`: Tu token personal de GitHub
- `SNYK_TOKEN`: Tu token de Snyk (si usas seguridad)
- `COMPOSIO_API_KEY`: Tu API key de Composio/RUBE
- `N8N_ENCRYPTION_KEY`: Generar con: `openssl rand -hex 16`

### Paso 2: Pre-Flight Check (2 min)
```powershell
# Verificar que todo esté listo
.\pre-flight-check.ps1
```

**Resultado esperado**: `✅ TODO LISTO PARA DEPLOYMENT`

Si hay errores, resolverlos antes de continuar.

### Paso 3: Deployment (10-15 min)
```powershell
# Ejecutar deployment automatizado
.\deploy-to-oci.ps1
```

El script automáticamente:
1. Verifica conexión SSH ✅
2. Copia archivos al servidor ✅
3. Construye imagen Docker ✅
4. Levanta servicios (backend, n8n, ollama) ✅
5. Verifica health checks ✅

### Paso 4: Verificar Backend (2 min)
```powershell
# Probar endpoint
curl http://100.69.240.73:8000/api/status
```

**Respuesta esperada**:
```json
{
  "status": "online",
  "message": "Gem Trinity Genesis API v2026.2.1 Running"
}
```

### Paso 5: Actualizar Frontend (5 min)

#### Si usas Vercel:
1. Ve a https://vercel.com/dashboard
2. Tu proyecto → Settings → Environment Variables
3. Editar `NEXT_PUBLIC_API_URL`:
   - **Desarrollo**: `http://100.69.240.73:8000`
   - **Producción**: Necesitas HTTPS (ver opciones abajo)

#### Si usas frontend local:
```powershell
cd frontend
# Ya está configurado para http://localhost:8000
npm run dev
```

### Paso 6: Pruebas E2E (5 min)
1. Abrir frontend (localhost:3000 o Vercel)
2. Probar Architect → Crear payload
3. Probar Builder → Compilar agente
4. Probar Engine → Ejecutar agente

### Paso 7: Desactivar Railway
⚠️ **SOLO después de confirmar que todo funciona**

1. Railway Dashboard → Tu proyecto
2. Settings → Delete Service
3. Confirmar eliminación

---

## 🚀 Ejecución Rápida (One-Liner)

Si tienes todo configurado:

```powershell
# 1. Configurar .env.production (manual)
notepad .env.production

# 2. Pre-flight + Deploy (automatizado)
.\pre-flight-check.ps1 && .\deploy-to-oci.ps1
```

---

## 📊 Estado Esperado Post-Deployment

### Servicios Activos
| Servicio | Puerto | URL | Status |
|----------|--------|-----|--------|
| Backend | 8000 | http://100.69.240.73:8000 | 🟢 Running |
| n8n | 5678 | http://100.69.240.73:5678 | 🟢 Running |
| Ollama | 11434 | http://100.69.240.73:11434 | 🟢 Running |

### Verificar con:
```powershell
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose ps'
```

---

## ⚠️ Problemas Comunes

### 1. Backend no responde
```powershell
# Ver logs
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose logs gem-backend'

# Reiniciar
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose restart gem-backend'
```

### 2. Error de build Docker
```powershell
# Rebuild sin cache
ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose build --no-cache gem-backend && docker-compose up -d'
```

### 3. Conexión SSH falla
```powershell
# Verificar Tailscale
tailscale status

# Verificar SSH key
ssh -i C:\Users\ASUS\.ssh\id_rsa -v ubuntu@100.69.240.73
```

### 4. Frontend no conecta con backend
- **Local**: Asegúrate de estar en la VPN Tailscale
- **Vercel**: Necesitas exponer backend con HTTPS (ver FRONTEND_UPDATE.md)

---

## 📞 Soporte y Recursos

- **Guía completa**: `MIGRATION_GUIDE.md`
- **Frontend setup**: `FRONTEND_UPDATE.md`
- **Logs del servidor**: 
  ```powershell
  ssh ubuntu@100.69.240.73 'cd /home/ubuntu/gem-trinity-genesis && docker-compose logs -f'
  ```

---

## ✅ Criterios de Éxito

- [ ] Backend responde en http://100.69.240.73:8000/api/status
- [ ] n8n accesible en http://100.69.240.73:5678
- [ ] Ollama funcionando en http://100.69.240.73:11434
- [ ] Frontend puede listar proyectos
- [ ] Architect puede generar payload
- [ ] Builder puede compilar agente
- [ ] Engine puede ejecutar agente
- [ ] Railway desactivado

---

**🎉 ¡Listo para migrar! Todo está preparado.**

**Siguiente acción**: 
```powershell
notepad .env.production  # Configura tus API keys
.\pre-flight-check.ps1   # Luego ejecuta esto
```
