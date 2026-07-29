from datetime import datetime
from pathlib import Path

from file_haven.domain import FileRecord
from file_haven.services import DuplicateFinder


def create_record(path: Path) -> FileRecord:
    stats = path.stat()

    return FileRecord(
        path=path,
        size_bytes=stats.st_size,
        modified_at=datetime.fromtimestamp(stats.st_mtime),
    )


def test_finds_files_with_identical_contents(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("duplicate content")
    second.write_text("duplicate content")

    finder = DuplicateFinder()
    groups = finder.find(
        [
            create_record(first),
            create_record(second),
        ]
    )

    assert len(groups) == 1
    assert len(groups[0].files) == 2
    assert groups[0].reclaimable_bytes == first.stat().st_size


def test_ignores_same_size_files_with_different_contents(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("abcd")
    second.write_text("wxyz")

    finder = DuplicateFinder()
    groups = finder.find(
        [
            create_record(first),
            create_record(second),
        ]
    )

    assert groups == []


def test_ignores_files_with_unique_sizes(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("small")
    second.write_text("considerably larger")

    finder = DuplicateFinder()
    groups = finder.find(
        [
            create_record(first),
            create_record(second),
        ]
    )

    assert groups == []
