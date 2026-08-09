"""
GemPlan Generator - Combina Plan JSON de AGCCE con Gem Bundle

Este script genera automáticamente un GemPlan a partir de:
- Un Gem Bundle compilado
- Objetivo del usuario
- Lista de tareas a ejecutar

Uso:
    python gem_plan_generator.py --gem gems/mi_gem.json --goal "Objetivo..." --output plans/gemplan.json
    python gem_plan_generator.py --interactive
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse

try:
    from gem_loader import GemLoader
except ImportError:
    print("ERROR: gem_loader.py not found. Please ensure it's in the scripts/ directory.")
    sys.exit(1)


class GemPlanGenerator:
    """Generador de GemPlans (Plan AGCCE + Gem Bundle)"""
    
    def __init__(self):
        self.loader = GemLoader()
    
    def generate_gemplan(
        self,
        gem_bundle_path: str,
        user_goal: str,
        tasks: List[Dict],
        plan_id: Optional[str] = None,
        constraints: Optional[Dict] = None,
        agent_overrides: Optional[Dict] = None
    ) -> Dict:
        """
        Genera un GemPlan completo.
        
        Args:
            gem_bundle_path: Path al Gem Bundle
            user_goal: Objetivo del usuario
            tasks: Lista de tareas estilo AGCCE Plan
            plan_id: ID del plan (auto-generado si None)
            constraints: Restricciones opcionales
            agent_overrides: Overrides de configuración
        
        Returns:
            GemPlan dict (schema AGCCE_GemPlan_v1)
        """
        # Cargar metadata del Gem
        gem_info = self.loader.get_gem_info(gem_bundle_path)
        
        # Auto-generar plan_id si no se proporciona
        if plan_id is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            plan_id = f"gemplan_{gem_info['use_case_id']}_{timestamp}"
        
        # Defaults de agent_overrides
        if agent_overrides is None:
            agent_overrides = {
                "system_prompt_source": "gem",
                "model_source": "gem",
                "policies_source": "strictest",
                "mcps_source": "intersection"
            }
        
        return {
            # Compatible con AGCCE Plan v1
            "plan_id": plan_id,
            "goal": user_goal,
            "tasks": tasks,
            
            # Extensión con Gem
            "gem_configuration": {
                "gem_bundle_path": gem_bundle_path,
                "gem_version": gem_info['version'],
                "gem_use_case_id": gem_info['use_case_id'],
                "risk_score": gem_info['risk_score'],
                "agent_overrides": agent_overrides,
                "enable_gem_validation": True
            },
            
            # Constraints opcionales
            "constraints": constraints or {},
            
            # Metadata
            "schema_version": "AGCCE_GemPlan_v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "created_by": "gem_plan_generator"
        }
    
    def interactive_mode(self):
        """Modo interactivo para crear un GemPlan"""
        print("\n" + "="*60)
        print("  GemPlan Generator - Modo Interactivo")
        print("="*60 + "\n")
        
        # Paso 1: Seleccionar Gem
        print("[1/4] Seleccionar Gem Bundle\n")
        
        gems_dir = Path("gems")
        if not gems_dir.exists():
            print("ERROR: Directorio gems/ no encontrado")
            return None
        
        gems = list(gems_dir.glob("*.json"))
        if not gems:
            print("ERROR: No hay Gem Bundles en gems/")
            print("Copia un Gem Bundle compilado a la carpeta gems/")
            return None
        
        print("Gems disponibles:")
        for i, gem in enumerate(gems, 1):
            # Obtener info básica
            try:
                info = self.loader.get_gem_info(str(gem))
                print(f"  [{i}] {info['use_case_id']} v{info['version']}")
                print(f"      Model: {info['model']}, Risk: {info['risk_score']}")
            except:
                print(f"  [{i}] {gem.name} (error al leer)")
        
        while True:
            try:
                choice = int(input("\nSelecciona un Gem [1-{}]: ".format(len(gems))))
                if 1 <= choice <= len(gems):
                    selected_gem = str(gems[choice - 1])
                    break
            except:
                pass
            print("Opción inválida")
        
        print(f"\n✓ Gem seleccionado: {Path(selected_gem).name}\n")
        
        # Paso 2: Objetivo
        print("[2/4] Definir Objetivo\n")
        user_goal = input("¿Qué quieres que haga  AGCCE? (ej: 'Implementar autenticación OAuth2')\n> ").strip()
        
        if not user_goal:
            print("ERROR: Objetivo no puede estar vacío")
            return None
        
        print(f"\n✓ Objetivo: {user_goal}\n")
        
        # Paso 3: Tareas
        print("[3/4] Definir Tareas\n")
        print("Define las tareas para cada agente MAS:")
        print("  - researcher: Buscar contexto")
        print("  - architect: Diseñar solución")
        print("  - constructor: Escribir código")
        print("  - auditor: Revisar seguridad")
        print("  - tester: Crear tests\n")
        
        tasks = []
        agents = ["researcher", "architect", "constructor", "auditor", "tester"]
        
        for agent in agents:
            action = input(f"[{agent}] Acción (Enter para omitir): ").strip()
            if action:
                task = {
                    "agent": agent,
                    "action": action
                }
                
                # Contexto opcional
                context = input(f"    Contexto adicional (Enter para omitir): ").strip()
                if context:
                    task["context"] = context
                
                # Output path para constructor
                if agent == "constructor":
                    output = input(f"    Path de salida (ej: scripts/auth.py): ").strip()
                    if output:
                        task["output_path"] = output
                
                tasks.append(task)
        
        if not tasks:
            print("\nERROR: Debes definir al menos una tarea")
            return None
        
        print(f"\n✓ {len(tasks)} tareas definidas\n")
        
        # Paso 4: Output
        print("[4/4] Guardar GemPlan\n")
        
        default_name = f"gemplan_{Path(selected_gem).stem}.json"
        output_path = input(f"Nombre del archivo [{default_name}]: ").strip() or default_name
        
        if not output_path.endswith('.json'):
            output_path += '.json'
        
        output_path = os.path.join("plans", output_path)
        
        # Generar GemPlan
        gemplan = self.generate_gemplan(
            gem_bundle_path=selected_gem,
            user_goal=user_goal,
            tasks=tasks
        )
        
        # Guardar
        os.makedirs("plans", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gemplan, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ GemPlan guardado: {output_path}")
        print(f"\nPara ejecutar:")
        print(f"  python scripts/orchestrator.py {output_path}")
        
        return gemplan


def main():
    parser = argparse.ArgumentParser(
        description="Genera GemPlans para AGCCE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Modo interactivo
  python gem_plan_generator.py --interactive
  
  # Modo directo
  python gem_plan_generator.py \\
    --gem gems/sap_cost_analyzer_v1.0.0.json \\
    --goal "Analizar costos Q4 2025" \\
    --output plans/sap_cost_analysis.json
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Modo interactivo (recomendado)')
    parser.add_argument('--gem', type=str,
                        help='Path al Gem Bundle')
    parser.add_argument('--goal', type=str,
                        help='Objetivo del usuario')
    parser.add_argument('--output', type=str,
                        help='Path de salida del GemPlan')
    parser.add_argument('--tasks-json', type=str,
                        help='Path a JSON con lista de tareas')
    
    args = parser.parse_args()
    
    generator = GemPlanGenerator()
    
    # Modo interactivo
    if args.interactive or not args.gem:
        generator.interactive_mode()
        return
    
    # Modo directo
    if not args.goal:
        print("ERROR: --goal es requerido en modo directo")
        sys.exit(1)
    
    # Cargar tareas desde JSON o crear tarea básica
    if args.tasks_json:
        with open(args.tasks_json) as f:
            tasks = json.load(f)
    else:
        # Tarea básica por defecto
        tasks = [
            {"agent": "researcher", "action": "search_context"},
            {"agent": "architect", "action": "design_solution"},
            {"agent": "constructor", "action": "implement_code"},
            {"agent": "auditor", "action": "security_review"},
            {"agent": "tester", "action": "create_tests"}
        ]
    
    # Generar GemPlan
    gemplan = generator.generate_gemplan(
        gem_bundle_path=args.gem,
        user_goal=args.goal,
        tasks=tasks
    )
    
    # Output
    output_path = args.output or "plans/gemplan_generated.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(gemplan, f, indent=2, ensure_ascii=False)
    
    print(f"✓ GemPlan generado: {output_path}")


if __name__ == "__main__":
    main()
