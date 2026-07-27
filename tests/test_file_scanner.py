from pathlib import Path

from file_haven.services import FileScanner


def test_scanner_finds_files(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("hello")
    (tmp_path / "two.txt").write_text("world")

    scanner = FileScanner()

    results = list(scanner.scan(tmp_path))

    assert len(results) == 2


def test_scanner_recurses_into_subdirectories(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "docs"
    folder.mkdir()

    (folder / "file.txt").write_text("hello")

    scanner = FileScanner()

    results = list(scanner.scan(tmp_path))

    assert len(results) == 1
    assert results[0].name == "file.txt"


def test_scanner_raises_for_missing_folder() -> None:
    scanner = FileScanner()

    missing = Path("/definitely/does/not/exist")

    try:
        list(scanner.scan(missing))
    except FileNotFoundError:
        return

    assert False
