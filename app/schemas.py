from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Set

from pydantic import BaseModel, Field, field_validator, ConfigDict


class QuestionType(str, Enum):
    MCQ_SINGLE = "MCQ_SINGLE"
    MCQ_MULTI = "MCQ_MULTI"
    TRUE_FALSE = "TRUE_FALSE"
    SHORT_ANSWER = "SHORT_ANSWER"
    NUMERIC = "NUMERIC"


def _trimmed_nonempty(value: Optional[str], field_name: str) -> str:
    if value is None:
        raise ValueError(f"{field_name} is required")
    v = value.strip()
    if not v:
        raise ValueError(f"{field_name} cannot be empty")
    return v


class QuestionBase(BaseModel):
    stem: str = Field(..., max_length=1000)
    type: QuestionType
    choices: List[str] = Field(default_factory=list, max_length=50)
    correctIndexes: Set[int] = Field(default_factory=set)
    acceptableAnswers: List[str] = Field(default_factory=list, max_length=50)
    numericAnswer: Optional[float] = None
    explanation: Optional[str] = Field(default=None, max_length=2000)
    difficulty: int = Field(..., ge=1, le=5)
    tags: List[str] = Field(default_factory=list, max_length=50)
    subject: str = Field(..., max_length=100)
    gradeLevel: str = Field(..., max_length=50)
    bloomLevel: str = Field(..., max_length=100)
    mediaImageUrl: Optional[str] = Field(default=None, max_length=500)
    mediaAudioUrl: Optional[str] = Field(default=None, max_length=500)

    @field_validator("stem")
    @classmethod
    def validate_stem(cls, v: str) -> str:
        return _trimmed_nonempty(v, "stem")

    @field_validator("subject", "gradeLevel", "bloomLevel")
    @classmethod
    def validate_trimmed(cls, v: str, info):
        return _trimmed_nonempty(v, info.field_name)

    @field_validator("choices")
    @classmethod
    def strip_choices(cls, v: List[str]) -> List[str]:
        return [c.strip() for c in v if c is not None]

    @field_validator("acceptableAnswers", "tags")
    @classmethod
    def strip_lists(cls, v: List[str]) -> List[str]:
        return [s.strip() for s in v if s is not None]

    @field_validator("mediaImageUrl", "mediaAudioUrl")
    @classmethod
    def trim_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        t = v.strip()
        return t or None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(QuestionBase):
    pass


class QuestionRead(BaseModel):
    id: str
    createdAt: datetime
    updatedAt: datetime

    stem: str
    type: QuestionType
    choices: List[str]
    correctIndexes: Set[int]
    acceptableAnswers: List[str]
    numericAnswer: Optional[float]
    explanation: Optional[str]
    difficulty: int
    tags: List[str]
    subject: str
    gradeLevel: str
    bloomLevel: str
    mediaImageUrl: Optional[str]
    mediaAudioUrl: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class QuestionSearchQuery(BaseModel):
    query: Optional[str] = None
    type: Optional[QuestionType] = None
    tags: Optional[List[str]] = None
    difficultyMin: Optional[int] = Field(default=None, ge=1, le=5)
    difficultyMax: Optional[int] = Field(default=None, ge=1, le=5)
    subject: Optional[str] = None
    bloomLevel: Optional[str] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=200)


class VersionRead(BaseModel):
    id: int
    questionId: str
    version: int
    snapshotJson: dict
    createdAt: datetime


class QuizRules(BaseModel):
    numberOfQuestions: int = Field(..., ge=1, le=200)
    allowedTypes: Optional[List[QuestionType]] = None
    difficultyDistribution: Optional[dict] = None  # e.g., {"low":20,"medium":60,"high":20}
    tags: Optional[List[str]] = None
    subject: Optional[str] = None
    bloomLevel: Optional[str] = None
    shuffle: bool = True


class QuizCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    rules: QuizRules


class QuizRead(BaseModel):
    id: str
    name: str
    description: Optional[str]
    rules: QuizRules
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizItemRead(BaseModel):
    id: int
    quizId: str
    questionId: str
    position: int


class ImportRowError(BaseModel):
    rowNumber: int
    errors: List[str]


class ImportResult(BaseModel):
    created: int
    failed: int
    errors: List[ImportRowError]