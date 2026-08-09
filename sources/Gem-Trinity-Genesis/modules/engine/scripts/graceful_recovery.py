#!/usr/bin/env python3
"""
AGCCE Graceful Recovery v1.0
Manejo de fallos en Multi-Agent System.

Implementa:
- Recuperación de errores de Sub-Agentes
- Validación de JSON de respuestas
- Fallback a reintentos con feedback
- Logging de errores para auto-aprendizaje

Uso:
    from graceful_recovery import GracefulRecovery
    result = GracefulRecovery.execute_with_recovery(agent_id, task, max_retries=3)
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
RECOVERY_LOG = LOGS_DIR / "recovery_events.jsonl"


class GracefulRecovery:
    """Manejo de fallos para Multi-Agent System."""
    
    @classmethod
    def _log_recovery_event(cls, event: Dict):
        """Registra evento de recuperación."""
        LOGS_DIR.mkdir(exist_ok=True)
        
        event["timestamp"] = datetime.now().isoformat()
        
        with open(RECOVERY_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    @classmethod
    def validate_agent_response(cls, response: Any, agent_id: str) -> Tuple[bool, str]:
        """
        Valida que la respuesta de un agente es válida.
        
        Returns:
            Tuple[is_valid, error_message]
        """
        # 1. Verificar que no es None
        if response is None:
            return False, "Agent returned None"
        
        # 2. Si es string, intentar parsear como JSON
        if isinstance(response, str):
            try:
                json.loads(response)
            except json.JSONDecodeError as e:
                return False, f"Malformed JSON: {str(e)[:100]}"
        
        # 3. Si es dict, verificar campos mínimos esperados
        if isinstance(response, dict):
            # Campos mínimos según el agente
            required_fields = {
                "architect": ["plan", "steps"],
                "constructor": ["files_modified", "status"],
                "auditor": ["security_score", "findings"],
                "tester": ["tests_passed", "results"],
                "researcher": ["context", "sources"]
            }
            
            agent_fields = required_fields.get(agent_id, [])
            missing = [f for f in agent_fields if f not in response]
            
            if missing:
                return False, f"Missing required fields: {missing}"
        
        return True, ""
    
    @classmethod
    def generate_feedback(cls, error: str, agent_id: str, attempt: int) -> str:
        """
        Genera feedback para reintentar después de un fallo.
        """
        feedback_templates = {
            "Malformed JSON": "Tu respuesta anterior no era JSON válido. Asegúrate de responder con JSON estructurado.",
            "Agent returned None": "No recibí ninguna respuesta. Vuelve a procesar la tarea.",
            "Missing required fields": f"Tu respuesta está incompleta. Revisa los campos requeridos para el rol {agent_id}."
        }
        
        # Encontrar template apropiado
        for key in feedback_templates:
            if key in error:
                base_feedback = feedback_templates[key]
                break
        else:
            base_feedback = f"Error en tu respuesta: {error}"
        
        return f"""
[RECUPERACIÓN AUTOMÁTICA - Intento {attempt}]

{base_feedback}

Por favor, vuelve a intentar la tarea anterior con los siguientes ajustes:
1. Verifica que tu respuesta es JSON válido
2. Incluye todos los campos requeridos
3. No incluyas texto adicional fuera del JSON

Si el error persiste, proporciona un mensaje de error descriptivo.
"""
    
    @classmethod
    def execute_with_recovery(
        cls,
        agent_id: str,
        task_fn: Callable,
        max_retries: int = 3,
        on_failure: Optional[Callable] = None
    ) -> Dict:
        """
        Ejecuta una tarea con recuperación automática.
        
        Args:
            agent_id: ID del agente que ejecuta
            task_fn: Función que ejecuta la tarea (debe retornar Dict o str)
            max_retries: Número máximo de reintentos
            on_failure: Callback si todos los reintentos fallan
        
        Returns:
            Dict con resultado o error
        """
        last_error = None
        attempts = []
        
        for attempt in range(1, max_retries + 1):
            try:
                # Ejecutar tarea
                response = task_fn()
                
                # Validar respuesta
                is_valid, error_msg = cls.validate_agent_response(response, agent_id)
                
                if is_valid:
                    # Éxito
                    cls._log_recovery_event({
                        "agent_id": agent_id,
                        "status": "success",
                        "attempt": attempt,
                        "total_attempts": len(attempts)
                    })
                    
                    return {
                        "success": True,
                        "response": response,
                        "attempts": attempt,
                        "recovered": attempt > 1
                    }
                
                # Fallo de validación - preparar reintento
                last_error = error_msg
                feedback = cls.generate_feedback(error_msg, agent_id, attempt)
                
                attempts.append({
                    "attempt": attempt,
                    "error": error_msg,
                    "feedback_generated": True
                })
                
                cls._log_recovery_event({
                    "agent_id": agent_id,
                    "status": "retry",
                    "attempt": attempt,
                    "error": error_msg
                })
                
            except Exception as e:
                last_error = str(e)
                attempts.append({
                    "attempt": attempt,
                    "error": str(e),
                    "exception": True
                })
                
                cls._log_recovery_event({
                    "agent_id": agent_id,
                    "status": "exception",
                    "attempt": attempt,
                    "error": str(e)
                })
        
        # Todos los reintentos fallaron
        cls._log_recovery_event({
            "agent_id": agent_id,
            "status": "failed",
            "total_attempts": max_retries,
            "last_error": last_error
        })
        
        if on_failure:
            on_failure(agent_id, last_error, attempts)
        
        return {
            "success": False,
            "error": last_error,
            "attempts": attempts,
            "recovered": False
        }
    
    @classmethod
    def should_escalate_to_user(cls, agent_id: str, error: str) -> bool:
        """
        Determina si un error debe escalarse al usuario.
        """
        # Errores que siempre escalan
        critical_errors = [
            "security",
            "unauthorized",
            "permission denied",
            "api key",
            "authentication"
        ]
        
        error_lower = error.lower()
        return any(ce in error_lower for ce in critical_errors)
    
    @classmethod
    def get_recovery_stats(cls) -> Dict:
        """Obtiene estadísticas de recuperación."""
        if not RECOVERY_LOG.exists():
            return {"message": "No recovery events logged"}
        
        events = []
        with open(RECOVERY_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    continue
        
        if not events:
            return {"message": "No valid events"}
        
        stats = {
            "total_events": len(events),
            "success": len([e for e in events if e.get("status") == "success"]),
            "retries": len([e for e in events if e.get("status") == "retry"]),
            "failures": len([e for e in events if e.get("status") == "failed"]),
            "by_agent": {}
        }
        
        for event in events:
            agent = event.get("agent_id", "unknown")
            if agent not in stats["by_agent"]:
                stats["by_agent"][agent] = {"success": 0, "retry": 0, "failed": 0}
            
            status = event.get("status", "unknown")
            if status in stats["by_agent"][agent]:
                stats["by_agent"][agent][status] += 1
        
        return stats


# Ejemplo de uso
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats = GracefulRecovery.get_recovery_stats()
        print(json.dumps(stats, indent=2))
    else:
        print("""
AGCCE Graceful Recovery v1.0
Uso: python graceful_recovery.py stats
        """)
