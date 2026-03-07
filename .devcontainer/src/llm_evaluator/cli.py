"""CLI entrypoint for the evaluator."""

import logging

import typer

LOGGER = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def evaluate() -> None:
    """Run an evaluation."""
    LOGGER.info("Evaluate command invoked.")


def main() -> None:
    """Run the Typer application."""
    app()
