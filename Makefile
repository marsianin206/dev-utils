.PHONY: install test lint format mypy clean build release help

help:
	@echo "Доступные команды:"
	@echo "  make install    - установить пакет в режиме разработки"
	@echo "  make test     - запустить тесты"
	@echo "  make lint    - проверить код линтером"
	@echo "  make format  - форматировать код"
	@echo "  make mypy   - проверить типы"
	@echo "  make clean  - очистить временные файлы"
	@echo "  make build - собрать пакет"
	@echo "  make release - опубликовать пакет"

install:
	pip install -e ".[dev]"

test:
	pytest -v

test-cov:
	pytest --cov=devtools --cov-report=html --cov-report=term

test-fast:
	pytest -v -x --ignore=tests/test_integration.py

lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

format:
	ruff format src/ tests/

mypy:
	mypy src/

mypy-strict:
	mypy src/ --strict

clean:
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
	rm -rf .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.egg-info" -delete 2>/dev/null || true

build:
	pip install build
	python -m build

build-wheel:
	pip install build
	python -m build --wheel

release:
	@echo "Убедитесь, что версия обновлена в pyproject.toml"
	@echo "然后运行:"
	@echo "  make build"
	@echo "  pip install twine"
	@echo "  python -m twine upload dist/*"

all: install test lint mypy

.DEFAULT_GOAL := help