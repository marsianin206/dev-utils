"""Сетевые утилиты."""

import json
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import requests
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from devtools.apps import net_app
from devtools.console import console, error_console

console = Console()


@net_app.command("ip")
def get_ip(
    format: str = typer.Option("json", "--format", "-f", help="Формат: json, text"),
) -> None:
    """Получить внешний IP-адрес."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Получение IP...", total=None)

        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=10)
            data = response.json()
        except requests.RequestException as e:
            error_console.print(f"[red]Ошибка: {e}[/red]")
            raise typer.Exit(1)

        progress.update(task, completed=True)

    if format == "json":
        console.print_json(json.dumps(data))
    else:
        console.print(f"[cyan]{data['ip']}[/cyan]")


@net_app.command("info")
def ip_info(
    ip: str = typer.Argument(..., help="IP-адрес"),
) -> None:
    """Информация об IP-адресе."""
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as",
            timeout=10,
        )
        data = response.json()
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)

    if data.get("status") == "fail":
        error_console.print(f"[red]Ошибка: IP не найден[/red]")
        raise typer.Exit(1)

    table = Table(title=f"Информация об IP: {ip}")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    for key, value in data.items():
        if key != "status":
            table.add_row(key, str(value))

    console.print(table)


@net_app.command("headers")
def get_headers(
    url: str = typer.Argument(..., help="URL"),
    show: str = typer.Option("all", "--show", "-s", help="Показать: all, common"),
) -> None:
    """Получить заголовки ответа."""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)

    headers = dict(response.headers)

    if show == "common":
        common = ["content-type", "content-length", "server", "date", "cache-control", "connection"]
        headers = {k: v for k, v in headers.items() if k.lower() in common}

    table = Table(title=f"Заголовки: {url}")
    table.add_column("Заголовок", style="cyan")
    table.add_column("Значение", style="green")

    for key, value in headers.items():
        table.add_row(key, value)

    console.print(table)


@net_app.command("test")
def test_url(
    url: str = typer.Argument(..., help="URL для тестирования"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP метод"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Таймаут в секундах"),
    follow: bool = typer.Option(True, "--follow", "-f", help="Следовать редиректам"),
) -> None:
    """Тестирование URL."""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url

    try:
        start = time.time()
        response = requests.request(method, url, timeout=timeout, allow_redirects=follow)
        elapsed = time.time() - start
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)

    table = Table(title=f"Результат: {url}")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Статус", str(response.status_code))
    table.add_row("Время", f"{elapsed:.2f} сек")
    table.add_row("Content-Type", response.headers.get("Content-Type", "N/A"))
    table.add_row("Content-Length", response.headers.get("Content-Length", "N/A"))
    table.add_row("Server", response.headers.get("Server", "N/A"))

    console.print(table)

    if response.status_code >= 400:
        console.print(f"[red]Ошибка HTTP: {response.status_code}[/red]")


@net_app.command("download")
def download_file(
    url: str = typer.Argument(..., help="URL файла"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Выходной файл"),
    show_progress: bool = typer.Option(True, "--progress", "-p", help="Показывать прогресс"),
) -> None:
    """Скачать файл."""
    from rich.progress import DownloadColumn, Progress, TimeRemainingColumn

    if not output:
        parsed = urlparse(url)
        output = parsed.path.split("/")[-1]

    try:
        with Progress(
            *Progress.get_default_columns(),
            DownloadColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Скачивание...", start=False)

            def hook(progress_bar, chunk_size, total_size):
                if total_size:
                    progress_bar.update(task, total=total_size)
                progress_bar.update(task, advance=chunk_size)

            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            with open(output, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        if show_progress and total:
                            progress.update(task, advance=len(chunk))

        console.print(f"[green]✓ Скачано: {output}[/green]")
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)


@net_app.command("status")
def check_status(
    url: str = typer.Argument(..., help="URL"),
    follow: bool = typer.Option(True, "--follow", "-f", help="Следовать редиректам"),
) -> None:
    """Проверить статус всех редиректов."""
    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(url, timeout=10, allow_redirects=follow)
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)

    table = Table(title=f"Статусы: {url}")
    table.add_column("URL", style="cyan")
    table.add_column("Статус", style="green")
    table.add_column("Редирект", style="yellow")

    for r in response.history:
        table.add_row(r.url, str(r.status_code), "→")

    table.add_row(response.url, str(response.status_code), "")

    console.print(table)


@net_app.command("ping")
def ping_url(
    host: str = typer.Argument(..., help="Хост"),
    count: int = typer.Option(4, "--count", "-n", help="Количество пингов"),
) -> None:
    """Пинг хоста."""
    import socket

    if not host.startswith(("http://", "https://")):
        host = "https://" + host

    parsed = urlparse(host)
    hostname = parsed.netloc or parsed.path

    parts = hostname.split(":")
    host_part = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 80

    table = Table(title=f"Ping: {hostname}")
    table.add_column("#", style="cyan")
    table.add_column("Время", style="green")
    table.add_column("Статус", style="magenta")

    for i in range(count):
        start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host_part, port))
            elapsed = (time.time() - start) * 1000
            sock.close()
            table.add_row(str(i + 1), f"{elapsed:.0f} мс", "✓")
        except Exception:
            table.add_row(str(i + 1), "timeout", "✗")

    console.print(table)
