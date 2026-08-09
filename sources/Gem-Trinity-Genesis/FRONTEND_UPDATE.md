# ========================================
# Frontend Deployment Instructions
# Actualizar Vercel con nueva URL del backend
# ========================================

## Para Vercel

Si tu frontend está desplegado en Vercel:

1. Ve a: https://vercel.com/dashboard
2. Selecciona tu proyecto "Gem Trinity Genesis" o similar
3. Settings → Environment Variables
4. Edita o añade:

```
Variable: NEXT_PUBLIC_API_URL
Value:    http://100.69.240.73:8000
```

⚠️ **PROBLEMA POTENCIAL**: Vercel no puede acceder a tu red Tailscale

### Soluciones:

#### Opción 1: Frontend Local (Recomendado para desarrollo)
```bash
cd frontend
npm run dev
```
El frontend en localhost:3000 SÍ puede acceder a 100.69.240.73:8000 vía Tailscale

#### Opción 2: Exponer backend con HTTPS (Recomendado para producción)

Necesitarás:
1. Nginx reverse proxy con SSL
2. Dominio propio
3. Certificado SSL (Let's Encrypt)

Pasos:
```bash
# En el servidor OCI
sudo apt install nginx certbot python3-certbot-nginx

# Configurar nginx (ver ejemplo abajo)
sudo nano /etc/nginx/sites-available/gem-backend

# Obtener certificado SSL
sudo certbot --nginx -d api.tudominio.com

# Reiniciar nginx
sudo systemctl restart nginx
```

Ejemplo de configuración nginx:
```nginx
server {
    listen 80;
    server_name api.tudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Luego actualizar Vercel con:
```
NEXT_PUBLIC_API_URL=https://api.tudominio.com
```

#### Opción 3: Cloudflare Tunnel (Sin dominio propio)

```bash
# En el servidor OCI
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Autenticar
cloudflared tunnel login

# Crear tunnel
cloudflared tunnel create gem-backend

# Configurar
cloudflared tunnel route dns gem-backend api.tudominio.cloudflare.com

# Ejecutar
cloudflared tunnel run gem-backend
```

---

## Para desarrollo local

Ya está configurado `.env.local` con:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Pero puedes cambiarlo temporalmente a:
```
NEXT_PUBLIC_API_URL=http://100.69.240.73:8000
```

Para probar contra el backend remoto.

---

## Verificar configuración actual

```bash
# Desarrollo
cd frontend
cat .env.local

# Producción
cat .env.production
```
