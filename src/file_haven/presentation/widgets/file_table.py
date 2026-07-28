from collections.abc import Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView

from file_haven.domain import FileRecord
from file_haven.services import format_file_size

INVALID_MODEL_INDEX = QModelIndex()


class FileTableModel(QAbstractTableModel):
    HEADERS = [
        "Name",
        "Folder",
        "Size",
        "Modified",
        "Type",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._records: list[FileRecord] = []

    def rowCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = INVALID_MODEL_INDEX,
    ) -> int:
        if parent.isValid():
            return 0

        return len(self._records)

    def columnCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = INVALID_MODEL_INDEX,
    ) -> int:
        if parent.isValid():
            return 0

        return len(self.HEADERS)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if not index.isValid():
            return None

        record = self._records[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return self._display_value(record, index.column())

        if role == Qt.ItemDataRole.UserRole:
            return record

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
            and 0 <= section < len(self.HEADERS)
        ):
            return self.HEADERS[section]

        return super().headerData(section, orientation, role)

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def sort(
        self,
        column: int,
        order: Qt.SortOrder = Qt.SortOrder.AscendingOrder,
    ) -> None:
        if not 0 <= column < len(self.HEADERS):
            return

        reverse = order == Qt.SortOrder.DescendingOrder

        self.layoutAboutToBeChanged.emit()
        self._records.sort(
            key=lambda record: self._sort_value(record, column),
            reverse=reverse,
        )
        self.layoutChanged.emit()

    def set_files(
        self,
        records: Sequence[FileRecord],
    ) -> None:
        self.beginResetModel()
        self._records = list(records)
        self.endResetModel()

    def add_files(
        self,
        records: Sequence[FileRecord],
    ) -> None:
        if not records:
            return

        first_row = len(self._records)
        last_row = first_row + len(records) - 1

        self.beginInsertRows(QModelIndex(), first_row, last_row)
        self._records.extend(records)
        self.endInsertRows()

    def clear_files(self) -> None:
        self.beginResetModel()
        self._records.clear()
        self.endResetModel()

    def file_at(
        self,
        row: int,
    ) -> FileRecord | None:
        if not 0 <= row < len(self._records):
            return None

        return self._records[row]

    def records(self) -> list[FileRecord]:
        return list(self._records)

    def _display_value(
        self,
        record: FileRecord,
        column: int,
    ) -> str:
        if column == 0:
            return record.name

        if column == 1:
            return str(record.parent_folder)

        if column == 2:
            return format_file_size(record.size_bytes)

        if column == 3:
            return record.modified_at.strftime("%Y-%m-%d %H:%M")

        if column == 4:
            extension = record.extension.removeprefix(".")
            return extension.upper() if extension else "FILE"

        return ""

    def _sort_value(
        self,
        record: FileRecord,
        column: int,
    ) -> object:
        if column == 0:
            return record.name.casefold()

        if column == 1:
            return str(record.parent_folder).casefold()

        if column == 2:
            return record.size_bytes

        if column == 3:
            return record.modified_at.timestamp()

        if column == 4:
            return record.extension.casefold()

        return ""


class FileTable(QTableView):
    HEADERS = FileTableModel.HEADERS

    def __init__(self) -> None:
        super().__init__()

        self._model = FileTableModel()

        self.setObjectName("fileTable")
        self.setModel(self._model)

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

    def model(self) -> FileTableModel:
        return self._model

    def set_files(
        self,
        records: Sequence[FileRecord],
    ) -> None:
        self._model.set_files(records)
        self._sort_if_enabled()

    def add_file(
        self,
        record: FileRecord,
    ) -> None:
        self.add_files([record])

    def add_files(
        self,
        records: Sequence[FileRecord],
    ) -> None:
        self._model.add_files(records)
        self._sort_if_enabled()

    def clear_files(self) -> None:
        self._model.clear_files()

    def file_at(
        self,
        row: int,
    ) -> FileRecord | None:
        return self._model.file_at(row)

    def records(self) -> list[FileRecord]:
        return self._model.records()

    def _sort_if_enabled(self) -> None:
        if self.isSortingEnabled():
            header = self.horizontalHeader()
            self.sortByColumn(
                header.sortIndicatorSection(),
                header.sortIndicatorOrder(),
            )
