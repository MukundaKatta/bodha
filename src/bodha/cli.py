"""CLI entry point for bodha."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from bodha.models import ReadingLevel

console = Console()


@click.group()
@click.version_option()
def cli():
    """Bodha - AI Document Simplifier."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def analyze(file: str):
    """Analyze document complexity and readability."""
    from bodha.simplifier.analyzer import ComplexityAnalyzer
    from bodha.report import render_analysis

    text = Path(file).read_text(encoding="utf-8")
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(text, title=Path(file).stem)
    render_analysis(doc, console)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--level", "-l",
    type=click.Choice(["elementary", "middle_school", "general_public", "expert"]),
    default="general_public",
    help="Target reading level",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def simplify(file: str, level: str, output: str | None):
    """Simplify a document to a target reading level."""
    from bodha.simplifier.analyzer import ComplexityAnalyzer
    from bodha.simplifier.simplifier import TextSimplifier
    from bodha.simplifier.summarizer import KeyPointExtractor
    from bodha.report import render_simplified

    text = Path(file).read_text(encoding="utf-8")
    target = ReadingLevel(level)

    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(text, title=Path(file).stem)

    simplifier = TextSimplifier()
    result = simplifier.simplify(doc, target)

    extractor = KeyPointExtractor()
    result.key_points = extractor.extract(doc, max_points=5)
    result.summary = extractor.summarize(doc, max_sentences=3)

    render_simplified(result, console)

    if output:
        Path(output).write_text(result.simplified_text, encoding="utf-8")
        console.print(f"\n[green]Simplified text written to {output}[/green]")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--max-points", "-n", default=5, help="Maximum key points to extract")
def keypoints(file: str, max_points: int):
    """Extract key points from a document."""
    from bodha.simplifier.analyzer import ComplexityAnalyzer
    from bodha.simplifier.summarizer import KeyPointExtractor

    text = Path(file).read_text(encoding="utf-8")
    analyzer = ComplexityAnalyzer()
    doc = analyzer.analyze(text)

    extractor = KeyPointExtractor()
    points = extractor.extract(doc, max_points=max_points)

    console.print("[bold]Key Points:[/bold]\n")
    for i, kp in enumerate(points, 1):
        bar = "[green]" + "|" * int(kp.importance * 20) + "[/green]"
        console.print(f"  {i}. {bar} {kp.text[:120]}")


if __name__ == "__main__":
    cli()
