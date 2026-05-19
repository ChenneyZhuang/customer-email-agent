"""Command-line interface for the email triage agent.

Usage:
    email-agent run --from alice@example.com --subject "Need a quote" --body "..."
    email-agent run --file email.txt
    email-agent batch emails.csv
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from email_agent import __version__
from email_agent.config import validate
from email_agent.models import Category, Email, Urgency
from email_agent.pipeline import export_csv, export_json, run

app = typer.Typer(
    name="email-agent",
    help="AI agent that triages customer emails for small businesses.",
    add_completion=False,
)
console = Console()


def _style_category(cat: Category) -> str:
    colours = {
        Category.QUOTE_ENQUIRY: "green",
        Category.COMPLAINT: "red",
        Category.BOOKING: "blue",
        Category.SUPPORT: "yellow",
        Category.SPAM: "dim",
    }
    return f"[{colours.get(cat, 'white')}]{cat.value}[/]"


def _style_urgency(urg: Urgency) -> str:
    colours = {
        Urgency.LOW: "green",
        Urgency.MEDIUM: "yellow",
        Urgency.HIGH: "red",
        Urgency.CRITICAL: "bold red",
    }
    return f"[{colours.get(urg, 'white')}]{urg.value}[/]"


@app.callback()
def callback(
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    if version:
        console.print(f"email-agent v{__version__}")
        raise typer.Exit()


@app.command()
def run_cmd(
    from_: str = typer.Option(..., "--from", help="Sender email address"),
    subject: str = typer.Option("", "--subject", help="Email subject"),
    body: str = typer.Option("", "--body", help="Plain-text email body"),
    body_file: Path | None = typer.Option(
        None, "--body-file", help="Read body from a text file"
    ),
    email_id: str = typer.Option("cli-input", "--id", help="Email identifier"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Run the triage pipeline on a single email."""
    validate()

    body_text = body
    if body_file:
        body_text = body_file.read_text(encoding="utf-8")

    email = Email(
        id=email_id,
        from_address=from_,
        subject=subject,
        body=body_text,
    )

    with console.status("[bold green]Triaging email...[/]"):
        result = run(email)

    if json_output:
        console.print_json(json.dumps(result.model_dump(mode="json"), indent=2))
        return

    # ── Rich output ──────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel.fit(
            f"[bold]Classification:[/] {_style_category(result.classification.category)} "
            f"({result.classification.confidence:.0%} confidence)\n"
            f"[dim]{result.classification.reasoning}[/]",
            title="📬 Email Triage Result",
            border_style="cyan",
        )
    )

    table = Table(title="📋 Extracted Details", show_header=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")
    table.add_row("Customer", result.extracted.customer_name)
    table.add_row("Need", result.extracted.need)
    table.add_row("Location", result.extracted.location or "—")
    table.add_row("Urgency", _style_urgency(result.extracted.urgency))
    if result.extracted.key_facts:
        table.add_row("Key Facts", "\n".join(f"• {f}" for f in result.extracted.key_facts))
    console.print(table)

    console.print()
    console.print(
        Panel(
            result.reply.body,
            title=f"✉️  {result.reply.subject}",
            subtitle=f"Tone: {result.reply.tone} [dim]| Requires human review[/]",
            border_style="green",
        )
    )

    # Export
    csv_path = export_csv(result, email)
    json_path = export_json(result, email)
    console.print(f"\n[dim]CSV exported → {csv_path}[/]")
    console.print(f"[dim]JSON exported → {json_path}[/]")


@app.command()
def batch(
    csv_file: Path = typer.Argument(..., help="CSV with columns: id, from, subject, body"),
    output: Path | None = typer.Option(None, "--output", help="Output CSV file path"),
) -> None:
    """Process multiple emails from a CSV file.

    Expected CSV columns: id, from, subject, body
    """
    validate()

    if not csv_file.exists():
        console.print(f"[red]File not found: {csv_file}[/]")
        raise typer.Exit(1)

    rows: list[dict[str, str]] = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        console.print("[yellow]CSV file is empty.[/]")
        raise typer.Exit(0)

    console.print(f"Processing {len(rows)} email(s)...")

    for i, row in enumerate(rows, 1):
        email = Email(
            id=row.get("id", f"batch-{i}"),
            from_address=row.get("from", row.get("from_address", "")),
            subject=row.get("subject", ""),
            body=row.get("body", ""),
        )
        console.print(f"  [{i}/{len(rows)}] {email.subject[:60]}")
        result = run(email)
        csv_path = export_csv(result, email, output_path=output)
        export_json(result, email)

    console.print(f"\n[bold green]Done![/] CRM data → {csv_path}")


@app.command()
def version_cmd() -> None:
    """Print version number."""
    console.print(f"email-agent v{__version__}")


if __name__ == "__main__":
    app()
