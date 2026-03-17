"""Tests for bodha."""

import pytest

from bodha.models import Document, ReadingLevel, SimplifiedDocument, ReadabilityScores, KeyPoint
from bodha.simplifier.analyzer import ComplexityAnalyzer
from bodha.simplifier.simplifier import TextSimplifier
from bodha.simplifier.summarizer import KeyPointExtractor
from bodha.levels.elementary import ElementaryAdapter
from bodha.levels.middle import MiddleSchoolAdapter
from bodha.levels.general import GeneralPublicAdapter
from bodha.levels.expert import ExpertAdapter


SAMPLE_TEXT = (
    "The implementation of comprehensive infrastructure modifications "
    "necessitates substantial financial resources. Furthermore, the methodology "
    "employed must demonstrate sufficient scalability to accommodate future requirements. "
    "It is important to note that stakeholder engagement is a critical component "
    "of the overall project methodology. The paradigm shift requires leveraging "
    "existing organizational synergy to optimize deliverable quality."
)

SIMPLE_TEXT = "The cat sat on the mat. It was a good day. The sun was out."


# --- Analyzer ---

def test_analyzer_basic():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    assert doc.word_count > 0
    assert doc.sentence_count > 0
    assert doc.readability.flesch_kincaid_grade > 0


def test_analyzer_simple_text():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SIMPLE_TEXT)
    assert doc.readability.flesch_reading_ease > 50  # Should be easy


def test_analyzer_complex_vs_simple():
    analyzer = ComplexityAnalyzer()
    complex_doc = analyzer.analyze(SAMPLE_TEXT)
    simple_doc = analyzer.analyze(SIMPLE_TEXT)
    assert complex_doc.readability.flesch_kincaid_grade > simple_doc.readability.flesch_kincaid_grade


def test_analyzer_all_formulas():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    r = doc.readability
    assert r.flesch_reading_ease != 0
    assert r.flesch_kincaid_grade > 0
    assert r.gunning_fog > 0
    assert r.coleman_liau != 0
    assert r.ari != 0
    assert r.smog > 0
    assert r.dale_chall > 0


def test_analyzer_syllable_counting():
    analyzer = ComplexityAnalyzer()
    assert analyzer._count_syllables("cat") == 1
    assert analyzer._count_syllables("hello") == 2
    assert analyzer._count_syllables("beautiful") >= 3


def test_average_grade_level():
    scores = ReadabilityScores(flesch_kincaid_grade=8.0, gunning_fog=10.0, coleman_liau=9.0, ari=7.0)
    assert scores.average_grade_level == 8.5


# --- Simplifier ---

def test_simplifier_word_replacement():
    simplifier = TextSimplifier()
    text = "We need to utilize the methodology to facilitate the process."
    result = simplifier._replace_complex_words(text)
    assert "use" in result
    assert "help" in result


def test_simplifier_removes_parentheticals():
    simplifier = TextSimplifier()
    text = "The system (which was built last year) works well."
    result = simplifier._remove_parentheticals(text)
    assert "(" not in result
    assert "works well" in result


def test_simplifier_elementary():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    simplifier = TextSimplifier()
    result = simplifier.simplify(doc, ReadingLevel.ELEMENTARY)
    assert result.simplified_text != doc.text
    assert result.target_level == ReadingLevel.ELEMENTARY


def test_simplifier_general():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    simplifier = TextSimplifier()
    result = simplifier.simplify(doc, ReadingLevel.GENERAL_PUBLIC)
    assert result.simplified_text != doc.text


def test_simplifier_expert():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    simplifier = TextSimplifier()
    result = simplifier.simplify(doc, ReadingLevel.EXPERT)
    # Expert should preserve more content
    assert result.word_count > 0


# --- Key Point Extractor ---

def test_extractor_basic():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    extractor = KeyPointExtractor()
    points = extractor.extract(doc)
    assert len(points) > 0
    assert all(isinstance(p, KeyPoint) for p in points)


def test_extractor_max_points():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    extractor = KeyPointExtractor()
    points = extractor.extract(doc, max_points=2)
    assert len(points) <= 2


def test_extractor_summarize():
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(SAMPLE_TEXT)
    extractor = KeyPointExtractor()
    summary = extractor.summarize(doc, max_sentences=2)
    assert len(summary) > 0


# --- Level Adapters ---

def test_elementary_adapter():
    adapter = ElementaryAdapter()
    text = "However, the environment demonstrated significant changes."
    result = adapter.adapt(text)
    assert "but" in result.lower()
    assert adapter.max_sentence_words == 10


def test_middle_adapter():
    adapter = MiddleSchoolAdapter()
    text = "Furthermore, the methodology was predominantly qualitative."
    result = adapter.adapt(text)
    assert "also" in result.lower()
    assert adapter.max_sentence_words == 15


def test_general_adapter():
    adapter = GeneralPublicAdapter()
    text = "The aforementioned remuneration was cognizant of market rates."
    result = adapter.adapt(text)
    assert "mentioned earlier" in result.lower()
    assert adapter.max_sentence_words == 20


def test_expert_adapter():
    adapter = ExpertAdapter()
    text = "It is important to note that in order to achieve the goal, due to the fact that resources are limited."
    result = adapter.adapt(text)
    assert "in order to" not in result
    assert "to" in result
    assert adapter.max_sentence_words == 30
