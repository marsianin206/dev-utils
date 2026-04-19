"""Переводчик текста и файлов."""

import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from devtools.apps import text_app as trans_app
from devtools.console import console, error_console

console = Console()


LANG_CODES = {
    "en": "Английский",
    "ru": "Русский",
    "es": "Испанский",
    "fr": "Французский",
    "de": "Немецкий",
    "it": "Итальянский",
    "pt": "Португальский",
    "zh": "Китайский",
    "ja": "Японский",
    "ko": "Корейский",
}


def translate_text(text: str, from_lang: str = "en", to_lang: str = "ru") -> str:
    """Перевести текст через Google Translate (бесплатный API)."""
    try:
        from googletrans import Translator

        translator = Translator()
        result = translator.translate(text, src=from_lang, dest=to_lang)
        return result.text
    except ImportError:
        return _translate_fake(text, from_lang, to_lang)


def _translate_fake(text: str, from_lang: str, to_lang: str) -> str:
    """Заглушка если нет googletrans."""
    return f"[{from_lang}->{to_lang}] {text}"


@trans_app.command("translate")
def translate(
    text: str = typer.Argument(..., help="Текст для перевода"),
    from_lang: str = typer.Option("en", "--from", "-f", help="Исходный язык (en, ru, es...)"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык (en, ru, es...)"),
) -> None:
    """Перевести текст."""
    if from_lang not in LANG_CODES:
        error_console.print(f"[red]Ошибка: неизвестный язык '{from_lang}'[/red]")
        error_console.print(f"[dim]Доступные: {', '.join(LANG_CODES.keys())}[/dim]")
        raise typer.Exit(1)

    if to_lang not in LANG_CODES:
        error_console.print(f"[red]Ошибка: неизвестный язык '{to_lang}'[/red]")
        error_console.print(f"[dim]Доступные: {', '.join(LANG_CODES.keys())}[/dim]")
        raise typer.Exit(1)

    try:
        result = translate_text(text, from_lang, to_lang)
        console.print("")
        console.print(f"[bold cyan]{LANG_CODES[from_lang]} -> {LANG_CODES}[/bold cyan]")
        console.print("=" * 50)
        console.print(f"[white]{text}[/white]")
        console.print("")
        console.print(f"[green]{result}[/green]")
    except Exception as e:
        error_console.print(f"[red]Ошибка перевода: {e}[/red]")


@trans_app.command("langs")
def list_languages() -> None:
    """Список поддерживаемых языков."""
    table = Table(title="Поддерживаемые языки")
    table.add_column("Код", style="cyan")
    table.add_column("Язык", style="green")

    for code, name in sorted(LANG_CODES.items()):
        table.add_row(code, name)

    console.print(table)


@trans_app.command("file")
def translate_file(
    input_file: str = typer.Argument(..., help="Входной файл"),
    from_lang: str = typer.Option("en", "--from", "-f", help="Исходный язык"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Кодировка файла"),
) -> None:
    """Перевести содержимое файла."""
    p = Path(input_file)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{input_file}' не найден[/red]")
        raise typer.Exit(1)

    try:
        content = p.read_text(encoding=encoding)
    except Exception as e:
        error_console.print(f"[red]Ошибка чтения файла: {e}[/red]")
        raise typer.Exit(1)

    try:
        result = translate_text(content, from_lang, to_lang)
    except Exception as e:
        error_console.print(f"[red]Ошибка перевода: {e}[/red]")
        raise typer.Exit(1)

    if output_file:
        out_path = Path(output_file)
        out_path.write_text(result, encoding=encoding)
        console.print(f"[green]Перевод сохранен в {output_file}[/green]")
    else:
        console.print("")
        console.print(f"[green]{result}[/green]")


@trans_app.command("json")
def translate_json(
    input_file: str = typer.Argument(..., help="JSON файл"),
    key: str = typer.Option(
        "", "--key", "-k", help="Ключ для перевода (оставьте пустым для всего файла)"
    ),
    from_lang: str = typer.Option("en", "--from", "-f", help="Исходный язык"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
) -> None:
    """Перевести значения в JSON файле."""
    p = Path(input_file)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{input_file}' не найден[/red]")
        raise typer.Exit(1)

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        error_console.print(f"[red]Ошибка JSON: {e}[/red]")
        raise typer.Exit(1)

    def translate_dict(d: dict, path: str = "") -> dict:
        result = {}
        for k, v in d.items():
            current_path = f"{path}.{k}" if path else k
            if isinstance(v, dict):
                result[k] = translate_dict(v, current_path)
            elif isinstance(v, str) and v:
                if key and current_path != key:
                    result[k] = v
                else:
                    try:
                        result[k] = translate_text(v, from_lang, to_lang)
                    except:
                        result[k] = v
            else:
                result[k] = v
        return result

    result = translate_dict(data)

    output = json.dumps(result, indent=2, ensure_ascii=False)

    if output_file:
        out_path = Path(output_file)
        out_path.write_text(output, encoding="utf-8")
        console.print(f"[green]Перевод сохранен в {output_file}[/green]")
    else:
        console.print(output)


@trans_app.command("markdown")
def translate_markdown(
    input_file: str = typer.Argument(..., help="Markdown файл"),
    from_lang: str = typer.Option("en", "--from", "-f", help="Исходный язык"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
) -> None:
    """Перевести Markdown файл с сохранением форматирования."""
    p = Path(input_file)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{input_file}' не найден[/red]")
        raise typer.Exit(1)

    content = p.read_text(encoding="utf-8")

    import re

    blocks = re.split(r"(\n```[\s\S]*?```|\n##.*|\n#.*|\n\*\*.*\*\*)", content)

    translated_blocks = []
    for block in blocks:
        if (
            block.startswith("```")
            or block.startswith("##")
            or block.startswith("#")
            or block.startswith("**")
        ):
            translated_blocks.append(block)
        elif block.strip():
            try:
                translated_blocks.append(translate_text(block, from_lang, to_lang))
            except:
                translated_blocks.append(block)
        else:
            translated_blocks.append(block)

    result = "".join(translated_blocks)

    if output_file:
        out_path = Path(output_file)
        out_path.write_text(result, encoding="utf-8")
        console.print(f"[green]Перевод сохранен в {output_file}[/green]")
    else:
        console.print(result)
