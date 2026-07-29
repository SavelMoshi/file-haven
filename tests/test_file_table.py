import os
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QItemSelectionModel, QSortFilterProxyModel, Qt

from file_haven.domain import FileRecord
from file_haven.presentation.widgets.file_table import FileTable, FileTableModel


def _app() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    application = QApplication.instance()

    if application is None:
        QApplication([])


def test_model_returns_record_at_row(tmp_path: Path) -> None:
    record = FileRecord(
        path=tmp_path / "example.txt",
        size_bytes=128,
        modified_at=datetime(2026, 7, 29, 12, 0),
    )

    model = FileTableModel()
    model.set_files([record])

    assert model.record_at(0) == record
    assert model.record_at(999) is None


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


def test_file_table_uses_table_view() -> None:
    _app()
    from PySide6.QtWidgets import QTableView, QTableWidget

    table = FileTable()

    assert isinstance(table, QTableView)
    assert not isinstance(table, QTableWidget)


def test_file_table_selected_records_returns_empty_for_no_selection() -> None:
    _app()
    table = FileTable()
    record = _record("/files/example.txt", 1, datetime(2024, 1, 1, 10, 0))

    table.set_files([record])

    assert table.selected_records() == []


def test_file_table_selected_records_returns_selected_record() -> None:
    _app()
    table = FileTable()
    record = _record("/files/example.txt", 1, datetime(2024, 1, 1, 10, 0))

    table.set_files([record])
    table.selectRow(0)

    assert table.selected_records() == [record]


def test_file_table_selected_records_returns_multiple_selected_records() -> None:
    _app()
    first = _record("/files/a.txt", 1, datetime(2024, 1, 1, 10, 0))
    second = _record("/files/b.txt", 2, datetime(2024, 1, 2, 10, 0))
    third = _record("/files/c.txt", 3, datetime(2024, 1, 3, 10, 0))
    table = FileTable()
    table.setSortingEnabled(False)

    table.set_files([first, second, third])
    selection_model = table.selectionModel()

    assert selection_model is not None

    selection_model.select(
        table.model().index(0, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )
    selection_model.select(
        table.model().index(2, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )

    assert table.selected_records() == [first, third]


def test_file_table_selected_records_returns_record_at_sorted_view_row() -> None:
    _app()
    small = _record("/files/small.bin", 9, datetime(2024, 1, 1, 10, 0))
    medium = _record("/files/medium.bin", 100, datetime(2024, 1, 1, 10, 0))
    large = _record("/files/large.bin", 1000, datetime(2024, 1, 1, 10, 0))
    table = FileTable()

    table.set_files([small, large, medium])
    table.sortByColumn(2, Qt.SortOrder.DescendingOrder)
    table.selectRow(0)

    assert table.selected_records() == [large]


def test_file_table_selected_records_maps_proxy_selection_to_source_record() -> None:
    _app()
    first = _record("/files/b.txt", 1, datetime(2024, 1, 1, 10, 0))
    second = _record("/files/a.txt", 2, datetime(2024, 1, 2, 10, 0))
    table = FileTable()
    table.setSortingEnabled(False)
    table.set_files([first, second])

    proxy_model = QSortFilterProxyModel()
    proxy_model.setSourceModel(table.model())
    proxy_model.sort(0, Qt.SortOrder.AscendingOrder)
    table.setModel(proxy_model)

    table.selectRow(0)

    assert table.selected_records() == [second]


def test_file_table_selected_records_returns_empty_after_selection_is_invalidated() -> None:
    _app()
    table = FileTable()
    record = _record("/files/example.txt", 1, datetime(2024, 1, 1, 10, 0))

    table.set_files([record])
    table.selectRow(0)
    table.clear_files()

    assert table.selected_records() == []


def test_model_row_count_and_displayed_data() -> None:
    record = _record(
        "/home/example/Documents/report.txt",
        1536,
        datetime(2024, 1, 2, 3, 4),
    )
    model = FileTableModel()

    model.set_files([record])

    assert model.rowCount() == 1
    assert model.columnCount() == 5
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Name"
    assert model.data(model.index(0, 0)) == "report.txt"
    assert model.data(model.index(0, 1)) == "/home/example/Documents"
    assert model.data(model.index(0, 2)) == "1.5 KB"
    assert model.data(model.index(0, 3)) == "2024-01-02 03:04"
    assert model.data(model.index(0, 4)) == "TXT"
    assert model.data(model.index(0, 0), Qt.ItemDataRole.UserRole) is record


def test_model_sorts_file_size_numerically() -> None:
    small = _record("/files/small.bin", 9, datetime(2024, 1, 1, 10, 0))
    medium = _record("/files/medium.bin", 100, datetime(2024, 1, 1, 10, 0))
    large = _record("/files/large.bin", 1000, datetime(2024, 1, 1, 10, 0))
    model = FileTableModel()

    model.set_files([large, small, medium])
    model.sort(2, Qt.SortOrder.AscendingOrder)

    assert model.records() == [small, medium, large]


def test_model_sorts_modified_date_chronologically() -> None:
    oldest = _record("/files/old.txt", 1, datetime(2023, 5, 1, 10, 0))
    newest = _record("/files/new.txt", 1, datetime(2025, 5, 1, 10, 0))
    middle = _record("/files/middle.txt", 1, datetime(2024, 5, 1, 10, 0))
    model = FileTableModel()

    model.set_files([middle, newest, oldest])
    model.sort(3, Qt.SortOrder.DescendingOrder)

    assert model.records() == [newest, middle, oldest]


def test_model_inserts_files_in_batches() -> None:
    first = _record("/files/first.txt", 1, datetime(2024, 1, 1, 10, 0))
    second = _record("/files/second.txt", 2, datetime(2024, 1, 2, 10, 0))
    third = _record("/files/third.txt", 3, datetime(2024, 1, 3, 10, 0))
    model = FileTableModel()

    model.add_files([first])
    model.add_files([second, third])

    assert model.rowCount() == 3
    assert model.records() == [first, second, third]


def test_model_clears_files() -> None:
    model = FileTableModel()
    model.set_files(
        [
            _record("/files/one.txt", 1, datetime(2024, 1, 1, 10, 0)),
            _record("/files/two.txt", 2, datetime(2024, 1, 2, 10, 0)),
        ]
    )

    model.clear_files()

    assert model.rowCount() == 0
    assert model.records() == []
