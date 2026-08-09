#!/usr/bin/env python3
"""
AGCCE Event Dispatcher v2.0 (FINAL)
Webhook-First Event Dispatcher para integracion con n8n.

MEJORAS FINALES:
1. Healthcheck Handshake (Ping) - Verifica disponibilidad de n8n
2. Retry Logic con Backoff (1s, 5s, 15s) - Resiliencia ante micro-cortes
3. System Context - Incluye version del bundle y model_id en cada payload
4. Cola local - Si n8n no responde, guarda en logs/queue.jsonl

Uso:
  from event_dispatcher import EventDispatcher
  EventDispatcher.healthcheck()  # Verificar n8n disponible
  EventDispatcher.emit("PLAN_VALIDATED", {"plan_id": "PLAN-XXX", ...})
"""

import json
import os
import sys
import time
import hashlib
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Importar utilidades
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info
except ImportError:
    class Colors:
        GREEN = RED = YELLOW = BLUE = CYAN = RESET = BOLD = ''
    class Symbols:
        CHECK = '[OK]'
        CROSS = '[X]'
        WARN = '[!]'
        INFO = '[i]'
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_warn(msg): print(f"[!] {msg}")
    def log_info(msg): print(f"[i] {msg}")

# Importar telemetria
try:
    from metrics_collector import Telemetry
except ImportError:
    Telemetry = None


# =============================================================================
# CONFIGURACION
# =============================================================================

CONFIG_FILE = "config/n8n_webhooks.json"
BUNDLE_FILE = "config/bundle.json"
EVENT_LOG_FILE = "logs/events.jsonl"
IDEMPOTENCY_FILE = "logs/idempotency_keys.json"
QUEUE_FILE = "logs/queue.jsonl"  # Cola local para eventos fallidos

# Retry con Backoff exponencial (1s, 5s, 15s)
RETRY_DELAYS = [1, 5, 15]
MAX_RETRIES = 3

# Eventos criticos permitidos
CRITICAL_EVENTS = {
    "PLAN_VALIDATED": "Plan generado y validado exitosamente",
    "EXECUTION_ERROR": "Error durante la ejecucion del plan",
    "EVIDENCE_READY": "Evidencia lista para envio",
    "SECURITY_BREACH_ATTEMPT": "Intento de brecha de seguridad detectado",
    "HIGH_LATENCY_THRESHOLD": "Umbral de latencia excedido",
    "HITL_TIMEOUT": "Timeout esperando aprobacion humana",
    "HEARTBEAT": "Healthcheck ping"
}


# =============================================================================
# SYSTEM CONTEXT
# =============================================================================

def load_bundle_info() -> Dict[str, str]:
    """Carga informacion del bundle para system_context."""
    default_info = {
        "bundle_id": "BNDL-AGCCE-ULTRA-V2-FINAL",
        "version": "2.0.0-ULTRA-FINAL",
        "model_id": "gemini-2.5-pro"
    }
    
    if os.path.exists(BUNDLE_FILE):
        try:
            with open(BUNDLE_FILE, 'r', encoding='utf-8') as f:
                bundle = json.load(f)
                return {
                    "bundle_id": bundle.get("bundle_id", default_info["bundle_id"]),
                    "version": bundle.get("version", default_info["version"]),
                    "model_id": bundle.get("model_routing", {}).get(
                        "planning_and_debug", default_info["model_id"]
                    )
                }
        except:
            pass
    
    return default_info


def get_system_context() -> Dict[str, Any]:
    """Genera system_context para incluir en cada payload."""
    bundle_info = load_bundle_info()
    
    return {
        "bundle_id": bundle_info["bundle_id"],
        "bundle_version": bundle_info["version"],
        "model_id": bundle_info["model_id"],
        "hostname": os.environ.get("COMPUTERNAME", "local"),
        "dispatcher_version": "2.0.0-FINAL"
    }


# =============================================================================
# UTILIDADES
# =============================================================================

def load_webhook_config() -> Dict[str, str]:
    """Carga configuracion de webhooks."""
    default_config = {
        "PLAN_VALIDATED": "",
        "EXECUTION_ERROR": "",
        "EVIDENCE_READY": "",
        "SECURITY_BREACH_ATTEMPT": "",
        "HIGH_LATENCY_THRESHOLD": "",
        "HITL_TIMEOUT": "",
        "HEARTBEAT": "",
        "_comment": "Reemplaza URLs vacias con tus webhooks de n8n"
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2)
    
    return default_config


