#!/usr/bin/env python3
"""
AGCCE Common Utilities
Módulo común con utilidades compartidas y configuración de encoding para Windows.
"""

import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    # Forzar UTF-8 en stdout/stderr
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
    
    # Habilitar colores ANSI en Windows 10+
    os.system('')


class Colors:
    """Colores ANSI para terminal."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# Caracteres ASCII-safe para compatibilidad con Windows
class Symbols:
    """Símbolos compatibles con todas las consolas."""
    CHECK = '[OK]'      # En lugar de ✓
    CROSS = '[X]'       # En lugar de ✗
    WARN = '[!]'        # En lugar de ⚠
    INFO = '[i]'        # En lugar de ℹ
    ARROW = '->'        # En lugar de →
    LOCK = '[L]'        # En lugar de 🔒
    UNLOCK = '[U]'      # En lugar de 🔓
    PLAY = '>'          # En lugar de ►
    LINE_H = '='        # En lugar de ═
    LINE_V = '|'        # En lugar de ║
    CORNER_TL = '+'     # En lugar de ╔
    CORNER_TR = '+'     # En lugar de ╗
    CORNER_BL = '+'     # En lugar de ╚
    CORNER_BR = '+'     # En lugar de ╝


def make_header(title: str, width: int = 60) -> str:
    """Crea un header con bordes ASCII-safe."""
    line = Symbols.LINE_H * width
    return f"\n{Colors.BOLD}{line}\n  {title}\n{line}{Colors.RESET}\n"


def make_box(title: str, width: int = 55) -> str:
    """Crea un box con bordes ASCII-safe."""
    border_h = Symbols.LINE_H * width
    padding = ' ' * ((width - len(title)) // 2 - 1)
    return f"""
{Colors.BOLD}{Colors.CYAN}    +{border_h}+
    |{padding}{title}{padding}|
    +{border_h}+{Colors.RESET}
"""


def log_pass(msg: str) -> None:
    """Log de éxito."""
    print(f"{Colors.GREEN}{Symbols.CHECK} PASS:{Colors.RESET} {msg}")


def log_fail(msg: str) -> None:
    """Log de fallo."""
    print(f"{Colors.RED}{Symbols.CROSS} FAIL:{Colors.RESET} {msg}")


def log_warn(msg: str) -> None:
    """Log de advertencia."""
    print(f"{Colors.YELLOW}{Symbols.WARN} WARN:{Colors.RESET} {msg}")


def log_info(msg: str) -> None:
    """Log de información."""
    print(f"{Colors.BLUE}{Symbols.INFO} INFO:{Colors.RESET} {msg}")


def safe_print(text: str) -> None:
    """Print con manejo de errores de encoding."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback a ASCII
        print(text.encode('ascii', errors='replace').decode('ascii'))
