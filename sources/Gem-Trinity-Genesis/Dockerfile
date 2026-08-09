# Dockerfile para Gem Trinity Genesis Backend
# Optimizado para ARM64 (Oracle Cloud)

FROM python:3.11-slim

# Metadata
LABEL maintainer="Gem Trinity Genesis"
LABEL description="Backend API Server para Orquestador de Agentes"
LABEL version="2026.2.1"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p \
    artifacts/architect_payloads \
    artifacts/builder_agents \
    artifacts/project_outputs \
    logs \
    cache \
    static

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Comando de inicio
WORKDIR /app/local-watcher
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
