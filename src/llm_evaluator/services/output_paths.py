"""Helpers for evaluation artifact output paths."""

import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LOGGER = logging.getLogger(__name__)

IST_TIMEZONE = ZoneInfo("Asia/Kolkata")
RUN_DIRECTORY_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S_IST"


def format_run_directory_timestamp(now: datetime) -> str:
    """Format a run directory name for an IST timestamp."""
    return now.astimezone(IST_TIMEZONE).strftime(RUN_DIRECTORY_TIMESTAMP_FORMAT)


def create_timestamped_output_dir(base_dir: Path) -> Path:
    """Create a timestamped output directory beneath the configured base directory."""
    LOGGER.info("Preparing output base directory at %s.", base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    run_dir_name = format_run_directory_timestamp(datetime.now(tz=IST_TIMEZONE))
    run_dir = base_dir / run_dir_name
    LOGGER.info("Resolved timestamped run directory %s.", run_dir)
    if run_dir.exists():
        LOGGER.error("Timestamped run directory already exists: %s.", run_dir)
        raise FileExistsError(f"Timestamped run directory already exists: {run_dir}")
    run_dir.mkdir()
    LOGGER.info("Created timestamped run directory at %s.", run_dir)
    return run_dir
