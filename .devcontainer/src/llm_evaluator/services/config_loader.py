"""Load and validate run configuration files."""

from pathlib import Path
import logging

from pydantic import ValidationError
import yaml

from llm_evaluator.domain.config import RunConfig

LOGGER = logging.getLogger(__name__)


def load_config(path: Path) -> RunConfig:
    """Load and validate a YAML run configuration."""
    LOGGER.info("Loading run configuration from %s.", path)
    if not path.exists():
        LOGGER.error("Configuration file does not exist: %s.", path)
        raise ValueError(f"Configuration file does not exist: {path}")

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        LOGGER.error("Configuration payload must be a YAML mapping.")
        raise ValueError("Configuration payload must be a YAML mapping.")

    try:
        config = RunConfig.model_validate(payload)
    except ValidationError as exc:
        LOGGER.error("Configuration validation failed: %s", exc)
        raise ValueError("Configuration validation failed.") from exc

    LOGGER.info("Loaded run configuration for teacher model %s.", config.teacher_model)
    return config
