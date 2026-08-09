from typing import Dict, List, Optional

from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    action: str
    target: str


class ArchitectGenerateRequest(BaseModel):
    use_case: str
    domain: str
    complexity: str
    model: str


class BuilderCompileRequest(BaseModel):
    payload_id: str
    agent_name: str
    llm_config: Dict
    tools: Optional[List[str]] = []


class EngineExecuteRequest(BaseModel):
    agent_id: str
    task: str
    stream: bool = True


class SAPExecuteRequest(BaseModel):
    transaction: str
    params: Dict
    mode: str = "demo"


class SkillOrchestrationRequest(BaseModel):
    domain: str
    complexity: str
    useCase: str
    objectives: Optional[List[str]] = []


class SkillTransferRequest(BaseModel):
    project_id: str
    skills: List[Dict]
    mcps: List[Dict]
