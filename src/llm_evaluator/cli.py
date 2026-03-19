"""CLI entrypoint for the evaluator."""

import logging
import os
from pathlib import Path

import typer

from llm_evaluator.graph.workflow import build_workflow

LOGGER = logging.getLogger(__name__)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """LLM evaluator CLI."""


@app.command()
def evaluate(config: Path = typer.Option(..., exists=True, dir_okay=False, readable=True)) -> None:
    """Run an evaluation."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required.")

    LOGGER.info("Evaluate command invoked with config=%s.", config)
    workflow = build_workflow()
    workflow.invoke({"config_path": config, "api_key": api_key})


def main() -> None:
    """Run the Typer application."""
    app()
