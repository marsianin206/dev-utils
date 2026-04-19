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
║  [1] Файловые утилиты       [5] Криптография            ║
║  [2] Работа с данными       [6] Система                   ║
║  [3] Сетевые утилиты        [7] HTTP клиент              ║
║  [4] Текстовые утилиты      [8] Планировщик             ║
╠══════════════════════════════════════════════════════════════╣
║  [0] Выход                                                ║
╚══════════════════════════════════════════════════════════════╝
""".format(version=__version__)

COMMANDS = {
    "1": [
        ("Список файлов", "file list . --size", ""),
        ("Древовидный вид", "file list . --tree", ""),
        ("Найти файлы", "file find", "шаблон (например *.py)"),
        ("Хеш файла", "file hash", "путь к файлу"),
        ("Размер файла", "file size", "путь к файлу"),
        ("Сравнить файлы", "file diff", "файл1 файл2"),
    ],
    "2": [
        ("Валидировать JSON", "data validate", "путь к файлу"),
        ("Форматировать JSON", "data format", "путь к файлу"),
        ("Минифицировать JSON", "data minify", "путь к файлу"),
        ("Конвертировать JSON->YAML", "data convert", "файл json yaml"),
        ("Конвертировать YAML->JSON", "data convert", "файл yaml json"),
        ("Запрос к JSON", "data query", "путь ключ"),
        ("CSV в JSON", "data csv2json", "путь к CSV"),
    ],
    "3": [
        ("Мой IP", "net ip", ""),
        ("Информация об IP", "net info", "IP адрес"),
        ("Заголовки URL", "net headers", "URL"),
        ("Тест URL", "net test", "URL"),
        ("Статусы редиректов", "net status", "URL"),
    ],
    "4": [
        ("Подсчет текста", "text wc", "текст"),
        ("Поиск (grep)", "text grep", "паттерн --text текст"),
        ("Замена текста", "text replace", "что на что --text текст"),
        ("Кодировать base64", "text encode", "текст base64"),
        ("Декодировать base64", "text decode", "текст base64"),
        ("Сортировка строк", "text sort", "--text строка1\\nстрока2"),
        ("Изменить регистр", "text case", "текст --mode lower"),
    ],
    "5": [
        ("Хеш текста", "crypto hash", "текст"),
        ("Хеш файла", "crypto checksum", "путь к файлу"),
        ("Генератор паролей", "crypto generate-password --length 16", ""),
        ("Генератор токена", "crypto generate-token --length 32", ""),
        ("Генератор UUID", "crypto uuid", ""),
        ("Случайное число", "crypto randint --min 1 --max 100", ""),
        ("Случайная строка", "crypto random-string --length 16", ""),
        ("Проверить хеш", "crypto verify-hash", "текст хеш"),
    ],
    "6": [
        ("Список процессов", "sys ps --limit 15", ""),
        ("Топ процессов", "sys top --limit 10", ""),
        ("Информация о системе", "sys info", ""),
        ("Память", "sys memory", ""),
        ("Диск", "sys disk", ""),
        ("Процессы на порту", "sys port", "номер порта"),
    ],
    "7": [
        ("HTTP запрос (GET)", "http request", "URL"),
        ("HTTP запрос (POST)", "http request", "URL --method POST --data '{}'"),
        ("Бенчмарк URL", "http benchmark", "URL --count 5"),
    ],
    "8": [
        ("Следующий запуск cron", "cron next", "cron выражение"),
        ("Валидировать cron", "cron validate", "cron выражение"),
        ("Следующие 5 запусков", "cron", "*/5 * * * * --next 5"),
    ],
}


def run_command(cmd: str) -> None:
    """Выполнить команду."""
    if not cmd.strip():
        return
    try:
        subprocess.run(
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
        choice = console.input("[bold]Выберите пункт: [/bold]").strip()

        if choice == "0":
            console.print("")
            console.print("[green]До свидания![/green]")
            console.print("")
            break

        if choice in COMMANDS:
            commands = COMMANDS[choice]
            while True:
                clear_screen()
                console.print("")
                console.print("[bold cyan]Доступные команды:[/bold cyan]")
                console.print("=" * 50)
                for i, (desc, _, arg) in enumerate(commands, 1):
                    console.print(f"  [{i}] {desc}")
                console.print("  [0] Назад")

                sub_choice = console.input("\n[bold]Выберите команду: [/bold]").strip()

                if sub_choice == "0":
                    break

                try:
                    idx = int(sub_choice) - 1
                    if 0 <= idx < len(commands):
                        desc, cmd_base, arg_hint = commands[idx]

                        cmd = cmd_base
                        if arg_hint:
                            clear_screen()
                            console.print(f"[bold]{desc}[/bold]")
                            if arg_hint:
                                console.print(f"[dim]Подсказка: {arg_hint}[/dim]")
                            user_arg = console.input("\nВведите значение: ").strip()
                            if user_arg:
                                cmd = f"{cmd_base} {user_arg}"

                        clear_screen()
                        console.print(f"[bold cyan]Выполняю:[/bold cyan] {cmd}")
                        console.print("")
                        run_command(cmd)
                        console.input("\n[bold]Нажмите Enter для продолжения...[/bold]")
                except ValueError:
                    pass
        else:
            console.print("[red]Неверный выбор![/red]")
            time.sleep(1)


if __name__ == "__main__":
    main()
