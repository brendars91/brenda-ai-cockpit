import io
import json
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from runtime import architect, builder

router = APIRouter()


@router.get("/api/documentation/{project_id}")
async def get_project_documentation(project_id: str):
    payload = architect.get_payload(project_id)
    if not payload:
        agents = builder.get_agents()
        agent = next((a for a in agents if a.get("id") == project_id), None)
        if agent:
            payload = architect.get_payload(agent.get("payload_id", ""))

    if not payload:
        raise HTTPException(status_code=404, detail="Project not found")

    output_dir = Path(f"artifacts/project_outputs/{project_id}")
    transferred_skills = []
    transferred_mcps = []

    if output_dir.exists():
        skills_dir = output_dir / "skills"
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    transferred_skills.append({
                        "name": skill_dir.name.replace("-", " ").title(),
                        "description": f"Skill: {skill_dir.name}",
                        "adapted": True
                    })

        mcp_config_file = output_dir / "config" / "mcps.json"
        if mcp_config_file.exists():
            mcp_config = json.loads(mcp_config_file.read_text())
            for mcp_id, mcp_data in mcp_config.get("mcpServers", {}).items():
                transferred_mcps.append({
                    "name": mcp_data.get("name", mcp_id),
                    "description": mcp_data.get("description", "")
                })

    documentation = {
        "projectName": payload.get("project_name", f"Project {project_id[:8]}"),
        "createdAt": payload.get("iso_timestamp", ""),
        "domain": payload.get("domain", "custom"),
        "complexity": payload.get("complexity", "medium"),
        "prd": payload.get("prd", {}),
        "specContract": payload.get("spec_contract", {}),
        "transferredResources": {
            "skills": transferred_skills or [{
                "name": s,
                "description": f"Skill: {s}",
                "adapted": True
            } for s in payload.get("spec_contract", {}).get("skills_required", [])],
            "mcps": transferred_mcps or [{
                "name": m,
                "description": f"MCP: {m}"
            } for m in payload.get("spec_contract", {}).get("mcps_required", [])]
        }
    }

    return documentation


@router.get("/api/documentation/{project_id}/download")
async def download_project_documentation(project_id: str):
    payload = architect.get_payload(project_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Project not found")

    readme_content = f"""# {payload.get('project_name', 'Project')}

## Descripcion
{payload.get('use_case', 'Sin descripcion')}

## Dominio
**{payload.get('domain', 'custom').upper()}** | Complejidad: **{payload.get('complexity', 'medium').title()}**

## Fecha de Creacion
{payload.get('iso_timestamp', 'N/A')}

---

## PRD (Product Requirements Document)

### Resumen
- **Version**: {payload.get('prd', {}).get('meta', {}).get('format_version', '2.0-gated')}
- **Nivel**: {payload.get('prd', {}).get('meta', {}).get('complexity_level', 'medium')}

### Gates
{chr(10).join([f"- **{k}**: {v.get('name', k)} ({v.get('status', 'pending')})" for k, v in payload.get('prd', {}).get('gates', {}).items()])}

---

## Spec Contract

- **Version**: {payload.get('spec_contract', {}).get('version', '2.1.0')}
- **Nivel de Usuario**: {payload.get('spec_contract', {}).get('configuration', {}).get('user_level', 'basic')}

---

## Instalacion

```bash
# Clonar repositorio
git clone <repo-url>

# Instalar dependencias
pip install -r requirements.txt
npm install (si hay frontend)
```

## Uso

Consultar la documentacion del PRD y Spec Contract para instrucciones detalladas.

---

*Generado automaticamente por Gem Trinity Genesis*
"""

    dev_log = f"""# Development Log - {payload.get('project_name', 'Project')}

## Historial de Decisiones

### {payload.get('iso_timestamp', 'N/A')} - Proyecto Creado
- **Dominio**: {payload.get('domain', 'custom')}
- **Complejidad**: {payload.get('complexity', 'medium')}
- **Modelo LLM**: {payload.get('model', 'gemini-2.0')}

### PRD Gates Status
{chr(10).join([f"- Gate {k}: {v.get('status', 'pending')}" for k, v in payload.get('prd', {}).get('gates', {}).items()])}

### Items Pendientes (TBD)
{chr(10).join([f"- {item.get('field', 'N/A')}: {item.get('question', 'N/A')}" for item in payload.get('prd', {}).get('tbd_items', [])])}

---

*Generado automaticamente por Gem Trinity Genesis*
"""

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.md", readme_content)
        zf.writestr("DEVELOPMENT_LOG.md", dev_log)
        zf.writestr("payload.json", json.dumps(payload, indent=2, ensure_ascii=False))
        zf.writestr("prd.json", json.dumps(payload.get("prd", {}), indent=2, ensure_ascii=False))
        zf.writestr("spec_contract.json", json.dumps(payload.get("spec_contract", {}), indent=2, ensure_ascii=False))

    zip_buffer.seek(0)

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={payload.get('project_name', 'project').replace(' ', '_')}_docs.zip"
        }
    )
