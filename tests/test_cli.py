"""Тесты для DevTools."""

import pytest
from typer.testing import CliRunner

from devtools.cli import app

runner = CliRunner()


def test_version():
    """Тест команды version."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DevTools" in result.output


def test_help():
    """Тест команды help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "DevTools" in result.output


def test_data_help():
    """Тест справки data."""
    result = runner.invoke(app, ["data", "--help"])
    assert result.exit_code == 0


def test_file_help():
    """Тест справки file."""
    result = runner.invoke(app, ["file", "--help"])
    assert result.exit_code == 0


def test_net_help():
    """Тест справки net."""
    result = runner.invoke(app, ["net", "--help"])
    assert result.exit_code == 0


def test_text_help():
    """Тест справки text."""
    result = runner.invoke(app, ["text", "--help"])
    assert result.exit_code == 0


def test_crypto_help():
    """Тест справки crypto."""
    result = runner.invoke(app, ["crypto", "--help"])
    assert result.exit_code == 0
