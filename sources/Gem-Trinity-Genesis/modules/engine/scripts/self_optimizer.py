#!/usr/bin/env python3
"""
AGCCE Self-Optimization Analyzer v1.0
Analiza patrones de error en telemetría y sugiere reglas.

Uso:
  python self_optimizer.py analyze        # Analiza patrones
  python self_optimizer.py suggest-rules  # Sugiere reglas nuevas
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, Counter

# Importar utilidades
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info
except ImportError:
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_warn(msg): print(f"[!] {msg}")
    def log_info(msg): print(f"[i] {msg}")


TELEMETRY_FILE = "logs/telemetry.jsonl"
SECURITY_FILE = "logs/security_events.jsonl"
RULES_FILE = ".agent/rules/agcce_ultra_rules.md"
SUGGESTED_RULES_FILE = "logs/suggested_rules.json"


class SelfOptimizer:
    """Analizador de patrones para auto-optimización."""
    
    def __init__(self, days: int = 7):
        self.days = days
        self.since = datetime.now() - timedelta(days=days)
        self.patterns = []
        self.suggestions = []
    
    def load_telemetry(self) -> List[Dict]:
        """Carga entradas de telemetría."""
        entries = []
        
        for filepath in [TELEMETRY_FILE, SECURITY_FILE]:
            if not os.path.exists(filepath):
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                        if entry_time >= self.since:
                            entries.append(entry)
                    except:
                        continue
        
        return entries
    
    def analyze_patterns(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analiza patrones en las entradas."""
        patterns = {
            "snyk_failures_by_lib": defaultdict(int),
            "hallucinations_by_path": defaultdict(int),
            "errors_by_type": defaultdict(int),
            "high_latency_operations": [],
            "repeated_corrections": defaultdict(int),
            "blocked_commits_reasons": defaultdict(int)
        }
        
        for entry in entries:
            entry_type = entry.get('type', '')
            metrics = entry.get('metrics', {})
            
            # Analizar fallos Snyk
            if 'snyk' in entry_type:
                if metrics.get('blocked_commit') or metrics.get('vulnerabilities_found', 0) > 0:
                    # Intentar extraer librería afectada
                    details = metrics.get('details', {})
                    if isinstance(details, dict):
                        for lib in details.get('affected_libs', []):
                            patterns["snyk_failures_by_lib"][lib] += 1
            
            # Analizar alucinaciones
            if metrics.get('hallucinations_blocked', 0) > 0:
                file_path = metrics.get('file_path', 'unknown')
                patterns["hallucinations_by_path"][file_path] += metrics['hallucinations_blocked']
            
            # Analizar intentos de path no autorizado
            if entry_type == 'security.event':
                if metrics.get('event_type') == 'unauthorized_path':
                    path = metrics.get('file_path', 'unknown')
                    patterns["hallucinations_by_path"][path] += 1
            
            # Analizar latencia alta (> 5 segundos)
            latency = metrics.get('latency_ms', 0)
            if latency > 5000:
                patterns["high_latency_operations"].append({
                    "type": entry_type,
                    "latency_ms": latency,
                    "timestamp": entry.get('timestamp')
                })
            
            # Analizar correcciones repetidas
            if 'plan_generation' in entry_type:
                attempts = metrics.get('self_correction_attempts', 0)
                if attempts > 1:
                    patterns["repeated_corrections"][entry_type] += attempts - 1
            
            # Analizar commits bloqueados
            if metrics.get('blocked_commit'):
                reason = metrics.get('scan_type', 'unknown')
                patterns["blocked_commits_reasons"][reason] += 1
        
        return patterns
    
    def generate_suggestions(self, patterns: Dict) -> List[Dict]:
        """Genera sugerencias de reglas basadas en patrones."""
        suggestions = []
        
        # Sugerencia para librerías problemáticas
        for lib, count in patterns["snyk_failures_by_lib"].items():
            if count >= 3:
                suggestions.append({
                    "type": "security_rule",
                    "priority": "high",
                    "pattern": f"Snyk failures in library: {lib} ({count} times)",
                    "suggested_rule": f"PROHIBIDO: Usar la librería '{lib}' sin verificar vulnerabilidades conocidas y alternativas más seguras.",
                    "action": f"Considerar reemplazar '{lib}' por una alternativa más segura o actualizar a la última versión."
                })
        
        # Sugerencia para paths problemáticos (alucinaciones)
        for path, count in patterns["hallucinations_by_path"].items():
            if count >= 2 and path != 'unknown':
                # Extraer patrón del path
                path_pattern = path.split('/')[-1] if '/' in path else path
                suggestions.append({
                    "type": "validation_rule",
                    "priority": "medium",
                    "pattern": f"Hallucination pattern: {path} ({count} times)",
                    "suggested_rule": f"VERIFICAR: Antes de referenciar paths que contienen '{path_pattern}', confirmar existencia en filesystem.",
                    "action": "Añadir validación explícita para este patrón de path."
                })
        
        # Sugerencia para operaciones lentas
        if len(patterns["high_latency_operations"]) >= 3:
            slow_types = Counter([op["type"] for op in patterns["high_latency_operations"]])
            most_common = slow_types.most_common(1)[0]
            suggestions.append({
                "type": "performance_rule",
                "priority": "low",
                "pattern": f"High latency in: {most_common[0]} ({most_common[1]} times)",
                "suggested_rule": f"OPTIMIZAR: La operación '{most_common[0]}' excede 5s frecuentemente. Considerar indexación incremental o cache.",
                "action": "Revisar configuración de timeouts y considerar optimizaciones."
            })
        
        # Sugerencia para correcciones repetidas
        total_corrections = sum(patterns["repeated_corrections"].values())
        if total_corrections >= 5:
            suggestions.append({
                "type": "generation_rule",
                "priority": "medium",
                "pattern": f"Excessive self-corrections: {total_corrections} in {self.days} days",
                "suggested_rule": "MEJORAR: Los prompts de generación de planes requieren más contexto específico.",
                "action": "Revisar templates de prompts y añadir más ejemplos."
            })
        
        return suggestions
    
    def save_suggestions(self, suggestions: List[Dict]) -> None:
        """Guarda sugerencias en archivo."""
        os.makedirs("logs", exist_ok=True)
        
        data = {
            "analysis_date": datetime.now().isoformat(),
            "period_days": self.days,
            "suggestions": suggestions
        }
        
        with open(SUGGESTED_RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def run(self) -> List[Dict]:
        """Ejecuta análisis completo."""
        entries = self.load_telemetry()
        
        if not entries:
            log_info("No hay suficientes datos para analizar")
            return []
        
        patterns = self.analyze_patterns(entries)
        suggestions = self.generate_suggestions(patterns)
        
        if suggestions:
            self.save_suggestions(suggestions)
        
        return suggestions


def main():
    if len(sys.argv) < 2:
        print("Uso: python self_optimizer.py [analyze | suggest-rules]")
        return
    
    cmd = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    
    optimizer = SelfOptimizer(days=days)
    
    if cmd == "analyze":
        print(f"\n{'='*60}")
        print(f"  AGCCE Self-Optimizer - Análisis de {days} días")
        print(f"{'='*60}\n")
        
        entries = optimizer.load_telemetry()
        log_info(f"Entradas analizadas: {len(entries)}")
        
        patterns = optimizer.analyze_patterns(entries)
        
        print(f"\n{Colors.BOLD}Patrones detectados:{Colors.RESET}")
        
        if patterns["snyk_failures_by_lib"]:
            print(f"\n  Fallos Snyk por librería:")
            for lib, count in patterns["snyk_failures_by_lib"].items():
                print(f"    - {lib}: {count}")
        
        if patterns["hallucinations_by_path"]:
            print(f"\n  Alucinaciones por path:")
            for path, count in patterns["hallucinations_by_path"].items():
                print(f"    - {path}: {count}")
        
        if patterns["high_latency_operations"]:
            print(f"\n  Operaciones lentas (>5s): {len(patterns['high_latency_operations'])}")
    
    elif cmd == "suggest-rules":
        print(f"\n{'='*60}")
        print(f"  AGCCE Self-Optimizer - Sugerencias de Reglas")
        print(f"{'='*60}\n")
        
        suggestions = optimizer.run()
        
        if not suggestions:
            log_pass("No hay sugerencias de reglas en este momento")
            return
        
        print(f"{Colors.YELLOW}He detectado los siguientes patrones:{Colors.RESET}\n")
        
        for i, sug in enumerate(suggestions, 1):
            priority_color = Colors.RED if sug["priority"] == "high" else (
                Colors.YELLOW if sug["priority"] == "medium" else Colors.BLUE
            )
            
            print(f"{i}. [{priority_color}{sug['priority'].upper()}{Colors.RESET}] {sug['pattern']}")
            print(f"   {Colors.GREEN}Regla sugerida:{Colors.RESET}")
            print(f"   \"{sug['suggested_rule']}\"")
            print(f"   {Colors.BLUE}Acción:{Colors.RESET} {sug['action']}\n")
        
        log_pass(f"Sugerencias guardadas en: {SUGGESTED_RULES_FILE}")
        print(f"\n{Colors.CYAN}Para aplicar estas reglas, edita:{Colors.RESET}")
        print(f"  {RULES_FILE}")


if __name__ == '__main__':
    main()
