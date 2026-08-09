import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api_models import SkillOrchestrationRequest, SkillTransferRequest
from skill_orchestrator import skill_orchestrator, Skill, MCP

router = APIRouter()


@router.post("/api/skills/orchestrate")
async def orchestrate_skills(req: SkillOrchestrationRequest):
    try:
        result = skill_orchestrator.orchestrate({
            "domain": req.domain,
            "complexity": req.complexity,
            "useCase": req.useCase,
            "objectives": req.objectives
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/skills/available")
async def get_available_skills():
    skills = skill_orchestrator.get_available_skills()
    return {"skills": skills}


@router.post("/api/skills/transfer")
async def transfer_resources(req: SkillTransferRequest):
    skills = [Skill(**s) for s in req.skills]
    mcps = [MCP(**m) for m in req.mcps]

    result = skill_orchestrator.transfer_resources(req.project_id, skills, mcps)
    return result


@router.get("/api/skills/transferred/{project_id}")
async def get_transferred_resources(project_id: str):
    output_dir = Path(f"artifacts/project_outputs/{project_id}")

    if not output_dir.exists():
        return {"skills": [], "mcps": [], "status": "not_found"}

    skills = []
    skills_dir = output_dir / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skills.append({
                    "id": skill_dir.name,
                    "name": skill_dir.name.replace("-", " ").title(),
                    "path": str(skill_dir)
                })

    mcps = []
    mcp_config_file = output_dir / "config" / "mcps.json"
    if mcp_config_file.exists():
        mcp_config = json.loads(mcp_config_file.read_text())
        for mcp_id, mcp_data in mcp_config.get("mcpServers", {}).items():
            mcps.append({"id": mcp_id, **mcp_data})

    return {"skills": skills, "mcps": mcps, "status": "found"}
