"""Консольный вывод и логирование."""

import logging
import sys
from rich.console import Console
from rich.logging import RichHandler

console = Console(stderr=False)
error_console = Console(stderr=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

logger = logging.getLogger("devtools")


def setup_logging(verbose: bool = False) -> None:
    """Настроить уровень логирования."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
