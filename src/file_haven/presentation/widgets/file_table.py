from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from file_haven.domain import FileRecord
from file_haven.services import format_file_size


class SortableTableItem(QTableWidgetItem):
    """Sort using a hidden value instead of the displayed text."""

    def __lt__(self, other: "QTableWidgetItem") -> bool:
        left = self.data(Qt.ItemDataRole.UserRole)
        right = other.data(Qt.ItemDataRole.UserRole)

        if left is not None and right is not None:
            return left < right

        return super().__lt__(other)


class FileTable(QTableWidget):
    HEADERS = [
        "Name",
        "Folder",
        "Size",
        "Modified",
        "Type",
    ]

    def __init__(self) -> None:
        super().__init__(0, len(self.HEADERS))

        self.setObjectName("fileTable")
        self.setHorizontalHeaderLabels(self.HEADERS)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setStretchLastSection(False)

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def add_file(self, record: FileRecord) -> None:
        sorting = self.isSortingEnabled()
        self.setSortingEnabled(False)

        row = self.rowCount()
        self.insertRow(row)

        name_item = QTableWidgetItem(record.name)
        folder_item = QTableWidgetItem(str(record.parent_folder))

        size_item = SortableTableItem(format_file_size(record.size_bytes))
        size_item.setData(
            Qt.ItemDataRole.UserRole,
            record.size_bytes,
        )

        modified_item = SortableTableItem(record.modified_at.strftime("%Y-%m-%d %H:%M"))
        modified_item.setData(
            Qt.ItemDataRole.UserRole,
            record.modified_at.timestamp(),
        )

        extension = record.extension.removeprefix(".")
        type_item = QTableWidgetItem(extension.upper() if extension else "FILE")

        name_item.setData(
            Qt.ItemDataRole.UserRole,
            str(record.path),
        )

        self.setItem(row, 0, name_item)
        self.setItem(row, 1, folder_item)
        self.setItem(row, 2, size_item)
        self.setItem(row, 3, modified_item)
        self.setItem(row, 4, type_item)

        self.setSortingEnabled(sorting)

    def clear_files(self) -> None:
        self.setRowCount(0)
