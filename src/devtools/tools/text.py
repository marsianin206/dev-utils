"""Текстовые утилиты."""

import re
import base64
from pathlib import Path
from typing import Optional, List, Tuple
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from devtools.apps import text_app
from devtools.console import console, error_console

console = Console()


@text_app.command("wc")
def word_count(
    text: str = typer.Argument(..., help="Текст или - для stdin"),
    bytes: bool = typer.Option(False, "--bytes", "-c", help="Считать байты"),
    lines: bool = typer.Option(False, "--lines", "-l", help="Считать строки"),
    words: bool = typer.Option(False, "--words", "-w", help="Считать слова"),
    chars: bool = typer.Option(False, "--chars", "-m", help="Считать символы"),
) -> None:
    """Подсчитать строки, слова, символы."""
    if text == "-":
        text = console.input()

    lines_count = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    words_count = len(text.split())
    chars_count = len(text)
    bytes_count = len(text.encode("utf-8"))

    if not any([bytes, lines, words, chars]):
        lines, words, chars = True, True, True

    table = Table(title="Статистика текста")
    table.add_column("Метрика", style="cyan")
    table.add_column("Значение", style="green")

    if lines:
        table.add_row("Строк", str(lines_count))
    if words:
        table.add_row("Слов", str(words_count))
    if chars:
        table.add_row("Символов", str(chars_count))
    if bytes:
        table.add_row("Байт", str(bytes_count))

    console.print(table)


