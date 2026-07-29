from PySide6.QtCore import QObject, Signal, Slot

from file_haven.domain import DuplicateGroup, FileRecord
from file_haven.services import DuplicateFinder


class DuplicateWorker(QObject):
    """Find duplicate files outside the main UI thread."""

    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, records: list[FileRecord]) -> None:
        super().__init__()

        self._records = records
        self._finder = DuplicateFinder()

    @Slot()
    def run(self) -> None:
        try:
            groups: list[DuplicateGroup] = self._finder.find(self._records)
        except Exception as error:
            self.failed.emit(str(error))
            return

        self.completed.emit(groups)
