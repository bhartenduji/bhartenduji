from __future__ import annotations

from fastapi import APIRouter

from ..services.assist import diagnose_stem

router = APIRouter()


@router.post("/diagnose")
async def diagnose(payload: dict):
    stem = (payload or {}).get("stem", "")
    result = diagnose_stem(stem)
    return result