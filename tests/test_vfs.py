"""Проверки операций виртуальной файловой системы."""

import unittest

from vfs import VFS


class VFSTests(unittest.TestCase):
    def setUp(self):
        self.vfs = VFS.from_json("vfs/full.json")

    def test_root_listing(self):
        self.assertEqual(
            [name for name, _ in self.vfs.list_dir()],
            ["data.bin", "etc", "home", "README.txt"],
        )

    def test_change_directory_and_parent(self):
        self.vfs.change_dir("home/student/projects/demo")
        self.assertEqual(self.vfs.pwd(), "/home/student/projects/demo")
        self.vfs.change_dir("../..")
        self.assertEqual(self.vfs.pwd(), "/home/student")

    def test_read_text_file(self):
        self.assertIn("памяти", self.vfs.read_file("home/student/notes.txt"))

    def test_read_base64_file(self):
        self.assertEqual(self.vfs.read_file("data.bin"), "\x00\x01\x02\ufffd")

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.vfs.read_file("missing.txt")


if __name__ == "__main__":
    unittest.main()
