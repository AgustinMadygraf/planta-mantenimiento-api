"""Pruebas para utilidades de configuración."""

import os
from pathlib import Path

import pytest

from src.shared import config


def test_load_env_uses_manual_parser_when_python_dotenv_is_missing(tmp_path, monkeypatch):
    env_file = tmp_path / "manual.env"
    env_file.write_text("CUSTOM_KEY=custom_value\n", encoding="utf-8")

    monkeypatch.setattr(config, "load_dotenv", None)
    monkeypatch.delenv("CUSTOM_KEY", raising=False)

    loaded = config.load_env(str(env_file))

    assert loaded is True
    assert os.environ.get("CUSTOM_KEY") == "custom_value"

    monkeypatch.delenv("CUSTOM_KEY", raising=False)


def test_load_env_wraps_io_and_encoding_errors(tmp_path, monkeypatch):
    env_file = tmp_path / "broken.env"
    env_file.touch()

    def raise_unicode_error(*_args, **_kwargs):
        raise UnicodeDecodeError("utf-8", b"", 0, 1, "boom")

    monkeypatch.setattr(config, "load_dotenv", raise_unicode_error)

    with pytest.raises(RuntimeError):
        config.load_env(str(env_file))


def test_load_env_propagates_unexpected_errors(tmp_path, monkeypatch):
    env_file = tmp_path / "unexpected.env"
    env_file.touch()

    def raise_value_error(*_args, **_kwargs):
        raise ValueError("unexpected failure")

    monkeypatch.setattr(config, "load_dotenv", raise_value_error)

    with pytest.raises(ValueError):
        config.load_env(str(env_file))
