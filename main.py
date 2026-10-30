"""Точка входа в эмулятор оболочки первого этапа."""

import getpass
import socket

from shell import Shell


def main() -> int:
    """Сформировать системное приглашение и запустить REPL."""
    username = getpass.getuser()
    hostname = socket.gethostname()
    prompt = f"{username}@{hostname}:~$ "
    Shell(prompt).repl()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
