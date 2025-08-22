from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from .db import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True)
    stem = Column(Text, nullable=False)
    type = Column(String, nullable=False)

    # Stored as JSON arrays
    choices = Column(Text, nullable=False, default="[]")
    correct_indexes = Column(Text, nullable=False, default="[]")
    acceptable_answers = Column(Text, nullable=False, default="[]")

    numeric_answer = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)

    difficulty = Column(Integer, nullable=False)
    tags = Column(Text, nullable=False, default="[]")
    subject = Column(String, nullable=False)
    grade_level = Column(String, nullable=False)
    bloom_level = Column(String, nullable=False)

    media_image_url = Column(String, nullable=True)
    media_audio_url = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    versions = relationship("Version", back_populates="question", cascade="all, delete-orphan")


class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column(String, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    snapshot_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    question = relationship("Question", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("question_id", "version", name="uq_versions_question_version"),
    )


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    rules_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship("QuizItem", back_populates="quiz", cascade="all, delete-orphan")


class QuizItem(Base):
    __tablename__ = "quiz_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(String, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)

    quiz = relationship("Quiz", back_populates="items")