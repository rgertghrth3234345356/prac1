"""Интерактивная командная оболочка второго этапа."""

from pathlib import Path

from parser import CommandParseError, parse_command


class Shell:
    """Оболочка с REPL, заглушками команд и поддержкой стартовых скриптов."""

    def __init__(self, prompt: str) -> None:
        self.prompt = prompt
        self.should_exit = False

    def repl(self) -> None:
        """Запустить интерактивный цикл."""
        while not self.should_exit:
            try:
                line = input(self.prompt)
            except EOFError:
                print()
                break
            self.execute_line(line)

    def run_script(self, filename: str) -> None:
        """Выполнить скрипт, показывая команды как введённые пользователем."""
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
        """Разобрать и выполнить команду."""
        try:
            args = parse_command(line)
        except CommandParseError as error:
            print(f"Синтаксическая ошибка: {error}")
            return
        if not args:
            return

        command, *argv = args
        handlers = {"ls": self.cmd_ls, "cd": self.cmd_cd, "exit": self.cmd_exit}
        handler = handlers.get(command)
        if handler is None:
            print(f"{command}: команда не найдена")
            return
        try:
            handler(argv)
        except ValueError as error:
            print(f"{command}: {error}")

    @staticmethod
    def require_count(command: str, args: list[str], minimum: int, maximum: int) -> None:
        """Проверить число аргументов команды."""
        if not minimum <= len(args) <= maximum:
            expected = str(minimum) if minimum == maximum else f"от {minimum} до {maximum}"
            raise ValueError(
                f"ожидалось аргументов: {expected}, получено: {len(args)}"
            )

    def cmd_ls(self, args: list[str]) -> None:
        """Заглушка команды ls до реализации VFS на третьем этапе."""
        self.require_count("ls", args, 0, 1)
        print("Команда: ls")
        print(f"Аргументы: {args}")

    def cmd_cd(self, args: list[str]) -> None:
        """Заглушка команды cd до реализации VFS на третьем этапе."""
        self.require_count("cd", args, 0, 1)
        print("Команда: cd")
        print(f"Аргументы: {args}")

    def cmd_exit(self, args: list[str]) -> None:
        """Завершить работу оболочки."""
        self.require_count("exit", args, 0, 0)
        self.should_exit = True
