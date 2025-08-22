from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Question, Quiz, QuizItem
from ..schemas import QuizCreate, QuizRead, QuizRules
from ..services.assembly import generate_selection, save_quiz

router = APIRouter()


@router.post("", response_model=QuizRead)
def create_quiz(payload: QuizCreate, db: Session = Depends(get_db)):
    selection = generate_selection(db, payload.rules)
    quiz = save_quiz(db, payload.name, payload.description, payload.rules, selection.question_ids)
    db.commit()
    db.refresh(quiz)
    return _to_quiz_read(quiz)


@router.get("/{quiz_id}", response_model=QuizRead)
def get_quiz(quiz_id: str, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return _to_quiz_read(quiz)


@router.post("/{quiz_id}/generate")
def regenerate_quiz(quiz_id: str, rules: QuizRules, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    selection = generate_selection(db, rules)
    # delete old items
    db.query(QuizItem).filter(QuizItem.quiz_id == quiz.id).delete()
    for idx, qid in enumerate(selection.question_ids, start=1):
        db.add(QuizItem(quiz_id=quiz.id, question_id=qid, position=idx))
    quiz.rules_json = json.dumps(rules.model_dump())
    db.commit()
    db.refresh(quiz)
    return _to_quiz_read(quiz)


@router.get("/{quiz_id}/export")
def export_quiz(quiz_id: str, format: str = "json", db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    items = db.query(QuizItem).filter(QuizItem.quiz_id == quiz_id).order_by(QuizItem.position.asc()).all()
    questions = {q.id: q for q in db.query(Question).all()}

    if format == "json":
        payload = {
            "id": quiz.id,
            "name": quiz.name,
            "description": quiz.description,
            "rules": json.loads(quiz.rules_json or "{}"),
            "items": [
                {
                    "position": it.position,
                    "question": _q_to_json(questions.get(it.question_id)),
                }
                for it in items
            ],
        }
        return JSONResponse(content=payload)

    # html
    html = _render_quiz_html(quiz, [questions.get(it.question_id) for it in items])
    return HTMLResponse(content=html)


def _q_to_json(q: Question) -> dict:
    import json as _json

    return {
        "id": q.id,
        "stem": q.stem,
        "type": q.type,
        "choices": _json.loads(q.choices or "[]"),
        "correctIndexes": _json.loads(q.correct_indexes or "[]"),
        "acceptableAnswers": _json.loads(q.acceptable_answers or "[]"),
        "numericAnswer": q.numeric_answer,
        "explanation": q.explanation,
        "difficulty": q.difficulty,
        "tags": _json.loads(q.tags or "[]"),
        "subject": q.subject,
        "gradeLevel": q.grade_level,
        "bloomLevel": q.bloom_level,
        "mediaImageUrl": q.media_image_url,
        "mediaAudioUrl": q.media_audio_url,
    }


def _render_quiz_html(quiz: Quiz, questions: list[Question]) -> str:
    def render_q(q: Question, idx: int) -> str:
        import json as _json

        body = f"<p><strong>{idx}. {q.stem}</strong></p>"
        if q.type in ("MCQ_SINGLE", "MCQ_MULTI"):
            options = _json.loads(q.choices or "[]")
            inputs = []
            input_type = "radio" if q.type == "MCQ_SINGLE" else "checkbox"
            for i, opt in enumerate(options):
                inputs.append(
                    f"<label style='display:block; margin-left:1rem'><input type='{input_type}' name='q{idx}'> {opt}</label>"
                )
            body += "\n".join(inputs)
        elif q.type == "TRUE_FALSE":
            body += f"<div style='margin-left:1rem'><label><input type='radio' name='q{idx}'> True</label> <label style='margin-left:1rem'><input type='radio' name='q{idx}'> False</label></div>"
        elif q.type == "SHORT_ANSWER":
            body += "<div style='margin-left:1rem'><input type='text' style='width:80%'></div>"
        elif q.type == "NUMERIC":
            body += "<div style='margin-left:1rem'><input type='number' step='any' style='width:50%'></div>"
        return f"<div style='margin-bottom:1rem'>{body}</div>"

    items_html = "\n".join([render_q(q, idx + 1) for idx, q in enumerate(questions) if q is not None])
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>{quiz.name} - Printable Quiz</title>
    <style>
      body {{ font-family: Arial, sans-serif; padding: 1rem; }}
      h1 {{ font-size: 1.5rem; }}
      .meta {{ color: #555; margin-bottom: 1rem; }}
    </style>
  </head>
  <body>
    <h1>{quiz.name}</h1>
    <div class='meta'>{quiz.description or ''}</div>
    {items_html}
  </body>
</html>
"""


def _to_quiz_read(quiz: Quiz) -> QuizRead:
    return QuizRead(
        id=quiz.id,
        name=quiz.name,
        description=quiz.description,
        rules=QuizRules(**json.loads(quiz.rules_json or "{}")),
        createdAt=quiz.created_at,
    )