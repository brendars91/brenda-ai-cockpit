#!/usr/bin/env python3
"""
AGCCE Type Check
Ejecuta verificación de tipos estáticos en código Python.

Uso: python type_check.py <archivo_o_directorio>
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Ejecuta un comando y retorna código, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Comando no encontrado: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -2, "", "Timeout ejecutando comando"


def check_mypy(target: str) -> Tuple[bool, str, int, int]:
    """Ejecuta mypy para verificación de tipos."""
    code, stdout, stderr = run_command([
        "mypy",
        "--ignore-missing-imports",
        "--no-error-summary",
        "--show-column-numbers",
        target
    ])
    
    if code == -1:
        return True, "mypy no instalado - instalar con: pip install mypy", 0, 0
    
    # Contar errores y warnings
    lines = stdout.strip().split("\n") if stdout.strip() else []
    errors = sum(1 for l in lines if ": error:" in l)
    warnings = sum(1 for l in lines if ": warning:" in l or ": note:" in l)
    
    if code == 0:
        return True, "mypy: Sin errores de tipos", 0, warnings
    
    return False, stdout, errors, warnings


def check_pyright(target: str) -> Tuple[bool, str, int]:
    """Ejecuta pyright si está disponible."""
    code, stdout, stderr = run_command([
        "pyright",
        "--outputjson",
        target
    ])
    
    if code == -1:
        return True, "pyright no instalado (opcional)", 0
    
    try:
        import json
        data = json.loads(stdout)
        error_count = data.get("summary", {}).get("errorCount", 0)
        
        if error_count == 0:
            return True, "pyright: Sin errores", 0
        
        # Formatear errores
        errors = []
        for diag in data.get("generalDiagnostics", [])[:5]:
            file = diag.get("file", "")
            line = diag.get("range", {}).get("start", {}).get("line", 0)
            msg = diag.get("message", "")
            errors.append(f"  {file}:{line}: {msg}")
        
        return False, "\n".join(errors), error_count
    except:
        if code == 0:
            return True, "pyright: Sin errores", 0
        return False, stderr or stdout, 1


def analyze_type_coverage(target: str) -> str:
    """Analiza cobertura de type hints en el código."""
    if os.path.isfile(target):
        files = [Path(target)]
    else:
        files = list(Path(target).rglob("*.py"))
    
    total_functions = 0
    typed_functions = 0
    
    import ast
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1
                    # Tiene return annotation o algún argumento con annotation
                    has_types = (
                        node.returns is not None or
                        any(arg.annotation is not None for arg in node.args.args)
                    )
                    if has_types:
                        typed_functions += 1
        except:
            continue
    
    if total_functions == 0:
        return "No se encontraron funciones para analizar"
    
    coverage = (typed_functions / total_functions) * 100
    return f"Type coverage: {typed_functions}/{total_functions} funciones ({coverage:.1f}%)"


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <archivo_o_directorio>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if not os.path.exists(target):
        print(f"{Colors.RED}Error: '{target}' no existe{Colors.RESET}")
        sys.exit(1)
    
    print(f"\n{Colors.BOLD}══════════════════════════════════════════════════════════")
    print(f"  AGCCE Type Check v1.0")
    print(f"══════════════════════════════════════════════════════════{Colors.RESET}\n")
    
    print(f"{Colors.BLUE}ℹ Analizando:{Colors.RESET} {target}\n")
    
    all_passed = True
    
    # mypy check
    passed, msg, errors, warnings = check_mypy(target)
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} mypy")
    if not passed:
        all_passed = False
        for line in msg.split("\n")[:10]:
            print(f"        {line}")
        print(f"        ... ({errors} errores, {warnings} warnings)")
    elif "no instalado" in msg:
        print(f"        {Colors.YELLOW}{msg}{Colors.RESET}")
    
    # pyright check (opcional)
    passed, msg, error_count = check_pyright(target)
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} pyright")
    if not passed:
        # pyright es opcional, no marca fallo global
        for line in msg.split("\n")[:5]:
            print(f"        {line}")
    elif "no instalado" in msg:
        print(f"        {Colors.YELLOW}{msg}{Colors.RESET}")
    
    # Type coverage analysis
    coverage = analyze_type_coverage(target)
    print(f"\n  {Colors.BLUE}ℹ{Colors.RESET} {coverage}")
    
    print()
    
    if all_passed:
        print(f"{Colors.GREEN}═══ TYPE CHECK PASSED ═══{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}═══ TYPE CHECK FAILED ═══{Colors.RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
