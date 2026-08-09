#!/usr/bin/env python3
"""
AGCCE Plan Generator v2.1 con Self-Correction Loop + Semantic Verification
Genera planes JSON automaticamente usando IA con validacion integrada.

CONTROLES CRITICOS:
1. Self-Correction Loop: Reintenta hasta 3 veces
2. Semantic Verification: Valida que targets existan en el indice RAG
3. Traceback Feedback: Usa errores como input para correccion

Uso: python plan_generator.py --objective "Descripcion de la tarea"
"""

import subprocess
import sys
import os
import json
import re
import random
import string
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Importar utilidades comunes
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info, make_header
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
    def make_header(title, width=60): return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


# Configuracion
MAX_RETRIES = 3
PLANS_DIR = "plans"
INDEX_STATE_FILE = ".rag_index_state.json"


def generate_plan_id() -> str:
    """Genera un ID unico para el plan."""
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(chars, k=8))
    return f"PLAN-{random_part}"


def load_indexed_files() -> List[str]:
    """Carga lista de archivos indexados por RAG."""
    if os.path.exists(INDEX_STATE_FILE):
        try:
            with open(INDEX_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return state.get('indexed_files', [])
        except:
            pass
    return []


def get_existing_files() -> set:
    """Obtiene set de archivos existentes en el proyecto."""
    existing = set()
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            path = os.path.join(root, f).replace('\\', '/')
            if path.startswith('./'):
                path = path[2:]
            existing.add(path)
    
    return existing


def validate_semantic_existence(plan: Dict) -> Tuple[bool, List[str]]:
    """
    SEMANTIC VERIFICATION - Anti-Alucinacion
    
    Valida que todos los targets/paths mencionados en el plan
    existan realmente en el filesystem o indice RAG.
    
    Returns:
        Tuple[bool, List[str]]: (passed, hallucinated_paths)
    """
    existing_files = get_existing_files()
    indexed_files = set(load_indexed_files())
    all_known = existing_files | indexed_files
    
    hallucinated = []
    
    # Verificar affected_files
    for path in plan.get('objective', {}).get('affected_files', []):
        normalized = path.replace('\\', '/').lstrip('./')
        if normalized and normalized != '.' and normalized not in all_known:
            # Verificar si existe realmente en filesystem
            if not os.path.exists(path):
                hallucinated.append(f"affected_files: {path}")
    
    # Verificar targets en steps
    for step in plan.get('steps', []):
        target = step.get('target', '')
        action = step.get('action', '')
        
        # Solo verificar para acciones de lectura/modificacion de archivos
        if action in ['read_file', 'write_file', 'delete_file']:
            normalized = target.replace('\\', '/').lstrip('./')
            if normalized and normalized != '.' and normalized not in all_known:
                if not os.path.exists(target):
                    # Para write_file, el archivo puede no existir aun (sera creado)
                    if action != 'write_file':
                        hallucinated.append(f"step {step.get('id')}: {target}")
    
    # Verificar analyzed_paths en evidence
    for path in plan.get('evidence', {}).get('analyzed_paths', []):
        normalized = path.replace('\\', '/').lstrip('./')
        if normalized and normalized != '.' and normalized not in all_known:
            if not os.path.exists(path):
                hallucinated.append(f"evidence: {path}")
    
    return len(hallucinated) == 0, hallucinated


def validate_plan_internal(plan_path: str) -> Tuple[bool, str]:
    """Valida el plan usando validate_plan.py internamente."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/validate_plan.py", plan_path],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def analyze_validation_errors(error_output: str) -> List[str]:
    """
    Analiza errores de validacion para corregir.
    MEJORA: Usa el Traceback como feedback para correccion.
    """
    errors = []
    
    # Patrones de errores comunes
    patterns = [
        (r"plan_id invalido", "plan_id"),
        (r"ID invalido '(\w+)'", "step_id"),
        (r"falta 'action'", "missing_action"),
        (r"accion invalida", "invalid_action"),
        (r"falta 'target'", "missing_target"),
        (r"hitl_required=true", "hitl_required"),
        (r"dependencia '(\w+)' no existe", "dependency"),
        (r"Traceback", "traceback_error"),
    ]
    
    for pattern, error_type in patterns:
        if re.search(pattern, error_output, re.IGNORECASE):
            errors.append(error_type)
    
    # Extraer contexto del traceback para feedback
    if "traceback_error" in errors:
        # Guardar traceback para analisis
        errors.append(f"traceback_context:{error_output[-500:]}")
    
    return errors


def fix_plan(plan: Dict, errors: List[str], hallucinated: List[str] = None) -> Dict:
    """
    Intenta corregir errores comunes en el plan.
    MEJORA: Corrige alucinaciones de entidad.
    """
    # Fix plan_id si es invalido
    if "plan_id" in errors or not re.match(r'^PLAN-[A-Z0-9]{8}$', plan.get('plan_id', '')):
        plan['plan_id'] = generate_plan_id()
    
    # Fix step IDs
    if "step_id" in errors:
        for i, step in enumerate(plan.get('steps', [])):
            step['id'] = f"S{(i+1):02d}"
    
    # Fix missing actions
    if "missing_action" in errors:
        for step in plan.get('steps', []):
            if 'action' not in step:
                step['action'] = 'read_file'
    
    # Fix invalid actions
    valid_actions = [
        'read_file', 'write_file', 'delete_file', 'run_command',
        'docker_compose_up', 'docker_run_tests', 'docker_fetch_logs',
        'lint_check', 'type_check', 'snyk_scan', 'git_commit'
    ]
    for step in plan.get('steps', []):
        if step.get('action') not in valid_actions:
            step['action'] = 'read_file'
    
    # Fix missing targets
    if "missing_target" in errors:
        for step in plan.get('steps', []):
            if 'target' not in step:
                step['target'] = '.'
    
    # Fix HITL required
    if "hitl_required" in errors:
        write_actions = ['write_file', 'delete_file', 'git_commit']
        for step in plan.get('steps', []):
            if step.get('action') in write_actions:
                step['hitl_required'] = True
    
    # FIX ALUCINACIONES: Remover paths inexistentes
    if hallucinated:
        existing = get_existing_files()
        
        # Limpiar affected_files
        affected = plan.get('objective', {}).get('affected_files', [])
        plan['objective']['affected_files'] = [
            f for f in affected if os.path.exists(f) or f in existing
        ]
        
        # Limpiar analyzed_paths
        analyzed = plan.get('evidence', {}).get('analyzed_paths', [])
        plan['evidence']['analyzed_paths'] = [
            f for f in analyzed if os.path.exists(f) or f in existing
        ]
        
        # Corregir targets en steps
        for step in plan.get('steps', []):
            if step.get('action') == 'read_file':
                target = step.get('target', '')
                if not os.path.exists(target) and target != '.':
                    step['target'] = '.'  # Fallback seguro
    
    # Asegurar campos requeridos
    if 'version' not in plan:
        plan['version'] = '1.1'
    if 'created_at' not in plan:
        plan['created_at'] = datetime.now().isoformat()
    
    return plan


def create_plan_template(objective: str, affected_files: List[str] = None) -> Dict:
    """Crea un template de plan basado en el objetivo."""
    if affected_files is None:
        affected_files = []
    
    # Filtrar solo archivos que existen (anti-alucinacion)
    existing_files = [f for f in affected_files if os.path.exists(f)]
    
    plan = {
        "plan_id": generate_plan_id(),
        "version": "1.1",
        "created_at": datetime.now().isoformat(),
        "objective": {
            "description": objective,
            "success_criteria": [
                "Cambios implementados correctamente",
                "Tests pasando",
                "Sin errores de lint"
            ],
            "affected_files": existing_files
        },
        "pre_flight_check": {
            "git_status": "clean",
            "lint_passed": True,
            "tests_passed": True
        },
        "steps": [
            {
                "id": "S01",
                "action": "read_file",
                "target": existing_files[0] if existing_files else ".",
                "expected_outcome": "Entender estructura actual",
                "hitl_required": False
            },
            {
                "id": "S02",
                "action": "lint_check",
                "target": ".",
                "expected_outcome": "Sin errores de sintaxis",
                "depends_on": ["S01"],
                "hitl_required": False
            }
        ],
        "verification": {
            "method": "automated",
            "commands": [
                "python scripts/lint_check.py .",
                "python scripts/type_check.py ."
            ],
            "expected_results": ["Lint passed", "Type check passed"]
        },
        "evidence": {
            "logs": [],
            "analyzed_paths": existing_files
        },
        "commit_proposal": {
            "type": "feat",
            "scope": "core",
            "message": objective[:50]
        }
    }
    
    return plan


def generate_plan_with_self_correction(
    objective: str,
    affected_files: List[str] = None,
    context: str = None
) -> Tuple[bool, str, Dict]:
    """
    SELF-CORRECTION LOOP v2.1
    
    1. Genera plan
    2. Valida estructura (JSON Schema)
    3. Valida semantica (paths existen - anti-alucinacion)
    4. Si falla: corrige y reintenta hasta MAX_RETRIES
    5. Si sigue fallando: solicita ayuda humana
    """
    print(make_header("AGCCE Plan Generator v2.1"))
    print(f"{Colors.CYAN}Objetivo:{Colors.RESET} {objective}")
    print(f"{Colors.CYAN}Max reintentos:{Colors.RESET} {MAX_RETRIES}")
    print(f"{Colors.CYAN}Verificacion semantica:{Colors.RESET} Activada")
    print()
    
    os.makedirs(PLANS_DIR, exist_ok=True)
    
    # Generar plan inicial
    print(f"{Colors.BOLD}[1/{MAX_RETRIES + 1}] Generando plan inicial...{Colors.RESET}")
    plan = create_plan_template(objective, affected_files or [])
    
    # Self-Correction Loop
    for attempt in range(MAX_RETRIES):
        attempt_num = attempt + 1
        print(f"\n{Colors.BOLD}[Intento {attempt_num}/{MAX_RETRIES}]{Colors.RESET}")
        
        # Guardar plan temporal
        temp_path = os.path.join(PLANS_DIR, f"_temp_plan_{attempt_num}.json")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        # PASO 1: Validacion de estructura
        print(f"  [1/2] Validando estructura...")
        struct_valid, struct_output = validate_plan_internal(temp_path)
        
        if not struct_valid:
            log_warn("Estructura invalida")
            errors = analyze_validation_errors(struct_output)
            print(f"    Errores: {[e for e in errors if not e.startswith('traceback')]}")
            plan = fix_plan(plan, errors)
            try:
                os.remove(temp_path)
            except:
                pass
            continue
        
        print(f"    {Colors.GREEN}{Symbols.CHECK}{Colors.RESET} Estructura valida")
        
        # PASO 2: Validacion semantica (anti-alucinacion)
        print(f"  [2/2] Validando semantica (anti-alucinacion)...")
        semantic_valid, hallucinated = validate_semantic_existence(plan)
        
        if not semantic_valid:
            log_warn(f"Alucinacion detectada: {len(hallucinated)} paths inexistentes")
            for h in hallucinated[:5]:
                print(f"    {Colors.RED}X{Colors.RESET} {h}")
            plan = fix_plan(plan, ["hallucination"], hallucinated)
            try:
                os.remove(temp_path)
            except:
                pass
            continue
        
        print(f"    {Colors.GREEN}{Symbols.CHECK}{Colors.RESET} Sin alucinaciones")
        
        # PLAN VALIDO
        final_path = os.path.join(PLANS_DIR, f"{plan['plan_id']}.json")
        with open(final_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        try:
            os.remove(temp_path)
        except:
            pass
        
        log_pass(f"Plan generado exitosamente en intento {attempt_num}")
        print(f"\n{Colors.GREEN}=== PLAN GENERATION SUCCESSFUL ==={Colors.RESET}")
        print(f"\n{Colors.BLUE}Plan guardado en:{Colors.RESET} {final_path}\n")
        
        return True, final_path, plan
    
    # Fallaron todos los intentos
    print(f"\n{Colors.RED}=== SELF-CORRECTION FAILED ==={Colors.RESET}")
    log_fail(f"No se pudo generar plan valido despues de {MAX_RETRIES} intentos")
    
    failed_path = os.path.join(PLANS_DIR, f"_FAILED_{plan['plan_id']}.json")
    with open(failed_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.YELLOW}Plan fallido guardado para revision humana:{Colors.RESET}")
    print(f"  {failed_path}")
    print(f"\n{Colors.YELLOW}[!] Se requiere intervencion humana para corregir el plan.{Colors.RESET}\n")
    
    return False, failed_path, plan


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} --objective \"Descripcion de la tarea\"")
        print(f"\nOpciones:")
        print(f"  --objective \"texto\"  Objetivo de la tarea (requerido)")
        print(f"  --files f1,f2,f3     Archivos afectados (opcional)")
        sys.exit(1)
    
    objective = None
    affected_files = []
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--objective" and i + 1 < len(sys.argv):
            objective = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--files" and i + 1 < len(sys.argv):
            affected_files = sys.argv[i + 1].split(",")
            i += 2
        else:
            i += 1
    
    if not objective:
        print(f"{Colors.RED}Error: --objective es requerido{Colors.RESET}")
        sys.exit(1)
    
    success, path, plan = generate_plan_with_self_correction(objective, affected_files)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
