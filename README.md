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
pip install devtools
```

### Из исходников

```bash
git clone https://github.com/username/devtools.git
cd devtools
pip install -e ".[dev]"
```

## Быстрый старт

```bash
# Показать справку
devtools --help

# Показать версию
devtools version

# Список команд
devtools help
```

## Файловые утилиты

### list - Список файлов

```bash
# Простой список
devtools file list

# С размером файлов
devtools file list --size

# Древовидный вид
devtools file list --tree

# Скрытые файлы
devtools file list --hidden

# С ограничением
devtools file list --limit 20
```

### find - Поиск файлов

```bash
# Найти все txt файлы
devtools file find "*.txt"

# Только имена
devtools file find "*.py" --name-only
```

### hash - Хеш файла

```bash
# SHA-256 хеш
devtools file hash file.txt

# MD5 хеш
devtools file hash file.txt --algorithm md5

# SHA-512 хеш
devtools file hash file.txt --algorithm sha512
```

### size - Размер файла

```bash
# Человекочитаемый формат
devtools file size myfolder --human

# Точный размер в байтах
devtools file size myfolder
```

### diff - Сравнение файлов

```bash
devtools file diff file1.txt file2.txt
```

## Работа с данными

### validate - Валидация JSON

```bash
devtools data validate config.json
```

### format - Форматирование JSON

```bash
# Отступ 2 пробела
devtools data format config.json

# Сортировать ключи
devtools data format config.json --sort
```

### minify - Минификация JSON

```bash
devtools data minify config.json

# С сохранением в файл
devtools data minify config.json --output config.min.json
```

### query - Запрос к JSON

```bash
# Получить ключ
devtools data query config.json "database.host"

# Вложенные ключи
devtools data query config.json "users.0.name"
```

### convert - Конвертация форматов

```bash
# JSON в YAML
devtools data convert config.json yaml

# YAML в JSON
devtools data convert config.yaml json
```

### csv2json - CSV в JSON

```bash
devtools data csv2json data.csv

# С разделителем
devtools data csv2json data.csv --delimiter ";"
```

### json2csv - JSON в CSV

```bash
devtools data json2csv data.json
```

## Сетевые утилиты

### ip - Внешний IP

```bash
# JSON формат
devtools net ip

# Простой текст
devtools net ip --format text
```

### info - Информация об IP

```bash
devtools net info 8.8.8.8
```

### headers - Заголовки

```bash
# Все заголовки
devtools net headers https://example.com

# Только основные
devtools net headers https://example.com --show common
```

### test - Тестирование URL

```bash
# GET запрос
devtools net test https://example.com

# POST запрос
devtools net test https://api.example.com --method POST
```

### status - Статусы редиректов

```bash
devtools net status https://google.com
```

### download - Скачивание

```bash
# Скачать файл
devtools net download https://example.com/file.zip

# С указанием имени
devtools net download https://example.com/file.zip -o myfile.zip
```

## Текстовые утилиты

### wc - Подсчёт

```bash
# Весь текст
devtools text wc "hello world"

# Только слова
devtools text wc "hello world" --words
```

### grep - Поиск

```bash
# Поиск в тексте
devtools text grep "error" --text "error occurred"

# Поиск в файле
devtools text grep "error" --file app.log

# Регистронезависимый
devtools text grep "error" --text "ERROR occurred" --ignore-case
```

### replace - Замена

```bash
# Простая замена
devtools text replace "foo" "bar" --text "foo world"

# С regex
devtools text replace "\d+" "42" --text "foo 123 bar" --regex
```

### encode - Кодирование

```bash
# Base64
devtools text encode "hello" base64

# URL
devtools text encode "hello world" url

# Hex
devtools text encode "hello" hex
```

### decode - Декодирование

```bash
# Base64
devtools text decode aGVsbG8= base64

# URL
devtools text decode "hello%20world" url
```

### sort - Сортировка

```bash
# Сортировка строк
devtools text sort --text "banana\napple\ncherry"

# В обратном порядке
devtools text sort --text "banana\napple\ncherry" --reverse
```

### case - Регистр

```bash
# В нижний регистр
devtools text case "HELLO WORLD" --mode lower

# В заглавные
devtools text case "hello world" --mode upper

# Title case
devtools text case "hello world" --mode title
```

## Криптографические утилиты

### hash - Хеш

```bash
# SHA-256
devtools crypto hash "hello"

# SHA-512
devtools crypto hash "hello" --algorithm sha512

# Несколько раундов
devtools crypto hash "hello" --rounds 1000
```

### hmac - HMAC

```bash
devtools crypto hmac "message" "secret_key"
```

### generate-password - Генератор паролей

```bash
# Пароль 16 символов
devtools crypto generate-password

# Без спецсимволов
devtools crypto generate-password --symbols false
```

### generate-token - Генератор токенов

```bash
# Hex токен
devtools crypto generate-token

# Base64 токен
devtools crypto generate-token --format base64

# UUID
devtools crypto generate-token --format uuid
```

### verify-hash - Проверка хеша

```bash
devtools crypto verify-hash "hello" "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
```

### uuid - Генератор UUID

```bash
# UUID v4
devtools crypto uuid

# UUID v1
devtools crypto uuid --version 1
```

### checksum - Контрольная сумма файла

```bash
devtools crypto checksum file.zip
```

## Конфи��урация

### Файл конфигурации

Создайте `.devtools.yaml` в домашней директории:

```yaml
# .devtools.yaml
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
pytest --cov=devtools --cov-report=html
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

DevTools - [GitHub](https://github.com/username/devtools)