from pathlib import Path

from file_haven.services import TrashService


def test_moves_existing_file_to_trash(
    tmp_path: Path,
    monkeypatch,
) -> None:
    file_path = tmp_path / "unused.txt"
    file_path.write_text("temporary file")

    moved_paths: list[str] = []

    monkeypatch.setattr(
        "file_haven.services.trash_service.send2trash",
        moved_paths.append,
    )

    result = TrashService().move_files([file_path])

    assert result.moved == (file_path,)
    assert result.failed == ()
    assert moved_paths == [str(file_path)]


def test_reports_missing_file_as_failed(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing.txt"

    result = TrashService().move_files([missing_path])

    assert result.moved == ()
    assert result.failed == (missing_path,)


def test_continues_when_one_file_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("first")
    second.write_text("second")

    def fake_send_to_trash(path: str) -> None:
        if path == str(first):
            raise OSError("Unable to move file")

    monkeypatch.setattr(
        "file_haven.services.trash_service.send2trash",
        fake_send_to_trash,
    )

    result = TrashService().move_files([first, second])

    assert result.moved == (second,)
    assert result.failed == (first,)
