# Dev-utils

Профессиональные CLI-утилиты для разработчиков. Полный набор инструментов для работы с файлами, данными, сетью, текстом и криптографией.

## Возможности

- **Файловые утилиты** - поиск, хеширование, сравнение файлов
- **Работа с данными** - JSON/YAML парсинг, валидация, конвертация
- **Сетевые утилиты** - HTTP тестирование, IP информация, заголовки
- **Текстовые утилиты** - grep, сортировка, кодирование
- **Криптография** - генерация паролей, токенов, HMAC

## Установка

### Из PyPI

```bash
pip install dev-utils
```

### Из исходников

```bash
git clone https://github.com/marsianin206/dev-utils.git
cd dev-utils
pip install -e ".[dev]"
```

## Быстрый старт

```bash
# Показать справку
dev-utils --help

# Показать версию
dev-utils version

# Список команд
dev-utils help
```

## Файловые утилиты

### list - Список файлов

```bash
# Простой список
dev-utils file list

# С размером файлов
dev-utils file list --size

# Древовидный вид
dev-utils file list --tree

# Скрытые файлы
dev-utils file list --hidden

# С ограничением
dev-utils file list --limit 20
```

### find - Поиск файлов

```bash
# Найти все txt файлы
dev-utils file find "*.txt"

# Только имена
dev-utils file find "*.py" --name-only
```

### hash - Хеш файла

```bash
# SHA-256 хеш
dev-utils file hash file.txt

# MD5 хеш
dev-utils file hash file.txt --algorithm md5

# SHA-512 хеш
dev-utils file hash file.txt --algorithm sha512
```

### size - Размер файла

```bash
# Человекочитаемый формат
dev-utils file size myfolder --human

# Точный размер в байтах
dev-utils file size myfolder
```

### diff - Сравнение файлов

```bash
dev-utils file diff file1.txt file2.txt
```

## Работа с данными

### validate - Валидация JSON

```bash
dev-utils data validate config.json
```

### format - Форматирование JSON

```bash
# Отступ 2 пробела
dev-utils data format config.json

# Сортировать ключи
dev-utils data format config.json --sort
```

### minify - Минификация JSON

```bash
dev-utils data minify config.json

# С сохранением в файл
dev-utils data minify config.json --output config.min.json
```

### query - Запрос к JSON

```bash
# Получить ключ
dev-utils data query config.json "database.host"

# Вложенные ключи
dev-utils data query config.json "users.0.name"
```

### convert - Конвертация форматов

```bash
# JSON в YAML
dev-utils data convert config.json yaml

# YAML в JSON
dev-utils data convert config.yaml json
```

### csv2json - CSV в JSON

```bash
dev-utils data csv2json data.csv

# С разделителем
dev-utils data csv2json data.csv --delimiter ";"
```

### json2csv - JSON в CSV

```bash
dev-utils data json2csv data.json
```

## Сетевые утилиты

### ip - Внешний IP

```bash
# JSON формат
dev-utils net ip

# Простой текст
dev-utils net ip --format text
```

### info - Информация об IP

```bash
dev-utils net info 8.8.8.8
```

### headers - Заголовки

```bash
# Все заголовки
dev-utils net headers https://example.com

# Только основные
dev-utils net headers https://example.com --show common
```

### test - Тестирование URL

```bash
# GET запрос
dev-utils net test https://example.com

# POST запрос
dev-utils net test https://api.example.com --method POST
```

### status - Статусы редиректов

```bash
dev-utils net status https://google.com
```

### download - Скачивание

```bash
# Скачать файл
dev-utils net download https://example.com/file.zip

# С указанием имени
dev-utils net download https://example.com/file.zip -o myfile.zip
```

## Текстовые утилиты

### wc - Подсчёт

```bash
# Весь текст
dev-utils text wc "hello world"

# Только слова
dev-utils text wc "hello world" --words
```

### grep - Поиск

```bash
# Поиск в тексте
dev-utils text grep "error" --text "error occurred"

# Поиск в файле
dev-utils text grep "error" --file app.log

# Регистронезависимый
dev-utils text grep "error" --text "ERROR occurred" --ignore-case
```

### replace - Замена

```bash
# Простая замена
dev-utils text replace "foo" "bar" --text "foo world"

# С regex
dev-utils text replace "\d+" "42" --text "foo 123 bar" --regex
```

### encode - Кодирование

```bash
# Base64
dev-utils text encode "hello" base64

# URL
dev-utils text encode "hello world" url

# Hex
dev-utils text encode "hello" hex
```

### decode - Декодирование

```bash
# Base64
dev-utils text decode aGVsbG8= base64

# URL
dev-utils text decode "hello%20world" url
```

### sort - Сортировка

```bash
# Сортировка строк
dev-utils text sort --text "banana\napple\ncherry"

# В обратном порядке
dev-utils text sort --text "banana\napple\ncherry" --reverse
```

### case - Регистр

```bash
# В нижний регистр
dev-utils text case "HELLO WORLD" --mode lower

# В заглавные
dev-utils text case "hello world" --mode upper

# Title case
dev-utils text case "hello world" --mode title
```

## Криптографические утилиты

### hash - Хеш

```bash
# SHA-256
dev-utils crypto hash "hello"

# SHA-512
dev-utils crypto hash "hello" --algorithm sha512

# Несколько раундов
dev-utils crypto hash "hello" --rounds 1000
```

### hmac - HMAC

```bash
dev-utils crypto hmac "message" "secret_key"
```

### generate-password - Генератор паролей

```bash
# Пароль 16 символов
dev-utils crypto generate-password

# Без спецсимволов
dev-utils crypto generate-password --symbols false
```

### generate-token - Генератор токенов

```bash
# Hex токен
dev-utils crypto generate-token

# Base64 токен
dev-utils crypto generate-token --format base64

# UUID
dev-utils crypto generate-token --format uuid
```

### verify-hash - Проверка хеша

```bash
dev-utils crypto verify-hash "hello" "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
```

### uuid - Генератор UUID

```bash
# UUID v4
dev-utils crypto uuid

# UUID v1
dev-utils crypto uuid --version 1
```

### checksum - Контрольная сумма файла

```bash
dev-utils crypto checksum file.zip
```

## Конфи��урация

### Файл конфигурации

Создайте `.dev-utils.yaml` в домашней директории:

```yaml
# .dev-utils.yaml
defaults:
  algorithm: sha256
  format: json

network:
  timeout: 30
  user-agent: DevTools/1.0
```

## Разработка

### Установка для разработки

```bash
pip install -e ".[dev]"
```

### Запуск тестов

```bash
pytest
```

### Покрытие тестами

```bash
pytest --cov=dev-utils --cov-report=html
```

### Линтинг

```bash
ruff check src/
```

### Типизация

```bash
mypy src/
```

### Форматирование

```bash
ruff format src/
```

## Лицензия

MIT License - подробности в файле [LICENSE](LICENSE)

## Авторы

DevTools - [GitHub](https://github.com/username/dev-utils)