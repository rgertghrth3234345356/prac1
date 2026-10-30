"""Виртуальная файловая система в оперативной памяти."""

import base64
import binascii
import json
from pathlib import Path
from typing import Any


class VFSLoadError(Exception):
    """Ошибка загрузки или проверки образа виртуальной ФС."""


class VFS:
    """Дерево виртуальных каталогов и файлов в оперативной памяти."""

    def __init__(self, root: dict[str, Any]) -> None:
        if not isinstance(root, dict) or root.get("type") != "dir":
            raise VFSLoadError("корневой элемент должен быть каталогом")
        self.root = root
        self.cwd: tuple[str, ...] = ()

    @classmethod
    def from_json(cls, filename: str) -> "VFS":
        """Загрузить JSON-образ и проверить каждый узел дерева."""
        try:
            with Path(filename).open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError as error:
            raise VFSLoadError(f"файл не найден: {filename}") from error
        except json.JSONDecodeError as error:
            raise VFSLoadError(f"некорректный JSON: {error}") from error
        except OSError as error:
            raise VFSLoadError(f"ошибка чтения файла: {error}") from error

        try:
            cls._validate_node(data, "/")
        except (TypeError, ValueError, KeyError) as error:
            raise VFSLoadError(f"неверная структура VFS: {error}") from error
        return cls(data)

    @classmethod
    def _validate_node(cls, node: Any, path: str) -> None:
        """Рекурсивно проверить каталог или файл."""
        if not isinstance(node, dict):
            raise ValueError(f"{path}: узел должен быть JSON-объектом")
        node_type = node.get("type")
        if node_type == "dir":
            children = node.get("children", {})
            if not isinstance(children, dict):
                raise ValueError(f"{path}: поле children должно быть объектом")
            for name, child in children.items():
                invalid_name = (
                    not isinstance(name, str)
                    or not name
                    or name in {".", ".."}
                    or "/" in name
                    or "\\" in name
                    or "\x00" in name
                )
                if invalid_name:
                    raise ValueError(
                        f"{path}: недопустимое имя элемента {name!r}"
                    )
                cls._validate_node(child, f"{path.rstrip('/')}/{name}")
        elif node_type == "file":
            content = node.get("content", "")
            if not isinstance(content, str):
                raise ValueError(
                    f"{path}: содержимое файла должно быть строкой"
                )
            encoding = node.get("encoding", "utf-8")
            if encoding not in {"utf-8", "base64"}:
                raise ValueError(f"{path}: допустимы кодировки utf-8 и base64")
            if encoding == "base64":
                try:
                    base64.b64decode(content, validate=True)
                except (ValueError, binascii.Error) as error:
                    raise ValueError(
                        f"{path}: некорректные данные Base64"
                    ) from error
        else:
            raise ValueError(f"{path}: тип узла должен быть dir или file")

    def normalize(self, path: str | None) -> tuple[str, ...]:
        """Преобразовать путь с учётом текущего каталога."""
        if path is None or path == "":
            return self.cwd
        parts = [] if path.startswith("/") else list(self.cwd)
        for part in path.split("/"):
            if part in {"", "."}:
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return tuple(parts)

    def _node_at(self, path: tuple[str, ...]) -> dict[str, Any]:
        """Найти узел дерева по абсолютному пути-кортежу."""
        node = self.root
        for index, part in enumerate(path):
            if node.get("type") != "dir":
                raise NotADirectoryError("/" + "/".join(path[:index]))
            children = node.get("children", {})
            if part not in children:
                raise FileNotFoundError("/" + "/".join(path))
            node = children[part]
        return node

    def pwd(self) -> str:
        """Вернуть текущий виртуальный путь."""
        return "/" + "/".join(self.cwd) if self.cwd else "/"

    def list_dir(self, path: str | None = None) -> list[tuple[str, str]]:
        """Вернуть отсортированный список элементов каталога."""
        target = self.normalize(path)
        node = self._node_at(target)
        if node.get("type") != "dir":
            raise NotADirectoryError(path or self.pwd())
        return sorted(
            (
                (name, child["type"])
                for name, child in node.get("children", {}).items()
            ),
            key=lambda item: item[0].casefold(),
        )

    def change_dir(self, path: str) -> None:
        """Перейти в существующий виртуальный каталог."""
        target = self.normalize(path)
        node = self._node_at(target)
        if node.get("type") != "dir":
            raise NotADirectoryError(path)
        self.cwd = target

    def read_file(self, path: str) -> str:
        """Прочитать виртуальный файл, декодировав Base64 при необходимости."""
        node = self._node_at(self.normalize(path))
        if node.get("type") != "file":
            raise IsADirectoryError(path)
        content = node.get("content", "")
        if node.get("encoding", "utf-8") == "base64":
            return base64.b64decode(content, validate=True).decode(
                "utf-8", errors="replace"
            )
        return content
