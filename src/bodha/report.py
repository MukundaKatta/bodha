"""Rich console report rendering for document simplification."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bodha.models import Document, SimplifiedDocument


def render_analysis(doc: Document, console: Console | None = None) -> None:
    """Render document analysis to console."""
    console = console or Console()
    r = doc.readability

    console.print(Panel(
        f"[bold]Document Analysis[/bold]\n"
        f"Title: {doc.title or '(untitled)'}\n"
        f"Words: {doc.word_count} | Sentences: {doc.sentence_count}\n"
        f"Avg sentence length: {doc.avg_sentence_length:.1f} words\n"
        f"Complex word ratio: {doc.complex_word_ratio:.1%}",
        title="Bodha",
    ))

    table = Table(title="Readability Scores")
    table.add_column("Formula", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Interpretation", style="dim")

    table.add_row("Flesch Reading Ease", f"{r.flesch_reading_ease:.1f}", _fre_interpret(r.flesch_reading_ease))
    table.add_row("Flesch-Kincaid Grade", f"{r.flesch_kincaid_grade:.1f}", f"Grade {r.flesch_kincaid_grade:.0f}")
    table.add_row("Gunning Fog", f"{r.gunning_fog:.1f}", f"Grade {r.gunning_fog:.0f}")
    table.add_row("Coleman-Liau", f"{r.coleman_liau:.1f}", f"Grade {r.coleman_liau:.0f}")
    table.add_row("ARI", f"{r.ari:.1f}", f"Grade {r.ari:.0f}")
    table.add_row("SMOG", f"{r.smog:.1f}", f"Grade {r.smog:.0f}")
    table.add_row("Dale-Chall", f"{r.dale_chall:.1f}", _dc_interpret(r.dale_chall))
    table.add_row("[bold]Average Grade Level[/bold]", f"[bold]{r.average_grade_level:.1f}[/bold]", "")

    console.print(table)


def render_simplified(result: SimplifiedDocument, console: Console | None = None) -> None:
    """Render simplification result to console."""
    console = console or Console()

    render_analysis(result.original, console)

    console.print(Panel(
        f"[bold]Simplified ({result.target_level.value})[/bold]\n"
        f"Words: {result.word_count} (ratio: {result.simplification_ratio:.1%})\n"
        f"New avg grade: {result.readability.average_grade_level:.1f}",
        title="Simplified Output",
    ))

    console.print(f"\n{result.simplified_text[:500]}{'...' if len(result.simplified_text) > 500 else ''}")

    if result.key_points:
        console.print("\n[bold]Key Points:[/bold]")
        for i, kp in enumerate(result.key_points, 1):
            console.print(f"  {i}. {kp.text[:100]}")

    if result.summary:
        console.print(f"\n[bold]Summary:[/bold] {result.summary}")


def _fre_interpret(score: float) -> str:
    if score >= 90:
        return "Very easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly easy (7th grade)"
    elif score >= 60:
        return "Standard (8-9th grade)"
    elif score >= 50:
        return "Fairly difficult (10-12th)"
    elif score >= 30:
        return "Difficult (college)"
    return "Very difficult (graduate)"


def _dc_interpret(score: float) -> str:
    if score <= 4.9:
        return "Grade 4 and below"
    elif score <= 5.9:
        return "Grade 5-6"
    elif score <= 6.9:
        return "Grade 7-8"
    elif score <= 7.9:
        return "Grade 9-10"
    elif score <= 8.9:
        return "Grade 11-12"
    return "College level"
