"""Text simplifier reducing complexity while preserving meaning."""

from __future__ import annotations

import re

from bodha.models import Document, ReadingLevel, SimplifiedDocument, ReadabilityScores


class TextSimplifier:
    """Simplifies text by applying rule-based transformations.

    Strategies:
    - Split long sentences
    - Replace complex words with simpler synonyms
    - Remove parenthetical asides
    - Shorten passive constructions
    - Reduce clause nesting
    """

    # Complex -> simple word mapping
    WORD_MAP: dict[str, str] = {
        "utilize": "use", "utilization": "use", "implement": "set up",
        "facilitate": "help", "subsequent": "next", "prior": "before",
        "sufficient": "enough", "demonstrate": "show", "approximately": "about",
        "numerous": "many", "commence": "start", "terminate": "end",
        "endeavor": "try", "indicate": "show", "regarding": "about",
        "nevertheless": "still", "consequently": "so", "furthermore": "also",
        "additional": "more", "assist": "help", "obtain": "get",
        "purchase": "buy", "require": "need", "provide": "give",
        "establish": "set up", "maintain": "keep", "sufficient": "enough",
        "accomplish": "do", "determine": "find out", "comprehend": "understand",
        "initiate": "start", "modification": "change", "component": "part",
        "methodology": "method", "functionality": "feature",
        "infrastructure": "system", "paradigm": "model",
        "leveraging": "using", "leverage": "use", "optimize": "improve",
        "streamline": "simplify", "robust": "strong", "scalable": "flexible",
        "synergy": "teamwork", "stakeholder": "person involved",
        "deliverable": "result", "bandwidth": "time",
        "incentivize": "encourage", "proactive": "active",
    }

    def simplify(self, doc: Document, target_level: ReadingLevel) -> SimplifiedDocument:
        """Simplify document text to match the target reading level."""
        from bodha.levels.elementary import ElementaryAdapter
        from bodha.levels.middle import MiddleSchoolAdapter
        from bodha.levels.general import GeneralPublicAdapter
        from bodha.levels.expert import ExpertAdapter

        adapters = {
            ReadingLevel.ELEMENTARY: ElementaryAdapter(),
            ReadingLevel.MIDDLE_SCHOOL: MiddleSchoolAdapter(),
            ReadingLevel.GENERAL_PUBLIC: GeneralPublicAdapter(),
            ReadingLevel.EXPERT: ExpertAdapter(),
        }
        adapter = adapters[target_level]

        text = doc.text
        text = self._replace_complex_words(text)
        text = self._split_long_sentences(text, adapter.max_sentence_words)
        text = self._remove_parentheticals(text)
        text = adapter.adapt(text)

        from bodha.simplifier.analyzer import ComplexityAnalyzer
        analyzer = ComplexityAnalyzer()
        simplified_doc = analyzer.analyze(text)

        return SimplifiedDocument(
            original=doc,
            simplified_text=text,
            target_level=target_level,
            readability=simplified_doc.readability,
            word_count=simplified_doc.word_count,
            simplification_ratio=simplified_doc.word_count / max(doc.word_count, 1),
        )

    def _replace_complex_words(self, text: str) -> str:
        """Replace complex words with simpler alternatives."""
        for complex_word, simple_word in self.WORD_MAP.items():
            pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
            def replacer(m, simple=simple_word):
                if m.group()[0].isupper():
                    return simple.capitalize()
                return simple
            text = pattern.sub(replacer, text)
        return text

    def _split_long_sentences(self, text: str, max_words: int) -> str:
        """Split sentences exceeding max_words at natural break points."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) <= max_words:
                result.append(sentence)
                continue
            # Split at conjunctions or commas
            chunks: list[list[str]] = [[]]
            for word in words:
                chunks[-1].append(word)
                if len(chunks[-1]) >= max_words and word.rstrip(",") in (
                    "and", "but", "or", "which", "that", "because", "while",
                    "although", "however", "therefore",
                ):
                    last_word = chunks[-1][-1]
                    if last_word.endswith(","):
                        chunks[-1][-1] = last_word.rstrip(",") + "."
                    else:
                        chunks[-1].append(".")  # This will be joined
                    chunks.append([])
            for chunk in chunks:
                if chunk:
                    s = " ".join(chunk)
                    if not s.rstrip().endswith((".", "!", "?")):
                        s = s.rstrip() + "."
                    result.append(s)
        return " ".join(result)

    def _remove_parentheticals(self, text: str) -> str:
        """Remove parenthetical asides that add complexity."""
        text = re.sub(r"\s*\([^)]{0,100}\)\s*", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
