# ========================================
# Cloudflare Tunnel Setup Guide
# Exponer Backend con HTTPS (sin dominio propio)
# ========================================

## Paso 1: Autenticar Cloudflared

En tu servidor OCI, ejecuta:

```bash
ssh -i C:\Users\ASUS\.ssh\id_rsa ubuntu@100.69.240.73
cloudflared tunnel login
```

Esto abrirá un navegador para autenticarte con Cloudflare.
Si no tienes cuenta de Cloudflare, créala gratis en: https://dash.cloudflare.com/sign-up

## Paso 2: Crear Tunnel

```bash
cloudflared tunnel create gem-backend
```

Esto generará:
- Un UUID único del tunnel
- Credenciales en: `~/.cloudflared/<UUID>.json`

Guarda el UUID que te muestra (ej: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

## Paso 3: Configurar Tunnel

Crea el archivo de configuración:

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Contenido del archivo:

```yaml
url: http://localhost:8000
tunnel: <TU-TUNNEL-UUID>
credentials-file: /home/ubuntu/.cloudflared/<TU-TUNNEL-UUID>.json
```

Reemplaza `<TU-TUNNEL-UUID>` con el UUID real.

## Paso 4: Ejecutar Tunnel (Modo Manual - Testing)

```bash
cloudflared tunnel run gem-backend
```

Cloudflare te dará una URL pública tipo:
`https://<random-name>.trycloudflare.com`

⚠️ Esta URL cambia cada vez que reinicias el tunnel.

## Paso 5: Tunnel Permanente con Dominio

### Opción A: Usar dominio gratuito de Cloudflare

```bash
cloudflared tunnel route dns gem-backend <tu-subdominio>.cfargodomain.com
```

Cloudflare te asignará un subdominio gratuito.

### Opción B: Usar tu propio dominio (si lo tienes)

Si tienes un dominio en Cloudflare:

```bash
cloudflared tunnel route dns gem-backend api.tudominio.com
```

## Paso 6: Ejecutar como Servicio (AutoStart)

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

Verifica estado:
```bash
sudo systemctl status cloudflared
```

## Paso 6B: Ejecutar con Docker Compose (Recomendado)

Si usas `docker-compose.yml`, configura el token y levanta el servicio:

```bash
export CLOUDFLARE_TUNNEL_TOKEN=tu-token
docker compose up -d cloudflared
```

El servicio se reinicia automaticamente (`restart: always`) y expone metricas en `:2000`.

## Paso 7: Obtener URL Pública

Tu backend estará disponible en:
- **Sin dominio propio**: `https://<random-name>.trycloudflare.com`
- **Con subdominio Cloudflare**: `https://<tu-subdominio>.cfargodomain.com`
- **Con dominio propio**: `https://api.tudominio.com`

## Paso 8: Actualizar Frontend en Vercel

Con la URL de Cloudflare:

```
NEXT_PUBLIC_API_URL=https://<tu-url-cloudflare>
```

---

## Alternativa Rápida (Sin Autenticación)

Para testing rápido sin cuenta:

```bash
cloudflared tunnel --url http://localhost:8000
```

Te dará una URL temporal tipo: `https://random-words.trycloudflare.com`

⚠️ Esta URL cambia cada vez y solo funciona mientras el comando esté corriendo.

---

## Verificar Tunnel

```bash
# Listar tunnels
cloudflared tunnel list

# Ver info de un tunnel
cloudflared tunnel info gem-backend

# Limpiar tunnels no usados
cloudflared tunnel cleanup gem-backend
```

---

## Troubleshooting

### Error: "tunnel not found"
```bash
cloudflared tunnel delete gem-backend
cloudflared tunnel create gem-backend
```

### Error de permisos
```bash
sudo chown ubuntu:ubuntu ~/.cloudflared/*
chmod 600 ~/.cloudflared/*.json
```

### Ver logs
```bash
sudo journalctl -u cloudflared -f
```
