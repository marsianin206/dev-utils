"""Криптографические утилиты."""

import hashlib
import hmac
import secrets
import uuid
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

from devtools.apps import crypto_app
from devtools.console import console, error_console

console = Console()


@crypto_app.command("hash")
def hash_text(
    text: str = typer.Argument(..., help="Текст для хеширования"),
    algorithm: str = typer.Option("sha256", "--algorithm", "-a", help="Алгоритм"),
    output: str = typer.Option("hex", "--output", "-o", help="Формат: hex, base64"),
    rounds: int = typer.Option(1, "--rounds", "-r", help="Количество раундов"),
) -> None:
    """Вычислить хеш текста."""
    algo = algorithm.lower().replace("-", "")

    if algo not in ("md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256", "sha3_512"):
        error_console.print(f"[red]Ошибка: алгоритм '{algorithm}' не поддерживается[/red]")
        raise typer.Exit(1)

    try:
        h = hashlib.new(algo)
    except ValueError:
        if algo == "sha3_256":
            h = hashlib.sha3_256()
        elif algo == "sha3_512":
            h = hashlib.sha3_512()
        else:
            error_console.print(f"[red]Ошибка: алгоритм '{algorithm}' не поддерживается[/red]")
            raise typer.Exit(1)

    for _ in range(rounds):
        h.update(text.encode("utf-8"))
        text = h.hexdigest()

    result = h.hexdigest() if output == "hex" else h.digest()

    if output == "base64":
        import base64

        result = base64.b64encode(h.digest()).decode("ascii")

    console.print(f"[green]{result}[/green]")


@crypto_app.command("hmac")
def hmac_text(
    text: str = typer.Argument(..., help="Текст"),
    key: str = typer.Argument(..., help="Секретный ключ"),
    algorithm: str = typer.Option("sha256", "--algorithm", "-a", help="Алгоритм"),
) -> None:
    """Вычислить HMAC."""
    algo = algorithm.upper().replace("-", "")

    try:
        h = hmac.new(key.encode(), text.encode(), algo)
    except ValueError:
        error_console.print(f"[red]Ошибка: алгоритм '{algorithm}' не поддерживается[/red]")
        raise typer.Exit(1)

    console.print(f"[green]{h.hexdigest()}[/green]")


@crypto_app.command("generate-password")
def generate_password(
    length: int = typer.Option(16, "--length", "-l", help="Длина пароля"),
    numbers: bool = typer.Option(True, "--numbers", "-n", help="Включить цифры"),
    symbols: bool = typer.Option(True, "--symbols", "-s", help="Включить спецсимволы"),
    uppercase: bool = typer.Option(True, "--uppercase", "-u", help="Включить заглавные"),
    exclude_ambiguous: bool = typer.Option(
        False, "--no-ambiguous", help="Исключить похожие символы"
    ),
) -> None:
    """Сгенерировать безопасный пароль."""
    import string

    chars = ""

    if numbers:
        chars += string.digits
    if symbols:
        chars += string.punctuation

    if uppercase:
        chars += string.ascii_uppercase

    chars += string.ascii_lowercase

    if exclude_ambiguous:
        chars = chars.replace("l", "").replace("1", "").replace("O", "").replace("0", "")

    password = "".join(secrets.choice(chars) for _ in range(length))

    if not secrets.compare_digest(secrets.token_bytes(1), secrets.token_bytes(1)):
        console.print(f"[green]{password}[/green]")
    else:
        console.print(f"[red]Ошибка генерации случайных чисел[/red]")
        raise typer.Exit(1)


@crypto_app.command("generate-token")
def generate_token(
    length: int = typer.Option(32, "--length", "-l", help="Длина токена"),
    format: str = typer.Option("hex", "--format", "-f", help="Формат: hex, base64, uuid"),
) -> None:
    """Сгенерировать случайный токен."""
    if format == "uuid":
        result = str(uuid.uuid4())
    elif format == "base64":
        import base64

        result = base64.urlsafe_b64encode(secrets.token_bytes(length)).decode().rstrip("=")
    else:
        result = secrets.token_hex(length)

    console.print(f"[green]{result}[/green]")


