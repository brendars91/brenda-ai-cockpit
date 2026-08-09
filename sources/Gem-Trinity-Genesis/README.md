# 💎 Gem Trinity Genesis - Orquestador de Agentes IA

Plataforma Autónoma de Orquestación de Agentes IA con filosofía Deterministic-First.
**Versión:** 2026.2.1

### 🌍 Despliegue en Vivo
Accede a la aplicación desde cualquier dispositivo:
- 🔗 **Producción:** https://covered-bar-identity-bedford.trycloudflare.com
- 🔗 **Frontend:** https://app-eta-fawn-42.vercel.app

---

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.10+
- Node.js 18+
- Git
- API Key de Google Gemini (obtener en https://aistudio.google.com/app/apikey)

### 1. Iniciar el Backend (API Server)

```powershell
# 1. Navegar al directorio
cd "C:\Users\ASUS\.gemini\Gem-Trinity-Genesis\local-watcher"

# 2. Crear archivo .env con tu API key
echo "GOOGLE_API_KEY=tu_api_key_aqui" > .env

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Arrancar el Servidor
python api_server.py
```
*Deberías ver: `INFO: Uvicorn running on http://0.0.0.0:8000`*

### 2. Iniciar la Interfaz (Frontend)
En una **nueva terminal**:

```powershell
# 1. Navegar al directorio del frontend
cd "C:\Users\ASUS\.gemini\Gem-Trinity-Genesis\frontend"

# 2. Instalar dependencias
npm install

# 3. Arrancar en modo desarrollo
npm run dev
```
*Abre tu navegador en: `http://localhost:3000`*

---

## 🌟 Características Clave

### Agentes IA
- **🤖 Architect**: Genera PRD (Product Requirements Document) y especificaciones técnicas
- **🛠️ Builder**: Compila y construye agentes según las especificaciones
- **⚙️ Engine**: Ejecuta tareas de los agentes de forma autónoma

### Sistema de Transparencia
- **🔍 Input/Output logging**: Cada ejecución de agente registra entrada y salida
- **📊 Endpoint de transparencia**: `/api/transparency/executions` y `/api/transparency/execution/{id}`
- **✅ Monitoreo en tiempo real**: Ver qué hacen los agentes en cada momento

### Resiliencia y Rendimiento
- **🛡️ Circuit Breaker**: Protege contra fallos en cascada de APIs externas
- **💾 Semantic Cache**: Cachea respuestas de LLM para evitar重复 requests
- **📈 Error Tracking**: Registro y categorización de errores por severidad

### Despliegue
- **☁️ Oracle Cloud**: Servidor backend en 100.69.240.73
- **🌐 Cloudflare Tunnel**: Acceso público sin necesidad de configurar DNS
- **🐳 Docker**: Contenedor listo para producción

---

## 📂 Estructura del Proyecto

```
Gem-Trinity-Genesis/
├── modules/              # Módulos de agentes (Architect, Builder, Engine)
│   ├── gem-architect/   # Agente Arquitecto
│   ├── gem-builder/     # Agente Constructor
│   └── engine/          # Motor de ejecución
├── resources/           # Skills y MCPs
│   └── skills/          # Habilidades de los agentes
├── local-watcher/       # Backend FastAPI + Orquestador
│   ├── routers/         # Endpoints de API
│   ├── agent_transparency.py  # Sistema de transparencia
│   ├── circuit_breaker.py     # Resiliencia
│   ├── semantic_cache.py      # Cache
│   └── api_server.py         # Servidor principal
└── frontend/            # Interfaz Next.js 14
```

---

## 📡 API Endpoints

### Generación de PRD (Architect)
```bash
POST /api/architect/generate
{
  "use_case": "Sistema de inventario",
  "domain": "enterprise",
  "complexity": "avanzada",
  "model": "gemini"
}
```

### Transparencia
```bash
# Listar ejecuciones
GET /api/transparency/executions?agent_type=architect&limit=50

# Ver detalle de ejecución
GET /api/transparency/execution/{execution_id}
```

### Estado del Sistema
```bash
GET /api/status
GET /api/health
```

---

## 🧪 Pruebas

```powershell
# Ejecutar tests unitarios
cd local-watcher
pytest tests/ -v
```

---

## ☁️ Despliegue en Producción

### Backend (Oracle Cloud)
1. Construir imagen Docker: `docker build -t gem-trinity-genesis .`
2. Ejecutar contenedor con mounts:
```bash
docker run -d --name gem-trinity-backend \
  -p 8000:8000 \
  -v /home/ubuntu/gem-trinity-genesis/resources:/app/resources \
  -v /home/ubuntu/gem-trinity-genesis/modules:/app/modules \
  -v /home/ubuntu/gem-trinity-genesis/config:/app/config \
  gem-trinity-genesis
```

### Cloudflare Tunnel
```bash
cloudflared tunnel --url http://localhost:8000
```

---

## 🔧 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | API Key de Gemini | `AIza...` |
| `PORT` | Puerto del servidor | `8000` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `CORS_ORIGINS` | Orígenes permitidos | `http://localhost:3000` |

---

## 📄 Licencia

MIT License - Proyecto personal de código abierto.
