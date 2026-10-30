"""Оболочка, работающая с виртуальной файловой системой."""

from pathlib import Path

from parser import CommandParseError, parse_command
from vfs import VFS


class Shell:
    """REPL и команды для работы с виртуальным деревом файлов."""

    def __init__(self, vfs: VFS, prompt: str) -> None:
        self.vfs = vfs
        self.prompt = prompt
        self.should_exit = False

    def repl(self) -> None:
        """Запустить интерактивный цикл оболочки."""
        while not self.should_exit:
            try:
                line = input(self.prompt)
            except EOFError:
                print()
                break
            self.execute_line(line)

    def run_script(self, filename: str) -> None:
        """Выполнить команды из файла, отображая их в терминале."""
        with Path(filename).open("r", encoding="utf-8") as script:
            for raw_line in script:
                line = raw_line.rstrip("\r\n")
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                print(f"{self.prompt}{line}")
                self.execute_line(line)
                if self.should_exit:
                    break

    def execute_line(self, line: str) -> None:
        """Разобрать команду, проверить аргументы и выполнить её."""
        try:
            args = parse_command(line)
        except CommandParseError as error:
            print(f"Синтаксическая ошибка: {error}")
            return
        if not args:
            return

        command, *argv = args
        handlers = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "pwd": self.cmd_pwd,
            "cat": self.cmd_cat,
            "exit": self.cmd_exit,
        }
        handler = handlers.get(command)
        if handler is None:
            print(f"{command}: команда не найдена")
            return
        try:
            handler(argv)
        except (
            FileNotFoundError,
            NotADirectoryError,
            IsADirectoryError,
        ) as error:
            print(f"{command}: {error}")
        except ValueError as error:
            print(f"{command}: {error}")

    @staticmethod
    def require_count(args: list[str], minimum: int, maximum: int) -> None:
        """Проверить допустимое количество аргументов команды."""
        if not minimum <= len(args) <= maximum:
            if minimum == maximum:
                expected = str(minimum)
            else:
                expected = f"от {minimum} до {maximum}"
            raise ValueError(
                "ожидалось аргументов: "
                f"{expected}, получено: {len(args)}"
            )

    def cmd_ls(self, args: list[str]) -> None:
        """Показать содержимое указанного или текущего каталога."""
        self.require_count(args, 0, 1)
        entries = self.vfs.list_dir(args[0] if args else None)
        if not entries:
            print("(пусто)")
            return
        for name, node_type in entries:
            print(f"{name}{'/' if node_type == 'dir' else ''}")

    def cmd_cd(self, args: list[str]) -> None:
        """Изменить каталог; без аргумента перейти в корень."""
        self.require_count(args, 0, 1)
        self.vfs.change_dir(args[0] if args else "/")

    def cmd_pwd(self, args: list[str]) -> None:
        """Вывести текущий виртуальный путь."""
        self.require_count(args, 0, 0)
        print(self.vfs.pwd())

    def cmd_cat(self, args: list[str]) -> None:
        """Вывести содержимое одного или нескольких файлов VFS."""
        self.require_count(args, 1, 100)
        for index, filename in enumerate(args):
            if index:
                print()
            content = self.vfs.read_file(filename)
            print(content, end="" if content.endswith("\n") else "\n")

    def cmd_exit(self, args: list[str]) -> None:
        """Завершить работу эмулятора."""
        self.require_count(args, 0, 0)
        self.should_exit = True
