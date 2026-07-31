from pathlib import Path

from file_haven.services import FileRevealService, file_reveal_service


def test_returns_false_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.txt"

    result = FileRevealService().reveal(missing_file)

    assert result is False


def test_uses_macos_reveal_method(
    tmp_path: Path,
    monkeypatch,
) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text("test")

    revealed_paths: list[Path] = []

    monkeypatch.setattr(
        file_reveal_service.sys,
        "platform",
        "darwin",
    )
    monkeypatch.setattr(
        FileRevealService,
        "_reveal_on_macos",
        lambda self, path: revealed_paths.append(path) or True,
    )

    result = FileRevealService().reveal(file_path)

    assert result is True
    assert revealed_paths == [file_path.absolute()]


def test_uses_explorer_on_windows(
    tmp_path: Path,
    monkeypatch,
) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text("test")

    commands: list[list[str]] = []

    monkeypatch.setattr(
        file_reveal_service.sys,
        "platform",
        "win32",
    )
    monkeypatch.setattr(
        file_reveal_service.subprocess,
        "Popen",
        lambda command: commands.append(command),
    )

    result = FileRevealService().reveal(file_path)

    assert result is True
    assert commands == [
        [
            "explorer.exe",
            "/select,",
            str(file_path.absolute()),
        ]
    ]


def test_opens_parent_folder_on_linux(
    tmp_path: Path,
    monkeypatch,
) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text("test")

    commands: list[list[str]] = []

    monkeypatch.setattr(
        file_reveal_service.sys,
        "platform",
        "linux",
    )
    monkeypatch.setattr(
        file_reveal_service.subprocess,
        "run",
        lambda command, check: commands.append(command),
    )

    result = FileRevealService().reveal(file_path)

    assert result is True
    assert commands == [["xdg-open", str(file_path.absolute().parent)]]
