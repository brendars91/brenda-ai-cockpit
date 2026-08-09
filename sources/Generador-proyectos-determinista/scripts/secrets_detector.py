#!/usr/bin/env python3
"""
AGCCE Secrets Detector v1.0
Detecta API keys, contraseñas y secretos en código antes de commit.

Patrones detectados:
- API Keys (AWS, GCP, Azure, GitHub, Stripe, etc.)
- Tokens de acceso
- Contraseñas hardcodeadas
- Connection strings
- Private keys

Uso:
  python secrets_detector.py [archivo o directorio]
  python secrets_detector.py --scan-staged
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Importar utilidades
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info
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


# Patrones de secretos comunes
SECRET_PATTERNS = {
    "aws_access_key": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "description": "AWS Access Key ID",
        "severity": "critical"
    },
    "aws_secret_key": {
        "pattern": r"(?i)aws(.{0,20})?['\"][0-9a-zA-Z/+]{40}['\"]",
        "description": "AWS Secret Access Key",
        "severity": "critical"
    },
    "github_token": {
        "pattern": r"ghp_[0-9a-zA-Z]{36}",
        "description": "GitHub Personal Access Token",
        "severity": "critical"
    },
    "github_oauth": {
        "pattern": r"gho_[0-9a-zA-Z]{36}",
        "description": "GitHub OAuth Access Token",
        "severity": "critical"
    },
    "google_api_key": {
        "pattern": r"AIza[0-9A-Za-z\-_]{35}",
        "description": "Google API Key",
        "severity": "high"
    },
    "stripe_key": {
        "pattern": r"sk_(live|test)_[0-9a-zA-Z]{24,}",
        "description": "Stripe Secret Key",
        "severity": "critical"
    },
    "stripe_pk": {
        "pattern": r"pk_(live|test)_[0-9a-zA-Z]{24,}",
        "description": "Stripe Publishable Key",
        "severity": "medium"
    },
    "slack_token": {
        "pattern": r"xox[baprs]-[0-9A-Za-z\-]{10,}",
        "description": "Slack Token",
        "severity": "high"
    },
    "slack_webhook": {
        "pattern": r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+",
        "description": "Slack Webhook URL",
        "severity": "high"
    },
    "discord_webhook": {
        "pattern": r"https://discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+",
        "description": "Discord Webhook URL",
        "severity": "high"
    },
    "private_key": {
        "pattern": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "description": "Private Key",
        "severity": "critical"
    },
    "password_assignment": {
        "pattern": r"(?i)(password|passwd|pwd|secret|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
        "description": "Hardcoded Password/Secret",
        "severity": "high"
    },
    "connection_string": {
        "pattern": r"(?i)(mongodb|postgres|mysql|redis|amqp)://[^'\"\s]+",
        "description": "Database Connection String",
        "severity": "high"
    },
    "jwt_token": {
        "pattern": r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_.+/=]+",
        "description": "JWT Token",
        "severity": "high"
    },
    "bearer_token": {
        "pattern": r"(?i)bearer\s+[a-zA-Z0-9_\-\.=]+",
        "description": "Bearer Token",
        "severity": "high"
    },
    "azure_key": {
        "pattern": r"(?i)AccountKey=[A-Za-z0-9+/=]{88}",
        "description": "Azure Storage Account Key",
        "severity": "critical"
    },
    "sendgrid_key": {
        "pattern": r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}",
        "description": "SendGrid API Key",
        "severity": "high"
    },
    "twilio_key": {
        "pattern": r"SK[a-f0-9]{32}",
        "description": "Twilio API Key",
        "severity": "high"
    },
    "npm_token": {
        "pattern": r"npm_[A-Za-z0-9]{36}",
        "description": "NPM Access Token",
        "severity": "high"
    },
    "heroku_key": {
        "pattern": r"(?i)heroku[a-z0-9_-]*[=:]['\"]?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "description": "Heroku API Key",
        "severity": "high"
    }
}

# Archivos a ignorar
IGNORE_PATTERNS = [
    r"\.git/",
    r"node_modules/",
    r"\.venv/",
    r"venv/",
    r"__pycache__/",
    r"\.pyc$",
    r"\.min\.js$",
    r"\.min\.css$",
    r"package-lock\.json$",
    r"yarn\.lock$",
    r"\.lock$",
    r"\.png$",
    r"\.jpg$",
    r"\.gif$",
    r"\.ico$",
    r"\.woff",
    r"\.ttf$",
    r"\.eot$"
]

# Archivos de configuración de ejemplo (falsos positivos comunes)
EXAMPLE_FILES = [
    r"\.example",
    r"\.sample",
    r"\.template",
    r"_example\.",
    r"_sample\.",
    r"_template\."
]


def should_ignore_file(filepath: str) -> bool:
    """Verifica si el archivo debe ser ignorado."""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, filepath):
            return True
    return False


def is_example_file(filepath: str) -> bool:
    """Verifica si es un archivo de ejemplo."""
    for pattern in EXAMPLE_FILES:
        if re.search(pattern, filepath.lower()):
            return True
    return False


def scan_file(filepath: str) -> List[Dict]:
    """Escanea un archivo en busca de secretos."""
    findings = []
    
    if should_ignore_file(filepath):
        return findings
    
    is_example = is_example_file(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return findings
    
    for line_num, line in enumerate(lines, 1):
        for secret_type, config in SECRET_PATTERNS.items():
            matches = re.finditer(config["pattern"], line)
            for match in matches:
                # Reducir severidad para archivos de ejemplo
                severity = config["severity"]
                if is_example:
                    severity = "info"
                
                findings.append({
                    "file": filepath,
                    "line": line_num,
                    "type": secret_type,
                    "description": config["description"],
                    "severity": severity,
                    "match_preview": line.strip()[:80] + "..." if len(line.strip()) > 80 else line.strip(),
                    "is_example_file": is_example
                })
    
    return findings


def scan_directory(directory: str) -> List[Dict]:
    """Escanea recursivamente un directorio."""
    all_findings = []
    
    for root, dirs, files in os.walk(directory):
        # Filtrar directorios ignorados
        dirs[:] = [d for d in dirs if not should_ignore_file(os.path.join(root, d))]
        
        for file in files:
            filepath = os.path.join(root, file)
            findings = scan_file(filepath)
            all_findings.extend(findings)
    
    return all_findings


def scan_staged_files() -> List[Dict]:
    """Escanea solo archivos staged en git."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=30,
            encoding='utf-8', errors='replace'
        )
        
        if result.returncode != 0:
            return []
        
        staged_files = result.stdout.strip().split('\n')
        staged_files = [f for f in staged_files if f]
        
        all_findings = []
        for filepath in staged_files:
            if os.path.exists(filepath):
                findings = scan_file(filepath)
                all_findings.extend(findings)
        
        return all_findings
    
    except Exception as e:
        log_warn(f"Error escaneando archivos staged: {e}")
        return []


