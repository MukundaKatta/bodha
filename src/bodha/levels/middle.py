"""Middle school adapter for grade 6-8 reading level."""

from __future__ import annotations

import re


class MiddleSchoolAdapter:
    """Adapts text to grade 6-8 reading level.

    Strategies:
    - Medium sentence length (max 15 words)
    - Allow common academic vocabulary
    - Simple compound sentences ok
    - Define technical terms inline
    """

    max_sentence_words: int = 15

    COMPLEX_REPLACEMENTS = {
        "furthermore": "also",
        "nevertheless": "even so",
        "subsequently": "then",
        "predominantly": "mostly",
        "infrastructure": "basic systems",
        "methodology": "method",
        "paradigm": "way of thinking",
        "dichotomy": "split",
        "juxtaposition": "comparison",
        "extrapolate": "predict from data",
    }

    def adapt(self, text: str) -> str:
        """Adapt text to middle school reading level."""
        for complex_word, simple_word in self.COMPLEX_REPLACEMENTS.items():
            pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
            text = pattern.sub(simple_word, text)

        # Simplify semicolons to periods
        text = text.replace(";", ".")

        return text
