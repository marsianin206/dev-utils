"""Файловые утилиты."""

import os
import hashlib
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from devtools.cli import file_app
from devtools.console import console, error_console

console = Console()


@file_app.command("list")
def list_files(
    path: str = typer.Argument(".", help="Путь к директории"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Максимум файлов"),
    show_size: bool = typer.Option(False, "--size", "-s", help="Показать размер"),
    show_hidden: bool = typer.Option(False, "--hidden", "-a", help="Показать скрытые"),
    tree: bool = typer.Option(False, "--tree", "-t", help="Древовидный вид"),
) -> None:
    """Список файлов в директории."""
    p = Path(path).resolve()

    if not p.exists():
        error_console.print(f"[red]Ошибка: путь '{path}' не существует[/red]")
        raise typer.Exit(1)

    if not p.is_dir():
        error_console.print(f"[red]Ошибка: '{path}' не является директорией[/red]")
        raise typer.Exit(1)

    if tree:
        _show_tree(p, show_hidden)
    else:
        _show_list(p, limit, show_size, show_hidden)


def _show_tree(path: Path, show_hidden: bool) -> None:
    """Показать дерево файлов."""
    tree = Tree(f"[bold]{path.name}/[/bold]")
    _build_tree(path, tree, show_hidden)
    console.print(tree)


def _build_tree(path: Path, tree: Tree, show_hidden: bool) -> None:
    """Построить дерево рекурсивно."""
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    except PermissionError:
        return

    for item in items:
        if not show_hidden and item.name.startswith("."):
            continue

        if item.is_dir():
            branch = tree.add(f"[bold]{item.name}/[/bold]")
            _build_tree(item, branch, show_hidden)
        else:
            tree.add(f"[cyan]{item.name}[/cyan]")


def _show_list(path: Path, limit: Optional[int], show_size: bool, show_hidden: bool) -> None:
    """Показать список файлов."""
    files: List[dict] = []

    for item in path.iterdir():
        if not show_hidden and item.name.startswith("."):
            continue

        info = {"name": item.name, "type": "dir" if item.is_dir() else "file"}
        if show_size and item.is_file():
            info["size"] = item.stat().st_size
        files.append(info)

    files.sort(key=lambda x: (x["type"] != "file", x["name"]))

    if limit:
        files = files[:limit]

    table = Table(title=f"Файлы в {path}")
    table.add_column("Имя", style="cyan")
    table.add_column("Тип", style="magenta")

    if show_size:
        table.add_column("Размер", style="green")

    for f in files:
        row = [f["name"], f["type"]]
        if show_size and "size" in f:
            row.append(_format_size(f["size"]))
        table.add_row(*row)

    console.print(table)


def _format_size(size: int) -> str:
    """Форматировать размер файла."""
    for unit in ["Б", "КБ", "МБ", "ГБ"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ТБ"


@file_app.command("find")
def find_files(
    pattern: str = typer.Argument(..., help="Шаблон для поиска"),
    path: str = typer.Option(".", "--path", "-p", help="Директория поиска"),
    name_only: bool = typer.Option(False, "--name", "-n", help="Только имена"),
) -> None:
    """Найти файлы по шаблону."""
    from fnmatch import fnmatch

    p = Path(path).resolve()
    if not p.exists():
        error_console.print(f"[red]Ошибка: путь '{path}' не существует[/red]")
        raise typer.Exit(1)

    matches = list(p.rglob(pattern))
    matches = sorted(matches, key=lambda x: x.name)

    if not matches:
        console.print("[yellow]Файлы не найдены[/yellow]")
        return

    if name_only:
        for m in matches:
            console.print(m)
    else:
        table = Table(title=f"Найдено файлов: {len(matches)}")
        table.add_column("Путь", style="cyan")
        table.add_column("Размер", style="magenta")

        for m in matches:
            size = m.stat().st_size if m.is_file() else 0
            table.add_row(str(m), _format_size(size))

        console.print(table)


@file_app.command("hash")
def hash_file(
    path: str = typer.Argument(..., help="Путь к файлу"),
    algorithm: str = typer.Option(
        "sha256", "--algorithm", "-a", help="Алгоритм (md5, sha1, sha256, sha512)"
    ),
) -> None:
    """Вычислить хеш файла."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: файл '{path}' не существует[/red]")
        raise typer.Exit(1)

    if not p.is_file():
        error_console.print(f"[red]Ошибка: '{path}' не является файлом[/red]")
        raise typer.Exit(1)

    algo = algorithm.lower()
    if algo not in ["md5", "sha1", "sha256", "sha512"]:
        error_console.print(f"[red]Ошибка: алгоритм '{algorithm}' не поддерживается[/red]")
        raise typer.Exit(1)

    h = hashlib.new(algo)
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    console.print(f"[green]{h.hexdigest()}[/green]")
    console.print(f"[dim]({algorithm}: {path})[/dim]")


@file_app.command("size")
def file_size(
    path: str = typer.Argument(".", help="Путь к файлу или директории"),
    human: bool = typer.Option(True, "--human", "-h", help="Человекочитаемый формат"),
) -> None:
    """Размер файла или директории."""
    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: путь '{path}' не существует[/red]")
        raise typer.Exit(1)

    if p.is_file():
        size = p.stat().st_size
    else:
        size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())

    if human:
        console.print(f"[cyan]{_format_size(size)}[/cyan]")
    else:
        console.print(f"[cyan]{size}[/cyan]")


@file_app.command("diff")
def compare_files(
    file1: str = typer.Argument(..., help="Первый файл"),
    file2: str = typer.Argument(..., help="Второй файл"),
) -> None:
    """Сравнить два файла."""
    from difflib import unified_diff

    p1 = Path(file1)
    p2 = Path(file2)

    if not p1.exists():
        error_console.print(f"[red]Ошибка: файл '{file1}' не существует[/red]")
        raise typer.Exit(1)

    if not p2.exists():
        error_console.print(f"[red]Ошибка: файл '{file2}' не существует[/red]")
        raise typer.Exit(1)

    lines1 = p1.read_text().splitlines()
    lines2 = p2.read_text().splitlines()

    diff = list(unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm=""))

    if not diff:
        console.print("[green]Файлы идентичны[/green]")
    else:
        console.print("[bold]Различия:[/bold]")
        for line in diff:
            if line.startswith("---"):
                console.print(f"[red]{line}[/red]")
            elif line.startswith("+++"):
                console.print(f"[green]{line}[/green]")
            elif line.startswith("@@"):
                console.print(f"[yellow]{line}[/yellow]")
            else:
                console.print(line)


@file_app.command("permissions")
def show_permissions(
    path: str = typer.Argument(..., help="Путь к файлу"),
) -> None:
    """Показать права доступа к файлу."""
    import stat

    p = Path(path)

    if not p.exists():
        error_console.print(f"[red]Ошибка: путь '{path}' не существует[/red]")
        raise typer.Exit(1)

    mode = p.stat().st_mode

    table = Table(title=f"Права доступа: {path}")
    table.add_column("Свойство", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Тип", "Директория" if p.is_dir() else "Файл")
    table.add_row("Права", oct(stat.S_IMODE(mode)))
    table.add_row(" readable", "Да" if mode & stat.S_IRUSR else "Нет")
    table.add_row(" writable", "Да" if mode & stat.S_IWUSR else "Нет")
    table.add_row(" executable", "Да" if mode & stat.S_IXUSR else "Нет")

    console.print(table)
