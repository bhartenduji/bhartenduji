from __future__ import annotations

import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Question
from ..schemas import (
    QuestionCreate,
    QuestionRead,
    QuestionSearchQuery,
    QuestionType,
    QuestionUpdate,
    VersionRead,
)
from ..services.validation import validate_question_payload
from ..services.versioning import create_version_snapshot, list_versions, restore_version

router = APIRouter()


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    errs = validate_question_payload(payload)
    if errs:
        raise HTTPException(status_code=400, detail=errs)

    q = Question(
        id=str(uuid.uuid4()),
        stem=payload.stem.strip(),
        type=payload.type.value,
        choices=json.dumps(payload.choices),
        correct_indexes=json.dumps(sorted(list(payload.correctIndexes))),
        acceptable_answers=json.dumps(payload.acceptableAnswers),
        numeric_answer=payload.numericAnswer,
        explanation=payload.explanation.strip() if payload.explanation else None,
        difficulty=payload.difficulty,
        tags=json.dumps(payload.tags),
        subject=payload.subject.strip(),
        grade_level=payload.gradeLevel.strip(),
        bloom_level=payload.bloomLevel.strip(),
        media_image_url=payload.mediaImageUrl,
        media_audio_url=payload.mediaAudioUrl,
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    create_version_snapshot(db, q)
    db.commit()

    return _to_read(q)


@router.get("/{question_id}", response_model=QuestionRead)
def get_question(question_id: str, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return _to_read(q)


@router.put("/{question_id}", response_model=QuestionRead)
def update_question(question_id: str, payload: QuestionUpdate, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    errs = validate_question_payload(payload)
    if errs:
        raise HTTPException(status_code=400, detail=errs)

    # create version BEFORE update to capture prior state
    create_version_snapshot(db, q)

    q.stem = payload.stem.strip()
    q.type = payload.type.value
    q.choices = json.dumps(payload.choices)
    q.correct_indexes = json.dumps(sorted(list(payload.correctIndexes)))
    q.acceptable_answers = json.dumps(payload.acceptableAnswers)
    q.numeric_answer = payload.numericAnswer
    q.explanation = payload.explanation.strip() if payload.explanation else None
    q.difficulty = payload.difficulty
    q.tags = json.dumps(payload.tags)
    q.subject = payload.subject.strip()
    q.grade_level = payload.gradeLevel.strip()
    q.bloom_level = payload.bloomLevel.strip()
    q.media_image_url = payload.mediaImageUrl
    q.media_audio_url = payload.mediaAudioUrl

    db.commit()
    db.refresh(q)

    return _to_read(q)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: str, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return None


@router.get("", response_model=List[QuestionRead])
def list_questions(
    query: Optional[str] = Query(default=None),
    type: Optional[QuestionType] = Query(default=None),
    tags: Optional[str] = Query(default=None, description="Comma-separated tags (all must match)"),
    difficultyMin: Optional[int] = Query(default=None, ge=1, le=5),
    difficultyMax: Optional[int] = Query(default=None, ge=1, le=5),
    subject: Optional[str] = Query(default=None),
    bloomLevel: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Question)

    if query:
        like = f"%{query}%"
        q = q.filter(Question.stem.ilike(like))
    if type:
        q = q.filter(Question.type == type.value)
    if subject:
        q = q.filter(Question.subject.ilike(f"%{subject}%"))
    if bloomLevel:
        q = q.filter(Question.bloom_level.ilike(f"%{bloomLevel}%"))
    if difficultyMin is not None:
        q = q.filter(Question.difficulty >= difficultyMin)
    if difficultyMax is not None:
        q = q.filter(Question.difficulty <= difficultyMax)

    results = q.all()

    if tags:
        desired = set([t.strip().lower() for t in tags.split(",") if t.strip()])
        filtered = []
        for row in results:
            row_tags = set([t.lower() for t in json.loads(row.tags or "[]")])
            if desired.issubset(row_tags):
                filtered.append(row)
        results = filtered

    # pagination
    start = (page - 1) * size
    end = start + size
    page_rows = results[start:end]

    return [_to_read(r) for r in page_rows]


@router.get("/{question_id}/versions", response_model=List[VersionRead])
def get_versions(question_id: str, db: Session = Depends(get_db)):
    versions = list_versions(db, question_id)
    return [
        VersionRead(
            id=v.id,
            questionId=v.question_id,
            version=v.version,
            snapshotJson=json.loads(v.snapshot_json),
            createdAt=v.created_at,
        )
        for v in versions
    ]


@router.post("/{question_id}/restore")
def restore(question_id: str, version: int, db: Session = Depends(get_db)):
    try:
        q = restore_version(db, question_id, version)
        db.commit()
        return _to_read(q)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


def _to_read(q: Question) -> QuestionRead:
    return QuestionRead(
        id=q.id,
        createdAt=q.created_at,
        updatedAt=q.updated_at,
        stem=q.stem,
        type=q.type,
        choices=json.loads(q.choices or "[]"),
        correctIndexes=set(json.loads(q.correct_indexes or "[]")),
        acceptableAnswers=json.loads(q.acceptable_answers or "[]"),
        numericAnswer=q.numeric_answer,
        explanation=q.explanation,
        difficulty=q.difficulty,
        tags=json.loads(q.tags or "[]"),
        subject=q.subject,
        gradeLevel=q.grade_level,
        bloomLevel=q.bloom_level,
        mediaImageUrl=q.media_image_url,
        mediaAudioUrl=q.media_audio_url,
    )