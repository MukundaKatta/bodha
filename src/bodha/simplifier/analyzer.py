"""Complexity analyzer scoring document reading level with standard readability formulas."""

from __future__ import annotations

import math
import re

from bodha.models import Document, ReadabilityScores


class ComplexityAnalyzer:
    """Analyzes text complexity using multiple readability formulas."""

    # Common simple words (Dale-Chall inspired subset)
    SIMPLE_WORDS = frozenset({
        "a", "about", "after", "again", "all", "am", "an", "and", "any", "are",
        "as", "at", "back", "be", "because", "been", "before", "being", "big",
        "but", "by", "came", "can", "come", "could", "day", "did", "do", "down",
        "each", "end", "even", "every", "find", "first", "for", "from", "get",
        "give", "go", "going", "good", "got", "great", "had", "has", "have",
        "he", "her", "here", "him", "his", "how", "i", "if", "in", "into",
        "is", "it", "its", "just", "know", "last", "let", "life", "like",
        "little", "long", "look", "made", "make", "man", "many", "may", "me",
        "might", "more", "most", "much", "must", "my", "name", "new", "no",
        "not", "now", "of", "off", "old", "on", "one", "only", "or", "other",
        "our", "out", "over", "own", "part", "people", "place", "put", "read",
        "right", "said", "same", "saw", "say", "see", "she", "should", "show",
        "small", "so", "some", "something", "still", "such", "take", "tell",
        "than", "that", "the", "them", "then", "there", "these", "they",
        "thing", "think", "this", "those", "through", "time", "to", "too",
        "two", "under", "up", "upon", "us", "use", "very", "want", "was",
        "way", "we", "well", "went", "were", "what", "when", "where", "which",
        "while", "who", "why", "will", "with", "work", "world", "would",
        "year", "you", "your",
    })

    def analyze(self, text: str, title: str = "") -> Document:
        """Analyze text and return a Document with readability scores."""
        words = self._tokenize_words(text)
        sentences = self._tokenize_sentences(text)
        syllable_counts = [self._count_syllables(w) for w in words]

        word_count = len(words)
        sentence_count = max(len(sentences), 1)
        total_syllables = sum(syllable_counts)
        complex_words = [w for w, s in zip(words, syllable_counts) if s >= 3]
        avg_sentence_length = word_count / sentence_count
        avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
        total_chars = sum(len(w) for w in words)

        scores = ReadabilityScores(
            flesch_reading_ease=self._flesch_reading_ease(word_count, sentence_count, total_syllables),
            flesch_kincaid_grade=self._flesch_kincaid(word_count, sentence_count, total_syllables),
            gunning_fog=self._gunning_fog(word_count, sentence_count, len(complex_words)),
            coleman_liau=self._coleman_liau(total_chars, word_count, sentence_count),
            ari=self._automated_readability(total_chars, word_count, sentence_count),
            smog=self._smog(len(complex_words), sentence_count),
            dale_chall=self._dale_chall(words, sentence_count),
        )

        return Document(
            text=text,
            title=title,
            readability=scores,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            complex_word_ratio=len(complex_words) / max(word_count, 1),
        )

    def _tokenize_words(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z']+", text.lower())

    def _tokenize_sentences(self, text: str) -> list[str]:
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _count_syllables(self, word: str) -> int:
        word = word.lower().rstrip("e")
        if not word:
            return 1
        count = len(re.findall(r"[aeiouy]+", word))
        return max(count, 1)

    # --- Readability Formulas ---

    @staticmethod
    def _flesch_reading_ease(words: int, sentences: int, syllables: int) -> float:
        """Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)"""
        if words == 0 or sentences == 0:
            return 0.0
        return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)

    @staticmethod
    def _flesch_kincaid(words: int, sentences: int, syllables: int) -> float:
        """Flesch-Kincaid Grade Level."""
        if words == 0 or sentences == 0:
            return 0.0
        return 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59

    @staticmethod
    def _gunning_fog(words: int, sentences: int, complex_words: int) -> float:
        """Gunning Fog Index."""
        if words == 0 or sentences == 0:
            return 0.0
        return 0.4 * ((words / sentences) + 100 * (complex_words / words))

    @staticmethod
    def _coleman_liau(chars: int, words: int, sentences: int) -> float:
        """Coleman-Liau Index."""
        if words == 0:
            return 0.0
        l = (chars / words) * 100
        s = (sentences / words) * 100
        return 0.0588 * l - 0.296 * s - 15.8

    @staticmethod
    def _automated_readability(chars: int, words: int, sentences: int) -> float:
        """Automated Readability Index."""
        if words == 0 or sentences == 0:
            return 0.0
        return 4.71 * (chars / words) + 0.5 * (words / sentences) - 21.43

    @staticmethod
    def _smog(complex_words: int, sentences: int) -> float:
        """SMOG Grade."""
        if sentences == 0:
            return 0.0
        return 1.0430 * math.sqrt(complex_words * (30 / max(sentences, 1))) + 3.1291

    def _dale_chall(self, words: list[str], sentences: int) -> float:
        """Dale-Chall Readability Score."""
        if not words or sentences == 0:
            return 0.0
        difficult = sum(1 for w in words if w.lower() not in self.SIMPLE_WORDS)
        pdw = (difficult / len(words)) * 100
        raw = 0.1579 * pdw + 0.0496 * (len(words) / sentences)
        if pdw > 5:
            raw += 3.6365
        return raw
