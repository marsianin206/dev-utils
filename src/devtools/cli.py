"""Главный CLI-интерфейс."""

import typer
from typing import Optional
from devtools import __version__
from devtools.console import console

app = typer.Typer(
    name="devtools",
    help="DevTools - профессиональные CLI-утилиты для разработчиков",
    add_completion=False,
    no_args_is_help=True,
)

data_app = typer.Typer(help="Утилиты для работы с данными")
file_app = typer.Typer(help="Файловые утилиты")
net_app = typer.Typer(help="Сетевые утилиты")
text_app = typer.Typer(help="Текстовые утилиты")
crypto_app = typer.Typer(help="Криптографические утилиты")

app.add_typer(data_app, name="data")
app.add_typer(file_app, name="file")
app.add_typer(net_app, name="net")
app.add_typer(text_app, name="text")
app.add_typer(crypto_app, name="crypto")


@app.command()
def version() -> None:
    """Показать версию программы."""
    from rich.theme import Theme
    from rich.console import Console

    theme = Theme({"info": "cyan", "bold": "bold cyan"})
    con = Console(theme=theme)
    con.print(f"[bold]DevTools[/bold] v{__version__}", style="info")


@app.command()
def help() -> None:
    """Показать справку."""
    console.print("[bold]DevTools[/bold] - доступные команды:")
    console.print("  devtools data    - работа с данными (JSON, YAML, CSV)")
    console.print("  devtools file    - файловые утилиты")
    console.print("  devtools net     - сетевые утилиты")
    console.print("  devtools text    - текстовые утилиты")
    console.print("  devtools crypto  - криптографические утилиты")
    console.print("  devtools version - версия программы")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
