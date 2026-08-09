#!/usr/bin/env python3
"""
AGCCE Blackboard v1.0
Estado compartido entre agentes (Blackboard Architecture).

Permite:
- Lectura/escritura del estado global
- Historial de cambios
- Aislamiento de contexto por agente

Uso:
    from blackboard import Blackboard
    Blackboard.set("current_phase", "implementation")
    phase = Blackboard.get("current_phase")
"""

import os
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
STATE_FILE = LOGS_DIR / "current_state.json"
HISTORY_FILE = LOGS_DIR / "state_history.jsonl"

# Lock para thread-safety
_lock = threading.Lock()


class Blackboard:
    """Estado compartido entre agentes."""
    
    @classmethod
    def _ensure_dirs(cls):
        """Asegura que los directorios existan."""
        LOGS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def _load_state(cls) -> Dict:
        """Carga el estado actual."""
        cls._ensure_dirs()
        
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return cls._default_state()
        
        return cls._default_state()
    
    @classmethod
    def _default_state(cls) -> Dict:
        """Estado por defecto."""
        return {
            "_version": "1.0",
            "_created_at": datetime.now().isoformat(),
            "_updated_at": datetime.now().isoformat(),
            "current_phase": None,
            "current_agent": None,
            "current_plan_id": None,
            "current_step": 0,
            "context": {},
            "results": {},
            "errors": []
        }
    
    @classmethod
    def _save_state(cls, state: Dict):
        """Guarda el estado."""
        cls._ensure_dirs()
        
        state["_updated_at"] = datetime.now().isoformat()
        
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def _log_change(cls, key: str, old_value: Any, new_value: Any, agent: str = None):
        """Registra cambio en historial."""
        cls._ensure_dirs()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "key": key,
            "old_value": str(old_value)[:100] if old_value else None,
            "new_value": str(new_value)[:100] if new_value else None,
            "agent": agent
        }
        
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del estado.
        
        Args:
            key: Clave a obtener (soporta dot notation: "context.files")
            default: Valor por defecto si no existe
        """
        with _lock:
            state = cls._load_state()
            
            # Soportar dot notation
            keys = key.split('.')
            value = state
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    @classmethod
    def set(cls, key: str, value: Any, agent: str = None) -> bool:
        """
        Establece un valor en el estado.
        
        Args:
            key: Clave a establecer (soporta dot notation)
            value: Valor a guardar
            agent: Agente que hace el cambio (para auditoría)
        """
        with _lock:
            state = cls._load_state()
            
            # Obtener valor anterior para logging
            old_value = cls.get(key)
            
            # Soportar dot notation
            keys = key.split('.')
            target = state
            
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            
            target[keys[-1]] = value
            
            cls._save_state(state)
            cls._log_change(key, old_value, value, agent)
            
            return True
    
    @classmethod
    def update(cls, updates: Dict, agent: str = None) -> bool:
        """
        Actualiza múltiples valores.
        
        Args:
            updates: Dict con key-value pairs
            agent: Agente que hace el cambio
        """
        for key, value in updates.items():
            cls.set(key, value, agent)
        return True
    
    @classmethod
    def get_all(cls) -> Dict:
        """Obtiene todo el estado."""
        with _lock:
            return cls._load_state()
    
    @classmethod
    def clear(cls, keep_history: bool = True):
        """
        Limpia el estado a valores por defecto.
        
        Args:
            keep_history: Si mantener el historial de cambios
        """
        with _lock:
            cls._save_state(cls._default_state())
            
            if not keep_history and HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
    
    @classmethod
    def get_history(cls, limit: int = 50) -> List[Dict]:
        """
        Obtiene historial de cambios.
        
        Args:
            limit: Número máximo de entradas
        """
        cls._ensure_dirs()
        
        if not HISTORY_FILE.exists():
            return []
        
        history = []
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    history.append(json.loads(line))
                except:
                    continue
        
        return history[-limit:]
    
    # === Métodos de conveniencia para MAS ===
    
    @classmethod
    def start_phase(cls, phase: str, agent: str, plan_id: str = None):
        """Inicia una nueva fase."""
        cls.update({
            "current_phase": phase,
            "current_agent": agent,
            "current_plan_id": plan_id,
            "phase_started_at": datetime.now().isoformat()
        }, agent)
    
    @classmethod
    def end_phase(cls, result: Dict, agent: str):
        """Finaliza la fase actual."""
        phase = cls.get("current_phase")
        
        # Guardar resultado de la fase
        results = cls.get("results", {})
        results[phase] = {
            "completed_at": datetime.now().isoformat(),
            "agent": agent,
            "result": result
        }
        
        cls.set("results", results, agent)
        cls.set("current_phase", None, agent)
    
    @classmethod
    def add_error(cls, error: str, agent: str):
        """Registra un error."""
        errors = cls.get("errors", [])
        errors.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "error": error
        })
        cls.set("errors", errors, agent)
    
    @classmethod
    def handoff(cls, from_agent: str, to_agent: str, context: Dict):
        """
        Pasa el contexto de un agente a otro.
        
        Args:
            from_agent: Agente que entrega
            to_agent: Agente que recibe
            context: Contexto a pasar
        """
        cls.update({
            "current_agent": to_agent,
            f"handoff_{from_agent}_to_{to_agent}": {
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
        }, from_agent)


def main():
    """CLI para Blackboard."""
    import sys
    
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════╗
║               AGCCE Blackboard v1.0                         ║
║         Estado Compartido entre Agentes                     ║
╚══════════════════════════════════════════════════════════════╝

Uso:
  python blackboard.py get <key>
  python blackboard.py set <key> <value>
  python blackboard.py status
  python blackboard.py history [limit]
  python blackboard.py clear

Ejemplos:
  python blackboard.py get current_phase
  python blackboard.py set current_phase implementation
  python blackboard.py status
        """)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "get":
        key = sys.argv[2] if len(sys.argv) > 2 else ""
        if not key:
            print("Error: especifica una clave")
            return
        
        value = Blackboard.get(key)
        print(f"{key} = {json.dumps(value, indent=2, ensure_ascii=False)}")
    
    elif cmd == "set":
        if len(sys.argv) < 4:
            print("Error: especifica clave y valor")
            return
        
        key = sys.argv[2]
        value = sys.argv[3]
        
        # Intentar parsear como JSON
        try:
            value = json.loads(value)
        except:
            pass
        
        Blackboard.set(key, value, "cli")
        print(f"✓ {key} = {value}")
    
    elif cmd == "status":
        state = Blackboard.get_all()
        print(f"\n{'='*60}")
        print("  BLACKBOARD STATUS")
        print(f"{'='*60}")
        
        print(f"\nPhase:    {state.get('current_phase', 'None')}")
        print(f"Agent:    {state.get('current_agent', 'None')}")
        print(f"Plan ID:  {state.get('current_plan_id', 'None')}")
        print(f"Step:     {state.get('current_step', 0)}")
        print(f"Updated:  {state.get('_updated_at', 'Never')}")
        
        errors = state.get('errors', [])
        if errors:
            print(f"\nErrors: {len(errors)}")
    
    elif cmd == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        history = Blackboard.get_history(limit)
        
        print(f"\n{'='*60}")
        print("  CHANGE HISTORY")
        print(f"{'='*60}")
        
        for entry in history:
            print(f"\n[{entry.get('timestamp', '')}] {entry.get('agent', 'unknown')}")
            print(f"  {entry['key']}: {entry.get('old_value', 'None')} → {entry.get('new_value', 'None')}")
    
    elif cmd == "clear":
        Blackboard.clear()
        print("✓ Estado limpiado")
    
    else:
        print(f"Comando desconocido: {cmd}")


if __name__ == '__main__':
    main()
