"""Тесты для крипто утилит."""

import pytest
from typer.testing import CliRunner

from devtools.tools.crypto import hash_text, generate_password, generate_token, random_string

runner = CliRunner()


def test_hash_text():
    """Тест хеширования."""
    result = runner.invoke(hash_text, ["hello"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 64


def test_hash_text_sha512():
    """Тест хеширования SHA-512."""
    result = runner.invoke(hash_text, ["hello", "--algorithm", "sha512"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 128


def test_generate_password():
    """Тест генерации пароля."""
    result = runner.invoke(generate_password, ["--length", "16"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 16


def test_generate_token():
    """Тест генерации токена."""
    result = runner.invoke(generate_token, ["--length", "32"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 64


def test_random_string():
    """Тест случайной строки."""
    result = runner.invoke(random_string, ["--length", "16"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 16


def test_random_int():
    """Тест случайного числа."""
    from devtools.tools.crypto import random_int

    result = runner.invoke(random_int, ["--min", "1", "--max", "10"])
    assert result.exit_code == 0
