"""Expert adapter maintaining technical accuracy."""

from __future__ import annotations

import re


class ExpertAdapter:
    """Adapts text for expert readers while maintaining technical accuracy.

    Strategies:
    - Preserve technical terminology
    - Allow longer sentences (max 30 words)
    - Maintain precision of language
    - Only simplify unnecessarily verbose constructions
    """

    max_sentence_words: int = 30

    # Only remove truly unnecessary verbosity
    VERBOSE_REPLACEMENTS = {
        "it is important to note that": "",
        "it should be noted that": "",
        "it is worth mentioning that": "",
        "as a matter of fact": "",
        "in order to": "to",
        "due to the fact that": "because",
        "in the event that": "if",
        "at this point in time": "now",
        "for the purpose of": "to",
        "in light of the fact that": "since",
        "on the grounds that": "because",
        "with regard to": "about",
        "in reference to": "about",
        "in terms of": "regarding",
        "the fact that": "that",
    }

    def adapt(self, text: str) -> str:
        """Adapt text for expert readers - minimal changes, reduce verbosity."""
        for verbose, concise in self.VERBOSE_REPLACEMENTS.items():
            pattern = re.compile(re.escape(verbose), re.IGNORECASE)
            text = pattern.sub(concise, text)

        # Clean up any double spaces from removals
        text = re.sub(r"\s+", " ", text)
        # Clean up sentence starts
        text = re.sub(r"\.\s+([a-z])", lambda m: ". " + m.group(1).upper(), text)

        return text
