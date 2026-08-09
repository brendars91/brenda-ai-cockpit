#!/usr/bin/env python3
"""
AGCCE Security Guardian v1.0
Razonamiento de seguridad proactivo - Red Team automatizado.

Implementa:
- Generación de hipótesis de ataque
- Análisis de flujo de datos
- Protocolo Red-to-Green
- Tracking de vulnerabilidades lógicas

Uso:
    python security_guardian.py analyze <file>
    python security_guardian.py verify
    python security_guardian.py stats
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
SECURITY_LOG = LOGS_DIR / "security_analysis.jsonl"


# Patrones de vulnerabilidades lógicas (que Snyk no detecta)
LOGICAL_VULNERABILITY_PATTERNS = {
    "IDOR": {
        "description": "Insecure Direct Object Reference",
        "patterns": [
            r"request\.(args|form|json)\s*\[\s*['\"]id['\"]\s*\]",
            r"\.get\(\s*['\"].*_id['\"]\s*\)",
            r"/\{.*id\}",
            r"params\[.*id.*\]"
        ],
        "risky_if": "No ownership verification before access"
    },
    "RACE_CONDITION": {
        "description": "Time-of-check to time-of-use vulnerability",
        "patterns": [
            r"if\s+.*exists.*:\s*\n.*\s*(create|update|delete)",
            r"balance\s*[><=]+.*\n.*withdraw",
            r"count\s*<.*\n.*increment"
        ],
        "risky_if": "No locks or atomic operations"
    },
    "AUTH_BYPASS": {
        "description": "Authentication bypass potential",
        "patterns": [
            r"if\s+.*admin.*==.*True",
            r"role\s*==\s*['\"]admin['\"]",
            r"@public\s*\n.*def",
            r"auth.*=.*False"
        ],
        "risky_if": "Role check can be manipulated"
    },
    "LOGIC_FLAW": {
        "description": "Business logic vulnerability",
        "patterns": [
            r"price\s*=.*request",
            r"discount\s*=.*user",
            r"skip.*validation",
            r"if.*debug.*:"
        ],
        "risky_if": "User can control business-critical values"
    },
    "DATA_EXPOSURE": {
        "description": "Sensitive data exposure",
        "patterns": [
            r"\.password",
            r"\.secret",
            r"\.api_key",
            r"print\(.*token",
            r"log.*password"
        ],
        "risky_if": "Data logged or returned without filtering"
    },
    "SSRF": {
        "description": "Server-Side Request Forgery",
        "patterns": [
            r"requests\.(get|post)\(.*\+.*\)",
            r"urllib.*open\(.*request",
            r"fetch\(.*user.*\)"
        ],
        "risky_if": "URL constructed from user input"
    }
}


class SecurityGuardian:
    """Guardián de seguridad proactivo."""
    
    def __init__(self):
        LOGS_DIR.mkdir(exist_ok=True)
    
    def analyze_file(self, filepath: Path) -> Dict:
        """
        Analiza un archivo buscando vulnerabilidades lógicas.
        
        Returns:
            Dict con findings y attack hypotheses
        """
        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}
        
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        
        findings = []
        attack_hypotheses = []
        
        # Buscar patrones de vulnerabilidades lógicas
        for vuln_type, config in LOGICAL_VULNERABILITY_PATTERNS.items():
            for pattern in config["patterns"]:
                matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
                
                for match in matches:
                    # Encontrar número de línea
                    line_num = content[:match.start()].count('\n') + 1
                    
                    finding = {
                        "type": vuln_type,
                        "description": config["description"],
                        "line": line_num,
                        "match": match.group()[:100],
                        "risky_if": config["risky_if"],
                        "severity": self._calculate_severity(vuln_type)
                    }
                    findings.append(finding)
                    
                    # Generar hipótesis de ataque
                    hypothesis = self._generate_attack_hypothesis(
                        vuln_type, 
                        config["description"],
                        filepath.name,
                        line_num
                    )
                    if hypothesis not in attack_hypotheses:
                        attack_hypotheses.append(hypothesis)
        
        result = {
            "file": str(filepath),
            "analyzed_at": datetime.now().isoformat(),
            "findings_count": len(findings),
            "findings": findings,
            "attack_hypotheses": attack_hypotheses,
            "security_score": self._calculate_security_score(findings)
        }
        
        # Log analysis
        self._log_analysis(result)
        
        return result
    
    def _calculate_severity(self, vuln_type: str) -> str:
        """Calcula severidad de vulnerabilidad."""
        critical = ["AUTH_BYPASS", "SSRF"]
        high = ["IDOR", "RACE_CONDITION"]
        medium = ["LOGIC_FLAW", "DATA_EXPOSURE"]
        
        if vuln_type in critical:
            return "critical"
        elif vuln_type in high:
            return "high"
        else:
            return "medium"
    
    def _generate_attack_hypothesis(
        self, 
        vuln_type: str, 
        description: str,
        filename: str,
        line: int
    ) -> str:
        """Genera hipótesis de ataque en lenguaje natural."""
        templates = {
            "IDOR": f"Un atacante podría cambiar el ID en la request ({filename}:L{line}) para acceder a recursos de otros usuarios sin autorización.",
            "RACE_CONDITION": f"Un atacante podría enviar múltiples requests simultáneas ({filename}:L{line}) para explotar una condición de carrera y manipular el estado.",
            "AUTH_BYPASS": f"Un atacante podría manipular el rol o flag de admin ({filename}:L{line}) para obtener acceso privilegiado.",
            "LOGIC_FLAW": f"Un atacante podría modificar valores críticos del negocio ({filename}:L{line}) para obtener beneficios no autorizados.",
            "DATA_EXPOSURE": f"Un atacante podría extraer datos sensibles ({filename}:L{line}) desde logs o respuestas de API.",
            "SSRF": f"Un atacante podría inyectar URLs maliciosas ({filename}:L{line}) para hacer requests a sistemas internos."
        }
        return templates.get(vuln_type, f"Potencial {description} detectado en {filename}:L{line}")
    
    def _calculate_security_score(self, findings: List[Dict]) -> int:
        """Calcula score de seguridad (100 = perfecto, 0 = crítico)."""
        if not findings:
            return 100
        
        # Penalización por severidad
        penalties = {"critical": 30, "high": 20, "medium": 10}
        total_penalty = sum(penalties.get(f["severity"], 5) for f in findings)
        
        return max(0, 100 - total_penalty)
    
    def _log_analysis(self, result: Dict):
        """Registra análisis en log."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "security_analysis",
            "file": result["file"],
            "findings_count": result["findings_count"],
            "security_score": result["security_score"],
            "detected_by": "security_guardian"
        }
        
        with open(SECURITY_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def analyze_directory(self, dirpath: Path, extensions: List[str] = None) -> Dict:
        """Analiza todos los archivos de un directorio."""
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".jsx", ".tsx"]
        
        all_findings = []
        all_hypotheses = []
        files_analyzed = 0
        
        for ext in extensions:
            for filepath in dirpath.rglob(f"*{ext}"):
                # Skip test files and cache
                if "test" in str(filepath).lower() or "__pycache__" in str(filepath):
                    continue
                
                result = self.analyze_file(filepath)
                if "error" not in result:
                    files_analyzed += 1
                    all_findings.extend(result["findings"])
                    all_hypotheses.extend(result["attack_hypotheses"])
        
        return {
            "directory": str(dirpath),
            "files_analyzed": files_analyzed,
            "total_findings": len(all_findings),
            "unique_hypotheses": list(set(all_hypotheses)),
            "findings_by_type": self._group_findings_by_type(all_findings),
            "overall_security_score": self._calculate_security_score(all_findings)
        }
    
    def _group_findings_by_type(self, findings: List[Dict]) -> Dict[str, int]:
        """Agrupa findings por tipo."""
        grouped = {}
        for f in findings:
            vuln_type = f["type"]
            grouped[vuln_type] = grouped.get(vuln_type, 0) + 1
        return grouped
    
    def generate_plan_security_section(self, analysis: Dict) -> Dict:
        """Genera sección de seguridad para Plan JSON."""
        return {
            "security_analysis": {
                "analyzed_at": datetime.now().isoformat(),
                "assumptions": [
                    "El código ha sido analizado con Security Guardian",
                    "Los findings requieren validación manual"
                ],
                "attack_vectors": [
                    {
                        "type": vuln_type,
                        "count": count,
                        "likelihood": "high" if vuln_type in ["IDOR", "AUTH_BYPASS"] else "medium"
                    }
                    for vuln_type, count in analysis.get("findings_by_type", {}).items()
                ],
                "mitigations": [
                    "Implementar verificación de ownership para recursos",
                    "Usar operaciones atómicas para prevenir race conditions",
                    "Filtrar datos sensibles de logs y respuestas"
                ],
                "validation_tests": [
                    f"tests/security/test_{vuln_type.lower()}.py"
                    for vuln_type in analysis.get("findings_by_type", {}).keys()
                ],
                "security_score": analysis.get("overall_security_score", 0)
            }
        }
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas de análisis de seguridad."""
        if not SECURITY_LOG.exists():
            return {"message": "No security analyses recorded yet"}
        
        analyses = []
        with open(SECURITY_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    analyses.append(json.loads(line))
                except:
                    continue
        
        if not analyses:
            return {"message": "No valid analyses found"}
        
        total_findings = sum(a.get("findings_count", 0) for a in analyses)
        avg_score = sum(a.get("security_score", 100) for a in analyses) / len(analyses)
        
        return {
            "total_analyses": len(analyses),
            "total_findings": total_findings,
            "average_security_score": round(avg_score, 1),
            "logical_vulnerabilities_detected": total_findings,
            "last_analysis": analyses[-1]["timestamp"] if analyses else None
        }


def main():
    """CLI para Security Guardian."""
    guardian = SecurityGuardian()
    
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════╗
║              AGCCE Security Guardian v1.0                   ║
║         Razonamiento de Seguridad Proactivo                 ║
╚══════════════════════════════════════════════════════════════╝

Uso:
  python security_guardian.py analyze <file|directory>
  python security_guardian.py verify
  python security_guardian.py stats

Ejemplos:
  python security_guardian.py analyze scripts/
  python security_guardian.py analyze path/to/file.py
  python security_guardian.py stats
        """)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "analyze":
        target = sys.argv[2] if len(sys.argv) > 2 else "."
        target_path = Path(target)
        
        if target_path.is_file():
            result = guardian.analyze_file(target_path)
        else:
            result = guardian.analyze_directory(target_path)
        
        print(f"\n{'='*60}")
        print("  SECURITY ANALYSIS REPORT")
        print(f"{'='*60}")
        
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            return
        
        if "overall_security_score" in result:
            # Directory analysis
            print(f"\nArchivos analizados: {result['files_analyzed']}")
            print(f"Vulnerabilidades encontradas: {result['total_findings']}")
            print(f"\nPor tipo:")
            for vuln_type, count in result.get("findings_by_type", {}).items():
                print(f"  - {vuln_type}: {count}")
            
            if result.get("unique_hypotheses"):
                print(f"\n🔴 HIPÓTESIS DE ATAQUE:")
                for i, hyp in enumerate(result["unique_hypotheses"][:5], 1):
                    print(f"  {i}. {hyp}")
        else:
            # File analysis
            print(f"\nArchivo: {result['file']}")
            print(f"Vulnerabilidades: {result['findings_count']}")
            
            for f in result.get("findings", []):
                print(f"\n  [{f['severity'].upper()}] {f['type']} (L{f['line']})")
                print(f"    → {f['risky_if']}")
        
        score = result.get("overall_security_score", result.get("security_score", 100))
        color = "🟢" if score > 80 else "🟡" if score > 50 else "🔴"
        print(f"\n{color} Security Score: {score}/100")
    
    elif cmd == "stats":
        stats = guardian.get_stats()
        print(f"\n{'='*60}")
        print("  SECURITY GUARDIAN STATISTICS")
        print(f"{'='*60}")
        
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif cmd == "verify":
        print("\n🔍 Verificando tests de seguridad...")
        # TODO: Ejecutar tests en tests/security/
        print("  (Ejecuta: pytest tests/security/ -v)")
    
    else:
        print(f"Comando desconocido: {cmd}")


if __name__ == '__main__':
    main()
