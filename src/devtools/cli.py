"""Главный CLI-интерфейс."""

import typer
from devtools import __version__
from devtools.console import console
from devtools.apps import (
    data_app,
    file_app,
    net_app,
    text_app,
    crypto_app,
    sys_app,
    http_app,
    scheduler_app,
    trans_app,
)

app = typer.Typer(
    name="dev-utils",
    help="Dev-utils - профессиональные CLI-утилиты для разработчиков",
    add_completion=False,
    no_args_is_help=True,
)

app.add_typer(data_app, name="data")
app.add_typer(file_app, name="file")
app.add_typer(net_app, name="net")
app.add_typer(text_app, name="text")
app.add_typer(crypto_app, name="crypto")
app.add_typer(sys_app, name="sys")
app.add_typer(http_app, name="http")
app.add_typer(scheduler_app, name="cron")
app.add_typer(trans_app, name="translate")


@app.command()
def version() -> None:
    """Показать версию программы."""
    from rich.theme import Theme
    from rich.console import Console

    theme = Theme({"info": "cyan", "bold": "bold cyan"})
    con = Console(theme=theme)
    con.print(f"[bold]Dev-utils[/bold] v{__version__}", style="info")


@app.command()
def help_cmd() -> None:
    """Показать справку."""
    console.print("[bold]Dev-utils[/bold] - доступные команды:")
    console.print("  dev-utils menu    - интерактивное меню")
    console.print("  dev-utils data    - работа с данными (JSON, YAML, CSV)")
    console.print("  dev-utils file    - файловые утилиты")
    console.print("  dev-utils net     - сетевые утилиты")
    console.print("  dev-utils text    - текстовые утилиты")
    console.print("  dev-utils crypto  - криптографические утилиты")
    console.print("  dev-utils sys     - системные утилиты (процессы, память)")
    console.print("  dev-utils http   - HTTP клиент")
    console.print("  dev-utils cron   - планировщик")
    console.print("  dev-utils version - версия программы")


@app.command()
def menu() -> None:
    """Запустить интерактивное меню."""
    from devtools.menu import main as menu_main

    menu_main()


def main() -> None:
    import devtools.tools.data
    import devtools.tools.file
    import devtools.tools.net
    import devtools.tools.text
    import devtools.tools.crypto
    import devtools.tools.sys
    import devtools.tools.http

    app()


if __name__ == "__main__":
    main()
