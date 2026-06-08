"""
SovHarn — Open-Source Agent Harness Platform
FastAPI 后端入口
"""
import asyncio, json, os, uuid
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SovHarn Agent Harness", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Import core modules
from sovharn.core.memory import MemoryManager
from sovharn.core.spec_engine import SpecEngine
from sovharn.core.gate_keeper import GateKeeper

memory_mgr = MemoryManager(DATA_DIR / "memory")
spec_engine = SpecEngine(DATA_DIR / "specs")
gate_keeper = GateKeeper(DATA_DIR / "gates")

# Import API routers
from sovharn.api import sessions, agents, skills, memory, audit, settings
app.include_router(sessions.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(settings.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0", "name": "SovHarn"}


@app.get("/api/")
async def root():
    return {"message": "🐴 SovHarn Agent Harness", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

def main():
    import uvicorn
    print("🐴 SovHarn Agent Harness v0.1.0")
    print("=" * 35)
    print("    http://127.0.0.1:8080")
    print()
    uvicorn.run("sovharn:app", host="127.0.0.1", port=8080, reload=False)

if __name__ == "__main__":
    main()
