"""Проверки парсера командной строки."""

import unittest

from parser import CommandParseError, parse_command


class ParserTests(unittest.TestCase):
    def test_quotes(self):
        self.assertEqual(
            parse_command('cat "my file.txt"'),
            ["cat", "my file.txt"],
        )

    def test_unclosed_quote(self):
        with self.assertRaises(CommandParseError):
            parse_command('cat "unfinished')


if __name__ == "__main__":
    unittest.main()
