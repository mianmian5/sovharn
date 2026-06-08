"""
Skills, Specs, Gates, Audit, Settings API (stubs)
"""
import yaml
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent / "data"
from sovharn.core.spec_engine import SpecEngine
from sovharn.core.gate_keeper import GateKeeper
spec_engine = SpecEngine(BASE_DIR / "data" / "specs")
gate_keeper = GateKeeper(BASE_DIR / "data" / "gates")

router = APIRouter()

# ═══════ Skills ═══════
SKILLS_DIR = BASE_DIR / "data" / "skills"

@router.get("/skills")
async def list_skills():
    skills = []
    for path in sorted(SKILLS_DIR.glob("*.yaml")) + sorted(SKILLS_DIR.glob("*.yml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if data:
            skills.append({"name": data.get("name", path.stem), "description": data.get("description", "")})
    return skills

# ═══════ Specs ═══════
@router.get("/specs")
async def list_specs():
    return spec_engine.list_specs()

class SpecCreate(BaseModel):
    name: str
    data: dict

@router.post("/specs")
async def create_spec(spec: SpecCreate):
    return spec_engine.create_spec(spec.name, spec.data)

# ═══════ Gates ═══════
GATES_DIR = BASE_DIR / "data" / "gates"

@router.get("/gates")
async def list_gates():
    gates = []
    if GATES_DIR.exists():
        for path in sorted(GATES_DIR.glob("*.yaml")):
            with open(path) as f:
                data = yaml.safe_load(f)
            if data:
                gates.append({"name": path.stem, "rules": data.get("rules", [])})
    return gates

@router.post("/gates/check")
async def gate_check(tool: str, agent: str = "default", args: dict = None):
    return gate_keeper.check_tool_call(tool, agent, args)

# ═══════ Audit ═══════
@router.get("/audit/stats")
async def audit_stats():
    return {"sessions": 0, "total_calls": 0, "total_cost": 0}

# ═══════ Settings ═══════
@router.get("/settings")
async def get_settings():
    import os
    return {
        "llm_api_key": bool(os.environ.get("LLM_API_KEY")),
        "llm_base_url": os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        "llm_model": os.environ.get("LLM_MODEL", "deepseek-chat"),
    }
