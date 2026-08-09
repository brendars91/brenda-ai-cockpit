"""
Gem Dependency Graph - Visualización de dependencias entre Gems

Features:
- Análisis de dependencias entre Gems
- Detección de dependencias circulares
- Generación de grafo visual (Mermaid)
- Análisis de impacto de cambios
- Ordenamiento topológico
"""
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class GemNode:
    """Nodo del grafo de dependencias"""
    name: str
    version: str
    use_case_id: str
    risk_score: int
    tools: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)


@dataclass
class DependencyAnalysis:
    """Resultado del análisis de dependencias"""
    total_gems: int
    total_edges: int
    root_gems: List[str]  # Sin dependencias
    leaf_gems: List[str]  # Nadie depende de ellos
    circular_dependencies: List[Tuple[str, str]]
    isolated_gems: List[str]  # Sin conexiones
    max_depth: int


class GemDependencyGraph:
    """Analizador de dependencias de Gems"""
    
    def __init__(self, gems_dir: str = None):
        """
        Args:
            gems_dir: Directorio de Gems
        """
        if gems_dir is None:
            gems_dir = Path(__file__).parent.parent / "gems"
        
        self.gems_dir = Path(gems_dir)
        self.nodes: Dict[str, GemNode] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)  # gem -> dependencias
        self.reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)  # gem -> dependientes
    
    def load_gems(self) -> int:
        """
        Carga todos los Gems y construye el grafo.
        
        Returns:
            Número de gems cargados
        """
        self.nodes.clear()
        self.adjacency.clear()
        self.reverse_adjacency.clear()
        
        for gem_file in self.gems_dir.glob("*.json"):
            if gem_file.name.startswith("."):
                continue
            
            try:
                with open(gem_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                meta = data.get("bundle_meta", {})
                use_case_id = meta.get("use_case_id", gem_file.stem)
                
                # Extraer tools
                tools = [
                    t.get("name", "") 
                    for t in data.get("tools", {}).get("contracts", [])
                ]
                
                # Extraer dependencias (de metadata si existe)
                depends_on = meta.get("depends_on", [])
                
                # También inferir dependencias de tools compartidos
                # (gems que usan los mismos MCPs tienen relación potencial)
                
                node = GemNode(
                    name=use_case_id,
                    version=meta.get("version", "0.0.0"),
                    use_case_id=use_case_id,
                    risk_score=meta.get("risk_score", 0),
                    tools=tools,
                    depends_on=depends_on
                )
                
                self.nodes[use_case_id] = node
                
                # Construir adjacency lists
                for dep in depends_on:
                    self.adjacency[use_case_id].add(dep)
                    self.reverse_adjacency[dep].add(use_case_id)
                
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Actualizar lista de dependientes en cada nodo
        for name, node in self.nodes.items():
            node.dependents = list(self.reverse_adjacency.get(name, set()))
        
        return len(self.nodes)
    
    def analyze(self) -> DependencyAnalysis:
        """
        Analiza el grafo de dependencias.
        
        Returns:
            DependencyAnalysis con métricas
        """
        total_edges = sum(len(deps) for deps in self.adjacency.values())
        
        # Root gems (sin dependencias)
        root_gems = [
            name for name, node in self.nodes.items()
            if not node.depends_on
        ]
        
        # Leaf gems (nadie depende de ellos)
        leaf_gems = [
            name for name, node in self.nodes.items()
            if not node.dependents
        ]
        
        # Gems aislados (ni dependencias ni dependientes)
        isolated_gems = [
            name for name in self.nodes.keys()
            if name in root_gems and name in leaf_gems
        ]
        
        # Detectar ciclos
        circular = self._detect_cycles()
        
        # Calcular profundidad máxima
        max_depth = self._calculate_max_depth()
        
        return DependencyAnalysis(
            total_gems=len(self.nodes),
            total_edges=total_edges,
            root_gems=root_gems,
            leaf_gems=leaf_gems,
            circular_dependencies=circular,
            isolated_gems=isolated_gems,
            max_depth=max_depth
        )
    
    def _detect_cycles(self) -> List[Tuple[str, str]]:
        """Detecta dependencias circulares usando DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.adjacency.get(node, set()):
                if neighbor not in visited:
                    result = dfs(neighbor, path.copy())
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Ciclo encontrado
                    cycles.append((node, neighbor))
            
            rec_stack.remove(node)
            return None
        
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _calculate_max_depth(self) -> int:
        """Calcula la profundidad máxima del grafo"""
        if not self.nodes:
            return 0
        
        depths = {}
        
        def get_depth(node: str, visited: Set[str]) -> int:
            if node in visited:
                return 0  # Ciclo, evitar
            
            if node in depths:
                return depths[node]
            
            visited.add(node)
            
            if not self.adjacency.get(node):
                depths[node] = 1
            else:
                max_child = max(
                    get_depth(child, visited.copy())
                    for child in self.adjacency[node]
                    if child in self.nodes
                )
                depths[node] = 1 + max_child
            
            return depths[node]
        
        return max(get_depth(node, set()) for node in self.nodes)
    
    def get_impact(self, gem_name: str) -> Dict:
        """
        Analiza el impacto de cambios en un Gem.
        
        Args:
            gem_name: Nombre del gem
        
        Returns:
            Dict con gems afectados directa e indirectamente
        """
        if gem_name not in self.nodes:
            return {"error": f"Gem '{gem_name}' no encontrado"}
        
        # BFS para encontrar todos los dependientes
        direct = list(self.reverse_adjacency.get(gem_name, set()))
        
        indirect = set()
        queue = list(direct)
        visited = {gem_name}
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            dependents = self.reverse_adjacency.get(current, set())
            for dep in dependents:
                if dep not in visited:
                    indirect.add(dep)
                    queue.append(dep)
        
        return {
            "gem": gem_name,
            "direct_impact": direct,
            "indirect_impact": list(indirect),
            "total_affected": len(direct) + len(indirect)
        }
    
    def get_topological_order(self) -> List[str]:
        """
        Obtiene orden topológico (para build/deployment).
        
        Returns:
            Lista de gems en orden de dependencias
        """
        in_degree = {name: len(deps) for name, deps in 
                     {n: self.nodes[n].depends_on for n in self.nodes}.items()}
        
        queue = [n for n, d in in_degree.items() if d == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for dependent in self.reverse_adjacency.get(node, set()):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # Si hay ciclos, algunos nodos no estarán en result
        remaining = set(self.nodes.keys()) - set(result)
        result.extend(remaining)
        
        return result
    
    def to_mermaid(self) -> str:
        """
        Genera diagrama Mermaid del grafo.
        
        Returns:
            String con código Mermaid
        """
        lines = ["graph TD"]
        
        # Definir nodos con estilos según risk score
        for name, node in self.nodes.items():
            # Escapar caracteres especiales
            safe_name = name.replace("-", "_")
            
            if node.risk_score > 60:
                style = f'{safe_name}["{name}<br/>v{node.version}<br/>🔴 Risk: {node.risk_score}"]'
            elif node.risk_score > 30:
                style = f'{safe_name}["{name}<br/>v{node.version}<br/>🟡 Risk: {node.risk_score}"]'
            else:
                style = f'{safe_name}["{name}<br/>v{node.version}<br/>🟢 Risk: {node.risk_score}"]'
            
            lines.append(f"    {style}")
        
        # Definir edges
        for gem_name, deps in self.adjacency.items():
            safe_from = gem_name.replace("-", "_")
            for dep in deps:
                safe_to = dep.replace("-", "_")
                if dep in self.nodes:
                    lines.append(f"    {safe_from} --> {safe_to}")
        
        # Estilos para risk levels
        lines.append("")
        lines.append("    classDef high fill:#ffcccc,stroke:#ff0000")
        lines.append("    classDef medium fill:#ffffcc,stroke:#ffcc00")
        lines.append("    classDef low fill:#ccffcc,stroke:#00cc00")
        
        return "\n".join(lines)
    
    def to_json(self) -> Dict:
        """Exporta grafo como JSON"""
        return {
            "nodes": [
                {
                    "name": node.name,
                    "version": node.version,
                    "risk_score": node.risk_score,
                    "tools": node.tools,
                    "depends_on": node.depends_on,
                    "dependents": node.dependents
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {"from": src, "to": dst}
                for src, dsts in self.adjacency.items()
                for dst in dsts
            ]
        }


# CLI para testing standalone
if __name__ == "__main__":
    import sys
    
    graph = GemDependencyGraph()
    count = graph.load_gems()
    
    print("\n" + "="*60)
    print("  GEM DEPENDENCY GRAPH")
    print("="*60)
    
    print(f"\n📦 Gems cargados: {count}")
    
    if count == 0:
        print("  No hay gems en el directorio")
        sys.exit(0)
    
    analysis = graph.analyze()
    
    print(f"\n📊 Análisis:")
    print(f"  Total edges: {analysis.total_edges}")
    print(f"  Root gems (sin deps): {len(analysis.root_gems)}")
    print(f"  Leaf gems (sin dependientes): {len(analysis.leaf_gems)}")
    print(f"  Isolated gems: {len(analysis.isolated_gems)}")
    print(f"  Max depth: {analysis.max_depth}")
    
    if analysis.circular_dependencies:
        print(f"\n⚠️ Dependencias circulares detectadas:")
        for a, b in analysis.circular_dependencies:
            print(f"  {a} ↔ {b}")
    
    print(f"\n📋 Orden topológico (build order):")
    for i, gem in enumerate(graph.get_topological_order(), 1):
        print(f"  {i}. {gem}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--mermaid":
        print(f"\n```mermaid")
        print(graph.to_mermaid())
        print("```")
