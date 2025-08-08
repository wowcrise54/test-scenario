from __future__ import annotations

import click


@click.group(help="RangeForge orchestrator CLI.")
def app() -> None:
    """CLI group for orchestrator."""


@app.command()
def version() -> None:
    """Show version information."""
    click.echo("RangeForge orchestrator 0.1.0")


if __name__ == "__main__":
    app()
