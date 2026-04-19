"""Сетевые утилиты."""

import json
import socket
import ssl
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
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
    format: str = typer.Option("text", "--format", "-f", help="Формат: json, text"),
) -> None:
    """Получить внешний IP-адрес."""
    console.print("[cyan]Получение IP...[/cyan]")
    
    try:
        # Try multiple services for reliability
        services = [
            "https://api.ipify.org?format=json",
            "https://ipapi.co/json/",
            "https://httpbin.org/ip",
        ]
        
        data = None
        for url in services:
            try:
                response = requests.get(url, timeout=5)
                if "ipify" in url:
                    data = response.json()
                    ip = data.get("ip")
                elif "ipapi" in url:
                    data = response.json()
                    ip = data.get("ip")
                elif "httpbin" in url:
                    data = response.json()
                    ip = data.get("origin", "").split(",")[0].strip()
                
                if ip:
                    break
            except:
                continue
        
        if not ip:
            # Fallback to what's my ip
            response = requests.get("https://httpbin.org/ip", timeout=10)
            ip = response.json().get("origin", "Не удалось определить").split(",")[0].strip()
        
        if format == "json":
            console.print_json(json.dumps({"ip": ip}))
        else:
            console.print(f"[green]{ip}[/green]")
            
    except Exception as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)


@net_app.command("info")
def ip_info(
    ip: str = typer.Argument(..., help="IP-адрес"),
) -> None:
    """Информация об IP-адресе."""
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,currency",
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

    field_names = {
        "country": "Страна",
        "countryCode": "Код страны",
        "region": "Регион",
        "regionName": "Область/Штат",
        "city": "Город",
        "zip": "Индекс",
        "lat": "Широта",
        "lon": "Долгота",
        "timezone": "Часовой пояс",
        "isp": "Провайдер",
        "org": "Организация",
        "as": "AS",
        "currency": "Валюта",
    }

    for key, value in data.items():
        if key != "status" and value:
            name = field_names.get(key, key)
            table.add_row(name, str(value))

    console.print(table)


@net_app.command("myip")
def my_ip_extended() -> None:
    """Расширенная информация о вашем IP."""
    try:
        response = requests.get("http://ip-api.com/json/?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as", timeout=10)
        data = response.json()
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)

    table = Table(title="Ваш IP")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("IP", data.get("query", "N/A"))
    table.add_row("Страна", f"{data.get('country', '')} ({data.get('countryCode', '')})"))
    table.add_row("Город", data.get("city", "N/A"))
    table.add_row("Провайдер", data.get("isp", "N/A"))
    table.add_row("Организация", data.get("org", "N/A"))
    table.add_row("Часовой пояс", data.get("timezone", "N/A"))

    console.print(table)


@net_app.command("headers")
def get_headers(
    url: str = typer.Argument(..., help="URL"),
    show: str = typer.Option("common", "--show", "-s", help="Показать: all, common, security"),
) -> None:
    """Получить заголовки ответа."""
    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)

    headers = dict(response.headers)

    if show == "common":
        common = ["content-type", "content-length", "server", "date", "cache-control", "connection"]
        headers = {k: v for k, v in headers.items() if k.lower() in common}
    elif show == "security":
        security = ["content-security-policy", "strict-transport-security", "x-frame-options", "x-content-type-options", "x-xss-protection"]
        headers = {k: v for k, v in headers.items() if k.lower() in security}

    field_names = {
        "content-type": "Тип контента",
        "content-length": "Размер",
        "server": "Сервер",
        "date": "Дата",
        "cache-control": "Кэширование",
        "connection": "Соединение",
    }

    table = Table(title=f"Заголовки: {url}")
    table.add_column("Заголовок", style="cyan")
    table.add_column("Значение", style="green")

    for key, value in headers.items():
        name = field_names.get(key.lower(), key)
        table.add_row(name, value)

    console.print(table)


