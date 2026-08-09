# Sistema de Monitoreo - Gem Trinity Genesis

## Overview

Sistema completo de monitoreo y observabilidad para uso personal.

## Componentes

### 1. Health Checks
- **Endpoint:** `/api/health/detailed`
- **Frecuencia:** Cada 5 minutos (cron)
- **Alertas:** Email y Slack

### 2. Métricas (Prometheus)
- **Endpoint:** `/api/metrics`
- **Formato:** Prometheus exposition format
- **Retención:** 30 días

### 3. Dashboard (Grafana)
- **URL:** http://localhost:3001
- **Login:** admin / weiden_91
- **Dashboards:** Overview, System, API

## Inicio Rápido

### Iniciar Monitoreo Completo:
```bash
# 1. Iniciar stack de monitoreo
docker-compose -f docker-compose.monitoring.yml up -d

# 2. Verificar que todo esté corriendo
docker-compose -f docker-compose.monitoring.yml ps

# 3. Acceder a Grafana
# http://localhost:3001
```

### Verificar Health Check Manual:
```bash
# Ejecutar script de health check
bash ops/monitoring/health-check.sh

# Debería ver: ✓ System is healthy
```

## Configuración

### Environment Variables:
```bash
# Backend URL para health check
export BACKEND_URL="http://localhost:8000"

# Email para alertas (opcional)
export ALERT_EMAIL="your-email@example.com"

# Slack webhook para alertas (opcional)
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK"
```

### Cron Job Setup:
```bash
# Editar crontab
crontab -e

# Agregar línea:
*/5 * * * * cd /path/to/Gem-Trinity-Genesis && bash ops/monitoring/health-check.sh >> logs/health-check.log 2>&1
```

## Métricas Principales

### API Metrics:
- `gem_api_requests_total` - Total de requests
- `gem_api_request_duration_seconds` - Latencia de requests
- `gem_api_errors_total` - Total de errores
- `gem_cache_hits_total` - Cache hits
- `gem_cache_misses_total` - Cache misses

### System Metrics:
- CPU usage por core
- Memory disponible y usada
- Disk usage por partición
- Network I/O
- Container stats (via cAdvisor)

### Business Metrics:
- Agentes generados por día
- Success rate por tipo de agente
- LLM costs por día
- Promedio de tiempo de generación

## Alertas

### Tipos de Alertas:

**1. Backend Down (CRITICAL)**
- Trigger: Health check falla
- Acción: Email + Slack inmediato
- Recovery: Notificación cuando vuelve

**2. High Error Rate (WARNING)**
- Trigger: > 10% de errores en 5min
- Acción: Email de advertencia
- Recovery: Notificación cuando normaliza

**3. High Resource Usage (INFO)**
- Trigger: CPU > 90% o Memory > 85%
- Acción: Log al archivo
- Recovery: N/A

### Customizar Alertas:

```bash
# Editar script de health check
nano ops/monitoring/health-check.sh

# Modificar umbrales:
HIGH_CPU=90          # Porcentaje CPU
HIGH_MEMORY=85       # Porcentaje memoria
HIGH_DISK=90         # Porcentaje disco
HIGH_ERROR_RATE=10   # Errores por minuto
```

## Dashboards

### Dashboard Principal: Gem Trinity Overview

**Panels:**
1. API Request Rate - Requests por segundo por endpoint
2. Error Rate - Porcentaje de errores (gauge)
3. Cache Hit Rate - Efectividad del cache
4. Memory Available - Memoria disponible del sistema
5. API Response Time - Latencia p95 por endpoint

### Acceder a Dashboards:

1. Abrir Grafana: http://localhost:3001
2. Login: admin / weiden_91
3. Navegar a: Dashboards → Gem Trinity Genesis

## Troubleshooting

### Prometheus no arranca:
```bash
# Ver logs
docker-compose -f docker-compose.monitoring.yml logs prometheus

# Verificar configuración
docker-compose -f docker-compose.monitoring.yml config prometheus
```

### Grafana no muestra datos:
```bash
# Verificar que Prometheus esté scrapeando
curl http://localhost:9090/api/v1/targets

# Verificar datasource en Grafana
# Configuration → Data Sources → Prometheus → Test
```

### Health check no envía alertas:
```bash
# Probar manualmente
ALERT_EMAIL="test@example.com" bash ops/monitoring/health-check.sh

# Verificar configuración de email
echo "Test" | mail -s "Test Email" your-email@example.com
```

## Mantenimiento

### Diario:
- Los health checks corren automáticamente cada 5 min
- Logs se guardan en `logs/health-check.log`

### Semanal:
- Revisar `logs/health-check-alerts.log` para patrones
- Revisar dashboards de Grafana para anomalías

### Mensual:
- Limpiar logs antiguos (> 30 días)
- Actualizar dashboards si es necesario
- Revisar storage de Prometheus (retención 30 días)

### Anual:
- Actualizar versiones de Prometheus/Grafana
- Revisar y optimizar queries
- Archivar datos antiguos si es necesario

## Integraciones

### n8n Workflow:
1. Importar `ops/monitoring/n8n-health-check-workflow.json`
2. Configurar webhook URL de Slack
3. Activar workflow

### Slack Notifications:
```bash
# Configurar webhook en Slack
# https://api.slack.com/messaging/webhooks

# Actualizar variable de entorno
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK"

# El script de health check usará automáticamente el webhook
```

## Exportar/Importar Configuración

### Exportar Dashboard:
1. Abrir dashboard en Grafana
2. Settings (gear icon) → JSON Model
3. Copiar JSON
4. Guardar en `ops/monitoring/grafana/dashboards/`

### Importar Dashboard:
1. Dashboards → Import
2. Upload JSON file
3. Seleccionar datasource Prometheus

## Scripts Útiles

### Backup de Configuración:
```bash
# Backup de toda la configuración de monitoreo
tar -czf monitoring-backup-$(date +%Y%m%d).tar.gz ops/monitoring/
```

### Limpiar Datos de Prometheus:
```bash
# Detener Prometheus
docker-compose -f docker-compose.monitoring.yml stop prometheus

# Limpiar datos
rm -rf ops/monitoring/data/prometheus/*

# Reiniciar
docker-compose -f docker-compose.monitoring.yml up -d prometheus
```

## Referencias

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [cAdvisor Documentation](https://github.com/google/cadvisor)
- [Node Exporter Documentation](https://github.com/prometheus/node_exporter)
