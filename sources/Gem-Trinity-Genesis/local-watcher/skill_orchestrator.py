"""
Skill Orchestrator Service
Selecciona, adapta y crea skills/MCPs basado en el contexto del proyecto.
Sistema híbrido: Determinístico primero, LLM solo cuando es necesario.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from operation_tracker import track_operation

@dataclass
class Skill:
    id: str
    name: str
    description: str
    source: str  # 'existing', 'adapted', 'created'
    adapted_for: Optional[str] = None
    path: Optional[str] = None

@dataclass
class MCP:
    id: str
    name: str
    description: str
    status: str  # 'active', 'pending', 'unavailable'
    transferrable: bool
    config: Optional[Dict] = None

class SkillOrchestrator:
    def __init__(self):
        # Paths to skill directories
        self.resources_skills_dir = Path("resources/skills")
        self.gem_builder_skills_dir = Path("modules/gem-builder/skills")
        self.engine_skills_dir = Path("modules/engine/.agent/skills")
        self.mcp_config_path = Path("local-watcher/mcp_config_local.json")
        
        # Skill mapping by domain and keywords
        self.domain_skill_map = {
            "sap": [
                {"id": "sap-knowledge-base", "name": "SAP Knowledge Base", "desc": "Base de conocimiento SAP FI/CO/ABAP"},
                {"id": "abap-syntax", "name": "ABAP Syntax", "desc": "Parser y generador de código ABAP"},
                {"id": "financial-calculations", "name": "Financial Calculations", "desc": "Cálculos financieros IFRS/GAAP"}
            ],
            "devops": [
                {"id": "ci-cd-pipeline", "name": "CI/CD Pipeline", "desc": "Gestión de pipelines de integración"},
                {"id": "container-management", "name": "Container Management", "desc": "Docker y Kubernetes"},
                {"id": "infrastructure-as-code", "name": "Infrastructure as Code", "desc": "Terraform/Ansible templates"}
            ],
            "marketing": [
                {"id": "analytics-interpreter", "name": "Analytics Interpreter", "desc": "Interpretación de métricas marketing"},
                {"id": "content-generator", "name": "Content Generator", "desc": "Generación de contenido optimizado"}
            ],
            "custom": []
        }
        
        # MCP mapping by domain
        self.domain_mcp_map = {
            "sap": ["filesystem", "database", "sap-connector"],
            "devops": ["filesystem", "github", "docker", "context7"],
            "marketing": ["filesystem", "web-search", "social-media-api", "context7"],
            "custom": ["filesystem", "context7"]
        }
        
        # Complexity additions
        self.complexity_skills = {
            "simple": [],
            "medium": [
                {"id": "rag-pipeline", "name": "RAG Pipeline", "desc": "Retrieval Augmented Generation"}
            ],
            "difficult": [
                {"id": "rag-pipeline", "name": "RAG Pipeline", "desc": "Retrieval Augmented Generation"},
                {"id": "multi-agent-coordination", "name": "Multi-Agent Coordination", "desc": "Orquestación multi-agente"},
                {"id": "security-audit", "name": "Security Audit", "desc": "Auditoría de seguridad automática"}
            ]
        }
        
        self.complexity_mcps = {
            "simple": [],
            "medium": ["vector-db"],
            "difficult": ["vector-db", "snyk", "monitoring"]
        }
    
    @track_operation(op_type="deterministic", category="skill_orchestration")
    def orchestrate(self, context: Dict) -> Dict:
        """
        Main orchestration method.
        Returns selected skills and MCPs based on project context.
        
        This is DETERMINISTIC - no LLM calls here.
        """
        domain = context.get("domain", "custom")
        complexity = context.get("complexity", "medium")
        use_case = context.get("useCase", "")
        objectives = context.get("objectives", [])
        
        # === DETERMINISTIC SKILL SELECTION ===
        skills = []
        
        # Base skills (always included)
        skills.append(Skill(
            id="core-reasoning",
            name="Core Reasoning",
            description="Razonamiento lógico y análisis base",
            source="existing"
        ))
        skills.append(Skill(
            id="error-handling",
            name="Error Handling",
            description="Manejo robusto de errores y recuperación",
            source="existing"
        ))
        
        # Domain-specific skills
        for skill_def in self.domain_skill_map.get(domain, []):
            skills.append(Skill(
                id=skill_def["id"],
                name=skill_def["name"],
                description=skill_def["desc"],
                source="existing"
            ))
        
        # Complexity-based skills
        for skill_def in self.complexity_skills.get(complexity, []):
            if not any(s.id == skill_def["id"] for s in skills):
                skills.append(Skill(
                    id=skill_def["id"],
                    name=skill_def["name"],
                    description=skill_def["desc"],
                    source="existing"
                ))
        
        # Keyword-based skill detection from use case
        use_lower = use_case.lower()
        if "api" in use_lower or "rest" in use_lower:
            skills.append(Skill(
                id="api-integration",
                name="API Integration",
                description="Integración con APIs REST/GraphQL",
                source="existing"
            ))
        if "database" in use_lower or "sql" in use_lower or "datos" in use_lower:
            skills.append(Skill(
                id="database-queries",
                name="Database Queries",
                description="Consultas y operaciones de base de datos",
                source="existing"
            ))
        if "automation" in use_lower or "automatiz" in use_lower:
            skills.append(Skill(
                id="automation",
                name="Automation",
                description="Flujos de automatización y workflows",
                source="existing"
            ))
        if "excel" in use_lower or "xlsx" in use_lower:
            skills.append(Skill(
                id="xlsx",
                name="Excel Processing",
                description="Lectura y manipulación de archivos Excel",
                source="existing",
                path=str(self.resources_skills_dir / "xlsx")
            ))
        if "pdf" in use_lower:
            skills.append(Skill(
                id="pdf-processing",
                name="PDF Processing",
                description="Generación y lectura de PDFs",
                source="existing"
            ))
        
        # Check if skills exist in disk and adapt
        skills = self._check_and_adapt_skills(skills, context)
        
        # === DETERMINISTIC MCP SELECTION ===
        mcps = []
        
        # Base MCPs
        mcps.append(MCP(
            id="filesystem",
            name="Filesystem",
            description="Acceso a sistema de archivos",
            status="active",
            transferrable=True
        ))
        mcps.append(MCP(
            id="context7",
            name="Context7",
            description="Documentación en tiempo real",
            status="active",
            transferrable=True
        ))
        
        # Domain MCPs
        for mcp_id in self.domain_mcp_map.get(domain, []):
            if not any(m.id == mcp_id for m in mcps):
                mcps.append(self._create_mcp(mcp_id))
        
        # Complexity MCPs
        for mcp_id in self.complexity_mcps.get(complexity, []):
            if not any(m.id == mcp_id for m in mcps):
                mcps.append(self._create_mcp(mcp_id))
        
        return {
            "skills": [asdict(s) for s in skills],
            "mcps": [asdict(m) for m in mcps],
            "processing_type": "deterministic",
            "orchestration_summary": f"{len(skills)} skills, {len(mcps)} MCPs for {domain}/{complexity}"
        }
    
    def _check_and_adapt_skills(self, skills: List[Skill], context: Dict) -> List[Skill]:
        """
        Check if skills exist in resources and mark as adapted if context-specific.
        """
        adapted_skills = []
        domain = context.get("domain", "custom")
        
        for skill in skills:
            # Check if skill exists in resources
            skill_path = self.resources_skills_dir / skill.id
            if skill_path.exists():
                skill.path = str(skill_path)
                skill.source = "existing"
            
            # Mark domain-specific skills as adapted
            if domain != "custom" and skill.id in [s["id"] for s in self.domain_skill_map.get(domain, [])]:
                skill.source = "adapted"
                skill.adapted_for = f"Adaptado para {domain.upper()}"
            
            adapted_skills.append(skill)
        
        return adapted_skills
    
    def _create_mcp(self, mcp_id: str) -> MCP:
        """Create MCP object with config if available."""
        mcp_configs = {
            "database": {
                "name": "Database",
                "description": "Conexión a bases de datos SQL/NoSQL",
                "config": {"type": "postgresql", "pool_size": 10}
            },
            "sap-connector": {
                "name": "SAP Connector",
                "description": "RFC/BAPI connections a SAP",
                "config": {"mode": "demo", "client": "100"}
            },
            "github": {
                "name": "GitHub",
                "description": "GitHub API integration",
                "config": {"scope": "repo,read:org"}
            },
            "docker": {
                "name": "Docker",
                "description": "Docker management API",
                "config": {"socket": "/var/run/docker.sock"}
            },
            "vector-db": {
                "name": "Vector DB",
                "description": "Base de datos vectorial para RAG",
                "config": {"provider": "pgvector"}
            },
            "snyk": {
                "name": "Snyk",
                "description": "Security scanning",
                "config": {"scan_on_push": True}
            },
            "monitoring": {
                "name": "Monitoring",
                "description": "Telemetry and monitoring",
                "config": {"provider": "prometheus"}
            },
            "web-search": {
                "name": "Web Search",
                "description": "Búsqueda web integrada",
                "config": {"provider": "brave"}
            },
            "social-media-api": {
                "name": "Social Media API",
                "description": "APIs de redes sociales",
                "config": {"platforms": ["twitter", "linkedin"]}
            }
        }
        
        config = mcp_configs.get(mcp_id, {
            "name": mcp_id.replace("-", " ").title(),
            "description": f"MCP: {mcp_id}",
            "config": {}
        })
        
        return MCP(
            id=mcp_id,
            name=config["name"],
            description=config["description"],
            status="active" if mcp_id in ["filesystem", "context7", "github"] else "pending",
            transferrable=True,
            config=config.get("config")
        )
    
    def create_missing_skill(self, skill_id: str, context: Dict) -> Skill:
        """
        Create a new skill if it doesn't exist.
        This follows the skill creation best practices.
        """
        skill_dir = self.resources_skills_dir / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Create SKILL.md
        skill_md = f"""---
