from fastapi import APIRouter
import os
router = APIRouter()
@router.get("/settings")
async def get_settings():
    return {
        "llm_api_key": bool(os.environ.get("LLM_API_KEY")),
        "llm_base_url": os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        "llm_model": os.environ.get("LLM_MODEL", "deepseek-chat"),
    }
