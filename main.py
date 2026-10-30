"""Точка входа в эмулятор оболочки второго этапа."""

import argparse
import getpass
import socket
import sys
from pathlib import Path

from shell import Shell


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер параметров запуска."""
    parser = argparse.ArgumentParser(
        description="Учебный эмулятор UNIX-подобной командной оболочки."
    )
    parser.add_argument("--vfs", required=True, help="Путь к образу VFS.")
    parser.add_argument("--prompt", default=None, help="Пользовательское приглашение.")
    parser.add_argument("--script", default=None, help="Путь к стартовому скрипту.")
    return parser


def main() -> int:
    """Прочитать конфигурацию, выполнить скрипт и запустить REPL."""
    args = build_parser().parse_args()
    username = getpass.getuser()
    hostname = socket.gethostname()
    prompt = args.prompt if args.prompt is not None else f"{username}@{hostname}:~$ "

    print("=== Конфигурация эмулятора ===")
    print(f"Путь к VFS: {Path(args.vfs).resolve()}")
    print(f"Приглашение: {prompt!r}")
    script_path = Path(args.script).resolve() if args.script else "(не задан)"
    print(f"Стартовый скрипт: {script_path}")
    print("==============================")

    shell = Shell(prompt)
    if args.script:
        try:
            shell.run_script(args.script)
        except OSError as error:
            print(f"Ошибка чтения стартового скрипта: {error}", file=sys.stderr)
            return 1
        if shell.should_exit:
            return 0

    try:
        shell.repl()
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
