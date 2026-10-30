"""Разбор командной строки эмулятора."""

import shlex


class CommandParseError(ValueError):
    """Ошибка синтаксиса командной строки."""


def parse_command(line: str) -> list[str]:
    """Разбить строку на команду и аргументы с учётом кавычек."""
    try:
        return shlex.split(line, comments=False, posix=True)
    except ValueError as error:
        raise CommandParseError(str(error)) from error
