from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from send2trash import send2trash


@dataclass(frozen=True, slots=True)
class TrashResult:
    moved: tuple[Path, ...]
    failed: tuple[Path, ...]


class TrashService:
    """Safely move files to the operating system's Trash."""

    def move_files(self, paths: Iterable[Path]) -> TrashResult:
        moved: list[Path] = []
        failed: list[Path] = []

        for path in paths:
            try:
                if not path.is_file():
                    failed.append(path)
                    continue

                send2trash(str(path))
                moved.append(path)
            except OSError:
                failed.append(path)

        return TrashResult(
            moved=tuple(moved),
            failed=tuple(failed),
        )
