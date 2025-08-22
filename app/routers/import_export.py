from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.import_export import (
    export_questions_csv,
    export_questions_json,
    import_questions_csv,
    import_questions_json,
)

router = APIRouter()


@router.get("/export", response_class=PlainTextResponse)
def export_questions(format: str = Query(default="json", pattern="^(json|csv)$"), db: Session = Depends(get_db)):
    if format == "csv":
        content = export_questions_csv(db)
        return PlainTextResponse(content, media_type="text/csv")
    content = export_questions_json(db)
    return PlainTextResponse(content, media_type="application/json")


@router.post("/import")
async def import_questions(
    file: UploadFile = File(...),
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    data = (await file.read()).decode("utf-8")
    if format == "json":
        result = import_questions_json(db, data)
        return result.model_dump()
    elif format == "csv":
        result = import_questions_csv(db, data)
        return result.model_dump()
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")