"""
Módulo de Tracking de Operaciones - Determinismo vs LLM
Permite medir y visualizar qué porcentaje del proyecto usa lógica determinista vs llamadas a LLM.
"""
import json
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Literal, Optional
from dataclasses import dataclass, asdict

# Ubicación del log
LOG_PATH = Path(__file__).parent / "logs" / "execution_trace.jsonl"
LOG_PATH.parent.mkdir(exist_ok=True)

@dataclass
class OperationRecord:
    """Registro de una operación ejecutada."""
    timestamp: str
    operation_type: Literal["deterministic", "llm"]
    category: str
    function_name: str
    duration_ms: float
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    
def _log_operation(record: OperationRecord):
    """Escribe una operación al log."""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

def track_operation(
    op_type: Literal["deterministic", "llm"],
    category: str
):
    """
    Decorador para trackear operaciones.
    
    Uso:
        @track_operation(op_type="deterministic", category="schema_validation")
        def validate_spec(spec):
            ...
            
        @track_operation(op_type="llm", category="user_intent")
        def parse_user_request(prompt):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            
            # Crear resumen de input (primeros 100 chars del primer arg)
            input_summary = None
            if args:
                input_summary = str(args[0])[:100]
            
            # Crear resumen de output
            output_summary = None
            if result is not None:
                output_summary = str(result)[:100]
            
            record = OperationRecord(
                timestamp=datetime.now().isoformat(),
                operation_type=op_type,
                category=category,
                function_name=func.__name__,
                duration_ms=round(duration_ms, 2),
                input_summary=input_summary,
                output_summary=output_summary
            )
            _log_operation(record)
            
            return result
        return wrapper
    return decorator

def get_metrics() -> dict:
    """
    Calcula métricas de determinismo vs LLM.
    
    Returns:
        {
            "total_operations": int,
            "deterministic_pct": float,
            "llm_pct": float,
            "by_category": {
                "deterministic": {"schema_validation": 35, ...},
                "llm": {"user_intent": 12, ...}
            }
        }
    """
    if not LOG_PATH.exists():
        return {"total_operations": 0, "deterministic_pct": 0, "llm_pct": 0, "by_category": {}}
    
    deterministic_count = 0
    llm_count = 0
    categories = {"deterministic": {}, "llm": {}}
    
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            op_type = record.get("operation_type", "deterministic")
            category = record.get("category", "unknown")
            
            if op_type == "deterministic":
                deterministic_count += 1
            else:
                llm_count += 1
            
            if category not in categories[op_type]:
                categories[op_type][category] = 0
            categories[op_type][category] += 1
    
    total = deterministic_count + llm_count
    if total == 0:
        return {"total_operations": 0, "deterministic_pct": 0, "llm_pct": 0, "by_category": categories}
    
    return {
        "total_operations": total,
        "deterministic_pct": round((deterministic_count / total) * 100, 1),
        "llm_pct": round((llm_count / total) * 100, 1),
        "by_category": categories
    }

def print_dashboard():
    """Imprime el dashboard de métricas en formato visual."""
    metrics = get_metrics()
    
    det_pct = metrics["deterministic_pct"]
    llm_pct = metrics["llm_pct"]
    
    # Barras de progreso
    det_bar = "█" * int(det_pct / 5) + "░" * (20 - int(det_pct / 5))
    llm_bar = "█" * int(llm_pct / 5) + "░" * (20 - int(llm_pct / 5))
    
    print("┌─────────────────────────────────────┐")
    print("│ 📊 Métricas de Ejecución            │")
    print("├─────────────────────────────────────┤")
    print(f"│ Determinismo: {det_bar} {det_pct}%    │")
    print(f"│ LLM:          {llm_bar} {llm_pct}%    │")
    print("├─────────────────────────────────────┤")
    
    # Desglose por categoría
    for op_type, cats in metrics["by_category"].items():
        if cats:
            print(f"│ {op_type.upper()} usado en:                 │")
            for cat, count in cats.items():
                pct = round((count / metrics["total_operations"]) * 100, 1) if metrics["total_operations"] > 0 else 0
                print(f"│  • {cat}: {pct}%              │")
    
    print("└─────────────────────────────────────┘")

# Ejemplo de uso
if __name__ == "__main__":
    # Simular algunas operaciones
    @track_operation(op_type="deterministic", category="schema_validation")
    def validate_schema(data):
        return True
    
    @track_operation(op_type="llm", category="user_intent")
    def parse_intent(prompt):
        return {"intent": "create_project"}
    
    # Ejecutar operaciones de ejemplo
    validate_schema({"test": "data"})
    validate_schema({"another": "test"})
    parse_intent("Quiero crear un proyecto de React")
    
    # Mostrar dashboard
    print_dashboard()
