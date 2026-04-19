"""Тесты для текстовых утилит."""

import pytest
from typer.testing import CliRunner

from devtools.tools.text import sort_lines, case_change, unique_lines

runner = CliRunner()


def test_sort_lines():
    """Тест сортировки строк."""
    result = runner.invoke(sort_lines, ["--text", "banana\napple\ncherry"])
    assert result.exit_code == 0


def test_case_change():
    """Тест изменения регистра."""
    result = runner.invoke(case_change, ["hello world", "--mode", "upper"])
    assert result.exit_code == 0
    assert "HELLO WORLD" in result.output


def test_unique_lines():
    """Тест уникальных строк."""
    result = runner.invoke(unique_lines, ["--text", "apple\nbanana\napple\ncherry"])
    assert result.exit_code == 0