def load_idempotency_keys() -> Dict[str, str]:
    """Carga registro de idempotency keys."""
    if os.path.exists(IDEMPOTENCY_FILE):
        try:
            with open(IDEMPOTENCY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_idempotency_key(key: str, timestamp: str) -> None:
    """Guarda idempotency key."""
    keys = load_idempotency_keys()
    keys[key] = timestamp
    
    os.makedirs(os.path.dirname(IDEMPOTENCY_FILE), exist_ok=True)
    with open(IDEMPOTENCY_FILE, 'w', encoding='utf-8') as f:
        json.dump(keys, f, indent=2)


def generate_idempotency_key(event_type: str, plan_id: str) -> str:
    """Genera idempotency key basada en plan_id y evento."""
    data = f"{event_type}:{plan_id}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def log_event(event_type: str, payload: Dict, success: bool, error: str = None) -> None:
    """Registra evento en log."""
    os.makedirs("logs", exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "success": success,
        "error": error,
        "plan_id": payload.get("plan_id"),
        "idempotency_key": payload.get("idempotency_key")
    }
    
    with open(EVENT_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def queue_event(event_type: str, payload: Dict) -> None:
    """Guarda evento en cola local para reintento posterior."""
    os.makedirs("logs", exist_ok=True)
    
    entry = {
        "queued_at": datetime.now().isoformat(),
        "event_type": event_type,
        "payload": payload,
        "status": "pending"
    }
    
    with open(QUEUE_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    log_warn(f"Evento encolado localmente: {event_type}")


# =============================================================================
# EVENT DISPATCHER
# =============================================================================

class EventDispatcher:
    """
    Dispatcher de eventos v2.0 para n8n.
    
    Mejoras:
    - Healthcheck Handshake
    - Retry con Backoff (1s, 5s, 15s)
    - System Context en cada payload
    - Cola local si n8n no disponible
    """
    
    _config: Dict[str, str] = None
    _initialized: bool = False
    _n8n_available: bool = None
    
    @classmethod
    def _ensure_initialized(cls) -> None:
        """Inicializa configuracion si no esta cargada."""
        if not cls._initialized:
            cls._config = load_webhook_config()
            cls._initialized = True
    
    @classmethod
    def get_webhook_url(cls, event_type: str) -> Optional[str]:
        """Obtiene URL de webhook para un evento."""
        cls._ensure_initialized()
        url = cls._config.get(event_type, "")
        return url if url and not url.startswith("_") else None
    
    @classmethod
    def is_event_valid(cls, event_type: str) -> bool:
        """Verifica si el evento es valido."""
        return event_type in CRITICAL_EVENTS
    
    @classmethod
    def check_idempotency(cls, event_type: str, plan_id: str) -> Tuple[bool, str]:
        """Verifica idempotencia. Returns: (is_duplicate, idempotency_key)"""
        if not plan_id:
            return False, None
        
        key = generate_idempotency_key(event_type, plan_id)
        existing_keys = load_idempotency_keys()
        
        if key in existing_keys:
            return True, key
        
        return False, key
    
    # =========================================================================
    # HEALTHCHECK HANDSHAKE
    # =========================================================================
    
    @classmethod
    def healthcheck(cls, timeout: int = 5) -> bool:
        """
        HEALTHCHECK HANDSHAKE
        Verifica si n8n esta disponible enviando un ping al webhook HEARTBEAT.
        """
        cls._ensure_initialized()
        
        heartbeat_url = cls.get_webhook_url("HEARTBEAT")
        if not heartbeat_url:
            # Intentar con cualquier webhook configurado
            for event_type in CRITICAL_EVENTS:
                url = cls.get_webhook_url(event_type)
                if url:
                    heartbeat_url = url
                    break
        
        if not heartbeat_url:
            log_warn("ADVERTENCIA: n8n no configurado. Los reportes se guardaran en cola local.")
            cls._n8n_available = False
            return False
        
        try:
            ping_payload = {
                "event_type": "HEARTBEAT",
                "timestamp": datetime.now().isoformat(),
                "system_context": get_system_context()
            }
            
            data = json.dumps(ping_payload).encode('utf-8')
            request = Request(
                heartbeat_url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urlopen(request, timeout=timeout) as response:
                if response.status >= 200 and response.status < 300:
                    log_pass("n8n disponible (healthcheck OK)")
                    cls._n8n_available = True
                    return True
        
        except Exception as e:
            log_warn(f"ADVERTENCIA: n8n no disponible ({e}). Reportes en cola local.")
            cls._n8n_available = False
        
        return False
    
    @classmethod
    def is_n8n_available(cls) -> bool:
        """Retorna estado de disponibilidad de n8n."""
        if cls._n8n_available is None:
            cls.healthcheck()
        return cls._n8n_available or False
    
    # =========================================================================
    # EMIT CON RETRY + BACKOFF
    # =========================================================================
    
    @classmethod
    def emit(
        cls,
        event_type: str,
        payload: Dict[str, Any],
        force: bool = False,
        async_mode: bool = True
    ) -> bool:
        """
        Emite un evento via webhook con retry logic.
        
        Args:
            event_type: Tipo de evento critico
            payload: Datos del evento (debe incluir plan_id)
            force: Ignorar idempotencia
            async_mode: Emitir en background
        """
        cls._ensure_initialized()
        
        # Validar evento
        if not cls.is_event_valid(event_type):
            log_warn(f"Evento no reconocido: {event_type}")
            return False
        
        # Obtener webhook URL
        webhook_url = cls.get_webhook_url(event_type)
        if not webhook_url:
            log_info(f"Webhook no configurado para {event_type}")
            return False
        
        # Verificar idempotencia
        plan_id = payload.get("plan_id", "")
        is_duplicate, idempotency_key = cls.check_idempotency(event_type, plan_id)
        
        if is_duplicate and not force:
            log_info(f"Evento duplicado ignorado: {event_type} ({idempotency_key})")
            return False
        
        # Preparar payload con SYSTEM CONTEXT
        full_payload = {
            "event_type": event_type,
            "event_description": CRITICAL_EVENTS.get(event_type, ""),
            "timestamp": datetime.now().isoformat(),
            "idempotency_key": idempotency_key,
            "system_context": get_system_context(),  # NUEVO
            "payload": payload
        }
        
        if async_mode:
            thread = threading.Thread(
                target=cls._send_with_retry,
                args=(webhook_url, full_payload, event_type, idempotency_key)
            )
            thread.daemon = True
            thread.start()
            return True
        else:
            return cls._send_with_retry(webhook_url, full_payload, event_type, idempotency_key)
    
    @classmethod
    def _send_with_retry(
        cls,
        url: str,
        payload: Dict,
        event_type: str,
        idempotency_key: str
    ) -> bool:
        """
        RETRY LOGIC CON BACKOFF EXPONENCIAL
        Intentos: 3 con delays de 1s, 5s, 15s
        """
        for attempt in range(MAX_RETRIES):
            success = cls._send_webhook(url, payload, event_type, idempotency_key)
            
            if success:
                return True
            
            # Si no es el ultimo intento, esperar con backoff
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                log_info(f"Reintentando en {delay}s... (intento {attempt + 2}/{MAX_RETRIES})")
                time.sleep(delay)
        
        # Todos los intentos fallaron - encolar localmente
        queue_event(event_type, payload)
        log_fail(f"Evento {event_type} encolado localmente despues de {MAX_RETRIES} intentos")
        
        return False
    
    @classmethod
    def _send_webhook(
        cls,
        url: str,
        payload: Dict,
        event_type: str,
        idempotency_key: str
    ) -> bool:
        """Envia webhook HTTP POST (un solo intento)."""
        try:
            data = json.dumps(payload).encode('utf-8')
            
            request = Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'X-AGCCE-Event': event_type,
                    'X-Idempotency-Key': idempotency_key or '',
                    'X-Bundle-Version': payload.get('system_context', {}).get('bundle_version', '')
                },
                method='POST'
            )
            
            with urlopen(request, timeout=10) as response:
                status = response.status
                
                if status >= 200 and status < 300:
                    if idempotency_key:
                        save_idempotency_key(idempotency_key, datetime.now().isoformat())
                    
                    log_pass(f"Webhook enviado: {event_type}")
                    log_event(event_type, payload.get("payload", {}), True)
                    
                    if Telemetry:
                        Telemetry.record_async({
                            "contract": "AGCCE-OBS-V1",
                            "type": "automation.webhook_sent",
                            "timestamp": datetime.now().isoformat(),
                            "metrics": {
                                "event_type": event_type,
                                "success": True,
                                "retries": 0
                            }
                        })
                    
                    return True
                else:
                    raise Exception(f"HTTP {status}")
        
        except (URLError, HTTPError) as e:
            log_event(event_type, payload.get("payload", {}), False, str(e))
            return False
        
        except Exception as e:
            log_event(event_type, payload.get("payload", {}), False, str(e))
            return False
    
    # =========================================================================
    # METODOS HELPERS
    # =========================================================================
    
    @classmethod
    def emit_plan_validated(cls, plan_id: str, plan_data: Dict) -> bool:
        """Emite evento PLAN_VALIDATED."""
        return cls.emit("PLAN_VALIDATED", {
            "plan_id": plan_id,
            "objective": plan_data.get("objective", {}).get("description", ""),
            "steps_count": len(plan_data.get("steps", [])),
            "validation_status": "passed"
        })
    
    @classmethod
    def emit_execution_error(cls, plan_id: str, step_id: str, error: str) -> bool:
        """Emite evento EXECUTION_ERROR."""
        return cls.emit("EXECUTION_ERROR", {
            "plan_id": plan_id,
            "step_id": step_id,
            "error": error,
            "severity": "high"
        })
    
    @classmethod
    def emit_evidence_ready(cls, plan_id: str, evidence_path: str, summary: Dict) -> bool:
        """Emite evento EVIDENCE_READY."""
        return cls.emit("EVIDENCE_READY", {
            "plan_id": plan_id,
            "evidence_path": evidence_path,
            "summary": summary
        })
    
    @classmethod
    def emit_security_alert(cls, plan_id: str, alert_type: str, details: Dict) -> bool:
        """Emite evento SECURITY_BREACH_ATTEMPT."""
        return cls.emit("SECURITY_BREACH_ATTEMPT", {
            "plan_id": plan_id,
            "alert_type": alert_type,
            "details": details,
            "severity": "critical"
        })
    
    @classmethod
    def process_queue(cls) -> int:
        """Procesa eventos encolados localmente. Retorna numero de eventos procesados."""
        if not os.path.exists(QUEUE_FILE):
            return 0
        
        processed = 0
        remaining = []
        
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get('status') == 'pending':
                        event_type = entry.get('event_type')
                        payload = entry.get('payload', {})
                        
                        webhook_url = cls.get_webhook_url(event_type)
                        if webhook_url:
                            success = cls._send_webhook(
                                webhook_url, payload, event_type,
                                payload.get('idempotency_key')
                            )
                            if success:
                                processed += 1
                                entry['status'] = 'sent'
                            else:
                                remaining.append(entry)
                except:
                    pass
        
        # Reescribir cola con elementos restantes
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            for entry in remaining:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        if processed > 0:
            log_pass(f"Procesados {processed} eventos de la cola")
        
        return processed


# =============================================================================
# CLI
# =============================================================================

def configure_webhooks():
    """CLI para configurar webhooks."""
    print("=== Configurar Webhooks n8n ===\n")
    
    config = load_webhook_config()
    
    for event in CRITICAL_EVENTS:
        current = config.get(event, "")
        print(f"{event}:")
        print(f"  Descripcion: {CRITICAL_EVENTS[event]}")
        print(f"  URL actual: {current or '(no configurado)'}")
        
        new_url = input(f"  Nueva URL (Enter para mantener): ").strip()
        if new_url:
            config[event] = new_url
        print()
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuracion guardada en: {CONFIG_FILE}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python event_dispatcher.py [configure | test | status | healthcheck | process-queue]")
        print("\nComandos:")
        print("  configure      Configurar URLs de webhooks")
        print("  test           Enviar evento de prueba")
        print("  status         Ver estado de configuracion")
        print("  healthcheck    Verificar disponibilidad de n8n")
        print("  process-queue  Procesar eventos encolados")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "configure":
        configure_webhooks()
    
    elif cmd == "test":
        event_type = sys.argv[2] if len(sys.argv) > 2 else "PLAN_VALIDATED"
        print(f"Enviando evento de prueba: {event_type}")
        
        success = EventDispatcher.emit(event_type, {
            "plan_id": "PLAN-TEST1234",
            "test": True,
            "message": "Evento de prueba AGCCE"
        }, force=True, async_mode=False)
        
        print(f"Resultado: {'OK' if success else 'FAILED (encolado localmente)'}")
    
    elif cmd == "status":
        config = load_webhook_config()
        print("=== Estado de Webhooks ===\n")
        
        for event, desc in CRITICAL_EVENTS.items():
            url = config.get(event, "")
            status = "Configurado" if url else "No configurado"
            icon = Symbols.CHECK if url else Symbols.CROSS
            print(f"{icon} {event}: {status}")
    
    elif cmd == "healthcheck":
        print("=== Healthcheck n8n ===\n")
        available = EventDispatcher.healthcheck()
        print(f"\nResultado: {'n8n DISPONIBLE' if available else 'n8n NO DISPONIBLE'}")
    
    elif cmd == "process-queue":
        print("=== Procesando cola local ===\n")
        processed = EventDispatcher.process_queue()
        print(f"\nEventos procesados: {processed}")
    
    else:
        print(f"Comando desconocido: {cmd}")


if __name__ == '__main__':
    main()
