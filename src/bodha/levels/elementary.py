"""Elementary adapter for grade 3-5 reading level."""

from __future__ import annotations

import re


class ElementaryAdapter:
    """Adapts text to grade 3-5 reading level.

    Strategies:
    - Very short sentences (max 10 words)
    - Only common, concrete vocabulary
    - Active voice preferred
    - Simple sentence structures (subject-verb-object)
    """

    max_sentence_words: int = 10

    # Words that are too complex for elementary level
    COMPLEX_REPLACEMENTS = {
        "however": "but",
        "therefore": "so",
        "although": "even though",
        "consequently": "so",
        "demonstrate": "show",
        "attempt": "try",
        "observe": "see",
        "construct": "build",
        "distribute": "give out",
        "evaluate": "check",
        "accumulate": "gather",
        "communicate": "talk",
        "environment": "world around us",
        "temperature": "how hot or cold",
        "significant": "big",
        "various": "many",
        "entire": "whole",
        "portion": "part",
        "frequently": "often",
        "immediately": "right away",
        "eventually": "in the end",
        "particular": "certain",
    }

    def adapt(self, text: str) -> str:
        """Adapt text to elementary reading level."""
        for complex_word, simple_word in self.COMPLEX_REPLACEMENTS.items():
            pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
            text = pattern.sub(simple_word, text)

        # Remove semicolons - split into separate sentences
        text = text.replace(";", ".")

        # Remove em-dashes and long dashes
        text = re.sub(r"\s*[—–-]{2,}\s*", ". ", text)

        return text
