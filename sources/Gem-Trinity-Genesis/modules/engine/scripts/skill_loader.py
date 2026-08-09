#!/usr/bin/env python3
"""
AGCCE Skill Loader v1.0
Carga contexto de herramientas según la fase del plan.

Uso:
  from skill_loader import SkillLoader
  tools = SkillLoader.get_tools_for_phase("validation")
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path

# Ruta al manifest
MANIFEST_PATH = Path(__file__).parent.parent / "config" / "skill_manifest.json"


class SkillLoader:
    """Cargador de skills por fase."""
    
    _manifest: Dict = None
    
    @classmethod
    def _load_manifest(cls) -> Dict:
        """Carga el manifest de skills."""
        if cls._manifest is None:
            if MANIFEST_PATH.exists():
                with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                    cls._manifest = json.load(f)
            else:
                cls._manifest = {"phases": {}, "mcps": {"active": {}}}
        return cls._manifest
    
    @classmethod
    def get_tools_for_phase(cls, phase: str) -> Dict:
        """
        Obtiene las herramientas recomendadas para una fase.
        
        Args:
            phase: Nombre de la fase (analysis, planning, validation, etc.)
        
        Returns:
            Dict con primary_tools, secondary_tools y cli_suggestion
        """
        manifest = cls._load_manifest()
        phases = manifest.get("phases", {})
        
        if phase not in phases:
            return {
                "primary_tools": ["filesystem"],
                "secondary_tools": [],
                "cli_suggestion": None,
                "phase_found": False
            }
        
        phase_config = phases[phase]
        return {
            "primary_tools": phase_config.get("primary_tools", []),
            "secondary_tools": phase_config.get("secondary_tools", []),
            "cli_suggestion": phase_config.get("cli_suggestion"),
            "description": phase_config.get("description", ""),
            "phase_found": True
        }
    
    @classmethod
    def get_mcp_info(cls, mcp_name: str) -> Optional[Dict]:
        """Obtiene información de un MCP específico."""
        manifest = cls._load_manifest()
        
        # Buscar en activos
        active = manifest.get("mcps", {}).get("active", {})
        if mcp_name in active:
            return {**active[mcp_name], "status": "active"}
        
        # Buscar en deshabilitados
        disabled = manifest.get("mcps", {}).get("available_but_disabled", {})
        if mcp_name in disabled:
            return {**disabled[mcp_name], "status": "disabled"}
        
        return None
    
    @classmethod
    def suggest_for_task(cls, task_description: str) -> Dict:
        """
        Sugiere herramientas basándose en la descripción de la tarea.
        
        Args:
            task_description: Descripción de lo que el usuario quiere hacer
        
        Returns:
            Dict con fase detectada y herramientas sugeridas
        """
        task_lower = task_description.lower()
        
        # Detectar fase por palabras clave
        phase_keywords = {
            "analysis": ["analizar", "entender", "revisar", "buscar", "encontrar"],
            "planning": ["planear", "diseñar", "arquitectura", "plan"],
            "implementation": ["implementar", "crear", "escribir", "añadir", "modificar"],
            "validation": ["validar", "verificar", "probar", "test"],
            "pre-commit": ["commit", "push", "subir"],
            "automation": ["automatizar", "workflow", "n8n", "webhook"],
            "research": ["investigar", "documentación", "api", "librería"]
        }
        
        detected_phase = "implementation"  # Default
        for phase, keywords in phase_keywords.items():
            if any(kw in task_lower for kw in keywords):
                detected_phase = phase
                break
        
        tools = cls.get_tools_for_phase(detected_phase)
        
        return {
            "detected_phase": detected_phase,
            "tools": tools,
            "message": f"Para esta tarea, he detectado fase '{detected_phase}'. "
                      f"Herramientas principales: {', '.join(tools['primary_tools'])}"
        }
    
    @classmethod
    def get_auto_suggestion(cls, context: str) -> Optional[str]:
        """Obtiene sugerencia automática según contexto."""
        manifest = cls._load_manifest()
        suggestions = manifest.get("auto_suggestions", {})
        
        context_map = {
            "commit": "before_commit",
            "push": "before_commit",
            "files": "after_many_files",
            "feature": "creating_feature",
            "debug": "debugging",
            "bug": "debugging"
        }
        
        for keyword, suggestion_key in context_map.items():
            if keyword in context.lower():
                return suggestions.get(suggestion_key)
        
        return None
    
    @classmethod
    def list_all_phases(cls) -> List[str]:
        """Lista todas las fases disponibles."""
        manifest = cls._load_manifest()
        return list(manifest.get("phases", {}).keys())
    
    @classmethod
    def list_active_mcps(cls) -> List[str]:
        """Lista todos los MCPs activos."""
        manifest = cls._load_manifest()
        return list(manifest.get("mcps", {}).get("active", {}).keys())


def main():
    """CLI para el Skill Loader."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python skill_loader.py [phase|mcp|suggest] <nombre>")
        print("\nEjemplos:")
        print("  python skill_loader.py phase validation")
        print("  python skill_loader.py mcp snyk")
        print("  python skill_loader.py suggest 'quiero añadir autenticación'")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "phase":
        phase = sys.argv[2] if len(sys.argv) > 2 else "implementation"
        result = SkillLoader.get_tools_for_phase(phase)
        print(f"\nFase: {phase}")
        print(f"Descripción: {result.get('description', 'N/A')}")
        print(f"Primary Tools: {', '.join(result['primary_tools'])}")
        print(f"Secondary Tools: {', '.join(result['secondary_tools']) or 'Ninguna'}")
        if result.get('cli_suggestion'):
            print(f"CLI Tip: {result['cli_suggestion']}")
    
    elif cmd == "mcp":
        mcp_name = sys.argv[2] if len(sys.argv) > 2 else ""
        if not mcp_name:
            print("MCPs activos:", ", ".join(SkillLoader.list_active_mcps()))
        else:
            info = SkillLoader.get_mcp_info(mcp_name)
            if info:
                print(f"\nMCP: {mcp_name}")
                print(f"Status: {info.get('status')}")
                print(f"Descripción: {info.get('description', 'N/A')}")
                if 'phases' in info:
                    print(f"Fases: {', '.join(info['phases'])}")
            else:
                print(f"MCP '{mcp_name}' no encontrado")
    
    elif cmd == "suggest":
        task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not task:
            print("Fases disponibles:", ", ".join(SkillLoader.list_all_phases()))
        else:
            result = SkillLoader.suggest_for_task(task)
            print(f"\n{result['message']}")
            if result['tools'].get('cli_suggestion'):
                print(f"CLI Tip: {result['tools']['cli_suggestion']}")


if __name__ == '__main__':
    main()
