"""Точка входа в финальную версию эмулятора UNIX-оболочки."""

import argparse
import getpass
import socket
import sys
from pathlib import Path

from shell import Shell
from vfs import VFS, VFSLoadError


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        description=(
            "Эмулятор UNIX-подобной оболочки с виртуальной ФС в памяти."
        )
    )
    parser.add_argument(
        "--vfs", required=True, help="Путь к JSON-образу VFS."
    )
    parser.add_argument(
        "--prompt", default=None, help="Пользовательское приглашение REPL."
    )
    parser.add_argument(
        "--script", default=None, help="Стартовый скрипт перед REPL."
    )
    return parser


def main() -> int:
    """Загрузить конфигурацию и VFS, выполнить скрипт, запустить REPL."""
    args = build_parser().parse_args()
    username = getpass.getuser()
    hostname = socket.gethostname()
    prompt = args.prompt
    if prompt is None:
        prompt = f"{username}@{hostname}:~$ "

    print("=== Конфигурация эмулятора ===")
    print(f"Путь к VFS: {Path(args.vfs).resolve()}")
    print(f"Приглашение: {prompt!r}")
    script_path = Path(args.script).resolve() if args.script else "(не задан)"
    print(f"Стартовый скрипт: {script_path}")
    print("==============================")

    try:
        vfs = VFS.from_json(args.vfs)
    except VFSLoadError as error:
        print(f"Ошибка загрузки VFS: {error}", file=sys.stderr)
        return 1

    shell = Shell(vfs, prompt)
    if args.script:
        try:
            shell.run_script(args.script)
        except OSError as error:
            print(
                f"Ошибка чтения стартового скрипта: {error}",
                file=sys.stderr,
            )
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
