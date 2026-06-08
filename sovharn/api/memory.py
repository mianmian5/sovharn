"""
Memory API
"""
from fastapi import APIRouter
from sovharn.core.memory import MemoryManager
from pathlib import Path
memory_mgr = MemoryManager(Path(__file__).resolve().parent.parent / "data" / "data" / "memory")

router = APIRouter()


@router.get("/memory")
async def list_memory(tier: str = "daily", limit: int = 30):
    if tier == "daily":
        return memory_mgr.list_daily(limit)
    elif tier == "permanent":
        return [{"topic": f.stem, "preview": f.read_text(encoding="utf-8")[:200]}
                for f in sorted(memory_mgr.permanent_dir.glob("*.md"))]
    return []


@router.get("/memory/{topic}")
async def get_memory(topic: str, tier: str = "permanent"):
    if tier == "daily":
        content = memory_mgr.get_daily(topic)
    else:
        content = memory_mgr.get_permanent(topic)
    return {"topic": topic, "content": content}


@router.post("/memory/distill")
async def distill_memory():
    count = 0
    for sid in list(memory_mgr._sessions.keys()):
        result = await memory_mgr.distill(sid)
        if result["status"] == "distilled":
            count += 1
    return {"status": "ok", "sessions_distilled": count}


@router.get("/memory/stats")
async def memory_stats():
    return memory_mgr.get_stats()
