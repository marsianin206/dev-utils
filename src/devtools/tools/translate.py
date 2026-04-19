"""Переводчик текста и файлов."""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, List, Dict
import typer
from rich.console import Console
from rich.table import Table

from devtools.apps import trans_app
from devtools.console import console, error_console

console = Console()


LANG_CODES = {
    "auto": "Автоопределение",
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
    "ar": "Арабский",
    "hi": "Хинди",
    "tr": "Турецкий",
    "pl": "Польский",
    "nl": "Нидерландский",
    "uk": "Украинский",
    "cs": "Чешский",
    "sv": "Шведский",
    "da": "Датский",
    "fi": "Финский",
    "no": "Норвежский",
    "th": "Тайский",
    "vi": "Вьетнамский",
    "id": "Индонезийский",
    "he": "Иврит",
}

CACHE_DIR = Path.home() / ".devtools" / "cache"
CACHE_FILE = CACHE_DIR / "translate_cache.json"


def _load_cache() -> Dict:
    """Загрузить кэш переводов."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def _save_cache(cache: Dict) -> None:
    """Сохранить кэш переводов."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_cache_key(text: str, from_lang: str, to_lang: str) -> str:
    """Получить ключ кэша."""
    return hashlib.md5(f"{text}:{from_lang}:{to_lang}".encode()).hexdigest()


def _translate_with_cache(text: str, from_lang: str, to_lang: str, use_cache: bool = True) -> str:
    """Перевести текст с использованием кэша."""
    if use_cache and from_lang != "auto":
        cache = _load_cache()
        key = _get_cache_key(text, from_lang, to_lang)
        if key in cache:
            return cache[key]

    result = _translate_google(text, from_lang, to_lang)

    if use_cache and from_lang != "auto":
        cache = _load_cache()
        cache[key] = result
        _save_cache(cache)

    return result


def _translate_google(text: str, from_lang: str, to_lang: str) -> str:
    """Перевести через Google Translate."""
    import random
    import time

    try:
        from googletrans import Translator

        translator = Translator()

        if from_lang == "auto":
            try:
                detected = translator.detect(text)
                from_lang = detected.lang
            except:
                from_lang = "en"

        # Retry logic for when Google returns None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = translator.translate(text, src=from_lang, dest=to_lang)
                if result and result.text:
                    return result.text
                # If result is None, try again after delay
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(0.5, 1.5))
            except TypeError as e:
                if "NoneType" in str(e) and attempt < max_retries - 1:
                    time.sleep(random.uniform(0.5, 1.5))
                    continue
                raise RuntimeError(f"Сервер перевода вернул пустой ответ. Попробуйте еще раз: {e}")
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(0.5, 1.5))
                    continue
                raise

        raise RuntimeError("Не удалось получить перевод после нескольких попыток")
    except ImportError:
        raise ImportError("googletrans не установлен. Установите: pip install googletrans")
    except RuntimeError:
        raise
    except AttributeError:
        raise AttributeError("Ошибка в googletrans. Попробуйте: pip install googletrans==4.0.0-rc1")
    except Exception as e:
        if "connection" in str(e).lower() or "network" in str(e).lower():
            raise ConnectionError(f"Ошибка сети: {e}")
        raise RuntimeError(f"Ошибка перевода: {e}")


def _translate_deepl(text: str, from_lang: str, to_lang: str) -> str:
    """Перевести через DeepL (если есть ключ)."""
    api_key = os.environ.get("DEEPL_API_KEY")
    if not api_key:
        return _translate_google(text, from_lang, to_lang)

    try:
        import requests

        url = "https://api-free.deepl.com/v2/translate"
        data = {
            "auth_key": api_key,
            "text": [text],
            "source_lang": from_lang.upper() if from_lang != "auto" else None,
            "target_lang": to_lang.upper(),
        }
        response = requests.post(url, data=data).json()
        return response["translations"][0]["text"]
    except:
        return _translate_google(text, from_lang, to_lang)


