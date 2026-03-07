"""CLI entrypoint for the evaluator."""

import typer

app = typer.Typer()


@app.command()
def evaluate() -> None:
    """Run an evaluation."""


def main() -> None:
    """Run the Typer application."""
    app()
