import os
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QItemSelectionModel
from PySide6.QtWidgets import QApplication, QMessageBox

from file_haven.domain import DuplicateGroup, FileRecord
from file_haven.presentation import main_window
from file_haven.presentation.main_window import MainWindow
from file_haven.services import TrashResult

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _app() -> QApplication:
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


def _record(
    path: str,
    size_bytes: int,
    modified_at: datetime,
) -> FileRecord:
    return FileRecord(
        path=Path(path),
        size_bytes=size_bytes,
        modified_at=modified_at,
    )


def _window(
    tmp_path: Path,
    monkeypatch,
) -> MainWindow:
    monkeypatch.setattr(main_window.Path, "home", staticmethod(lambda: tmp_path))

    return MainWindow()


def test_move_to_trash_button_follows_file_table_selection(
    tmp_path: Path,
    monkeypatch,
) -> None:
    application = _app()
    window = _window(tmp_path, monkeypatch)
    record = _record("/files/example.txt", 1, datetime(2024, 1, 1, 10, 0))

    window._file_table.setSortingEnabled(False)
    window._scan_results = [record]
    window._show_files([record])

    assert not window._trash_button.isEnabled()

    window._file_table.selectRow(0)
    application.processEvents()

    assert window._trash_button.isEnabled()

    window._file_table.clearSelection()
    application.processEvents()

    assert not window._trash_button.isEnabled()

    window.close()


def test_move_selected_to_trash_updates_results_duplicates_and_reports_failures(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _app()
    window = _window(tmp_path, monkeypatch)
    first = _record("/files/first.txt", 1, datetime(2024, 1, 1, 10, 0))
    second = _record("/files/second.txt", 1, datetime(2024, 1, 2, 10, 0))
    third = _record("/files/third.txt", 1, datetime(2024, 1, 3, 10, 0))
    warnings: list[tuple[str, str]] = []

    class FakeTrashService:
        moved_paths: tuple[Path, ...] = ()

        def move_files(self, paths) -> TrashResult:
            self.moved_paths = tuple(paths)

            return TrashResult(
                moved=(first.path,),
                failed=(second.path,),
            )

    def fake_warning(
        parent,
        title: str,
        text: str,
        *args,
    ) -> QMessageBox.StandardButton:
        warnings.append((title, text))

        if title == "Move to Trash":
            return QMessageBox.StandardButton.Yes

        return QMessageBox.StandardButton.Ok

    trash_service = FakeTrashService()

    monkeypatch.setattr(main_window.QMessageBox, "warning", fake_warning)
    window._trash_service = trash_service
    window._file_table.setSortingEnabled(False)
    window._scan_results = [first, second, third]
    window._duplicate_groups = [
        DuplicateGroup(
            fingerprint="same-content",
            files=(first, second, third),
        )
    ]
    window._show_files([first, second, third])

    selection_model = window._file_table.selectionModel()

    assert selection_model is not None

    selection_model.select(
        window._file_table.model().index(0, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )
    selection_model.select(
        window._file_table.model().index(1, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )

    window._move_selected_to_trash()

    assert warnings[0][0] == "Move to Trash"
    assert "Move 2 selected files" in warnings[0][1]
    assert trash_service.moved_paths == (first.path, second.path)
    assert window._scan_results == [second, third]
    assert window._duplicate_groups == [
        DuplicateGroup(
            fingerprint="same-content",
            files=(second, third),
        )
    ]
    assert window._file_table.records() == [second, third]
    assert warnings[1][0] == "Some Files Were Not Moved"
    assert not window._trash_button.isEnabled()

    window.close()
