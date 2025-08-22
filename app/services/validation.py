from __future__ import annotations

from typing import List, Set

from ..schemas import QuestionCreate, QuestionUpdate, QuestionType


def validate_question_payload(payload: QuestionCreate | QuestionUpdate) -> List[str]:
    errors: List[str] = []

    qtype = payload.type
    choices = payload.choices or []
    correct_indexes: Set[int] = payload.correctIndexes or set()
    acceptable_answers = payload.acceptableAnswers or []
    numeric_answer = payload.numericAnswer

    if qtype in (QuestionType.MCQ_SINGLE, QuestionType.MCQ_MULTI):
        if len(choices) < 2:
            errors.append("MCQ questions require at least 2 choices")
        if not correct_indexes:
            errors.append("MCQ questions must have at least one correct index")
        max_index = len(choices) - 1
        for idx in correct_indexes:
            if idx < 0 or idx > max_index:
                errors.append(f"Correct index {idx} out of bounds for {len(choices)} choices")
        if qtype == QuestionType.MCQ_SINGLE and len(correct_indexes) != 1:
            errors.append("MCQ_SINGLE must have exactly one correct index")

    elif qtype == QuestionType.TRUE_FALSE:
        # encode TRUE as index 1, FALSE as index 0 (or vice-versa). We'll require exactly one index in {0,1}
        if len(correct_indexes) != 1 or not ({0, 1} >= correct_indexes):
            errors.append("TRUE_FALSE must have exactly one boolean answer (index 0 for False or 1 for True)")

    elif qtype == QuestionType.SHORT_ANSWER:
        if len(acceptable_answers) < 1:
            errors.append("SHORT_ANSWER requires at least one acceptable answer")

    elif qtype == QuestionType.NUMERIC:
        if numeric_answer is None:
            errors.append("NUMERIC requires numericAnswer")

    if len(payload.stem.strip()) == 0:
        errors.append("Stem cannot be empty")

    if payload.difficulty < 1 or payload.difficulty > 5:
        errors.append("Difficulty must be between 1 and 5")

    # String length enforcement beyond Pydantic
    if len(payload.subject.strip()) == 0:
        errors.append("Subject cannot be empty")
    if len(payload.bloomLevel.strip()) == 0:
        errors.append("Bloom level cannot be empty")
    if len(payload.gradeLevel.strip()) == 0:
        errors.append("Grade level cannot be empty")

    return errors