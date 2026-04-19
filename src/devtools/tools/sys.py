"""Процессы и система."""

from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from devtools.apps import sys_app
from devtools.console import console, error_console

console = Console()


@sys_app.command("ps")
def list_processes(
    user: bool = typer.Option(False, "--user", "-u", help="Показать пользователя"),
    full: bool = typer.Option(False, "--full", "-f", help="Полная информация"),
    limit: int = typer.Option(20, "--limit", "-n", help="Количество процессов"),
) -> None:
    """Список процессов."""
    try:
        import psutil
    except ImportError:
        error_console.print("[red]Ошибка: установите psutil (pip install psutil)[/red]")
        raise typer.Exit(1)

    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
    processes = processes[:limit]

    table = Table(title=f"Процессы (всего: {len(processes)})")
    table.add_column("PID", style="cyan")
    table.add_column("Имя", style="green")
    table.add_column("CPU %", style="yellow")
    table.add_column("Память %", style="magenta")

    if full:
        table.add_column("Статус", style="white")

    for p in processes:
        row = [
            str(p.get("pid", "-")),
            p.get("name", "-")[:30],
            f"{p.get('cpu_percent', 0):.1f}",
            f"{p.get('memory_percent', 0):.1f}",
        ]
        if full:
            row.append(p.get("status", "-"))
        table.add_row(*row)

    console.print(table)


@sys_app.command("kill")
def kill_process(
    pid: int = typer.Argument(..., help="PID процесса"),
    force: bool = typer.Option(False, "--force", "-f", help="Принудительно (SIGKILL)"),
) -> None:
    """Завершить процесс."""
    try:
        import psutil
    except ImportError:
        error_console.print("[red]Ошибка: установите psutil (pip install psutil)[/red]")
        raise typer.Exit(1)

    try:
        proc = psutil.Process(pid)
        name = proc.name()
        if force:
            proc.kill()
        else:
            proc.terminate()
        console.print(f"[green]✓ Процесс {pid} ({name}) завершён[/green]")
    except psutil.NoSuchProcess:
        error_console.print(f"[red]Ошибка: процесс {pid} не найден[/red]")
        raise typer.Exit(1)
    except psutil.AccessDenied:
        error_console.print(f"[red]Ошибка: нет прав для завершения процесса {pid}[/red]")
        raise typer.Exit(1)


@sys_app.command("top")
def top_processes(
    limit: int = typer.Option(10, "--limit", "-n", help="Количество процессов"),
) -> None:
    """Топ процессов по использованию ресурсов."""
    try:
        import psutil
    except ImportError:
        error_console.print("[red]Ошибка: установите psutil (pip install psutil)[/red]")
        raise typer.Exit(1)

    table = Table(title="Top процессов")
    table.add_column("PID", style="cyan")
    table.add_column("Имя", style="green")
    table.add_column("CPU", style="yellow")
    table.add_column("Память", style="magenta")
    table.add_column("Диски", style="blue")
    table.add_column("Сеть", style="red")

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent", "io_counters", "connections"]
    ):
        try:
            info = proc.info
            io = info.get("io_counters")
            io_str = (
                f"R:{io.read_count if io else 0} W:{io.write_count if io else 0}" if io else "-"
            )
            net = len(info.get("connections", []))
            table.add_row(
                str(info.get("pid", "-")),
                info.get("name", "-")[:20],
                f"{info.get('cpu_percent', 0):.1f}%",
                f"{info.get('memory_percent', 0):.1f}%",
                io_str[:15],
                str(net) if net else "-",
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    console.print(table)


@sys_app.command("info")
def system_info() -> None:
    """Информация о системе."""
    try:
        import psutil
    except ImportError:
        error_console.print("[red]Ошибка: установите psutil (pip install psutil)[/red]")
        raise typer.Exit(1)

    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    table = Table(title="Системная информация")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("CPU", f"{cpu_count} ядер ({cpu_percent}%)")
    table.add_row(
        "Память", f"{memory.percent}% ({memory.used // (1024**3)}/{memory.total // (1024**3)} GB)"
    )
    table.add_row(
        "Диск", f"{disk.percent}% ({disk.used // (1024**3)}/{disk.total // (1024**3)} GB)"
    )
    table.add_row(
        "Загрузка CPU", ", ".join(f"{x:.1f}" for x in psutil.cpu_percent(interval=1, percpu=True))
    )

    console.print(table)


@sys_app.command("memory")
def memory_info() -> None:
    """Информация о памяти."""
    try:
        import psutil
    except ImportError:
        error_console.print("[red]Ошибка: установите psutil (pip install psutil)[/red]")
        raise typer.Exit(1)

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    table = Table(title="Использование памяти")
    table.add_column("Тип", style="cyan")
    table.add_column("Всего", style="green")
    table.add_column("Использовано", style="yellow")
    table.add_column("Свободно", style="magenta")
    table.add_column("%", style="red")

    for name, mem in [("Оперативная", memory), ("Swap", swap)]:
        table.add_row(
            name,
            f"{mem.total // (1024**3)} GB",
            f"{mem.used // (1024**3)} GB",
            f"{mem.free // (1024**3)} GB",
            f"{mem.percent:.1f}%",
        )

    console.print(table)


@sys_app.command("disk")
def disk_usage(
    path: str = typer.Option("/", "--path", "-p", help="П��ть"),
) -> None:
    """Использование диска."""
    try:
        import psutil
    except ImportError:
        error_console.print("[red]Ошибка: установите psutil (pip install psutil)[/red]")
        raise typer.Exit(1)

    disk = psutil.disk_usage(path)

    table = Table(title=f"Диск: {path}")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Всего", f"{disk.total // (1024**3)} GB")
    table.add_row("Использовано", f"{disk.used // (1024**3)} GB")
    table.add_row("Свободно", f"{disk.free // (1024**3)} GB")
    table.add_row("Процент", f"{disk.percent}%")

    console.print(table)


@sys_app.command("port")
def port_info(
    port: int = typer.Argument(..., help="Порт"),
) -> None:
    """Процессы на порту."""
    try:
        import psutil
    except ImportError:
        error_console.print("[red]Ошибка: установите psutil (pip install psutil)[/red]")
        raise typer.Exit(1)

    table = Table(title=f"Процессы на порту {port}")
    table.add_column("PID", style="cyan")
    table.add_column("Имя", style="green")
    table.add_column("Статус", style="yellow")

    found = False
    for proc in psutil.process_iter(["pid", "name", "status"]):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    table.add_row(str(proc.info["pid"]), proc.info["name"], proc.info["status"])
                    found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if found:
        console.print(table)
    else:
        console.print(f"[yellow]Нет процессов на порту {port}[/yellow]")
