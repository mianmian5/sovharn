"""
Sessions API with LLM support
"""
import asyncio, json, uuid, time, os, httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()
sessions = {}
cancel_flags = {}

class ChatRequest(BaseModel):
    message: str
    agent: str = "default-agent"
    spec: str = None

LLM_KEY = os.environ.get("LLM_API_KEY", "").replace("\u2026", "...")
LLM_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
SYS_PROMPT = "You are SovHarn Agent Harness. Be helpful, concise, use Chinese."

async def call_llm(messages: list) -> str:
    if not LLM_KEY:
        return "[模拟回复] LLM_API_KEY 未配置，请在 Settings 中设置。"
    hdrs = {"Authorization": "Bearer " + LLM_KEY, "Content-Type": "application/json"}
    payload = {"model": LLM_MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 4096}
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(LLM_URL.rstrip("/") + "/chat/completions", headers=hdrs, json=payload)
            if r.status_code != 200:
                return f"API Error ({r.status_code}): " + r.text[:200]
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM Error: " + str(e)[:100]

@router.post("/sessions")
async def create_session():
    sid = uuid.uuid4().hex[:12]
    sessions[sid] = {"id": sid, "messages": [], "created_at": time.time(), "status": "idle"}
    cancel_flags[sid] = asyncio.Event()
    return {"session_id": sid, "status": "created"}

@router.get("/sessions")
async def list_sessions():
    return sorted(
        [{"id": sid, "msgs": len(s.get("messages", [])), "created_at": s.get("created_at"), "status": s.get("status")}
         for sid, s in sessions.items()],
        key=lambda x: x["created_at"], reverse=True
    )[:50]

@router.get("/sessions/{sid}")
async def get_session(sid: str):
    s = sessions.get(sid)
    if not s: raise HTTPException(404)
    return s

@router.post("/sessions/{sid}/chat")
async def chat(sid: str, req: ChatRequest):
    s = sessions.get(sid)
    if not s: raise HTTPException(404)
    s["messages"].append({"role": "user", "content": req.message, "ts": time.time()})
    s["status"] = "running"

    from sovharn import memory_mgr
    memory_mgr.append_session(sid, "user", req.message)

    async def stream():
        try:
            msgs = [{"role": "system", "content": SYS_PROMPT}]
            for m in s["messages"]:
                msgs.append({"role": m["role"], "content": m["content"]})
            resp = await call_llm(msgs)
            s["messages"].append({"role": "assistant", "content": resp, "ts": time.time()})
            memory_mgr.append_session(sid, "assistant", resp)
            yield "data: " + json.dumps({"type": "text", "content": resp}, ensure_ascii=False) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({"type": "error", "content": str(e)[:200]}) + "\n\n"
        finally:
            s["status"] = "idle"

    return StreamingResponse(stream(), media_type="text/event-stream")

@router.post("/sessions/{sid}/stop")
async def stop_session(sid: str):
    f = cancel_flags.get(sid)
    if f: f.set()
    s = sessions.get(sid)
    if s: s["status"] = "stopped"
    return {"status": "stopped"}

@router.delete("/sessions/{sid}")
async def delete_session(sid: str):
    sessions.pop(sid, None)
    cancel_flags.pop(sid, None)
    from sovharn import memory_mgr
    await memory_mgr.distill(sid)
    return {"status": "deleted"}
