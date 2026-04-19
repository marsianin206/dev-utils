"""Утилиты для работы с данными."""

import json
import csv
from pathlib import Path
from typing import Optional, Any, Dict, List
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from devtools.apps import data_app
from devtools.console import console, error_console

console = Console()


def _load_json(path: Path) -> Any:
    """Загрузить JSON из файла."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: Path) -> Any:
    """Загрузить YAML из файла."""
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@data_app.command("validate")
def validate_json(
    path: str = typer.Argument(..., help="Путь к JSON-файлу"),
) -> None:
    """Валидировать JSON-файл."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    try:
        data = _load_json(p)
        console.print(f"[green]✓ JSON валиден[/green]")
        console.print(f"[dim]Тип: {type(data).__name__}[/dim]")
        if isinstance(data, dict):
            console.print(f"[dim]Ключей: {len(data)}[/dim]")
        elif isinstance(data, list):
            console.print(f"[dim]Элементов: {len(data)}[/dim]")
    except json.JSONDecodeError as e:
        error_console.print(f"[red]✗ Ошибка JSON: {e}[/red]")
        raise typer.Exit(1)


@data_app.command("format")
def format_json(
    path: str = typer.Argument(..., help="Путь к JSON-файлу"),
    indent: int = typer.Option(2, "--indent", "-i", help="Отступ"),
    sort: bool = typer.Option(False, "--sort", "-s", help="Сортировать ключи"),
) -> None:
    """Форматировать JSON-файл."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    try:
        data = _load_json(p)
    except json.JSONDecodeError as e:
        error_console.print(f"[red]✗ Ошибка JSON: {e}[/red]")
        raise typer.Exit(1)

    output = json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort)

    syntax = Syntax(output, "json", theme="monokai", line_numbers=True)
    console.print(syntax)


@data_app.command("minify")
def minify_json(
    path: str = typer.Argument(..., help="Путь к JSON-файлу"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
) -> None:
    """Минифицировать JSON."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    try:
        data = _load_json(p)
    except json.JSONDecodeError as e:
        error_console.print(f"[red]✗ Ошибка JSON: {e}[/red]")
        raise typer.Exit(1)

    result = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    if output:
        out_path = Path(output)
        out_path.write_text(result, encoding="utf-8")
        console.print(f"[green]✓ Сохранено в {output}[/green]")
    else:
        console.print(result)


@data_app.command("convert")
def convert_json_yaml(
    input_file: str = typer.Argument(..., help="Входной файл"),
    output_format: str = typer.Argument(..., help="Формат: yaml или json"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
) -> None:
    """Конвертировать JSON <-> YAML."""
    import yaml

    p = Path(input_file)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{input_file}' не существует[/red]")
        raise typer.Exit(1)

    suffix = p.suffix.lower()
    if suffix == ".json":
        data = _load_json(p)
    elif suffix in [".yaml", ".yml"]:
        data = _load_yaml(p)
    else:
        error_console.print(f"[red]Ошибка: неизвестный формат {suffix}[/red]")
        raise typer.Exit(1)

    if output_format.lower() == "yaml":
        result = yaml.dump(data, allow_unicode=True, default_flow_style=False)
    elif output_format.lower() == "json":
        result = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        error_console.print(f"[red]Ошибка: неизвестный формат {output_format}[/red]")
        raise typer.Exit(1)

    if output_file:
        Path(output_file).write_text(result, encoding="utf-8")
        console.print(f"[green]✓ Сохранено в {output_file}[/green]")
    else:
        console.print(result)


@data_app.command("query")
def query_json(
    path: str = typer.Argument(..., help="Путь к JSON-файлу"),
    key: str = typer.Argument(..., help="Ключ для поиска (поддерживает dot.notation)"),
) -> None:
    """Получить значение по ключу из JSON."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    try:
        data = _load_json(p)
    except json.JSONDecodeError as e:
        error_console.print(f"[red]✗ Ошибка JSON: {e}[/red]")
        raise typer.Exit(1)

    keys = key.split(".")
    current = data

    for k in keys:
        if isinstance(current, dict):
            current = current.get(k)
        elif isinstance(current, list):
            try:
                current = current[int(k)]
            except (ValueError, IndexError):
                error_console.print(f"[red]Ошибка: неверный индекс {k}[/red]")
                raise typer.Exit(1)
        else:
            error_console.print(f"[red]Ошибка: не могу пройти дальше[/red]")
            raise typer.Exit(1)

        if current is None:
            error_console.print(f"[red]Ошибка: ключ '{k}' не найден[/red]")
            raise typer.Exit(1)

    result = json.dumps(current, indent=2, ensure_ascii=False)
    syntax = Syntax(result, "json", theme="monokai")
    console.print(syntax)


@data_app.command("csv2json")
def csv_to_json(
    path: str = typer.Argument(..., help="Путь к CSV-файлу"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной JSON файл"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="Разделитель"),
) -> None:
    """Конвертировать CSV в JSON."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    result: List[Dict] = []

    with open(p, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        result = list(reader)

    json_data = json.dumps(result, indent=2, ensure_ascii=False)

    if output:
        Path(output).write_text(json_data, encoding="utf-8")
        console.print(f"[green]✓ Сохранено в {output}[/green]")
    else:
        syntax = Syntax(json_data, "json", theme="monokai")
        console.print(syntax)


@data_app.command("json2csv")
def json_to_csv(
    path: str = typer.Argument(..., help="Путь к JSON-файлу"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной CSV файл"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="Разделитель"),
) -> None:
    """Конвертировать JSON в CSV."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    try:
        data = _load_json(p)
    except json.JSONDecodeError as e:
        error_console.print(f"[red]✗ Ошибка JSON: {e}[/red]")
        raise typer.Exit(1)

    if not isinstance(data, list):
        data = [data]

    if not data:
        error_console.print("[red]Ошибка: JSON не содержит массив[/red]")
        raise typer.Exit(1)

    keys = set()
    for item in data:
        if isinstance(item, dict):
            keys.update(item.keys())

    with open(output or "output.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(keys), delimiter=delimiter)
        writer.writeheader()
        for item in data:
            if isinstance(item, dict):
                writer.writerow(item)

    console.print(f"[green]✓ Сохранено в {output or 'output.csv'}[/green]")


@data_app.command("preview")
def preview_json(
    path: str = typer.Argument(..., help="Путь к JSON-файлу"),
    lines: int = typer.Option(50, "--lines", "-n", help="Количество строк"),
) -> None:
    """Предпросмотр JSON-файла."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    content = p.read_text(encoding="utf-8")[: lines * 100]
    syntax = Syntax(content, "json", theme="monokai", line_numbers=True)
    console.print(syntax)
