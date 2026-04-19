"""HTTP клиент и планировщик."""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from devtools.cli import http_app, scheduler_app
from devtools.console import console, error_console

console = Console()


def _parse_cron(expression: str) -> Optional[datetime]:
    """Вычислить следующее время выполнения по cron выражению."""
    parts = expression.split()
    if len(parts) < 5:
        return None

    now = datetime.now()
    minute, hour, day, month, weekday = parts[:5]

    next_run = now + timedelta(minutes=1)
    for _ in range(60 * 24 * 366):
        if _matches(next_run, parts):
            return next_run
        next_run += timedelta(minutes=1)
    return None


def _matches(dt: datetime, parts: List[str]) -> bool:
    """Проверить соответствие cron выражения."""
    fn = lambda v, p: v in p.split(",") or p == "*" or (p.startswith("*/") and v % int(p[2:]) == 0)
    return (
        fn(dt.minute, parts[0])
        and fn(dt.hour, parts[1])
        and fn(dt.day, parts[2])
        and fn(dt.month, parts[3])
        and fn(dt.weekday, parts[4])
    )


@http_app.command("request")
def http_request(
    url: str = typer.Argument(..., help="URL"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP метод"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Данные (JSON)"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="Заголовки (JSON)"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Таймаут"),
) -> None:
    """Выполнить HTTP запрос."""
    import requests

    if not url.startswith("http"):
        url = "https://" + url

    req_headers = {}
    if headers:
        try:
            req_headers = json.loads(headers)
        except json.JSONDecodeError:
            error_console.print("[red]Ошибка: неверный формат заголовков[/red]")
            raise typer.Exit(1)

    req_data = None
    if data:
        try:
            req_data = json.loads(data)
        except json.JSONDecodeError:
            req_data = data

    try:
        start = time.time()
        response = requests.request(
            method, url, json=req_data, headers=req_headers, timeout=timeout
        )
        elapsed = time.time() - start
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)

    table = Table(title=f"HTTP {method} {url}")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Статус", str(response.status_code))
    table.add_row("Время", f"{elapsed:.2f}s")
    table.add_row("Content-Type", response.headers.get("Content-Type", "-"))
    table.add_row("Content-Length", str(len(response.content)))

    console.print(table)

    try:
        response_data = response.json()
        syntax = Syntax(
            json.dumps(response_data, indent=2, ensure_ascii=False), "json", theme="monokai"
        )
        console.print(syntax)
    except json.JSONDecodeError:
        console.print(response.text[:500])


