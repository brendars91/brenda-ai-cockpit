#!/usr/bin/env python3
"""
AGCCE Evidence Collector
Recopila y genera reportes de evidencia reproducible.

Uso: python collect_evidence.py <plan.json> [--output evidence_report.json]
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

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
        PLAY = '>'
    def make_header(title, width=60): return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


def run_command(cmd: str, cwd: str = ".") -> Dict[str, Any]:
    """Ejecuta un comando y captura output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=cwd,
            encoding='utf-8',
            errors='replace'
        )
        return {
            "command": cmd,
            "exit_code": result.returncode,
            "stdout": result.stdout[:5000],
            "stderr": result.stderr[:2000],
            "success": result.returncode == 0,
            "executed_at": datetime.now().isoformat()
        }
    except subprocess.TimeoutExpired:
        return {
            "command": cmd,
            "exit_code": -1,
            "stdout": "",
            "stderr": "TIMEOUT: Comando excedio 120s",
            "success": False,
            "executed_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "command": cmd,
            "exit_code": -2,
            "stdout": "",
            "stderr": str(e),
            "success": False,
            "executed_at": datetime.now().isoformat()
        }


def collect_git_info() -> Dict[str, Any]:
    """Recopila informacion del estado de git."""
    info = {}
    
    result = run_command("git branch --show-current")
    info["current_branch"] = result["stdout"].strip() if result["success"] else "unknown"
    
    result = run_command("git log -1 --format=%H|%s|%an|%ai")
    if result["success"]:
        parts = result["stdout"].strip().split("|")
        if len(parts) >= 4:
            info["last_commit"] = {
                "hash": parts[0],
                "message": parts[1],
                "author": parts[2],
                "date": parts[3]
            }
    
    result = run_command("git status --porcelain")
    info["status"] = "clean" if not result["stdout"].strip() else "dirty"
    info["changed_files"] = [
        line.strip() for line in result["stdout"].split("\n") if line.strip()
    ][:20]
    
    return info


def collect_file_info(paths: List[str]) -> List[Dict[str, Any]]:
    """Recopila informacion de archivos analizados."""
    files_info = []
    
    for path in paths:
        if os.path.exists(path):
            stat = os.stat(path)
            files_info.append({
                "path": path,
                "exists": True,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "lines": count_lines(path)
            })
        else:
            files_info.append({
                "path": path,
                "exists": False
            })
    
    return files_info


def count_lines(path: str) -> Optional[int]:
    """Cuenta lineas de un archivo."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return None


def run_verification_commands(plan: Dict) -> List[Dict[str, Any]]:
    """Ejecuta comandos de verificacion del plan."""
    verification = plan.get("verification", {})
    commands = verification.get("commands", [])
    
    results = []
    for cmd in commands:
        print(f"  {Colors.BLUE}>{Colors.RESET} Ejecutando: {cmd}")
        result = run_command(cmd)
        status = f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET}" if result["success"] else f"{Colors.RED}{Symbols.CROSS}{Colors.RESET}"
        print(f"    {status} Exit code: {result['exit_code']}")
        results.append(result)
    
    return results


def generate_evidence_report(plan_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Genera reporte completo de evidencia."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    print(make_header("AGCCE Evidence Collector v1.0"))
    
    print(f"{Colors.CYAN}Plan:{Colors.RESET} {plan.get('plan_id')}")
    print(f"{Colors.CYAN}Objetivo:{Colors.RESET} {plan.get('objective', {}).get('description', 'N/A')}\n")
    
    report = {
        "plan_id": plan.get("plan_id"),
        "plan_version": plan.get("version"),
        "collected_at": datetime.now().isoformat(),
        "collector_version": "1.0.0"
    }
    
    # 1. Informacion de Git
    print(f"{Colors.BOLD}[1/4] Recopilando informacion de Git...{Colors.RESET}")
    report["git_info"] = collect_git_info()
    print(f"  Branch: {report['git_info'].get('current_branch')}")
    print(f"  Status: {report['git_info'].get('status')}")
    
    # 2. Informacion de archivos
    print(f"\n{Colors.BOLD}[2/4] Analizando archivos...{Colors.RESET}")
    affected_files = plan.get("objective", {}).get("affected_files", [])
    analyzed_paths = plan.get("evidence", {}).get("analyzed_paths", [])
    all_paths = list(set(affected_files + analyzed_paths))
    report["files_analyzed"] = collect_file_info(all_paths)
    print(f"  {len(report['files_analyzed'])} archivos analizados")
    
    # 3. Comandos de verificacion
    print(f"\n{Colors.BOLD}[3/4] Ejecutando verificaciones...{Colors.RESET}")
    report["verification_results"] = run_verification_commands(plan)
    passed = sum(1 for r in report["verification_results"] if r["success"])
    total = len(report["verification_results"])
    print(f"  {passed}/{total} verificaciones pasadas")
    
    # 4. Resumen de pasos
    print(f"\n{Colors.BOLD}[4/4] Generando resumen de pasos...{Colors.RESET}")
    report["steps_summary"] = []
    for step in plan.get("steps", []):
        report["steps_summary"].append({
            "id": step.get("id"),
            "action": step.get("action"),
            "target": step.get("target"),
            "hitl_required": step.get("hitl_required", False),
            "expected_outcome": step.get("expected_outcome")
        })
    print(f"  {len(report['steps_summary'])} pasos documentados")
    
    if plan.get("commit_proposal"):
        report["commit_proposal"] = plan["commit_proposal"]
    
    # Validacion del plan
    print(f"\n{Colors.BOLD}Validando plan...{Colors.RESET}")
    validate_result = run_command(f"python scripts/validate_plan.py {plan_path}")
    report["plan_validation"] = {
        "passed": validate_result["success"],
        "output": validate_result["stdout"][:1000]
    }
    
    # Calcular score
    all_passed = all(r["success"] for r in report["verification_results"]) if report["verification_results"] else True
    plan_valid = report["plan_validation"]["passed"]
    
    report["evidence_score"] = {
        "verification_passed": all_passed,
        "plan_valid": plan_valid,
        "overall": "PASS" if (all_passed and plan_valid) else "FAIL"
    }
    
    # Guardar reporte
    if output_path is None:
        output_path = f"evidence_{plan.get('plan_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    
    if report["evidence_score"]["overall"] == "PASS":
        print(f"{Colors.GREEN}=== EVIDENCE COLLECTION PASSED ==={Colors.RESET}")
    else:
        print(f"{Colors.RED}=== EVIDENCE COLLECTION FAILED ==={Colors.RESET}")
    
    print(f"\n{Colors.BLUE}Reporte guardado en:{Colors.RESET} {output_path}\n")
    
    return report


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <plan.json> [--output report.json]")
        sys.exit(1)
    
    plan_path = sys.argv[1]
    output_path = None
    
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    if not os.path.exists(plan_path):
        print(f"{Colors.RED}Error: '{plan_path}' no existe{Colors.RESET}")
        sys.exit(1)
    
    report = generate_evidence_report(plan_path, output_path)
    
    sys.exit(0 if report["evidence_score"]["overall"] == "PASS" else 1)


if __name__ == '__main__':
    main()
