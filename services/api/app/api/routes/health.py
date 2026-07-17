"""Health check endpoint — used by Kubernetes liveness probe."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("")
async def health():
    return JSONResponse({"status": "ok", "service": "voice-assistant-api"})
