"""Key point extractor pulling essential information from documents."""

from __future__ import annotations

import re

from bodha.models import Document, KeyPoint


class KeyPointExtractor:
    """Extracts key points and essential information from documents."""

    # Signal phrases that often introduce important information
    SIGNAL_PHRASES = [
        "important", "key", "critical", "essential", "significant",
        "main", "primary", "fundamental", "crucial", "notably",
        "in conclusion", "in summary", "therefore", "as a result",
        "the purpose", "the goal", "must", "required", "necessary",
    ]

    def extract(self, doc: Document, max_points: int = 10) -> list[KeyPoint]:
        """Extract key points from a document."""
        sentences = self._split_sentences(doc.text)
        scored = [(s, self._score_sentence(s, i, len(sentences))) for i, s in enumerate(sentences)]
        scored.sort(key=lambda x: x[1], reverse=True)

        key_points = []
        for sentence, score in scored[:max_points]:
            key_points.append(KeyPoint(
                text=sentence.strip(),
                importance=min(score, 1.0),
                source_sentence=sentence.strip(),
            ))
        return key_points

    def summarize(self, doc: Document, max_sentences: int = 3) -> str:
        """Generate a brief summary from the most important sentences."""
        points = self.extract(doc, max_points=max_sentences)
        # Re-order by appearance in original text
        points_with_pos = []
        for p in points:
            pos = doc.text.find(p.source_sentence)
            points_with_pos.append((pos if pos >= 0 else 0, p))
        points_with_pos.sort(key=lambda x: x[0])
        return " ".join(p.text for _, p in points_with_pos)

    def _split_sentences(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def _score_sentence(self, sentence: str, position: int, total: int) -> float:
        """Score a sentence's importance (0-1)."""
        score = 0.0
        lower = sentence.lower()

        # Signal phrase bonus
        for phrase in self.SIGNAL_PHRASES:
            if phrase in lower:
                score += 0.2
                break

        # Position bonus: first and last sentences are often important
        if position == 0:
            score += 0.3
        elif position == total - 1:
            score += 0.15
        elif position < 3:
            score += 0.1

        # Length: medium-length sentences are usually more informative
        words = sentence.split()
        if 10 <= len(words) <= 25:
            score += 0.15
        elif len(words) > 5:
            score += 0.05

        # Contains numbers or data
        if re.search(r"\d+", sentence):
            score += 0.1

        # Contains a definition or explanation pattern
        if re.search(r"\b(is|are|means|refers to|defined as)\b", lower):
            score += 0.15

        return min(score, 1.0)
