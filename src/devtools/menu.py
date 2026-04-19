"""Интерактивное меню."""

import os
import sys
import subprocess
from devtools import __version__
from devtools.console import console, error_console


def clear_screen() -> None:
    """Очистить экран."""
    os.system("cls" if os.name == "nt" else "clear")


MENU = """
╔══════════════════════════════════════════════════════════════╗
║                    Dev-utils v{version}                       ║
║              Профессиональные CLI-утилиты                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  [1]  Файловые утилиты       (file list, hash, find...)     ║
║  [2]  Работа с данными       (JSON, YAML, CSV...)          ║
║  [3]  Сетевые утилиты        (ip, headers, test...)       ║
║  [4]  Текстовые утилиты      (grep, sort, encode...)     ║
║  [5]  Криптография            (hash, password, token...)   ║
║  [6]  Система                (ps, top, memory...)          ║
║  [7]  HTTP клиент            (request, benchmark...)         ║
║  [8]  Планировщик           (cron parse, validate...)     ║
║                                                              ║
║  [0]  Выход                                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""".format(version=__version__)

SUBMENUS = {
    "1": {
        "title": "Файловые утилиты",
        "commands": {
            "1": ("Список файлов", "file list . --size"),
            "2": ("Древовидный вид", "file list . --tree"),
            "3": ("Найти файлы", "file find *.py"),
            "4": ("Хеш файла", "file hash "),
        },
    },
    "2": {
        "title": "Работа с данными",
        "commands": {
            "1": ("Валидировать JSON", "data validate "),
            "2": ("Форматировать JSON", "data format "),
            "3": ("Минифицировать JSON", "data minify "),
            "4": ("Конвертировать JSON<->YAML", "data convert "),
            "5": ("Запрос к JSON", "data query "),
            "6": ("CSV в JSON", "data csv2json "),
            "7": ("JSON в CSV", "data json2csv "),
        },
    },
    "3": {
        "title": "Сетевые утилиты",
        "commands": {
            "1": ("Мой IP", "net ip"),
            "2": ("Информация об IP", "net info "),
            "3": ("Заголовки URL", "net headers "),
            "4": ("Тест URL", "net test "),
            "5": ("Статусы редиректов", "net status "),
            "6": ("Скачать файл", "net download "),
        },
    },
    "4": {
        "title": "Текстовые утилиты",
        "commands": {
            "1": ("Подсчет слов/строк", "text wc "),
            "2": ("Поиск (grep)", "text grep "),
            "3": ("Замена текста", "text replace "),
            "4": ("Кодировать", "text encode "),
            "5": ("Декодировать", "text decode "),
            "6": ("Сортировка", "text sort "),
            "7": ("Уникальные строки", "text unique "),
            "8": ("Изменить регистр", "text case "),
        },
    },
    "5": {
        "title": "Криптография",
        "commands": {
            "1": ("Хеш текста", "crypto hash "),
            "2": ("HMAC", "crypto hmac "),
            "3": ("Генератор паролей", "crypto generate-password"),
            "4": ("Генератор токена", "crypto generate-token"),
            "5": ("Генератор UUID", "crypto uuid"),
            "6": ("Случайное число", "crypto randint"),
            "7": ("Случайная строка", "crypto random-string "),
            "8": ("Проверить хеш", "crypto verify-hash "),
        },
    },
    "6": {
        "title": "Система",
        "commands": {
            "1": ("Список процессов", "sys ps"),
            "2": ("Топ процессов", "sys top"),
            "3": ("Информация о системе", "sys info"),
            "4": ("Память", "sys memory"),
            "5": ("Диск", "sys disk"),
            "6": ("Процессы на порту", "sys port "),
        },
    },
    "7": {
        "title": "HTTP клиент",
        "commands": {
            "1": ("HTTP запрос", "http request "),
            "2": ("Бенчмарк", "http benchmark "),
        },
    },
    "8": {
        "title": "Планировщик",
        "commands": {
            "1": ("Следующие запуски", "cron next "),
            "2": ("Валидировать cron", "cron validate "),
        },
    },
}


def print_submenu(submenu: dict) -> None:
    """Показать подменю."""
    console.print("")
    console.print(f"[bold cyan]{submenu['title']}[/bold cyan]")
    console.print("=" * 50)
    for key, value in submenu["commands"].items():
        desc = value[0]
        console.print(f"  [{key}] {desc}")
    console.print("  [b/0] Назад")


def run_command(cmd: str) -> None:
    """Выполнить команду."""
    if not cmd.strip():
        return

    try:
        result = subprocess.run(
            [sys.executable, "-m", "devtools.cli"] + cmd.split(),
            cwd="C:\\Users\\777\\Desktop\\экосистемма github",
            capture_output=False,
            text=True,
        )
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")


def main() -> None:
    """Главный цикл меню."""
    import time

    while True:
        clear_screen()
        console.print(MENU)
        choice = console.input("[bold]Вы��ерите пункт: [/bold]").strip()

        if choice == "0":
            console.print("")
            console.print("[green]До свидания![/green]")
            console.print("")
            break

        if choice in SUBMENUS:
            submenu = SUBMENUS[choice]
            while True:
                clear_screen()
                print_submenu(submenu)
                sub_choice = console.input("\n[bold]Выберите пункт: [/bold]").strip()

                if sub_choice in ["0", "b"]:
                    break

                if sub_choice in submenu["commands"]:
                    cmd = submenu["commands"][sub_choice][1]
                    if cmd == "back":
                        break
                    clear_screen()
                    console.print(f"[bold cyan]Выполняю:[/bold cyan] {cmd}")
                    console.print("")
                    run_command(cmd)
                    console.input("\n[bold]Нажмите Enter для продолжения...[/bold]")
        else:
            console.print("[red]Неверный выбор![/red]")
            time.sleep(1)


if __name__ == "__main__":
    main()
