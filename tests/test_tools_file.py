"""Тесты для файловых утилит."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from devtools.tools.file import list_files, hash_file, file_size, find_files

runner = CliRunner()


def test_hash_file(tmp_path):
    """Тест хеширования файла."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    result = runner.invoke(hash_file, [str(test_file)])
    assert result.exit_code == 0


def test_file_size(tmp_path):
    """Тест размера файла."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    result = runner.invoke(file_size, [str(test_file)])
    assert result.exit_code == 0


def test_find_files(tmp_path):
    """Тест поиска файлов."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    result = runner.invoke(find_files, ["*.txt", "--path", str(tmp_path)])
    assert result.exit_code == 0