@trans_app.command("translate")
def translate(
    text: str = typer.Argument(..., help="Текст для перевода"),
    from_lang: str = typer.Option("auto", "--from", "-f", help="Исходный язык"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Без кэша"),
) -> None:
    """Перевести текст."""
    if from_lang not in LANG_CODES:
        error_console.print(f"[red]Ошибка: неизвестный язык '{from_lang}'[/red]")
        error_console.print(f"[dim]Доступные: {', '.join(sorted(LANG_CODES.keys()))}[/dim]")
        raise typer.Exit(1)

    if to_lang not in LANG_CODES:
        error_console.print(f"[red]Ошибка: неизвестный язык '{to_lang}'[/red]")
        error_console.print(f"[dim]Доступные: {', '.join(sorted(LANG_CODES.keys()))}[/dim]")
        raise typer.Exit(1)

    with console.status(f"[bold green]Перевод..."):
        result = _translate_with_cache(text, from_lang, to_lang, use_cache=not no_cache)

    detected = ""
    if from_lang == "auto":
        try:
            from googletrans import Translator

            translator = Translator()
            detected = f" ({LANG_CODES.get(translator.detect(text).lang, 'unknown')})"
        except:
            pass

    console.print("")
    console.print(
        f"[bold cyan]{LANG_CODES.get(from_lang, from_lang)}{detected} -> {LANG_CODES.get(to_lang, to_lang)}[/bold cyan]"
    )
    console.print("-" * 50)
    console.print(f"[white]{text}[/white]")
    console.print("")
    console.print(f"[green]{result}[/green]")


@trans_app.command("batch")
def translate_batch(
    texts: str = typer.Argument(..., help="Тексты через | (pipe)"),
    from_lang: str = typer.Option("auto", "--from", "-f", help="Исходный язык"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык"),
    show_original: bool = typer.Option(True, "--show-original", help="Показать оригинал"),
) -> None:
    """Перевести несколько текстов."""
    text_list = [t.strip() for t in texts.split("|") if t.strip()]

    if not text_list:
        error_console.print("[red]Ошибка: не введены тексты[/red]")
        raise typer.Exit(1)

    console.print("")
    console.print(
        f"[bold cyan]Перевод {len(text_list)} текстов: {from_lang} -> {to_lang}[/bold cyan]"
    )
    console.print("")

    table = Table(show_header=True)
    table.add_column("#", style="cyan", width=4)
    if show_original:
        table.add_column("Оригинал", style="white", max_width=30)
    table.add_column("Перевод", style="green")

    for i, text in enumerate(text_list, 1):
        result = _translate_with_cache(text, from_lang, to_lang)
        if show_original:
            table.add_row(str(i), text[:30] + "..." if len(text) > 30 else text, result)
        else:
            table.add_row(str(i), result)

    console.print(table)


@trans_app.command("detect")
def detect_language(
    text: str = typer.Argument(..., help="Текст для определения языка"),
) -> None:
    """Определить язык текста."""
    try:
        from googletrans import Translator

        translator = Translator()
        detected = translator.detect(text)

        lang_name = LANG_CODES.get(detected.lang, detected.lang)

        console.print("")
        console.print(
            f"[bold]Определенный язык:[/bold] [green]{lang_name}[/green] ({detected.lang})"
        )
        console.print(f"[bold]Уверенность:[/bold] {detected.confidence * 100:.1f}%")
    except ImportError:
        error_console.print("[red]Ошибка: googletrans не установлен[/red]")
    except Exception as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")


@trans_app.command("langs")
def list_languages() -> None:
    """Список поддерживаемых языков."""
    table = Table(title="Поддерживаемые языки")
    table.add_column("Код", style="cyan", width=8)
    table.add_column("Язык", style="green")

    for code, name in sorted(LANG_CODES.items()):
        table.add_row(code, name)

    console.print(table)


@trans_app.command("file")
def translate_file(
    input_file: str = typer.Argument(..., help="Входной файл"),
    from_lang: str = typer.Option("auto", "--from", "-f", help="Исходный язык"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Кодировка"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Без кэша"),
) -> None:
    """Перевести содержимое файла."""
    p = Path(input_file)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{input_file}' не найден[/red]")
        raise typer.Exit(1)

    ext = p.suffix.lower()
    console.print(f"[cyan]Перевод файла {p.name} ({ext})[/cyan]")

    try:
        content = p.read_text(encoding=encoding)
    except Exception as e:
        error_console.print(f"[red]Ошибка чтения: {e}[/red]")
        raise typer.Exit(1)

    with console.status(f"[bold green]Перевод файла..."):
        if ext == ".json":
            result = _translate_json_content(content, from_lang, to_lang, no_cache)
        elif ext in [".md", ".markdown"]:
            result = _translate_markdown_content(content, from_lang, to_lang, no_cache)
        elif ext in [".txt", ".text"]:
            result = _translate_text_content(content, from_lang, to_lang, no_cache)
        elif ext in [".html", ".htm"]:
            result = _translate_html_content(content, from_lang, to_lang, no_cache)
        else:
            result = _translate_text_content(content, from_lang, to_lang, no_cache)

    if output_file:
        out_path = Path(output_file)
        out_path.write_text(result, encoding=encoding)
        console.print(f"[green]Сохранено: {output_file}[/green]")
    else:
        console.print("")
        console.print(result)


def _translate_text_content(text: str, from_lang: str, to_lang: str, no_cache: bool) -> str:
    """Перевести простой текст."""
    return _translate_with_cache(text, from_lang, to_lang, use_cache=not no_cache)


def _translate_json_content(text: str, from_lang: str, to_lang: str, no_cache: bool) -> str:
    """Перевести JSON с сохранением структуры."""
    data = json.loads(text)

    def translate_value(val):
        if isinstance(val, str):
            return _translate_with_cache(val, from_lang, to_lang, use_cache=not no_cache)
        elif isinstance(val, dict):
            return {k: translate_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [translate_value(item) for item in val]
        return val

    result = translate_value(data)
    return json.dumps(result, indent=2, ensure_ascii=False)


def _translate_markdown_content(text: str, from_lang: str, to_lang: str, no_cache: bool) -> str:
    """Перевести Markdown с сохранением форматирования."""
    import re

    parts = re.split(
        r"(```[\s\S]*?```|```.*?\n[\s\S]*?```|~~.*?~~|\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_|~~.*?~~|#+ .*?\n|```.*)",
        text,
    )

    translated = []
    for part in parts:
        if not part.strip():
            translated.append(part)
        elif part.startswith("```") or part.startswith("~~") or part.startswith("#"):
            translated.append(part)
        elif part.startswith("**") or part.startswith("__"):
            translated.append(part)
        elif part.startswith("*") or part.startswith("_"):
            translated.append(part)
        else:
            translated.append(
                _translate_with_cache(part, from_lang, to_lang, use_cache=not no_cache)
            )

    return "".join(translated)


def _translate_html_content(text: str, from_lang: str, to_lang: str, no_cache: bool) -> str:
    """Перевести HTML с сохранением тегов."""
    import re

    pattern = r">([^<]+)<"

    def replace_text(match):
        text = match.group(1).strip()
        if text:
            return (
                ">" + _translate_with_cache(text, from_lang, to_lang, use_cache=not no_cache) + "<"
            )
        return match.group(0)

    return re.sub(pattern, replace_text, text)


@trans_app.command("json")
def translate_json(
    input_file: str = typer.Argument(..., help="JSON файл"),
    keys: str = typer.Option("", "--keys", "-k", help="Ключи через запятую (или all)"),
    from_lang: str = typer.Option("auto", "--from", "-f", help="Исходный язык"),
    to_lang: str = typer.Option("ru", "--to", "-t", help="Целевой язык"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Без кэша"),
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

    keys_to_translate = [k.strip() for k in keys.split(",") if k.strip()] if keys else []
    translate_all = "all" in keys_to_translate

    def should_translate(key: str) -> bool:
        if translate_all:
            return True
        return key in keys_to_translate

    def translate_dict(d: dict, parent_key: str = "") -> dict:
        result = {}
        for k, v in d.items():
            current_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                result[k] = translate_dict(v, current_key)
            elif isinstance(v, str) and v:
                if translate_all or should_translate(current_key):
                    result[k] = _translate_with_cache(v, from_lang, to_lang, use_cache=not no_cache)
                else:
                    result[k] = v
            elif isinstance(v, list):
                result[k] = [
                    _translate_with_cache(item, from_lang, to_lang, use_cache=not no_cache)
                    if isinstance(item, str) and (translate_all or should_translate(current_key))
                    else item
                    for item in v
                ]
            else:
                result[k] = v
        return result

    with console.status(f"[bold green]Перевод JSON..."):
        result = translate_dict(data)

    output = json.dumps(result, indent=2, ensure_ascii=False)

    if output_file:
        Path(output_file).write_text(output, encoding="utf-8")
        console.print(f"[green]Сохранено: {output_file}[/green]")
    else:
        console.print(output)


@trans_app.command("cache")
def manage_cache(
    action: str = typer.Argument("show", help="show, clear"),
) -> None:
    """Управление кэшем переводов."""
    cache = _load_cache()

    if action == "clear":
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        console.print("[green]Кэш очищен[/green]")
    elif action == "show":
        console.print(f"[cyan]Записей в кэше: {len(cache)}[/cyan]")
        if cache:
            sample = list(cache.items())[:5]
            table = Table(title="Пример кэша")
            table.add_column("Ключ", style="cyan")
            table.add_column("Перевод", style="green", max_width=40)
            for key, value in sample:
                table.add_row(key[:20] + "...", value[:40] + "...")
            console.print(table)


@trans_app.command("service")
def set_service(
    service: str = typer.Argument(..., help="google, deepl"),
) -> None:
    """Выбрать сервис перевода."""
    valid = ["google", "deepl"]
    if service not in valid:
        error_console.print(f"[red]Ошибка: доступны {valid}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]Выбран сервис: {service}[/green]")
    console.print("[dim]Для DeepL требуется ключ API: export DEEPL_API_KEY=your_key[/dim]")
