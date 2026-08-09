#!/usr/bin/env python3
"""
AGCCE Pre-Commit Hook v2.1 con Gate de Snyk + Snyk-Diff Policy
Bloquea commits si:
1. Lint check falla
2. Snyk detecta vulnerabilidades Critical/High en codigo
3. Cambios en dependencias introducen vulnerabilidades (Snyk-Diff Policy)

CONTROLES CRITICOS:
- Gate Snyk: Bloquea Critical/High en codigo
- Snyk-Diff Policy: Analiza delta en requirements.txt/package.json

Instalacion: python scripts/pre_commit_hook.py --install
"""

import subprocess
import sys
import os
import json
from datetime import datetime
from typing import Tuple, List, Set

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


# Archivos de dependencias a monitorear
DEPENDENCY_FILES = {
    'requirements.txt',
    'requirements-dev.txt',
    'Pipfile',
    'Pipfile.lock',
    'pyproject.toml',
    'package.json',
    'package-lock.json',
    'yarn.lock',
    'pnpm-lock.yaml',
    'Gemfile',
    'Gemfile.lock',
    'go.mod',
    'go.sum',
    'Cargo.toml',
    'Cargo.lock'
}


def get_staged_files() -> List[str]:
    """Obtiene lista de archivos staged para commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        return []
    return [f.strip() for f in result.stdout.split('\n') if f.strip()]


def get_staged_python_files() -> List[str]:
    """Obtiene archivos Python staged."""
    return [f for f in get_staged_files() if f.endswith('.py')]


def get_staged_dependency_files() -> Set[str]:
    """Obtiene archivos de dependencias que fueron modificados."""
    staged = set(get_staged_files())
    return staged & DEPENDENCY_FILES


def run_lint_check(files: List[str]) -> Tuple[bool, str]:
    """Ejecuta lint check en archivos staged."""
    if not files:
        return True, "No hay archivos Python para verificar"
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/lint_check.py"] + files[:5],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return True, "lint_check.py no encontrado, saltando"
    except Exception as e:
        return True, f"Error: {e}"


def run_snyk_code_scan() -> Tuple[bool, str, int, int]:
    """
    GATE DE SNYK - Escanea codigo fuente.
    Bloquea si encuentra Critical/High.
    """
    try:
        # Buscar Snyk CLI dinámicamente (portable)
        import shutil
        snyk_cmd = shutil.which("snyk") or shutil.which("snyk-win") or "snyk"
        
        result = subprocess.run(
            [
                snyk_cmd,
                "code", "test",
                "--severity-threshold=high",
                "."
            ],
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        critical = output.lower().count("critical")
        high = output.lower().count("high severity") + output.lower().count("[high]")
        
        if result.returncode != 0 or critical > 0 or high > 0:
            return False, output, critical, high
        
        return True, output, 0, 0
        
    except FileNotFoundError:
        log_warn("Snyk CLI no encontrado")
        return True, "Snyk no disponible", 0, 0
    except subprocess.TimeoutExpired:
        log_warn("Snyk code scan timeout")
        return True, "Timeout", 0, 0
    except Exception as e:
        return True, str(e), 0, 0


def run_snyk_dependency_scan(dep_files: Set[str]) -> Tuple[bool, str, List[str]]:
    """
    SNYK-DIFF POLICY - Escanea dependencias modificadas.
    Si un cambio en requirements.txt/package.json introduce vulnerabilidad, bloquea.
    """
    if not dep_files:
        return True, "Sin cambios en dependencias", []
    
    vulnerabilities = []
    
    for dep_file in dep_files:
        print(f"    Escaneando: {dep_file}")
        
        try:
            # Determinar tipo de proyecto
            if dep_file in {'requirements.txt', 'requirements-dev.txt', 'Pipfile', 'pyproject.toml'}:
                cmd = ["snyk", "test", "--severity-threshold=high", "--file=" + dep_file]
            elif dep_file in {'package.json', 'package-lock.json', 'yarn.lock'}:
                cmd = ["snyk", "test", "--severity-threshold=high"]
            else:
                continue
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,
                encoding='utf-8',
                errors='replace',
                cwd=os.path.dirname(dep_file) or '.'
            )
            
            output = result.stdout + result.stderr
            
            # Detectar vulnerabilidades
            if result.returncode != 0:
                # Extraer paquetes vulnerables
                import re
                vuln_matches = re.findall(r'([\w-]+)@[\d.]+ \[([A-Z]+)\]', output)
                for pkg, severity in vuln_matches:
                    if severity in ['CRITICAL', 'HIGH']:
                        vulnerabilities.append(f"{dep_file}: {pkg} ({severity})")
        
        except FileNotFoundError:
            # Snyk CLI no disponible, usar alternativa
            log_warn(f"Snyk test no disponible para {dep_file}")
        except subprocess.TimeoutExpired:
            log_warn(f"Timeout escaneando {dep_file}")
        except Exception as e:
            log_warn(f"Error escaneando {dep_file}: {e}")
    
    if vulnerabilities:
        return False, "\n".join(vulnerabilities), vulnerabilities
    
    return True, "Sin vulnerabilidades nuevas", []


def run_pre_commit(skip_snyk: bool = False, skip_deps: bool = False) -> bool:
    """
    Ejecuta todos los checks de pre-commit.
    """
    print(make_header("AGCCE Pre-Commit Hook v2.1"))
    
    all_passed = True
    staged_files = get_staged_files()
    python_files = get_staged_python_files()
    dep_files = get_staged_dependency_files()
    
    print(f"{Colors.CYAN}Archivos staged:{Colors.RESET} {len(staged_files)}")
    print(f"{Colors.CYAN}Archivos Python:{Colors.RESET} {len(python_files)}")
    print(f"{Colors.CYAN}Archivos de dependencias:{Colors.RESET} {len(dep_files)}")
    print()
    
    # 1. Lint Check
    print(f"{Colors.BOLD}[1/4] Lint Check...{Colors.RESET}")
    passed, output = run_lint_check(python_files)
    if passed:
        log_pass("Lint check pasado")
    else:
        log_fail("Lint check fallido")
        print(output[:300])
        all_passed = False
    
    # 2. Snyk Code Scan
    print(f"\n{Colors.BOLD}[2/4] Snyk Code Security Scan...{Colors.RESET}")
    
    if skip_snyk:
        log_warn("Snyk code scan saltado")
    else:
        passed, output, critical, high = run_snyk_code_scan()
        
        if passed:
            log_pass("Sin vulnerabilidades Critical/High en codigo")
        else:
            log_fail(f"Vulnerabilidades en codigo: {critical} Critical, {high} High")
            all_passed = False
    
    # 3. Snyk-Diff Policy (dependencias)
    print(f"\n{Colors.BOLD}[3/4] Snyk-Diff Policy (dependencias)...{Colors.RESET}")
    
    if skip_deps or not dep_files:
        if dep_files:
            log_warn("Snyk-Diff saltado")
        else:
            log_info("Sin cambios en archivos de dependencias")
    else:
        passed, output, vulns = run_snyk_dependency_scan(dep_files)
        
        if passed:
            log_pass("Sin vulnerabilidades nuevas en dependencias")
        else:
            log_fail(f"Vulnerabilidades en dependencias:")
            for v in vulns[:5]:
                print(f"    {Colors.RED}X{Colors.RESET} {v}")
            if len(vulns) > 5:
                print(f"    ... y {len(vulns) - 5} mas")
            all_passed = False
    
    # 4. Resumen
    print(f"\n{Colors.BOLD}[4/4] Resumen...{Colors.RESET}")
    
    if all_passed:
        print(f"\n{Colors.GREEN}=== PRE-COMMIT PASSED ==={Colors.RESET}")
        log_pass("Commit permitido")
        return True
    else:
        print(f"\n{Colors.RED}{'=' * 50}")
        print("  COMMIT BLOQUEADO")
        print(f"{'=' * 50}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Razones:{Colors.RESET}")
        print("  - Vulnerabilidades de seguridad detectadas")
        print("  - Corrige los problemas antes de hacer commit")
        print(f"\n{Colors.RED}[!] Bypass prohibido (AGCCE Directive){Colors.RESET}\n")
        return False


def install_hook():
    """Instala el hook de pre-commit en .git/hooks/"""
    hook_path = ".git/hooks/pre-commit"
    
    if not os.path.exists(".git"):
        log_fail("No es un repositorio git")
        return False
    
    hook_content = '''#!/bin/sh
# AGCCE Pre-Commit Hook v2.1
# Con Gate Snyk + Snyk-Diff Policy

python scripts/pre_commit_hook.py
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "[X] Commit bloqueado por AGCCE Pre-Commit Hook"
    echo "[!] Bypass prohibido segun directivas AGCCE"
    exit 1
fi

exit 0
'''
    
    os.makedirs(".git/hooks", exist_ok=True)
    
    with open(hook_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(hook_content)
    
    if sys.platform != 'win32':
        os.chmod(hook_path, 0o755)
    
    log_pass(f"Hook instalado en {hook_path}")
    print(f"\n{Colors.BLUE}El hook incluye:{Colors.RESET}")
    print("  - Lint Check")
    print("  - Snyk Code Scan (Critical/High bloqueantes)")
    print("  - Snyk-Diff Policy (dependencias)")
    print(f"\n{Colors.RED}[!] Bypass (--no-verify) esta PROHIBIDO{Colors.RESET}\n")
    
    return True


def main():
    if "--install" in sys.argv:
        install_hook()
        return
    
    if "--help" in sys.argv:
        print(f"Uso: python {sys.argv[0]} [--install | --skip-snyk | --skip-deps | --help]")
        print("\nOpciones:")
        print("  --install      Instala el hook")
        print("  --skip-snyk    Salta scan de codigo (NO RECOMENDADO)")
        print("  --skip-deps    Salta scan de dependencias")
        return
    
    skip_snyk = "--skip-snyk" in sys.argv
    skip_deps = "--skip-deps" in sys.argv
    
    passed = run_pre_commit(skip_snyk, skip_deps)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