name: {skill_id.replace("-", " ").title()}
description: Auto-generated skill for {context.get('domain', 'custom')} domain
version: 1.0.0
---

# {skill_id.replace("-", " ").title()}

## Description
This skill was automatically generated for the project context.

## Usage
Refer to the main documentation for usage instructions.

## Customization
Adapt the functions below to your specific needs.
"""
        (skill_dir / "SKILL.md").write_text(skill_md)
        
        return Skill(
            id=skill_id,
            name=skill_id.replace("-", " ").title(),
            description=f"Skill creada para {context.get('domain', 'custom')}",
            source="created",
            path=str(skill_dir)
        )
    
    def get_available_skills(self) -> List[Dict]:
        """List all available skills from resources."""
        skills = []
        
        if self.resources_skills_dir.exists():
            for skill_dir in self.resources_skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_md = skill_dir / "SKILL.md"
                    description = "No description"
                    if skill_md.exists():
                        content = skill_md.read_text(encoding="utf-8", errors="replace")
                        # Extract description from YAML frontmatter
                        if "description:" in content:
                            lines = content.split("\n")
                            for line in lines:
                                if line.startswith("description:"):
                                    description = line.replace("description:", "").strip()
                                    break
                    
                    skills.append({
                        "id": skill_dir.name,
                        "name": skill_dir.name.replace("-", " ").title(),
                        "description": description,
                        "path": str(skill_dir)
                    })
        
        return skills
    
    def transfer_resources(self, project_id: str, skills: List[Skill], mcps: List[MCP]) -> Dict:
        """
        Transfer selected skills and MCPs to project output directory.
        """
        output_dir = Path(f"artifacts/project_outputs/{project_id}")
        skills_dir = output_dir / "skills"
        config_dir = output_dir / "config"
        
        skills_dir.mkdir(parents=True, exist_ok=True)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        transferred_skills = []
        transferred_mcps = []
        
        # Copy skills
        for skill in skills:
            if skill.path and Path(skill.path).exists():
                import shutil
                dest = skills_dir / skill.id
                if not dest.exists():
                    shutil.copytree(skill.path, dest)
                transferred_skills.append(skill.id)
        
        # Generate MCP config
        mcp_config = {
            "mcpServers": {}
        }
        for mcp in mcps:
            if mcp.transferrable:
                mcp_config["mcpServers"][mcp.id] = {
                    "name": mcp.name,
                    "description": mcp.description,
                    "config": mcp.config or {},
                    "status": mcp.status
                }
                transferred_mcps.append(mcp.id)
        
        (config_dir / "mcps.json").write_text(json.dumps(mcp_config, indent=2))
        
        return {
            "project_id": project_id,
            "output_dir": str(output_dir),
            "transferred_skills": transferred_skills,
            "transferred_mcps": transferred_mcps,
            "status": "success"
        }


# Create singleton instance
skill_orchestrator = SkillOrchestrator()
