"""
Agents API
"""
import yaml
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
AGENTS_DIR = Path(__file__).resolve().parent.parent / "data" / "data" / "agents"


class AgentCreate(BaseModel):
    name: str
    role: str = ""
    model: str = "deepseek-chat"
    system_prompt: str = "你是一个有用的AI助手。"
    skills: list = []
    specs: list = []
    memory: Optional[dict] = None


@router.get("/agents")
async def list_agents():
    agents = []
    for path in sorted(AGENTS_DIR.glob("*.yaml")) + sorted(AGENTS_DIR.glob("*.yml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if data:
            agents.append({
                "name": data.get("name", path.stem),
                "role": data.get("role", ""),
                "model": data.get("model", ""),
                "skills": data.get("skills", []),
                "specs": data.get("specs", []),
            })
    return agents


@router.get("/agents/{name}")
async def get_agent(name: str):
    for ext in [".yaml", ".yml"]:
        path = AGENTS_DIR / f"{name}{ext}"
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
    raise HTTPException(404, f"Agent '{name}' not found")


@router.post("/agents")
async def create_agent(agent: AgentCreate):
    path = AGENTS_DIR / f"{agent.name}.yaml"
    data = agent.dict(exclude_none=True)
    with open(path, "w") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    return {"name": agent.name, "status": "created"}


@router.delete("/agents/{name}")
async def delete_agent(name: str):
    for ext in [".yaml", ".yml"]:
        path = AGENTS_DIR / f"{name}{ext}"
        if path.exists():
            path.unlink()
            return {"name": name, "status": "deleted"}
    raise HTTPException(404, f"Agent '{name}' not found")
