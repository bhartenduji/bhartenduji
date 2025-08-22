from __future__ import annotations

import csv
import io
import json
import uuid
from typing import Iterable, List, Tuple

from sqlalchemy.orm import Session

from ..models import Question
from ..schemas import ImportResult, ImportRowError, QuestionCreate, QuestionType
from .validation import validate_question_payload


CSV_FIELDS = [
    "stem",
    "type",
    "choices",
    "correctIndexes",
    "acceptableAnswers",
    "numericAnswer",
    "explanation",
    "difficulty",
    "tags",
    "subject",
    "gradeLevel",
    "bloomLevel",
    "mediaImageUrl",
    "mediaAudioUrl",
]


def _parse_list(s: str) -> List[str]:
    if s is None or s == "":
        return []
    # accept JSON or pipe/comma separated
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except Exception:
        pass
    # fallback split
    parts = [p.strip() for p in s.split("|") if p.strip()]
    if not parts and "," in s:
        parts = [p.strip() for p in s.split(",") if p.strip()]
    return parts


def _parse_indexes(s: str) -> List[int]:
    if s is None or s == "":
        return []
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return [int(x) for x in parsed]
    except Exception:
        pass
    return [int(x.strip()) for x in s.split("|") if x.strip()]


def export_questions_json(db: Session) -> str:
    rows = db.query(Question).all()
    out = []
    import datetime
    for r in rows:
        out.append(
            {
                "id": r.id,
                "stem": r.stem,
                "type": r.type,
                "choices": json.loads(r.choices or "[]"),
                "correctIndexes": json.loads(r.correct_indexes or "[]"),
                "acceptableAnswers": json.loads(r.acceptable_answers or "[]"),
                "numericAnswer": r.numeric_answer,
                "explanation": r.explanation,
                "difficulty": r.difficulty,
                "tags": json.loads(r.tags or "[]"),
                "subject": r.subject,
                "gradeLevel": r.grade_level,
                "bloomLevel": r.bloom_level,
                "mediaImageUrl": r.media_image_url,
                "mediaAudioUrl": r.media_audio_url,
                "createdAt": r.created_at.isoformat() if r.created_at else None,
                "updatedAt": r.updated_at.isoformat() if r.updated_at else None,
            }
        )
    return json.dumps(out, ensure_ascii=False, indent=2)


def export_questions_csv(db: Session) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()

    rows = db.query(Question).all()
    for r in rows:
        writer.writerow(
            {
                "stem": r.stem,
                "type": r.type,
                "choices": json.dumps(json.loads(r.choices or "[]")),
                "correctIndexes": json.dumps(json.loads(r.correct_indexes or "[]")),
                "acceptableAnswers": json.dumps(json.loads(r.acceptable_answers or "[]")),
                "numericAnswer": r.numeric_answer if r.numeric_answer is not None else "",
                "explanation": r.explanation or "",
                "difficulty": r.difficulty,
                "tags": json.dumps(json.loads(r.tags or "[]")),
                "subject": r.subject,
                "gradeLevel": r.grade_level,
                "bloomLevel": r.bloom_level,
                "mediaImageUrl": r.media_image_url or "",
                "mediaAudioUrl": r.media_audio_url or "",
            }
        )

    return output.getvalue()


def import_questions_json(db: Session, content: str) -> ImportResult:
    payload = json.loads(content)
    errors: List[ImportRowError] = []
    created = 0

    for idx, item in enumerate(payload, start=1):
        try:
            qc = QuestionCreate(**item)
            errs = validate_question_payload(qc)
            if errs:
                errors.append(ImportRowError(rowNumber=idx, errors=errs))
                continue
            q = Question(
                id=item.get("id") or str(uuid.uuid4()),
                stem=qc.stem,
                type=qc.type.value,
                choices=json.dumps(qc.choices),
                correct_indexes=json.dumps(sorted(list(qc.correctIndexes))),
                acceptable_answers=json.dumps(qc.acceptableAnswers),
                numeric_answer=qc.numericAnswer,
                explanation=qc.explanation,
                difficulty=qc.difficulty,
                tags=json.dumps(qc.tags),
                subject=qc.subject,
                grade_level=qc.gradeLevel,
                bloom_level=qc.bloomLevel,
                media_image_url=qc.mediaImageUrl,
                media_audio_url=qc.mediaAudioUrl,
            )
            db.add(q)
            created += 1
        except Exception as e:  # validation error shape
            errors.append(ImportRowError(rowNumber=idx, errors=[str(e)]))
    db.commit()
    return ImportResult(created=created, failed=len(errors), errors=errors)


def import_questions_csv(db: Session, content: str) -> ImportResult:
    reader = csv.DictReader(io.StringIO(content))
    errors: List[ImportRowError] = []
    created = 0

    for idx, row in enumerate(reader, start=2):  # header is row 1
        try:
            qc = QuestionCreate(
                stem=row.get("stem", ""),
                type=QuestionType(row.get("type", "")),
                choices=_parse_list(row.get("choices", "")),
                correctIndexes=set(_parse_indexes(row.get("correctIndexes", ""))),
                acceptableAnswers=_parse_list(row.get("acceptableAnswers", "")),
                numericAnswer=float(row["numericAnswer"]) if row.get("numericAnswer") else None,
                explanation=row.get("explanation") or None,
                difficulty=int(row.get("difficulty") or 0),
                tags=_parse_list(row.get("tags", "")),
                subject=row.get("subject", ""),
                gradeLevel=row.get("gradeLevel", ""),
                bloomLevel=row.get("bloomLevel", ""),
                mediaImageUrl=row.get("mediaImageUrl") or None,
                mediaAudioUrl=row.get("mediaAudioUrl") or None,
            )
            errs = validate_question_payload(qc)
            if errs:
                errors.append(ImportRowError(rowNumber=idx, errors=errs))
                continue
            q = Question(
                id=str(uuid.uuid4()),
                stem=qc.stem,
                type=qc.type.value,
                choices=json.dumps(qc.choices),
                correct_indexes=json.dumps(sorted(list(qc.correctIndexes))),
                acceptable_answers=json.dumps(qc.acceptableAnswers),
                numeric_answer=qc.numericAnswer,
                explanation=qc.explanation,
                difficulty=qc.difficulty,
                tags=json.dumps(qc.tags),
                subject=qc.subject,
                grade_level=qc.gradeLevel,
                bloom_level=qc.bloomLevel,
                media_image_url=qc.mediaImageUrl,
                media_audio_url=qc.mediaAudioUrl,
            )
            db.add(q)
            created += 1
        except Exception as e:
            errors.append(ImportRowError(rowNumber=idx, errors=[str(e)]))
    db.commit()
    return ImportResult(created=created, failed=len(errors), errors=errors)