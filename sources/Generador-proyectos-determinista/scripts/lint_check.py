#!/usr/bin/env python3
"""
AGCCE Lint Check
Ejecuta verificación de estilo y errores comunes en código Python.

Uso: python lint_check.py <archivo_o_directorio>
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
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Comando no encontrado: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -2, "", "Timeout ejecutando comando"


def check_syntax(target: str) -> Tuple[bool, str]:
    """Verifica sintaxis Python básica."""
    if os.path.isfile(target):
        files = [target]
    else:
        files = list(Path(target).rglob("*.py"))
    
    errors = []
    for file in files:
        code, stdout, stderr = run_command([sys.executable, "-m", "py_compile", str(file)])
        if code != 0:
            errors.append(f"{file}: {stderr.strip()}")
    
    if errors:
        return False, "\n".join(errors)
    return True, f"Sintaxis OK: {len(files)} archivos verificados"


def check_ruff(target: str) -> Tuple[bool, str]:
    """Ejecuta ruff si está disponible."""
    code, stdout, stderr = run_command(["ruff", "check", target])
    
    if code == -1:
        return True, "ruff no instalado (opcional)"
    
    if code == 0:
        return True, "ruff: Sin problemas detectados"
    
    return False, f"ruff encontró problemas:\n{stdout}"


def check_flake8(target: str) -> Tuple[bool, str]:
    """Ejecuta flake8 si está disponible."""
    code, stdout, stderr = run_command([
        "flake8", 
        "--max-line-length=120",
        "--ignore=E501,W503",
        target
    ])
    
    if code == -1:
        return True, "flake8 no instalado (opcional)"
    
    if code == 0:
        return True, "flake8: Sin problemas detectados"
    
    return False, f"flake8 encontró problemas:\n{stdout}"


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <archivo_o_directorio>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if not os.path.exists(target):
        print(f"{Colors.RED}Error: '{target}' no existe{Colors.RESET}")
        sys.exit(1)
    
    print(f"\n{Colors.BOLD}══════════════════════════════════════════════════════════")
    print(f"  AGCCE Lint Check v1.0")
    print(f"══════════════════════════════════════════════════════════{Colors.RESET}\n")
    
    print(f"{Colors.BLUE}ℹ Analizando:{Colors.RESET} {target}\n")
    
    all_passed = True
    results = []
    
    # Verificación de sintaxis (obligatoria)
    passed, msg = check_syntax(target)
    results.append(("Syntax Check", passed, msg))
    if not passed:
        all_passed = False
    
    # ruff (opcional pero recomendado)
    passed, msg = check_ruff(target)
    results.append(("Ruff", passed, msg))
    if not passed and "no instalado" not in msg:
        all_passed = False
    
    # flake8 (opcional)
    passed, msg = check_flake8(target)
    results.append(("Flake8", passed, msg))
    if not passed and "no instalado" not in msg:
        all_passed = False
    
    # Mostrar resultados
    print(f"{Colors.BOLD}Resultados:{Colors.RESET}\n")
    for name, passed, msg in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {status} {name}")
        if not passed or "no instalado" in msg:
            for line in msg.split("\n")[:5]:  # Limitar output
                print(f"        {line}")
    
    print()
    
    if all_passed:
        print(f"{Colors.GREEN}═══ LINT CHECK PASSED ═══{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}═══ LINT CHECK FAILED ═══{Colors.RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
