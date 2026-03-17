"""General public adapter for grade 8-10 reading level."""

from __future__ import annotations

import re


class GeneralPublicAdapter:
    """Adapts text to grade 8-10 reading level (general public).

    Strategies:
    - Moderate sentence length (max 20 words)
    - Common vocabulary with some academic terms
    - Clear paragraph structure
    - Minimal jargon
    """

    max_sentence_words: int = 20

    JARGON_REPLACEMENTS = {
        "aforementioned": "mentioned earlier",
        "heretofore": "until now",
        "notwithstanding": "despite",
        "hereinafter": "from now on",
        "cognizant": "aware",
        "promulgate": "announce",
        "adjudicate": "decide",
        "remuneration": "payment",
        "pecuniary": "financial",
        "ameliorate": "improve",
    }

    def adapt(self, text: str) -> str:
        """Adapt text to general public reading level."""
        for jargon, replacement in self.JARGON_REPLACEMENTS.items():
            pattern = re.compile(re.escape(jargon), re.IGNORECASE)
            text = pattern.sub(replacement, text)

        return text