@crypto_app.command("verify-hash")
def verify_hash(
    text: str = typer.Argument(..., help="Текст"),
    hash: str = typer.Argument(..., help="Ожидаемый хеш"),
    algorithm: str = typer.Option("sha256", "--algorithm", "-a", help="Алгоритм"),
) -> None:
    """Проверить хеш текста."""
    algo = algorithm.lower().replace("-", "")

    try:
        h = hashlib.new(algo)
    except ValueError:
        error_console.print(f"[red]Ошибка: алгоритм '{algorithm}' не поддерживается[/red]")
        raise typer.Exit(1)

    h.update(text.encode())
    computed = h.hexdigest()

    if hmac.compare_digest(computed, hash.lower()):
        console.print("[green]✓ Хеш совпадает[/green]")
    else:
        console.print("[red]✗ Хеш не совпадает[/red]")
        console.print(f"[dim]Ожидалось: {hash}[/dim]")
        console.print(f"[dim]Получено:  {computed}[/dim]")


@crypto_app.command("encrypt")
def encrypt_password(
    password: str = typer.Argument(..., help="Пароль для шифрования"),
    salt: Optional[str] = typer.Option(None, "--salt", "-s", help="Соль (опционально)"),
) -> None:
    """Зашифровать пароль."""
    import hashlib

    if not salt:
        salt = secrets.token_hex(16)
        console.print(f"[dim]Соль: {salt}[/dim]")

    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    result = key.hex()

    console.print(f"[green]{result}[/green]")


@crypto_app.command("random-string")
def random_string(
    length: int = typer.Option(16, "--length", "-l", help="Длина строки"),
    charset: str = typer.Option(
        "alphanumeric", "--charset", "-c", help="Набор: alphanumeric, alpha, digits, ascii_letters"
    ),
) -> None:
    """Сгенерировать случайную строку."""
    import string

    if charset == "alphanumeric":
        chars = string.ascii_letters + string.digits
    elif charset == "alpha":
        chars = string.ascii_letters
    elif charset == "digits":
        chars = string.digits
    elif charset == "ascii_letters":
        chars = string.ascii_letters
    else:
        chars = charset

    result = "".join(secrets.choice(chars) for _ in range(length))

    console.print(f"[green]{result}[/green]")


@crypto_app.command("secure-compare")
def secure_compare(
    value1: str = typer.Argument(..., help="Первое значение"),
    value2: str = typer.Argument(..., help="Второе значение"),
) -> None:
    """Безопасное сравнение строк."""
    result = hmac.compare_digest(value1, value2)

    if result:
        console.print("[green]✓ Строки совпадают[/green]")
    else:
        console.print("[red]✗ Строки не совпадают[/red]")


@crypto_app.command("randint")
def random_int(
    min: int = typer.Option(0, "--min", help="Минимум"),
    max: int = typer.Option(100, "--max", help="Максимум"),
) -> None:
    """Сгенерировать случайное число."""
    result = secrets.randbelow(max - min + 1) + min

    console.print(f"[green]{result}[/green]")


@crypto_app.command("uuid")
def generate_uuid(
    version: int = typer.Option(4, "--version", "-v", help="Версия UUID (1, 4)"),
) -> None:
    """Сгенерировать UUID."""
    if version == 1:
        result = str(uuid.uuid1())
    else:
        result = str(uuid.uuid4())

    console.print(f"[green]{result}[/green]")


@crypto_app.command("checksum")
def checksum_file(
    path: str = typer.Argument(..., help="Путь к файлу"),
    algorithm: str = typer.Option("sha256", "--algorithm", "-a", help="Алгоритм"),
) -> None:
    """Вычислить контрольную сумму файла."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    algo = algorithm.lower()
    try:
        h = hashlib.new(algo)
    except ValueError:
        error_console.print(f"[red]Ошибка: алгоритм '{algorithm}' не поддерживается[/red]")
        raise typer.Exit(1)

    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    result = h.hexdigest()

    table = Table(title=f"Контрольная сумма: {path}")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Алгоритм", algorithm.upper())
    table.add_row("Хеш", result)

    console.print(table)
