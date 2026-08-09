#!/usr/bin/env python3
"""
n8n Workflow Validator

Validates n8n workflow JSON files for structural correctness,
connection integrity, and common issues.

Usage:
    python workflow_validator.py workflow.json
    python workflow_validator.py --help
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Resultado de validación"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]


def validate_workflow(workflow: Dict[str, Any]) -> ValidationResult:
    """Valida un workflow de n8n completo."""
    errors: List[str] = []
    warnings: List[str] = []
    info: List[str] = []
    
    # Validar estructura básica
    required_keys = ['nodes', 'connections']
    for key in required_keys:
        if key not in workflow:
            errors.append(f"Missing required key: '{key}'")
    
    if errors:
        return ValidationResult(False, errors, warnings, info)
    
    nodes = workflow.get('nodes', [])
    connections = workflow.get('connections', {})
    
    # Crear mapa de nodos
    node_names: Set[str] = set()
    node_map: Dict[str, Dict] = {}
    
    for node in nodes:
        name = node.get('name', '')
        if not name:
            errors.append("Node found without 'name' property")
            continue
            
        if name in node_names:
            errors.append(f"Duplicate node name: '{name}'")
        else:
            node_names.add(name)
            node_map[name] = node
        
        # Validar propiedades básicas del nodo
        if 'type' not in node:
            errors.append(f"Node '{name}' missing 'type' property")
        
        if 'position' not in node:
            warnings.append(f"Node '{name}' missing 'position' (may cause UI issues)")
        elif not isinstance(node['position'], list) or len(node['position']) != 2:
            warnings.append(f"Node '{name}' has invalid position format")
    
    # Validar conexiones
    for source_node, connections_data in connections.items():
        if source_node not in node_names:
            errors.append(f"Connection from non-existent node: '{source_node}'")
            continue
        
        if not isinstance(connections_data, dict):
            errors.append(f"Invalid connection format for '{source_node}'")
            continue
        
        for output_type, outputs in connections_data.items():
            if not isinstance(outputs, list):
                continue
                
            for output_index, targets in enumerate(outputs):
                if not isinstance(targets, list):
                    continue
                    
                for target in targets:
                    target_node = target.get('node', '')
                    if target_node and target_node not in node_names:
                        errors.append(
                            f"Connection to non-existent node: "
                            f"'{source_node}' -> '{target_node}'"
                        )
    
    # Detectar nodos huérfanos (sin conexiones de entrada ni salida)
    connected_nodes = set()
    
    for source_node, connections_data in connections.items():
        connected_nodes.add(source_node)
        for output_type, outputs in connections_data.items():
            if not isinstance(outputs, list):
                continue
            for targets in outputs:
                if not isinstance(targets, list):
                    continue
                for target in targets:
                    if 'node' in target:
                        connected_nodes.add(target['node'])
    
    # Excluir triggers de la validación de huérfanos
    trigger_types = [
        'n8n-nodes-base.manualTrigger',
        'n8n-nodes-base.scheduleTrigger',
        'n8n-nodes-base.webhook',
        'n8n-nodes-base.cron',
        'n8n-nodes-base.executeWorkflowTrigger',
        'n8n-nodes-base.errorTrigger',
    ]
    
    for node in nodes:
        name = node.get('name', '')
        node_type = node.get('type', '')
        
        # Triggers no necesitan conexiones de entrada
        if any(t in node_type for t in trigger_types):
            continue
            
        if name and name not in connected_nodes:
            warnings.append(f"Orphan node (no connections): '{name}'")
    
    # Validar credenciales referenciadas
    for node in nodes:
        credentials = node.get('credentials', {})
        if credentials:
            for cred_type, cred_data in credentials.items():
                if not cred_data.get('id') and not cred_data.get('name'):
                    warnings.append(
                        f"Node '{node.get('name')}' references credentials "
                        f"'{cred_type}' without ID"
                    )
    
    # Detectar expresiones potencialmente problemáticas
    def check_expressions(obj: Any, path: str = "") -> List[str]:
        issues = []
        if isinstance(obj, str):
            if '{{' in obj:
                # Verificar balance de llaves
                open_count = obj.count('{{')
                close_count = obj.count('}}')
                if open_count != close_count:
                    issues.append(f"Unbalanced expression braces at {path}: {obj[:50]}...")
                
                # Detectar patrones problemáticos comunes
                if '$json.' in obj and '?.' not in obj and '|| ' not in obj:
                    # Acceso sin optional chaining ni fallback
                    pass  # Podría ser warning pero muy ruidoso
                    
        elif isinstance(obj, dict):
            for key, value in obj.items():
                issues.extend(check_expressions(value, f"{path}.{key}"))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                issues.extend(check_expressions(item, f"{path}[{i}]"))
        return issues
    
    expression_issues = check_expressions(workflow, "workflow")
    for issue in expression_issues:
        warnings.append(issue)
    
    # Información general
    info.append(f"Total nodes: {len(nodes)}")
    info.append(f"Total connections: {sum(len(c.get('main', [[]])[0]) if 'main' in c else 0 for c in connections.values())}")
    
    triggers = [n for n in nodes if any(t in n.get('type', '') for t in trigger_types)]
    info.append(f"Trigger nodes: {len(triggers)}")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings, info)


def validate_file(filepath: Path) -> ValidationResult:
    """Valida un archivo JSON de workflow."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
    except json.JSONDecodeError as e:
        return ValidationResult(
            False, 
            [f"Invalid JSON: {e}"], 
            [], 
            []
        )
    except FileNotFoundError:
        return ValidationResult(
            False,
            [f"File not found: {filepath}"],
            [],
            []
        )
    
    return validate_workflow(workflow)


def print_result(result: ValidationResult, verbose: bool = False) -> None:
    """Imprime el resultado de la validación."""
    if result.is_valid:
        print("✅ Workflow is valid")
    else:
        print("❌ Workflow is INVALID")
    
    print()
    
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  ❌ {error}")
        print()
    
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
        print()
    
    if verbose and result.info:
        print("INFO:")
        for info in result.info:
            print(f"  ℹ️  {info}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate n8n workflow JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s workflow.json           # Validate single file
  %(prog)s *.json                  # Validate multiple files
  %(prog)s -v workflow.json        # Verbose output
  %(prog)s --json workflow.json    # JSON output
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        type=Path,
        help='Workflow JSON file(s) to validate'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    all_valid = True
    results = {}
    
    for filepath in args.files:
        if not filepath.exists():
            print(f"File not found: {filepath}")
            all_valid = False
            continue
        
        result = validate_file(filepath)
        results[str(filepath)] = {
            'valid': result.is_valid,
            'errors': result.errors,
            'warnings': result.warnings,
            'info': result.info
        }
        
        if not result.is_valid:
            all_valid = False
        
        if not args.json:
            print(f"\n{'='*50}")
            print(f"File: {filepath}")
            print('='*50)
            print_result(result, args.verbose)
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
