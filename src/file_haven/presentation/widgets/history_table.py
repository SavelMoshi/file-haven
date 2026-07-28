from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from file_haven.domain import ScanHistoryRecord


class HistoryTable(QTableWidget):
    HEADERS = [
        "Folder",
        "Files",
        "Scanned",
    ]

    def __init__(self) -> None:
        super().__init__(0, len(self.HEADERS))

        self.setObjectName("historyTable")
        self.setHorizontalHeaderLabels(self.HEADERS)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)

        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )

    def show_records(
        self,
        records: list[ScanHistoryRecord],
    ) -> None:
        self.setRowCount(0)

        for record in records:
            row = self.rowCount()
            self.insertRow(row)

            self.setItem(
                row,
                0,
                QTableWidgetItem(str(record.folder)),
            )
            self.setItem(
                row,
                1,
                QTableWidgetItem(f"{record.file_count:,}"),
            )
            self.setItem(
                row,
                2,
                QTableWidgetItem(record.scanned_at.strftime("%Y-%m-%d %H:%M")),
            )