@text_app.command("grep")
def grep_text(
    pattern: str = typer.Argument(..., help="Регулярное выражение"),
    path: Optional[str] = typer.Option(None, "--file", "-f", help="Файл для поиска"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Текст для поиска"),
    ignore_case: bool = typer.Option(False, "--ignore-case", "-i", help="Игнорировать регистр"),
    line_numbers: bool = typer.Option(True, "--line-numbers", "-n", help="Номера строк"),
    count: bool = typer.Option(False, "--count", "-c", help="Только количество"),
) -> None:
    """Поиск по регулярному выражению."""
    if not path and not text:
        error_console.print("[red]Ошибка: укажите --file или --text[/red]")
        raise typer.Exit(1)

    flags = re.IGNORECASE if ignore_case else 0

    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        error_console.print(f"[red]Ошибка regex: {e}[/red]")
        raise typer.Exit(1)

    if text:
        lines = text.splitlines()
    else:
        p = Path(path)
        if not p.exists():
            error_console.print(f"[red]Ошибка: файл '{path}' не найден[/red]")
            raise typer.Exit(1)
        lines = p.read_text(encoding="utf-8").splitlines()

    matches: List[Tuple[int, str]] = []

    for i, line in enumerate(lines, 1):
        if regex.search(line):
            matches.append((i, line))

    if count:
        console.print(f"[cyan]{len(matches)}[/cyan]")
        return

    if not matches:
        console.print("[yellow]Совпадений не найдено[/yellow]")
        return

    table = Table(title=f"Найдено совпадений: {len(matches)}")
    if line_numbers:
        table.add_column("Строка", style="cyan")
    table.add_column("Текст", style="green")

    for line_num, line in matches:
        if line_numbers:
            table.add_row(str(line_num), line)
        else:
            table.add_row(line)

    console.print(table)


@text_app.command("replace")
def replace_text(
    pattern: str = typer.Argument(..., help="Что заменить"),
    replacement: str = typer.Argument(..., help="На что заменить"),
    path: Optional[str] = typer.Option(None, "--file", "-f", help="Файл"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Текст"),
    regex: bool = typer.Option(True, "--regex", "-r", help="Использовать regex"),
    flags: str = typer.Option("", "--flags", help="Флаги: i (ignore), g (global)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Предпросмотр"),
) -> None:
    """Замена текста."""
    if not path and not text:
        error_console.print("[red]Ошибка: укажите --file или --text[/red]")
        raise typer.Exit(1)

    flag = 0
    if "i" in flags:
        flag |= re.IGNORECASE

    if text:
        source_text = text
    else:
        p = Path(path)
        if not p.exists():
            error_console.print(f"[red]Ошибка: файл '{path}' не найден[/red]")
            raise typer.Exit(1)
        source_text = p.read_text(encoding="utf-8")

    if regex:
        pattern_flags = flag
        result = re.sub(pattern, replacement, source_text)
    else:
        if "g" in flags:
            result = source_text.replace(pattern, replacement)
        else:
            result = source_text.replace(pattern, replacement, 1)

    if dry_run:
        syntax = Syntax(result, "text", theme="monokai", line_numbers=True)
        console.print("[bold]Результат (dry-run):[/bold]")
        console.print(syntax)
    else:
        if output:
            Path(output).write_text(result, encoding="utf-8")
            console.print(f"[green]✓ Сохранено в {output}[/green]")
        else:
            console.print(result)


@text_app.command("encode")
def encode_text(
    text: str = typer.Argument(..., help="Текст для кодирования"),
    algorithm: str = typer.Argument(..., help="base64, url, hex"),
) -> None:
    """Кодировать текст."""
    algo = algorithm.lower()

    if algo == "base64":
        result = base64.b64encode(text.encode("utf-8")).decode("ascii")
    elif algo == "url":
        from urllib.parse import quote

        result = quote(text)
    elif algo == "hex":
        result = text.encode("utf-8").hex()
    else:
        error_console.print(f"[red]Ошибка: неизвестный алгоритм '{algorithm}'[/red]")
        raise typer.Exit(1)

    console.print(result)


@text_app.command("decode")
def decode_text(
    text: str = typer.Argument(..., help="Текст для декодирования"),
    algorithm: str = typer.Argument(..., help="base64, url, hex"),
) -> None:
    """Декодировать текст."""
    algo = algorithm.lower()

    try:
        if algo == "base64":
            result = base64.b64decode(text.encode("ascii")).decode("utf-8")
        elif algo == "url":
            from urllib.parse import unquote

            result = unquote(text)
        elif algo == "hex":
            result = bytes.fromhex(text).decode("utf-8")
        else:
            error_console.print(f"[red]Ошибка: неизвестный алгоритм '{algorithm}'[/red]")
            raise typer.Exit(1)

        console.print(result)
    except Exception as e:
        error_console.print(f"[red]Ошибка декодирования: {e}[/red]")
        raise typer.Exit(1)


@text_app.command("sort")
def sort_lines(
    path: Optional[str] = typer.Option(None, "--file", "-f", help="Файл"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Текст"),
    numeric: bool = typer.Option(False, "--numeric", "-n", help="Числовая сортировка"),
    reverse: bool = typer.Option(False, "--reverse", "-r", help="В обратном порядке"),
    unique: bool = typer.Option(False, "--unique", "-u", help="Уникальные значения"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
) -> None:
    """Сортировать строки."""
    if not path and not text:
        error_console.print("[red]Ошибка: укажите --file или --text[/red]")
        raise typer.Exit(1)

    if text:
        lines = text.splitlines()
    else:
        p = Path(path)
        if not p.exists():
            error_console.print(f"[red]Ошибка: файл '{path}' не найден[/red]")
            raise typer.Exit(1)
        lines = p.read_text(encoding="utf-8").splitlines()

    if numeric:
        lines.sort(key=lambda x: float(x), reverse=reverse)
    else:
        lines.sort(reverse=reverse)

    if unique:
        lines = list(dict.fromkeys(lines))

    result = "\n".join(lines)

    if output:
        Path(output).write_text(result, encoding="utf-8")
        console.print(f"[green]✓ Сохранено в {output}[/green]")
    else:
        console.print(result)


@text_app.command("unique")
def unique_lines(
    path: Optional[str] = typer.Option(None, "--file", "-f", help="Файл"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Текст"),
    count: bool = typer.Option(False, "--count", "-c", help="Показать количество"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
) -> None:
    """Уникальные строки."""
    if not path and not text:
        error_console.print("[red]Ошибка: укажите --file или --text[/red]")
        raise typer.Exit(1)

    if text:
        lines = text.splitlines()
    else:
        p = Path(path)
        if not p.exists():
            error_console.print(f"[red]Ошибка: файл '{path}' не найден[/red]")
            raise typer.Exit(1)
        lines = p.read_text(encoding="utf-8").splitlines()

    if count:
        from collections import Counter

        counts = Counter(lines)
        table = Table(title=f"Уникальных строк: {len(counts)}")
        table.add_column("Строка", style="cyan")
        table.add_column("Количество", style="green")
        for line, cnt in counts.most_common():
            table.add_row(line, str(cnt))
        console.print(table)
    else:
        unique = list(dict.fromkeys(lines))
        result = "\n".join(unique)
        if output:
            Path(output).write_text(result, encoding="utf-8")
            console.print(f"[green]✓ Сохранено в {output}[/green]")
        else:
            console.print(result)


@text_app.command("case")
def change_case(
    text: str = typer.Argument(..., help="Текст"),
    mode: str = typer.Option("lower", "--mode", "-m", help="lower, upper, title, capitalize"),
) -> None:
    """Изменить регистр."""
    m = mode.lower()

    if m == "lower":
        result = text.lower()
    elif m == "upper":
        result = text.upper()
    elif m == "title":
        result = text.title()
    elif m == "capitalize":
        result = text.capitalize()
    else:
        error_console.print(f"[red]Ошибка: неизвестный режим '{mode}'[/red]")
        raise typer.Exit(1)

    console.print(result)


@text_app.command("template")
def fill_template(
    template: str = typer.Argument(..., help="Шаблон с {{переменными}}"),
    values: str = typer.Argument(..., help="values.json или текст"),
) -> None:
    """Заполнить шаблон значениями."""
    import json

    if values.endswith((".json", ".yaml", ".yml")):
        p = Path(values)
        if p.suffix == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
        else:
            import yaml

            data = yaml.safe_load(p.read_text(encoding="utf-8"))
    else:
        try:
            data = json.loads(values)
        except json.JSONDecodeError:
            error_console.print("[red]Ошибка: значения должны быть в JSON[/red]")
            raise typer.Exit(1)

    result = template
    for key, value in data.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))

    console.print(result)
