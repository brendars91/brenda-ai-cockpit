#!/usr/bin/env python3
"""
AGCCE Audit Trail v1.0
Sistema de registro inmutable para auditoría.

Características:
- Log inmutable con checksum de integridad
- Firma de cada entrada
- Retención configurable
- Export para auditorías

Uso:
  from audit_trail import AuditTrail
  AuditTrail.log("plan_approved", {"plan_id": "PLAN-XXX", "approver": "user"})
"""

import os
import sys
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Importar utilidades
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info
except ImportError:
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_warn(msg): print(f"[!] {msg}")
    def log_info(msg): print(f"[i] {msg}")


AUDIT_LOG_FILE = "logs/audit_trail.jsonl"
AUDIT_SECRET_KEY = os.environ.get("AGCCE_AUDIT_KEY", "agcce-audit-v1-default-key")


def _generate_checksum(data: str) -> str:
    """Genera checksum HMAC-SHA256."""
    return hmac.new(
        AUDIT_SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:16]


def _get_previous_hash() -> str:
    """Obtiene hash del último registro para encadenamiento."""
    if not os.path.exists(AUDIT_LOG_FILE):
        return "GENESIS"
    
    try:
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1].strip())
                return last_entry.get("entry_hash", "GENESIS")
    except:
        pass
    
    return "GENESIS"


class AuditTrail:
    """Sistema de audit trail inmutable."""
    
    # Tipos de eventos auditables
    EVENT_TYPES = {
        "plan_created": "Plan creado",
        "plan_approved": "Plan aprobado por HITL",
        "plan_rejected": "Plan rechazado por HITL",
        "plan_executed": "Plan ejecutado",
        "step_executed": "Paso ejecutado",
        "file_modified": "Archivo modificado",
        "file_created": "Archivo creado",
        "file_deleted": "Archivo eliminado",
        "security_block": "Bloqueo de seguridad",
        "snyk_scan": "Escaneo Snyk",
        "commit_blocked": "Commit bloqueado",
        "secret_detected": "Secreto detectado",
        "config_changed": "Configuración modificada",
        "webhook_sent": "Webhook enviado",
        "user_action": "Acción de usuario"
    }
    
    @staticmethod
    def log(
        event_type: str,
        details: Dict[str, Any],
        actor: str = "system",
        severity: str = "info"
    ) -> Dict:
        """
        Registra evento en audit trail.
        
        Args:
            event_type: Tipo de evento (ver EVENT_TYPES)
            details: Detalles del evento
            actor: Quien realizó la acción
            severity: info, warning, error, critical
        """
        os.makedirs("logs", exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        previous_hash = _get_previous_hash()
        
        entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "event_description": AuditTrail.EVENT_TYPES.get(event_type, event_type),
            "actor": actor,
            "severity": severity,
            "details": details,
            "previous_hash": previous_hash,
            "hostname": os.environ.get("COMPUTERNAME", "local"),
            "sequence": AuditTrail._get_sequence_number()
        }
        
        # Generar hash de la entrada (sin incluirse a sí mismo)
        entry_data = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        entry["entry_hash"] = _generate_checksum(entry_data)
        entry["checksum"] = _generate_checksum(f"{previous_hash}:{entry_data}")
        
        with open(AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        return entry
    
    @staticmethod
    def _get_sequence_number() -> int:
        """Obtiene número de secuencia."""
        if not os.path.exists(AUDIT_LOG_FILE):
            return 1
        
        try:
            with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) + 1
        except:
            return 1
    
    @staticmethod
    def verify_integrity() -> Dict[str, Any]:
        """Verifica integridad del audit trail."""
        if not os.path.exists(AUDIT_LOG_FILE):
            return {"valid": True, "entries": 0, "message": "No hay registros"}
        
        entries = []
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
        
        if not entries:
            return {"valid": True, "entries": 0, "message": "No hay registros"}
        
        errors = []
        previous_hash = "GENESIS"
        
        for i, entry in enumerate(entries):
            # Verificar encadenamiento
            if entry.get("previous_hash") != previous_hash:
                errors.append(f"Entrada {i+1}: Hash anterior no coincide")
            
            # Verificar checksum de entrada
            stored_hash = entry.pop("entry_hash", None)
            stored_checksum = entry.pop("checksum", None)
            entry_data = json.dumps(entry, sort_keys=True, ensure_ascii=False)
            
            expected_hash = _generate_checksum(entry_data)
            if stored_hash and stored_hash != expected_hash:
                errors.append(f"Entrada {i+1}: Hash de entrada corrupto")
            
            # Restaurar para siguiente iteración
            entry["entry_hash"] = stored_hash
            entry["checksum"] = stored_checksum
            previous_hash = stored_hash
        
        return {
            "valid": len(errors) == 0,
            "entries": len(entries),
            "errors": errors,
            "first_entry": entries[0]["timestamp"] if entries else None,
            "last_entry": entries[-1]["timestamp"] if entries else None
        }
    
    @staticmethod
    def export(
        filepath: str,
        since: datetime = None,
        event_types: List[str] = None
    ) -> int:
        """Exporta audit trail a archivo JSON."""
        if not os.path.exists(AUDIT_LOG_FILE):
            return 0
        
        entries = []
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line.strip())
                
                # Filtrar por fecha
                if since:
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time < since:
                        continue
                
                # Filtrar por tipo
                if event_types and entry["event_type"] not in event_types:
                    continue
                
                entries.append(entry)
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_entries": len(entries),
            "integrity_check": AuditTrail.verify_integrity(),
            "entries": entries
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return len(entries)


def main():
    if len(sys.argv) < 2:
        print("Uso: python audit_trail.py [verify | export | show]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "verify":
        result = AuditTrail.verify_integrity()
        if result["valid"]:
            log_pass(f"Audit trail íntegro - {result['entries']} entradas")
        else:
            log_fail("Audit trail CORRUPTO")
            for error in result.get("errors", []):
                log_warn(f"  {error}")
    
    elif cmd == "export":
        filepath = sys.argv[2] if len(sys.argv) > 2 else "audit_export.json"
        count = AuditTrail.export(filepath)
        log_pass(f"Exportadas {count} entradas a {filepath}")
    
    elif cmd == "show":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        since = datetime.now() - timedelta(days=days)
        
        if not os.path.exists(AUDIT_LOG_FILE):
            print("No hay registros de auditoría")
            return
        
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line.strip())
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= since:
                    ts = entry["timestamp"][:19]
                    print(f"{ts} [{entry['severity'].upper():8}] {entry['event_type']} - {entry.get('actor', 'system')}")


if __name__ == '__main__':
    main()
