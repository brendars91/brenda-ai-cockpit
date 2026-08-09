#!/usr/bin/env python3
"""
AGCCE Agent Switcher v1.0
Gestiona el cambio de contexto entre agentes.

Carga perfiles de agente y proporciona el contexto adecuado
para cada fase del proceso.

Uso:
    from agent_switcher import AgentSwitcher
    profile = AgentSwitcher.get_profile("architect")
    AgentSwitcher.activate("constructor", plan_context)
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROFILES_DIR = PROJECT_ROOT / "config" / "agent_profiles"


class AgentSwitcher:
    """Gestor de cambio entre agentes."""
    
    _profiles_cache: Dict[str, Dict] = {}
    
    @classmethod
    def _load_profiles(cls):
        """Carga todos los perfiles de agente."""
        if cls._profiles_cache:
            return cls._profiles_cache
        
        if not PROFILES_DIR.exists():
            return {}
        
        for profile_file in PROFILES_DIR.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    cls._profiles_cache[profile["profile_id"]] = profile
            except:
                continue
        
        return cls._profiles_cache
    
    @classmethod
    def get_profile(cls, profile_id: str) -> Optional[Dict]:
        """
        Obtiene un perfil de agente.
        
        Args:
            profile_id: ID del perfil (architect, constructor, etc.)
        
        Returns:
            Dict con el perfil o None si no existe
        """
        profiles = cls._load_profiles()
        return profiles.get(profile_id)
    
    @classmethod
    def list_profiles(cls) -> List[str]:
        """Lista todos los perfiles disponibles."""
        profiles = cls._load_profiles()
        return list(profiles.keys())
    
    @classmethod
    def get_workflow(cls) -> List[Dict]:
        """
        Obtiene el flujo de trabajo ordenado.
        
        Returns:
            Lista de perfiles en orden de ejecución
        """
        profiles = cls._load_profiles()
        
        # Construir grafo de handoffs
        workflow = []
        visited = set()
        
        # Encontrar el inicio (receives_from = null)
        for pid, profile in profiles.items():
            if profile.get("receives_from") is None and pid not in visited:
                cls._build_workflow(pid, profiles, workflow, visited)
        
        return workflow
    
    @classmethod
    def _build_workflow(cls, profile_id: str, profiles: Dict, 
                       workflow: List, visited: set):
        """Construye workflow recursivamente."""
        if profile_id in visited or profile_id not in profiles:
            return
        
        visited.add(profile_id)
        workflow.append(profiles[profile_id])
        
        # Seguir handoff
        next_agent = profiles[profile_id].get("handoff_to")
        if next_agent:
            cls._build_workflow(next_agent, profiles, workflow, visited)
    
    @classmethod
    def get_context_for_phase(cls, phase: str) -> Optional[Dict]:
        """
        Obtiene el perfil de agente para una fase específica.
        
        Args:
            phase: Nombre de la fase (planning, implementation, etc.)
        """
        profiles = cls._load_profiles()
        
        for profile in profiles.values():
            if profile.get("phase") == phase:
                return profile
        
        return None
    
    @classmethod
    def activate(cls, profile_id: str, context: Dict = None) -> Dict:
        """
        Activa un agente y prepara su contexto.
        
        Args:
            profile_id: ID del perfil a activar
            context: Contexto adicional a pasar
        
        Returns:
            Dict con información de activación
        """
        profile = cls.get_profile(profile_id)
        if not profile:
            return {"error": f"Profile not found: {profile_id}"}
        
        # Importar Blackboard para actualizar estado
        try:
            from blackboard import Blackboard
            Blackboard.start_phase(
                profile.get("phase", "unknown"),
                profile_id,
                context.get("plan_id") if context else None
            )
        except ImportError:
            pass
        
        activation = {
            "active_agent": profile_id,
            "name": profile.get("name"),
            "role": profile.get("role"),
            "phase": profile.get("phase"),
            "system_prompt_extension": profile.get("system_prompt_extension"),
            "mcps_allowed": profile.get("mcps_allowed", []),
            "mcps_denied": profile.get("mcps_denied", []),
            "responsibilities": profile.get("responsibilities", []),
            "quality_checks": profile.get("quality_checks", []),
            "handoff_to": profile.get("handoff_to"),
            "context": context or {}
        }
        
        return activation
    
    @classmethod
    def get_instructions_for_agent(cls, profile_id: str) -> str:
        """
        Genera instrucciones formateadas para el agente.
        
        Returns:
            String con instrucciones para el system prompt
        """
        profile = cls.get_profile(profile_id)
        if not profile:
            return ""
        
        lines = [
            f"# MODO: {profile.get('name', profile_id).upper()}",
            f"",
            f"## Rol",
            f"{profile.get('system_prompt_extension', '')}",
            f"",
            f"## Responsabilidades"
        ]
        
        for resp in profile.get("responsibilities", []):
            lines.append(f"- {resp}")
        
        lines.extend([
            f"",
            f"## Herramientas Permitidas",
            f"{', '.join(profile.get('mcps_allowed', []))}",
            f"",
            f"## Herramientas PROHIBIDAS",
            f"{', '.join(profile.get('mcps_denied', []))}",
            f"",
            f"## Checks de Calidad (antes de entregar)"
        ])
        
        for check in profile.get("quality_checks", []):
            lines.append(f"- [ ] {check}")
        
        if profile.get("handoff_to"):
            lines.extend([
                f"",
                f"## Siguiente Fase",
                f"Al terminar, entregar a: **{profile['handoff_to']}**"
            ])
        
        return "\n".join(lines)
    
    @classmethod
    def validate_output(cls, profile_id: str, output: Dict) -> Dict:
        """
        Valida que el output cumple los checks de calidad.
        
        Returns:
            Dict con resultado de validación
        """
        profile = cls.get_profile(profile_id)
        if not profile:
            return {"valid": False, "error": "Profile not found"}
        
        checks = profile.get("quality_checks", [])
        passed = []
        failed = []
        
        # Validación básica
        for check in checks:
            # Por ahora, todos pasan (TODO: implementar validación real)
            passed.append(check)
        
        return {
            "valid": len(failed) == 0,
            "passed": passed,
            "failed": failed,
            "ready_for_handoff": len(failed) == 0
        }


def main():
    """CLI para Agent Switcher."""
    import sys
    
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════╗
║              AGCCE Agent Switcher v1.0                      ║
║           Gestión de Perfiles de Agente                     ║
╚══════════════════════════════════════════════════════════════╝

Uso:
  python agent_switcher.py list
  python agent_switcher.py show <profile_id>
  python agent_switcher.py workflow
  python agent_switcher.py activate <profile_id>

Ejemplos:
  python agent_switcher.py list
  python agent_switcher.py show architect
  python agent_switcher.py workflow
        """)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        profiles = AgentSwitcher.list_profiles()
        print("\nPerfiles disponibles:")
        for pid in profiles:
            profile = AgentSwitcher.get_profile(pid)
            print(f"  - {pid}: {profile.get('name', 'N/A')} ({profile.get('phase', 'N/A')})")
    
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Error: especifica profile_id")
            return
        
        profile_id = sys.argv[2]
        instructions = AgentSwitcher.get_instructions_for_agent(profile_id)
        
        if instructions:
            print(f"\n{instructions}")
        else:
            print(f"Perfil no encontrado: {profile_id}")
    
    elif cmd == "workflow":
        workflow = AgentSwitcher.get_workflow()
        
        print("\n" + "="*60)
        print("  FLUJO DE TRABAJO")
        print("="*60)
        
        for i, profile in enumerate(workflow, 1):
            arrow = " → " if i < len(workflow) else " ✓"
            print(f"\n  [{i}] {profile['name']} ({profile['profile_id']})")
            print(f"      Fase: {profile.get('phase', 'N/A')}")
            print(f"      MCPs: {', '.join(profile.get('mcps_allowed', []))}")
            if profile.get('handoff_to'):
                print(f"      Entrega a: {profile['handoff_to']}")
    
    elif cmd == "activate":
        if len(sys.argv) < 3:
            print("Error: especifica profile_id")
            return
        
        profile_id = sys.argv[2]
        activation = AgentSwitcher.activate(profile_id)
        
        if "error" in activation:
            print(f"Error: {activation['error']}")
        else:
            print(f"\n✓ Agente activado: {activation['name']}")
            print(f"  Fase: {activation['phase']}")
            print(f"  MCPs: {', '.join(activation['mcps_allowed'])}")
    
    else:
        print(f"Comando desconocido: {cmd}")


if __name__ == '__main__':
    main()