@net_app.command("test")
def test_url(
    url: str = typer.Argument(..., help="URL для тестирования"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP метод"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Таймаут в секундах"),
    follow: bool = typer.Option(True, "--follow", "-f", help="Следовать редиректам"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="Дополнительные заголовки JSON"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Данные для POST"),
) -> None:
    """Тестирование URL с подробной информацией."""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url

    console.print(f"[cyan]Тестирование:[/cyan] {method} {url}")
    
    req_headers = {}
    if headers:
        try:
            req_headers = json.loads(headers)
        except:
            pass

    try:
        start = time.time()
        
        if data and method == "GET":
            method = "POST"
            
        response = requests.request(
            method, url, 
            timeout=timeout, 
            allow_redirects=follow,
            headers=req_headers if req_headers else None,
            json=data if data else None,
        )
        elapsed = time.time() - start
        
        status_colors = {
            "2": "green",
            "3": "yellow", 
            "4": "red",
            "5": "red",
        }
        status_prefix = str(response.status_code)[0]
        status_color = status_colors.get(status_prefix, "white")

        table = Table(title="Результат")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")

        table.add_row("Код ответа", f"[{status_color}]{response.status_code}[/{status_color}]")
        table.add_row("Статус", response.reason)
        table.add_row("Время", f"{elapsed*1000:.0f} мс")
        table.add_row("Content-Type", response.headers.get("Content-Type", "N/A").split(";")[0])
        table.add_row("Content-Length", response.headers.get("Content-Length", "N/A"))
        table.add_row("Server", response.headers.get("Server", "N/A"))
        table.add_row("Cookies", str(len(response.cookies)) if response.cookies else "0")

        console.print(table)

        if follow and response.history:
            redir_table = Table(title="Редиректы")
            redir_table.add_column("№", style="cyan", width=4)
            redir_table.add_column("URL", style="yellow")
            redir_table.add_column("Код", style="green")
            
            for i, r in enumerate(response.history, 1):
                redir_table.add_row(str(i), r.url, str(r.status_code))
            
            console.print(redir_table)

    except requests.Timeout:
        error_console.print(f"[red]Таймаут ({timeout} сек)[/red]")
        raise typer.Exit(1)
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

    table = Table(title=f"Цепочка редиректов: {url}")
    table.add_column("URL", style="cyan", max_width=50)
    table.add_column("Статус", style="green")
    table.add_column("Время", style="yellow")

    start = response.elapsed.total_seconds() * 1000
    
    for i, r in enumerate(response.history):
        table.add_row(r.url[:50] + "..." if len(r.url) > 50 else r.url, str(r.status_code), "")

    table.add_row(response.url[:50] + "..." if len(response.url) > 50 else response.url, str(response.status_code), f"{start:.0f} мс")

    console.print(table)


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
        if not output or output == "/":
            output = "download"

    console.print(f"[cyan]Скачивание:[/cyan] {url}")
    
    try:
        with Progress(
            *Progress.get_default_columns(),
            DownloadColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Скачивание...", start=False)

            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            with open(output, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        if show_progress and total:
                            progress.update(task, advance=len(chunk))

        console.print(f"[green]✓ Сохранено: {output}[/green]")
        console.print(f"[dim]Размер: {total/1024/1024:.2f} МБ[/dim]")
    except requests.RequestException as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)


@net_app.command("ping")
def ping_url(
    host: str = typer.Argument(..., help="Хост"),
    count: int = typer.Option(4, "--count", "-n", help="Количество пингов"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Порт"),
) -> None:
    """Пинг хоста (TCP)."""
    if not host.startswith(("http://", "https://")):
        host = "https://" + host

    parsed = urlparse(host)
    hostname = parsed.netloc or parsed.path

    parts = hostname.split(":")
    host_part = parts[0]
    target_port = port if port else (int(parts[1]) if len(parts) > 1 else 443 if parsed.scheme == "https" else 80)

    console.print(f"[cyan]Пинг:[/cyan] {host_part}:{target_port}")
    
    results = []
    for i in range(count):
        start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((host_part, target_port))
            elapsed = (time.time() - start) * 1000
            sock.close()
            results.append(elapsed)
        except Exception as e:
            results.append(None)

    # Show results
    table = Table(title="Результаты")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Время", style="green")
    table.add_column("Статус", style="magenta")

    success_count = 0
    for i, r in enumerate(results, 1):
        if r:
            table.add_row(str(i), f"{r:.0f} мс", "✓")
            success_count += 1
        else:
            table.add_row(str(i), "timeout", "✗")

    console.print(table)
    
    if results:
        valid_results = [r for r in results if r]
        console.print(f"[dim]Статистика: {success_count}/{count} успешно, мин {min(valid_results):.0f} мс, макс {max(valid_results):.0f} мс, сред {sum(valid_results)/len(valid_results):.0f} мс[/dim]")


@net_app.command("dns")
def dns_lookup(
    domain: str = typer.Argument(..., help="Домен"),
) -> None:
    """DNS lookup для домена."""
    console.print(f"[cyan]DNS lookup:[/cyan] {domain}")
    
    try:
        result = socket.gethostbyname(domain)
        console.print(f"[green]IP адрес:[/green] {result}")
    except socket.gaierror as e:
        error_console.print(f"[red]Ошибка DNS: {e}[/red]")
        raise typer.Exit(1)


@net_app.command("reverse-dns")
def reverse_dns(
    ip: str = typer.Argument(..., help="IP адрес"),
) -> None:
    """Reverse DNS lookup."""
    console.print(f"[cyan]Reverse DNS:[/cyan] {ip}")
    
    try:
        result = socket.gethostbyaddr(ip)
        console.print(f"[green]Домен:[/green] {result[0]}")
        console.print(f"[dim]Псевдонимы:[/dim] {', '.join(result[1])}")
    except socket.herror as e:
        error_console.print(f"[red]Не найдено: {e}[/red]")
        raise typer.Exit(1)


@net_app.command("ssl")
def ssl_info(
    url: str = typer.Argument(..., help="URL с HTTPS"),
) -> None:
    """Информация о SSL сертификате."""
    if not url.startswith("https://"):
        url = "https://" + url
    
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    port = parsed.port or 443

    console.print(f"[cyan]SSL се��тификат:[/cyan] {host}")
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
                table = Table(title="Сертификат")
                table.add_column("Параметр", style="cyan")
                table.add_column("Значение", style="green")
                
                subject = dict(x[0] for x in cert.get("subject", []))
                issuer = dict(x[0] for x in cert.get("issuer", []))
                
                table.add_row("Субъект", subject.get("commonName", "N/A"))
                table.add_row("Издатель", issuer.get("commonName", "N/A"))
                table.add_row("Действителен до", cert.get("notAfter", "N/A"))
                table.add_row("Действителен с", cert.get("notBefore", "N/A"))
                
                if "san" in cert:
                    table.add_row("Альтернативные имена", ", ".join(cert["san"]))
                
                console.print(table)
                
                # Check if expired
                not_after = datetime.strptime(cert.get("notAfter", ""), "%b %d %H:%M:%S %Y %Z")
                if not_after < datetime.now():
                    console.print("[red]⚠ Сертификат истёк![/red]")
                else:
                    console.print("[green]✓ Сертификат действителен[/green]")
                    
    except ssl.SSLError as e:
        error_console.print(f"[red]Ошибка SSL: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)


@net_app.command("check")
def check_urls(
    urls: str = typer.Argument(..., help="URL через |"),
    timeout: int = typer.Option(5, "--timeout", "-t", help="Таймаут"),
) -> None:
    """Проверить несколько URL."""
    url_list = [u.strip() for u in urls.split("|") if u.strip()]
    
    table = Table(title=f"Проверка {len(url_list)} URL")
    table.add_column("URL", style="cyan", max_width=40)
    table.add_column("Статус", style="green")
    table.add_column("Время", style="yellow")

    for url in url_list:
        if not url.startswith("http"):
            url = "https://" + url
            
        try:
            start = time.time()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            elapsed = time.time() - start
            
            status = "✓" if response.status_code < 400 else "✗"
            table.add_row(url[:40] + "..." if len(url) > 40 else url, str(response.status_code), f"{elapsed*1000:.0f}мс")
        except Exception as e:
            table.add_row(url[:40] + "..." if len(url) > 40 else url, "✗", str(e)[:20])

    console.print(table)


@net_app.command("port")
def check_port(
    host: str = typer.Argument(..., help="Хост"),
    port: int = typer.Argument(..., help="Порт"),
) -> None:
    """Проверить открыт ли порт."""
    console.print(f"[cyan]Проверка порта:[/cyan] {host}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            console.print(f"[green]✓ Порт {port} открыт[/green]")
        else:
            console.print(f"[red]✗ Порт {port} закрыт[/red]")
    except Exception as e:
        error_console.print(f"[red]Ошибка: {e}[/red]")
        raise typer.Exit(1)


@net_app.command("user-agent")
def check_user_agent(
    url: str = typer.Argument(..., help="URL"),
    user_agent: str = typer.Option("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "--ua", "-u", help="User-Agent"),
) -> None:
    """Проверить как сервер отвечает на разные User-Agent."""
    if not url.startswith("http"):
        url = "https://" + url
        
    user_agents = {
        "default": user_agent,
        "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "bot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    }
    
    table = Table(title=f"User-Agent проверка: {url}")
    table.add_column("User-Agent", style="cyan")
    table.add_column("Статус", style="green")
    table.add_column("Server", style="yellow")

    for name, ua in user_agents.items():
        try:
            response = requests.get(url, headers={"User-Agent": ua}, timeout=10)
            table.add_row(name, str(response.status_code), response.headers.get("Server", "N/A"))
        except Exception as e:
            table.add_row(name, "Ошибка", str(e)[:20])

    console.print(table)