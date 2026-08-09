#!/usr/bin/env python3
"""
AGCCE Plan Validator
Valida planes JSON contra el schema AGCCE_Plan_v1.

Uso: python validate_plan.py <plan.json>
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Importar utilidades comunes (con fix de encoding)
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info, make_header
except ImportError:
    # Fallback si no encuentra common.py
    class Colors:
        GREEN = RED = YELLOW = BLUE = RESET = BOLD = ''
    class Symbols:
        CHECK = '[OK]'
        CROSS = '[X]'
        WARN = '[!]'
        INFO = '[i]'
    def log_pass(msg): print(f"{Symbols.CHECK} PASS: {msg}")
    def log_fail(msg): print(f"{Symbols.CROSS} FAIL: {msg}")
    def log_warn(msg): print(f"{Symbols.WARN} WARN: {msg}")
    def log_info(msg): print(f"{Symbols.INFO} INFO: {msg}")
    def make_header(title, width=60): return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


def load_plan(path: str) -> Dict[str, Any]:
    """Carga el plan JSON desde archivo."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_required_fields(plan: Dict) -> List[str]:
    """Valida que existan los campos requeridos."""
    errors = []
    required = ['plan_id', 'version', 'created_at', 'objective', 'steps']
    
    for field in required:
        if field not in plan:
            errors.append(f"Campo requerido faltante: '{field}'")
    
    return errors


def validate_plan_id(plan: Dict) -> List[str]:
    """Valida formato del plan_id: PLAN-XXXXXXXX."""
    errors = []
    plan_id = plan.get('plan_id', '')
    
    if not re.match(r'^PLAN-[A-Z0-9]{8}$', plan_id):
        errors.append(f"plan_id invalido: '{plan_id}'. Formato esperado: PLAN-XXXXXXXX")
    
    return errors


def validate_steps(plan: Dict) -> List[str]:
    """Valida estructura y unicidad de pasos."""
    errors = []
    steps = plan.get('steps', [])
    
    if not steps:
        errors.append("El plan debe tener al menos un paso")
        return errors
    
    seen_ids = set()
    valid_actions = [
        'read_file', 'write_file', 'delete_file', 'run_command',
        'docker_compose_up', 'docker_run_tests', 'docker_fetch_logs',
        'lint_check', 'type_check', 'snyk_scan', 'git_commit'
    ]
    
    for i, step in enumerate(steps):
        step_id = step.get('id', '')
        
        # Validar formato de ID
        if not re.match(r'^S[0-9]{2}$', step_id):
            errors.append(f"Paso {i+1}: ID invalido '{step_id}'. Formato: S01, S02, etc.")
        
        # Validar unicidad
        if step_id in seen_ids:
            errors.append(f"ID duplicado: '{step_id}'")
        seen_ids.add(step_id)
        
        # Validar campos requeridos
        if 'action' not in step:
            errors.append(f"Paso {step_id}: falta 'action'")
        elif step['action'] not in valid_actions:
            errors.append(f"Paso {step_id}: accion invalida '{step['action']}'")
        
        if 'target' not in step:
            errors.append(f"Paso {step_id}: falta 'target'")
        
        # Validar HITL para acciones de escritura
        if step.get('action') in ['write_file', 'delete_file']:
            if not step.get('hitl_required', False):
                errors.append(f"Paso {step_id}: accion '{step['action']}' requiere hitl_required=true")
    
    return errors


def validate_dependencies(plan: Dict) -> List[str]:
    """Valida que no haya dependencias circulares."""
    errors = []
    steps = plan.get('steps', [])
    step_ids = {s.get('id') for s in steps}
    
    # Verificar que dependencias existan
    for step in steps:
        depends_on = step.get('depends_on', [])
        for dep in depends_on:
            if dep not in step_ids:
                errors.append(f"Paso {step.get('id')}: dependencia '{dep}' no existe")
    
    # Detectar ciclos (simple DFS)
    def has_cycle(step_id: str, visited: set, rec_stack: set) -> bool:
        visited.add(step_id)
        rec_stack.add(step_id)
        
        step = next((s for s in steps if s.get('id') == step_id), None)
        if step:
            for dep in step.get('depends_on', []):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
        
        rec_stack.remove(step_id)
        return False
    
    visited = set()
    for step in steps:
        step_id = step.get('id')
        if step_id not in visited:
            if has_cycle(step_id, visited, set()):
                errors.append(f"Dependencia circular detectada involucrando '{step_id}'")
    
    return errors


def validate_docker_mapping(plan: Dict) -> List[str]:
    """Valida que acciones Docker tengan script asociado."""
    errors = []
    docker_actions = ['docker_compose_up', 'docker_run_tests', 'docker_fetch_logs']
    
    for step in plan.get('steps', []):
        if step.get('action') in docker_actions:
            if not step.get('script'):
                errors.append(
                    f"Paso {step.get('id')}: accion Docker '{step.get('action')}' "
                    f"requiere campo 'script' (Directiva v1.1.0)"
                )
    
    return errors


def run_validation(plan_path: str) -> Tuple[bool, List[str], List[str]]:
    """Ejecuta todas las validaciones."""
    errors = []
    warnings = []
    
    try:
        plan = load_plan(plan_path)
    except json.JSONDecodeError as e:
        return False, [f"JSON invalido: {e}"], []
    except FileNotFoundError:
        return False, [f"Archivo no encontrado: {plan_path}"], []
    
    # Validaciones
    errors.extend(validate_required_fields(plan))
    errors.extend(validate_plan_id(plan))
    errors.extend(validate_steps(plan))
    errors.extend(validate_dependencies(plan))
    errors.extend(validate_docker_mapping(plan))
    
    # Warnings opcionales
    if not plan.get('pre_flight_check'):
        warnings.append("Falta seccion 'pre_flight_check'")
    if not plan.get('verification'):
        warnings.append("Falta seccion 'verification'")
    if not plan.get('evidence'):
        warnings.append("Falta seccion 'evidence'")
    
    success = len(errors) == 0
    return success, errors, warnings


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <plan.json>")
        sys.exit(1)
    
    plan_path = sys.argv[1]
    
    print(make_header("AGCCE Plan Validator v1.1.0"))
    
    log_info(f"Validando: {plan_path}")
    print()
    
    success, errors, warnings = run_validation(plan_path)
    
    # Mostrar warnings
    for warn in warnings:
        log_warn(warn)
    
    # Mostrar errores
    for error in errors:
        log_fail(error)
    
    print()
    
    if success:
        log_pass("Plan valido segun AGCCE_Plan_v1 schema")
        print(f"\n{Colors.GREEN}=== VALIDATION PASSED ==={Colors.RESET}\n")
        sys.exit(0)
    else:
        log_fail(f"{len(errors)} errores encontrados")
        print(f"\n{Colors.RED}=== VALIDATION FAILED ==={Colors.RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
