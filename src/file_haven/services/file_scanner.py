from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from file_haven.domain import FileRecord


class FileScanner:
    """Recursively scan a folder and yield file records."""

    def scan(self, root: Path) -> Iterator[FileRecord]:
        if not root.exists():
            raise FileNotFoundError(root)

        if not root.is_dir():
            raise NotADirectoryError(root)

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            try:
                stats = path.stat()
            except (PermissionError, FileNotFoundError, OSError):
                continue

            yield FileRecord(
                path=path,
                size_bytes=stats.st_size,
                modified_at=datetime.fromtimestamp(stats.st_mtime),
            )
