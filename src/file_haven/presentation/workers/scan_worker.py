from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from file_haven.services import FileScanner


class ScanWorker(QObject):
    file_found = Signal(object)
    progress_updated = Signal(int)
    finished = Signal()
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, folder: Path) -> None:
        super().__init__()

        self._folder = folder
        self._scanner = FileScanner()
        self._cancel_requested = Event()

    @Slot()
    def run(self) -> None:
        file_count = 0

        try:
            for record in self._scanner.scan(self._folder):
                if self._cancel_requested.is_set():
                    self.cancelled.emit()
                    return

                file_count += 1
                self.file_found.emit(record)

                if file_count % 25 == 0:
                    self.progress_updated.emit(file_count)

        except (FileNotFoundError, NotADirectoryError, OSError) as error:
            self.failed.emit(str(error))
            return

        if self._cancel_requested.is_set():
            self.cancelled.emit()
            return

        self.progress_updated.emit(file_count)
        self.finished.emit()

    def request_cancel(self) -> None:
        self._cancel_requested.set()
