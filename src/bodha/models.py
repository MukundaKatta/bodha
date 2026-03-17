"""Data models for document simplification."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReadingLevel(str, Enum):
    ELEMENTARY = "elementary"        # Grade 3-5
    MIDDLE_SCHOOL = "middle_school"  # Grade 6-8
    GENERAL_PUBLIC = "general_public" # Grade 8-10
    EXPERT = "expert"                # Preserves technical accuracy


class ReadabilityScores(BaseModel):
    """Collection of readability formula scores."""

    flesch_reading_ease: float = 0.0       # 0-100, higher = easier
    flesch_kincaid_grade: float = 0.0      # US grade level
    gunning_fog: float = 0.0              # Years of formal education
    coleman_liau: float = 0.0             # US grade level
    ari: float = 0.0                      # Automated Readability Index
    smog: float = 0.0                     # SMOG grade level
    dale_chall: float = 0.0               # Grade level estimate

    @property
    def average_grade_level(self) -> float:
        """Average of grade-level metrics."""
        grades = [self.flesch_kincaid_grade, self.gunning_fog, self.coleman_liau, self.ari]
        valid = [g for g in grades if g > 0]
        return sum(valid) / len(valid) if valid else 0.0


class Document(BaseModel):
    """Input document to be simplified."""

    text: str
    title: str = ""
    source: str = ""
    readability: ReadabilityScores = Field(default_factory=ReadabilityScores)
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    complex_word_ratio: float = 0.0


class KeyPoint(BaseModel):
    """An extracted key point from the document."""

    text: str
    importance: float = 1.0  # 0-1
    source_sentence: str = ""


class SimplifiedDocument(BaseModel):
    """Output simplified document."""

    original: Document
    simplified_text: str = ""
    target_level: ReadingLevel = ReadingLevel.GENERAL_PUBLIC
    readability: ReadabilityScores = Field(default_factory=ReadabilityScores)
    key_points: list[KeyPoint] = Field(default_factory=list)
    summary: str = ""
    word_count: int = 0
    simplification_ratio: float = 0.0  # simplified / original length
    generated_at: datetime = Field(default_factory=datetime.now)
