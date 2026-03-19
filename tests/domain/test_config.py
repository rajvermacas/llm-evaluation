from pathlib import Path

import pytest

from llm_evaluator.services.config_loader import load_config


def test_load_config_requires_teacher_model(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("candidate_models: []\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(config_path)
