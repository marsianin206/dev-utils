# Руководство для контрибьюторов

Спасибо за интерес к DevTools!

## Требования

- Python 3.10+
- pip
- Git

## Установка для разработки

```bash
git clone https://github.com/marsianin206/dev-utils.git
cd devtools
pip install -e ".[dev]"
```

## Структура проекта

```
devtools/
├── src/devtools/      # Исходный код
│   ├── cli.py         # Главный CLI
│   ├── console.py     # Консольный вывод
│   └── tools/         # Модули утилит
│       ├── data.py    # Работа с данными
│       ├── file.py    # Файловые утилиты
│       ├── net.py     # Сетевые утилиты
│       ├── text.py    # Текстовые утилиты
│       └── crypto.py  # Криптография
├── tests/             # Тесты
└── pyproject.toml     # Конфигурация
```

## Добавление новой команды

1. Создайте команду в соответствующем модуле в `src/devtools/tools/`
2. Зарегистрируйте в `cli.py`
3. Добавьте тесты

## Запуск тестов

```bash
pytest -v
```

## Стиль кода

- Используйте ruff для форматирования
- Соблюдайте type hints
- Добавляйте docstrings

## Pull Requests

1. Fork репозиторий
2. Создайте ветку `feature/your-feature`
3. Внесите изменения
4. Запустите тесты
5. Создайте PR