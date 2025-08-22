from __future__ import annotations

import json
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from ..models import Question, Version


EXCLUDED_FIELDS = {"created_at", "updated_at"}


def _question_to_snapshot(question: Question) -> dict:
    return {
        "id": question.id,
        "stem": question.stem,
        "type": question.type,
        "choices": json.loads(question.choices or "[]"),
        "correctIndexes": list(json.loads(question.correct_indexes or "[]")),
        "acceptableAnswers": json.loads(question.acceptable_answers or "[]"),
        "numericAnswer": question.numeric_answer,
        "explanation": question.explanation,
        "difficulty": question.difficulty,
        "tags": json.loads(question.tags or "[]"),
        "subject": question.subject,
        "gradeLevel": question.grade_level,
        "bloomLevel": question.bloom_level,
        "mediaImageUrl": question.media_image_url,
        "mediaAudioUrl": question.media_audio_url,
        "createdAt": question.created_at.isoformat() if question.created_at else None,
        "updatedAt": question.updated_at.isoformat() if question.updated_at else None,
    }


def create_version_snapshot(db: Session, question: Question) -> Version:
    latest = (
        db.query(Version)
        .filter(Version.question_id == question.id)
        .order_by(Version.version.desc())
        .first()
    )
    next_version = 1 if latest is None else latest.version + 1

    snapshot = _question_to_snapshot(question)
    version = Version(
        question_id=question.id,
        version=next_version,
        snapshot_json=json.dumps(snapshot),
        created_at=datetime.utcnow(),
    )
    db.add(version)
    db.flush()
    return version


def list_versions(db: Session, question_id: str) -> List[Version]:
    return (
        db.query(Version)
        .filter(Version.question_id == question_id)
        .order_by(Version.version.asc())
        .all()
    )


def restore_version(db: Session, question_id: str, version_number: int) -> Question:
    version = (
        db.query(Version)
        .filter(Version.question_id == question_id, Version.version == version_number)
        .first()
    )
    if version is None:
        raise ValueError("Version not found")

    snapshot = json.loads(version.snapshot_json)
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise ValueError("Question not found")

    # Restore fields
    question.stem = snapshot.get("stem", question.stem)
    question.type = snapshot.get("type", question.type)
    question.choices = json.dumps(snapshot.get("choices", []))
    question.correct_indexes = json.dumps(list(snapshot.get("correctIndexes", [])))
    question.acceptable_answers = json.dumps(snapshot.get("acceptableAnswers", []))
    question.numeric_answer = snapshot.get("numericAnswer")
    question.explanation = snapshot.get("explanation")
    question.difficulty = snapshot.get("difficulty", question.difficulty)
    question.tags = json.dumps(snapshot.get("tags", []))
    question.subject = snapshot.get("subject", question.subject)
    question.grade_level = snapshot.get("gradeLevel", question.grade_level)
    question.bloom_level = snapshot.get("bloomLevel", question.bloom_level)
    question.media_image_url = snapshot.get("mediaImageUrl")
    question.media_audio_url = snapshot.get("mediaAudioUrl")

    return question