def format_findings(findings: List[Dict]) -> str:
    """Formatea los hallazgos para mostrar."""
    if not findings:
        return ""
    
    output = []
    
    # Agrupar por severidad
    critical = [f for f in findings if f["severity"] == "critical"]
    high = [f for f in findings if f["severity"] == "high"]
    others = [f for f in findings if f["severity"] not in ["critical", "high"]]
    
    if critical:
        output.append(f"\n{Colors.RED}=== CRITICOS ({len(critical)}) ==={Colors.RESET}")
        for f in critical:
            output.append(f"  {Symbols.CROSS} {f['file']}:{f['line']}")
            output.append(f"      Tipo: {f['description']}")
            output.append(f"      Preview: {f['match_preview']}")
    
    if high:
        output.append(f"\n{Colors.YELLOW}=== ALTOS ({len(high)}) ==={Colors.RESET}")
        for f in high:
            output.append(f"  {Symbols.WARN} {f['file']}:{f['line']}")
            output.append(f"      Tipo: {f['description']}")
    
    if others:
        output.append(f"\n{Colors.BLUE}=== OTROS ({len(others)}) ==={Colors.RESET}")
        for f in others:
            output.append(f"  {Symbols.INFO} {f['file']}:{f['line']} - {f['description']}")
    
    return '\n'.join(output)


def main():
    print("=" * 60)
    print("  AGCCE Secrets Detector v1.0")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python secrets_detector.py <archivo o directorio>")
        print("  python secrets_detector.py --scan-staged")
        print("  python secrets_detector.py --list-patterns")
        return
    
    arg = sys.argv[1]
    
    if arg == "--list-patterns":
        print("\nPatrones detectados:")
        for name, config in SECRET_PATTERNS.items():
            print(f"  - {name}: {config['description']} [{config['severity']}]")
        return
    
    if arg == "--scan-staged":
        print("\nEscaneando archivos staged...")
        findings = scan_staged_files()
    elif os.path.isfile(arg):
        print(f"\nEscaneando archivo: {arg}")
        findings = scan_file(arg)
    elif os.path.isdir(arg):
        print(f"\nEscaneando directorio: {arg}")
        findings = scan_directory(arg)
    else:
        log_fail(f"Path no encontrado: {arg}")
        return
    
    # Filtrar solo críticos y altos para el bloqueo
    blocking_findings = [f for f in findings if f["severity"] in ["critical", "high"] and not f.get("is_example_file")]
    
    if blocking_findings:
        print(format_findings(findings))
        print(f"\n{Colors.RED}{Symbols.CROSS} SECRETOS DETECTADOS: {len(blocking_findings)}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Recomendaciones:{Colors.RESET}")
        print("  1. Remover secretos del código")
        print("  2. Usar variables de entorno")
        print("  3. Añadir archivo a .gitignore si es config local")
        sys.exit(1)
    else:
        log_pass(f"No se detectaron secretos en {len(findings) if not findings else 'archivos escaneados'}")
        sys.exit(0)


if __name__ == '__main__':
    main()
