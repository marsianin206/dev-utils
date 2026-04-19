"""Typer приложения."""

import typer

data_app = typer.Typer(help="Утилиты для работы с данными")
file_app = typer.Typer(help="Файловые утилиты")
net_app = typer.Typer(help="Сетевые утилиты")
text_app = typer.Typer(help="Текстовые утилиты")
crypto_app = typer.Typer(help="Криптографические утилиты")
sys_app = typer.Typer(help="Системные утилиты")
http_app = typer.Typer(help="HTTP клиент")
scheduler_app = typer.Typer(help="Планировщик")
