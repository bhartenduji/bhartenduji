from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quiz_creator.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    seed_data_if_empty()


def seed_data_if_empty() -> None:
    from .models import Question

    with SessionLocal() as session:
        existing = session.query(Question).count()
        if existing > 0:
            return

        # Seed 10 varied questions
        now = datetime.utcnow()
        samples: List[Question] = [
            Question(
                id=str(uuid.uuid4()),
                stem="What is the capital of France?",
                type="MCQ_SINGLE",
                choices=json.dumps(["Paris", "Berlin", "Madrid", "Rome"]),
                correct_indexes=json.dumps([0]),
                acceptable_answers=json.dumps([]),
                numeric_answer=None,
                explanation="Paris is the capital city of France.",
                difficulty=2,
                tags=json.dumps(["geography", "europe"]),
                subject="Geography",
                grade_level="6",
                bloom_level="Remember",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="Select prime numbers",
                type="MCQ_MULTI",
                choices=json.dumps(["2", "4", "5", "9"]),
                correct_indexes=json.dumps([0, 2]),
                acceptable_answers=json.dumps([]),
                numeric_answer=None,
                explanation="2 and 5 are prime numbers.",
                difficulty=3,
                tags=json.dumps(["math", "number theory"]),
                subject="Mathematics",
                grade_level="7",
                bloom_level="Understand",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="The earth revolves around the sun.",
                type="TRUE_FALSE",
                choices=json.dumps([]),
                correct_indexes=json.dumps([1]),
                acceptable_answers=json.dumps([]),
                numeric_answer=None,
                explanation="This statement is true.",
                difficulty=1,
                tags=json.dumps(["science", "astronomy"]),
                subject="Science",
                grade_level="5",
                bloom_level="Remember",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="Define photosynthesis.",
                type="SHORT_ANSWER",
                choices=json.dumps([]),
                correct_indexes=json.dumps([]),
                acceptable_answers=json.dumps([
                    "process by which plants make food using sunlight",
                    "process plants use to convert light into chemical energy",
                ]),
                numeric_answer=None,
                explanation=None,
                difficulty=3,
                tags=json.dumps(["biology", "plants"]),
                subject="Science",
                grade_level="8",
                bloom_level="Understand",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="What is 12.5 + 7.5?",
                type="NUMERIC",
                choices=json.dumps([]),
                correct_indexes=json.dumps([]),
                acceptable_answers=json.dumps([]),
                numeric_answer=20.0,
                explanation=None,
                difficulty=2,
                tags=json.dumps(["math", "arithmetic"]),
                subject="Mathematics",
                grade_level="6",
                bloom_level="Apply",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="Identify the verb in the sentence: 'She quickly ran home.'",
                type="MCQ_SINGLE",
                choices=json.dumps(["She", "quickly", "ran", "home"]),
                correct_indexes=json.dumps([2]),
                acceptable_answers=json.dumps([]),
                numeric_answer=None,
                explanation="'ran' is the action verb.",
                difficulty=2,
                tags=json.dumps(["english", "grammar"]),
                subject="English",
                grade_level="6",
                bloom_level="Remember",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="Which of the following are mammals?",
                type="MCQ_MULTI",
                choices=json.dumps(["Whale", "Frog", "Bat", "Shark"]),
                correct_indexes=json.dumps([0, 2]),
                acceptable_answers=json.dumps([]),
                numeric_answer=None,
                explanation=None,
                difficulty=2,
                tags=json.dumps(["science", "zoology"]),
                subject="Science",
                grade_level="7",
                bloom_level="Understand",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="Water boils at 100°C at sea level.",
                type="TRUE_FALSE",
                choices=json.dumps([]),
                correct_indexes=json.dumps([1]),
                acceptable_answers=json.dumps([]),
                numeric_answer=None,
                explanation=None,
                difficulty=1,
                tags=json.dumps(["science", "chemistry"]),
                subject="Science",
                grade_level="5",
                bloom_level="Remember",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="Solve for x: 2x + 6 = 18",
                type="NUMERIC",
                choices=json.dumps([]),
                correct_indexes=json.dumps([]),
                acceptable_answers=json.dumps([]),
                numeric_answer=6.0,
                explanation="2x=12 so x=6.",
                difficulty=3,
                tags=json.dumps(["math", "algebra"]),
                subject="Mathematics",
                grade_level="8",
                bloom_level="Apply",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="Explain the significance of the Magna Carta.",
                type="SHORT_ANSWER",
                choices=json.dumps([]),
                correct_indexes=json.dumps([]),
                acceptable_answers=json.dumps([
                    "limited the power of the king",
                    "foundation of constitutional law",
                ]),
                numeric_answer=None,
                explanation=None,
                difficulty=4,
                tags=json.dumps(["history", "civics"]),
                subject="History",
                grade_level="9",
                bloom_level="Analyze",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
            Question(
                id=str(uuid.uuid4()),
                stem="What is the derivative of x^2?",
                type="SHORT_ANSWER",
                choices=json.dumps([]),
                correct_indexes=json.dumps([]),
                acceptable_answers=json.dumps(["2x", "2*x"]),
                numeric_answer=None,
                explanation=None,
                difficulty=4,
                tags=json.dumps(["math", "calculus"]),
                subject="Mathematics",
                grade_level="11",
                bloom_level="Apply",
                media_image_url=None,
                media_audio_url=None,
                created_at=now,
                updated_at=now,
            ),
        ]

        session.add_all(samples)
        session.commit()