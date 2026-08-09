#!/usr/bin/env python3
"""
AGCCE Metrics Collector v2.0
Colector de metricas asincrono para observabilidad.

TELEMETRY CONTRACT: AGCCE-OBS-V1
- Persistencia: logs/telemetry.jsonl (append-only)
- Retencion: 30 dias
- Zero-latency: Collector asincrono
- Project-aware: Cada entrada incluye project_id

Uso:
  from metrics_collector import Telemetry
  Telemetry.set_project("mi-proyecto")
  Telemetry.record_plan_generated(success=True, attempts=1, latency_ms=150)
"""

import json
import os
import sys
import time
import threading
import subprocess
from queue import Queue
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configuracion
TELEMETRY_FILE = "logs/telemetry.jsonl"
SECURITY_LOG_FILE = "logs/security_events.jsonl"
RETENTION_DAYS = 30
TELEMETRY_CONTRACT = "AGCCE-OBS-V1"

# Cola asincrona para no bloquear pipeline
_telemetry_queue: Queue = Queue()
_worker_started = False
_current_project: str = None  # Proyecto activo
_current_agent: str = None  # Agente activo (v4.0 MAS)


def _get_branch_name() -> str:
    """Obtiene nombre del branch actual."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
            encoding='utf-8', errors='replace'
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        return "unknown"


def _ensure_log_dir():
    """Crea directorio de logs si no existe."""
    os.makedirs("logs", exist_ok=True)


def _append_to_log(filepath: str, entry: Dict) -> None:
    """Append entry to JSONL file (thread-safe)."""
    _ensure_log_dir()
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def _telemetry_worker():
    """Worker asincrono que procesa la cola de telemetria."""
    while True:
        try:
            entry = _telemetry_queue.get(timeout=1)
            if entry is None:  # Signal de shutdown
                break
            _append_to_log(TELEMETRY_FILE, entry)
            _telemetry_queue.task_done()
        except:
            continue


def _start_worker():
    """Inicia worker asincrono si no esta corriendo."""
    global _worker_started
    if not _worker_started:
        thread = threading.Thread(target=_telemetry_worker, daemon=True)
        thread.start()
        _worker_started = True


class Telemetry:
    """
    Clase principal de telemetria.
    Todos los metodos son estaticos y asincronos (zero-latency).
    """
    
    @staticmethod
    def _create_base_entry(metric_type: str) -> Dict[str, Any]:
        """Crea entrada base con dimensiones."""
        return {
            "contract": TELEMETRY_CONTRACT,
            "type": metric_type,
            "timestamp": datetime.now().isoformat(),
            "dimensions": {
                "branch_name": _get_branch_name(),
                "model_id": "gemini-2.5-pro",  # Default, puede sobreescribirse
                "hostname": os.environ.get("COMPUTERNAME", "local"),
                "project_id": _current_project or _get_project_from_cwd(),
                "agent_id": _current_agent or "orchestrator"  # v4.0: Trazabilidad MAS
            }
        }
    
    @staticmethod
    def set_project(project_id: str) -> None:
        """Establece el proyecto activo para todas las métricas."""
        global _current_project
        _current_project = project_id
    
    @staticmethod
    def set_agent(agent_id: str) -> None:
        """Establece el agente activo para trazabilidad MAS (v4.0)."""
        global _current_agent
        _current_agent = agent_id
    
    @staticmethod
    def record_async(entry: Dict) -> None:
        """Encola entrada para escritura asincrona."""
        _start_worker()
        _telemetry_queue.put(entry)
    
    # ===== RELIABILITY METRICS =====
    
    @staticmethod
    def record_plan_generated(
        success: bool,
        attempts: int,
        hallucinations_blocked: int = 0,
        latency_ms: int = 0,
        plan_id: str = None
    ) -> None:
        """Registra generacion de plan."""
        entry = Telemetry._create_base_entry("reliability.plan_generation")
        entry["metrics"] = {
            "success": success,
            "self_correction_attempts": attempts,
            "hallucinations_blocked": hallucinations_blocked,
            "latency_ms": latency_ms,
            "plan_id": plan_id
        }
        Telemetry.record_async(entry)
    
    @staticmethod
    def record_plan_execution(
        plan_id: str,
        success: bool,
        steps_completed: int,
        steps_total: int,
        latency_ms: int = 0
    ) -> None:
        """Registra ejecucion de plan."""
        entry = Telemetry._create_base_entry("reliability.plan_execution")
        entry["metrics"] = {
            "plan_id": plan_id,
            "success": success,
            "steps_completed": steps_completed,
            "steps_total": steps_total,
            "latency_ms": latency_ms,
            "completion_rate": round(steps_completed / steps_total * 100, 2) if steps_total > 0 else 0
        }
        Telemetry.record_async(entry)
    
    # ===== PERFORMANCE METRICS =====
    
    @staticmethod
    def record_rag_indexing(
        files_indexed: int,
        incremental: bool,
        delta_files: int = 0,
        latency_ms: int = 0
    ) -> None:
        """Registra indexacion RAG."""
        entry = Telemetry._create_base_entry("performance.rag_indexing")
        
        # Calcular eficiencia del delta
        efficiency = 0
        if incremental and files_indexed > 0:
            efficiency = round((1 - delta_files / files_indexed) * 100, 2)
        
        entry["metrics"] = {
            "files_indexed": files_indexed,
            "incremental": incremental,
            "delta_files": delta_files,
            "latency_ms": latency_ms,
            "delta_efficiency_pct": efficiency
        }
        Telemetry.record_async(entry)
    
    @staticmethod
    def record_semantic_search(
        query: str,
        results_count: int,
        latency_ms: int,
        degraded_to_text: bool = False
    ) -> None:
        """Registra busqueda semantica."""
        entry = Telemetry._create_base_entry("performance.semantic_search")
        entry["metrics"] = {
            "query_preview": query[:50] if query else "",
            "results_count": results_count,
            "latency_ms": latency_ms,
            "degraded_to_text": degraded_to_text
        }
        Telemetry.record_async(entry)
    
    # ===== SECURITY METRICS =====
    
    @staticmethod
    def record_security_event(
        event_type: str,
        blocked: bool,
        severity: str = None,
        details: Dict = None,
        file_path: str = None
    ) -> None:
        """
        Registra evento de seguridad.
        Tambien escribe a security_events.jsonl para timeline.
        """
        entry = Telemetry._create_base_entry("security.event")
        entry["metrics"] = {
            "event_type": event_type,  # snyk_code, snyk_diff, unauthorized_path
            "blocked": blocked,
            "severity": severity,
            "file_path": file_path,
            "details": details or {}
        }
        
        # Escribir a ambos logs
        Telemetry.record_async(entry)
        
        # Escribir a security log separado (sincrono para audit trail)
        _append_to_log(SECURITY_LOG_FILE, entry)
    
    @staticmethod
    def record_snyk_scan(
        scan_type: str,  # code, deps, diff
        vulnerabilities_found: int,
        critical_count: int = 0,
        high_count: int = 0,
        blocked_commit: bool = False
    ) -> None:
        """Registra scan de Snyk."""
        entry = Telemetry._create_base_entry("security.snyk_scan")
        entry["metrics"] = {
            "scan_type": scan_type,
            "vulnerabilities_found": vulnerabilities_found,
            "critical_count": critical_count,
            "high_count": high_count,
            "blocked_commit": blocked_commit
        }
        Telemetry.record_async(entry)
        
        # Si bloqueo, registrar evento de seguridad
        if blocked_commit:
            Telemetry.record_security_event(
                event_type=f"snyk_{scan_type}_block",
                blocked=True,
                severity="critical" if critical_count > 0 else "high",
                details={"critical": critical_count, "high": high_count}
            )
    
    @staticmethod
    def record_unauthorized_path_attempt(path: str, action: str) -> None:
        """Registra intento de acceso a path no autorizado (alucinacion)."""
        Telemetry.record_security_event(
            event_type="unauthorized_path",
            blocked=True,
            severity="warning",
            file_path=path,
            details={"attempted_action": action}
        )


class TelemetryReader:
    """Clase para leer y agregar metricas."""
    
    @staticmethod
    def read_entries(
        filepath: str = TELEMETRY_FILE,
        since: datetime = None,
        entry_type: str = None
    ) -> List[Dict]:
        """Lee entradas del log con filtros opcionales."""
        entries = []
        
        if not os.path.exists(filepath):
            return entries
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    
                    # Filtrar por fecha
                    if since:
                        entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                        if entry_time < since:
                            continue
                    
                    # Filtrar por tipo
                    if entry_type and entry.get('type') != entry_type:
                        continue
                    
                    entries.append(entry)
                except:
                    continue
        
        return entries
    
    @staticmethod
    def get_summary(days: int = 7) -> Dict[str, Any]:
        """Obtiene resumen de metricas de los ultimos N dias."""
        since = datetime.now() - timedelta(days=days)
        entries = TelemetryReader.read_entries(since=since)
        
        summary = {
            "period_days": days,
            "total_entries": len(entries),
            "reliability": {
                "plans_generated": 0,
                "plans_successful": 0,
                "success_rate_pct": 0,
                "total_self_corrections": 0,
                "hallucinations_blocked": 0
            },
            "performance": {
                "avg_plan_generation_ms": 0,
                "avg_rag_indexing_ms": 0,
                "avg_delta_efficiency_pct": 0
            },
            "security": {
                "snyk_scans": 0,
                "vulnerabilities_found": 0,
                "commits_blocked": 0,
                "unauthorized_paths_blocked": 0
            }
        }
        
        plan_latencies = []
        rag_latencies = []
        delta_efficiencies = []
        
        for entry in entries:
            entry_type = entry.get('type', '')
            metrics = entry.get('metrics', {})
            
            if entry_type == 'reliability.plan_generation':
                summary['reliability']['plans_generated'] += 1
                if metrics.get('success'):
                    summary['reliability']['plans_successful'] += 1
                summary['reliability']['total_self_corrections'] += metrics.get('self_correction_attempts', 0)
                summary['reliability']['hallucinations_blocked'] += metrics.get('hallucinations_blocked', 0)
                if metrics.get('latency_ms'):
                    plan_latencies.append(metrics['latency_ms'])
            
            elif entry_type == 'performance.rag_indexing':
                if metrics.get('latency_ms'):
                    rag_latencies.append(metrics['latency_ms'])
                if metrics.get('delta_efficiency_pct'):
                    delta_efficiencies.append(metrics['delta_efficiency_pct'])
            
            elif entry_type == 'security.snyk_scan':
                summary['security']['snyk_scans'] += 1
                summary['security']['vulnerabilities_found'] += metrics.get('vulnerabilities_found', 0)
                if metrics.get('blocked_commit'):
                    summary['security']['commits_blocked'] += 1
            
            elif entry_type == 'security.event':
                if metrics.get('event_type') == 'unauthorized_path':
                    summary['security']['unauthorized_paths_blocked'] += 1
        
        # Calcular promedios
        if summary['reliability']['plans_generated'] > 0:
            summary['reliability']['success_rate_pct'] = round(
                summary['reliability']['plans_successful'] / summary['reliability']['plans_generated'] * 100, 2
            )
        
        if plan_latencies:
            summary['performance']['avg_plan_generation_ms'] = round(sum(plan_latencies) / len(plan_latencies), 2)
        
        if rag_latencies:
            summary['performance']['avg_rag_indexing_ms'] = round(sum(rag_latencies) / len(rag_latencies), 2)
        
        if delta_efficiencies:
            summary['performance']['avg_delta_efficiency_pct'] = round(sum(delta_efficiencies) / len(delta_efficiencies), 2)
        
        return summary
    
    @staticmethod
    def get_security_timeline(days: int = 7) -> List[Dict]:
        """Obtiene timeline de eventos de seguridad."""
        since = datetime.now() - timedelta(days=days)
        events = TelemetryReader.read_entries(
            filepath=SECURITY_LOG_FILE,
            since=since
        )
        # Ordenar por timestamp descendente (mas reciente primero)
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return events


def cleanup_old_logs(days: int = RETENTION_DAYS) -> int:
    """Limpia entradas mas antiguas que N dias. Retorna entradas eliminadas."""
    cutoff = datetime.now() - timedelta(days=days)
    removed = 0
    
    for logfile in [TELEMETRY_FILE, SECURITY_LOG_FILE]:
        if not os.path.exists(logfile):
            continue
        
        # Leer, filtrar y reescribir
        entries = TelemetryReader.read_entries(filepath=logfile, since=cutoff)
        original_count = len(TelemetryReader.read_entries(filepath=logfile))
        removed += original_count - len(entries)
        
        with open(logfile, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    return removed


def main():
    """CLI para ver metricas."""
    if len(sys.argv) < 2:
        print("Uso: python metrics_collector.py [summary | timeline | cleanup]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "summary":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        summary = TelemetryReader.get_summary(days)
        print(json.dumps(summary, indent=2))
    
    elif cmd == "timeline":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        events = TelemetryReader.get_security_timeline(days)
        for event in events[:10]:
            ts = event.get('timestamp', '')[:19]
            evt_type = event.get('metrics', {}).get('event_type', 'unknown')
            severity = event.get('metrics', {}).get('severity', '')
            print(f"{ts} [{severity.upper()}] {evt_type}")
    
    elif cmd == "cleanup":
        removed = cleanup_old_logs()
        print(f"Entradas eliminadas: {removed}")
    
    else:
        print(f"Comando desconocido: {cmd}")


if __name__ == '__main__':
    main()