@http_app.command("batch")
def http_batch(
    file: str = typer.Argument(..., help="Файл с запросами (JSON)"),
    parallel: int = typer.Option(1, "--parallel", "-p", help="Параллельных запросов"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Таймаут"),
) -> None:
    """Выполнить пакет HTTP запросов."""
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed

    p = __import__("pathlib").Path(file)
    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{file}' не найден[/red]")
        raise typer.Exit(1)

    with open(p) as f:
        requests_list = json.load(f)

    if not isinstance(requests_list, list):
        requests_list = [requests_list]

    results: Dict = {}

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task(
            f"Выполнение {len(requests_list)} запросов...", total=len(requests_list)
        )

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {}
            for i, req in enumerate(requests_list):
                url = req.get("url", "")
                method = req.get("method", "GET")
                futures[executor.submit(requests.request, method, url, timeout=timeout)] = i

            for future in as_completed(futures):
                i = futures[future]
                try:
                    response = future.result()
                    results[i] = {"status": response.status_code, "ok": response.ok}
                except Exception as e:
                    results[i] = {"error": str(e)}
                progress.advance(task)

    table = Table(title=f"Результаты ({len(results)}/{len(requests_list)})")
    table.add_column("#", style="cyan")
    table.add_column("URL", style="green")
    table.add_column("Статус", style="yellow")
    table.add_column("OK", style="magenta")

    for i, req in enumerate(requests_list):
        res = results.get(i, {})
        table.add_row(
            str(i + 1),
            req.get("url", "")[:40],
            str(res.get("status", res.get("error", "-"))),
            "✓" if res.get("ok") else "✗",
        )

    console.print(table)


@http_app.command("benchmark")
def http_benchmark(
    url: str = typer.Argument(..., help="URL"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP метод"),
    count: int = typer.Option(10, "--count", "-n", help="Количество запросов"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Таймаут"),
) -> None:
    """Бенчмарк HTTP запросов."""
    import requests

    if not url.startswith("http"):
        url = "https://" + url

    times: List[float] = []
    errors = 0

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task(f"Бенчмарк {count} запросов...", total=count)

        for _ in range(count):
            start = time.time()
            try:
                response = requests.request(method, url, timeout=timeout)
                elapsed = time.time() - start
                times.append(elapsed)
                if not response.ok:
                    errors += 1
            except Exception:
                errors += 1
            progress.advance(task)

    if times:
        avg = sum(times) / len(times)
        min_t = min(times)
        max_t = max(times)

        table = Table(title=f"Бенчмарк: {url}")
        table.add_column("Метрика", style="cyan")
        table.add_column("Значение", style="green")

        table.add_row("Запросов", str(len(times)))
        table.add_row("Ошибок", str(errors))
        table.add_row("Среднее", f"{avg * 1000:.1f}ms")
        table.add_row("Мин", f"{min_t * 1000:.1f}ms")
        table.add_row("Макс", f"{max_t * 1000:.1f}ms")
        table.add_row("RPS", f"{len(times) / sum(times):.1f}")

        console.print(table)


@scheduler_app.command("cron")
def cron_parse(
    expression: str = typer.Argument(..., help="Cron выражение"),
    next_n: int = typer.Option(5, "--next", "-n", help="Следующих запусков"),
) -> None:
    """Парсить и показать следующие запуски cron."""
    parts = expression.split()
    if len(parts) < 5:
        error_console.print(
            "[red]Ошибка: неверное cron выражение (минута час день месяц день_недели)[/red]"
        )
        raise typer.Exit(1)

    table = Table(title=f"Cron: {expression}")
    table.add_column("#", style="cyan")
    table.add_column("Дата и время", style="green")
    table.add_column("Описание", style="yellow")

    descriptions = {
        "0": "воскресенье",
        "1": "понедельник",
        "2": "вторник",
        "3": "среда",
        "4": "четверг",
        "5": "пятница",
        "6": "суббота",
        "7": "воскресенье",
    }

    now = datetime.now()
    found = 0
    check_time = now

    while found < next_n:
        check_time += timedelta(minutes=1)
        if _matches(check_time, parts):
            table.add_row(
                str(found + 1), check_time.strftime("%Y-%m-%d %H:%M"), check_time.strftime("%A")
            )
            found += 1

    console.print(table)


@scheduler_app.command("next")
def cron_next(
    expression: str = typer.Argument(..., help="Cron выражение"),
) -> None:
    """Показать следующий запуск."""
    parts = expression.split()
    if len(parts) < 5:
        error_console.print("[red]Ошибка: неверное cron выражение[/red]")
        raise typer.Exit(1)

    next_run = _parse_cron(expression)
    if next_run:
        console.print(f"[green]Следующий запуск: {next_run.strftime('%Y-%m-%d %H:%M')}[/green]")
    else:
        error_console.print("[red]Ошибка: невозможно вычислить следующий запуск[/red]")
        raise typer.Exit(1)


@scheduler_app.command("validate")
def cron_validate(
    expression: str = typer.Argument(..., help="Cron выражение"),
) -> None:
    """Валидировать cron выражение."""
    parts = expression.split()

    if len(parts) < 5:
        error_console.print(f"[red]Ошибка: ожидалось 5 частей, получено {len(parts)}[/red]")
        raise typer.Exit(1)

    labels = ["минута (0-59)", "час (0-23)", "день (1-31)", "месяц (1-12)", "день недели (0-7)"]

    table = Table(title=f"Валидация: {expression}")
    table.add_column("Поле", style="cyan")
    table.add_column("Значение", style="green")
    table.add_column("Статус", style="yellow")

    valid = True
    for label, value in zip(labels, parts):
        status = (
            "✓" if value in ["*", "*/" + value.split("/")[-1] if "/" in value else True] else "?"
        )
        if value != "*" and "/" not in value and value.isdigit():
            try:
                idx = labels.index(label)
                min_val, max_val = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)][idx]
                if not (min_val <= int(value) <= max_val):
                    status = "✗"
                    valid = False
            except ValueError:
                status = "✗"
                valid = False
        table.add_row(label, value, status)

    console.print(table)

    if valid:
        console.print("[green]✓ Cron выражение валидно[/green]")
    else:
        error_console.print("[red]✗ Cron выражение содержит ошибки[/red]")
