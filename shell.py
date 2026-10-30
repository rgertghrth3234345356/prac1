"""Интерактивная командная оболочка первого этапа."""

from parser import CommandParseError, parse_command


class Shell:
    """Минимальная оболочка с заглушками команд ls и cd."""

    def __init__(self, prompt: str) -> None:
        self.prompt = prompt
        self.should_exit = False

    def repl(self) -> None:
        """Запустить цикл чтения и выполнения команд."""
        while not self.should_exit:
            try:
                line = input(self.prompt)
            except EOFError:
                print()
                break
            self.execute_line(line)

    def execute_line(self, line: str) -> None:
        """Разобрать строку и вызвать соответствующую команду."""
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
        """Проверить допустимое количество аргументов."""
        if not minimum <= len(args) <= maximum:
            if minimum == maximum:
                expected = str(minimum)
            else:
                expected = f"от {minimum} до {maximum}"
            raise ValueError(
                f"ожидалось аргументов: {expected}, получено: {len(args)}"
            )

    def cmd_ls(self, args: list[str]) -> None:
        """Заглушка ls: вывести имя команды и переданные аргументы."""
        self.require_count("ls", args, 0, 1)
        print("Команда: ls")
        print(f"Аргументы: {args}")

    def cmd_cd(self, args: list[str]) -> None:
        """Заглушка cd: вывести имя команды и переданные аргументы."""
        self.require_count("cd", args, 0, 1)
        print("Команда: cd")
        print(f"Аргументы: {args}")

    def cmd_exit(self, args: list[str]) -> None:
        """Завершить работу оболочки."""
        self.require_count("exit", args, 0, 0)
        self.should_exit = True
