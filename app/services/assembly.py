from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Question, Quiz, QuizItem
from ..schemas import QuizRules, QuestionType


@dataclass
class SelectionResult:
    question_ids: List[str]


def _difficulty_bucket(d: int) -> str:
    if d <= 2:
        return "low"
    if d == 3:
        return "medium"
    return "high"


def _apply_filters(db: Session, rules: QuizRules) -> List[Question]:
    q = db.query(Question)

    if rules.allowedTypes:
        q = q.filter(Question.type.in_([t.value if isinstance(t, QuestionType) else t for t in rules.allowedTypes]))
    if rules.subject:
        q = q.filter(Question.subject.ilike(f"%{rules.subject}%"))
    if rules.bloomLevel:
        q = q.filter(Question.bloom_level.ilike(f"%{rules.bloomLevel}%"))

    candidates = q.all()

    if rules.tags:
        desired = set([t.lower() for t in rules.tags])
        filtered = []
        for qi in candidates:
            tags = set([t.lower() for t in json.loads(qi.tags or "[]")])
            if desired.issubset(tags):
                filtered.append(qi)
        candidates = filtered

    return candidates


def generate_selection(db: Session, rules: QuizRules) -> SelectionResult:
    candidates = _apply_filters(db, rules)

    buckets = {"low": [], "medium": [], "high": []}
    for q in candidates:
        buckets[_difficulty_bucket(q.difficulty)].append(q)

    distribution = rules.difficultyDistribution or {"low": 34, "medium": 33, "high": 33}

    total = rules.numberOfQuestions
    counts = {
        k: max(0, round((distribution.get(k, 0) / 100.0) * total)) for k in ["low", "medium", "high"]
    }
    assigned = sum(counts.values())
    # adjust rounding to match total
    while assigned < total:
        for k in ["medium", "low", "high"]:
            if assigned < total:
                counts[k] += 1
                assigned += 1
    while assigned > total:
        for k in ["high", "low", "medium"]:
            if assigned > total and counts[k] > 0:
                counts[k] -= 1
                assigned -= 1

    selection: List[Question] = []
    for k in ["low", "medium", "high"]:
        pool = buckets[k][:]
        random.shuffle(pool)
        selection.extend(pool[: counts[k]])

    if rules.shuffle:
        random.shuffle(selection)

    return SelectionResult(question_ids=[q.id for q in selection])


def save_quiz(db: Session, name: str, description: Optional[str], rules: QuizRules, question_ids: List[str]) -> Quiz:
    import uuid as _uuid
    quiz = Quiz(
        id=str(_uuid.uuid4()),
        name=name,
        description=description,
        rules_json=json.dumps(rules.model_dump()),
    )
    db.add(quiz)
    db.flush()

    for idx, qid in enumerate(question_ids, start=1):
        db.add(QuizItem(quiz_id=quiz.id, question_id=qid, position=idx))

    return quiz