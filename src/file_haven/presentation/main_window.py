from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from file_haven.constants import (
    LARGE_FILE_THRESHOLD_MB,
    OLD_FILE_THRESHOLD_DAYS,
)
from file_haven.domain import DuplicateGroup, FileRecord, ScanHistoryRecord
from file_haven.infrastructure import ScanHistoryRepository
from file_haven.presentation.widgets.file_table import FileTable
from file_haven.presentation.widgets.history_table import HistoryTable
from file_haven.presentation.widgets.sidebar import Sidebar
from file_haven.presentation.workers import DuplicateWorker, ScanWorker
from file_haven.services import FileRevealService, TrashService, format_file_size

MAX_DISPLAYED_FILES = 5_000


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("File Haven")
        self.resize(1280, 760)
        self.setMinimumSize(1000, 620)

        self._selected_folder: Path | None = None
        self._scan_thread: QThread | None = None
        self._scan_worker: ScanWorker | None = None
        self._scan_file_count = 0
        self._scan_results: list[FileRecord] = []

        self._duplicate_thread: QThread | None = None
        self._duplicate_worker: DuplicateWorker | None = None
        self._duplicate_groups: list[DuplicateGroup] = []
        self._duplicate_analysis_complete = False

        self._current_page = "all_files"
        self._scan_cancel_requested = False

        self._sidebar = Sidebar()
        self._file_table = FileTable()

        self._history_table = HistoryTable()
        self._history_table.hide()

        data_directory = Path.home() / ".file_haven"
        data_directory.mkdir(parents=True, exist_ok=True)

        self._history_repository = ScanHistoryRepository(data_directory / "file_haven.db")

        self._page_title = QLabel("All Files")
        self._folder_path_input = QLineEdit()
        self._search_input = QLineEdit()

        self._choose_folder_button = QPushButton("Choose Folder")
        self._scan_button = QPushButton("Scan Folder")
        self._cancel_button = QPushButton("Cancel")

        self._trash_service = TrashService()
        self._trash_button = QPushButton("Move to Trash")

        self._file_reveal_service = FileRevealService()
        self._reveal_button = QPushButton("Reveal in Folder")

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        root_widget = QWidget()
        root_widget.setObjectName("rootWidget")

        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._sidebar)
        root_layout.addWidget(self._build_content_area())

        self.setCentralWidget(root_widget)
        self._build_status_bar()

    def _build_content_area(self) -> QWidget:
        content = QWidget()
        content.setObjectName("contentArea")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(20)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_folder_controls())
        layout.addWidget(self._build_results_header())
        layout.addWidget(self._file_table)
        layout.addWidget(self._history_table)

        return content

    def _build_header(self) -> QWidget:
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel("File Haven")
        title.setObjectName("appTitle")

        subtitle = QLabel("Find clutter, review files, and clean folders safely.")
        subtitle.setObjectName("appSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return container

    def _build_folder_controls(self) -> QFrame:
        card = QFrame()
        card.setObjectName("controlCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self._folder_path_input.setObjectName("folderPathInput")
        self._folder_path_input.setPlaceholderText("Choose a folder to scan")
        self._folder_path_input.setReadOnly(True)
        self._folder_path_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self._choose_folder_button.setObjectName("secondaryButton")
        self._choose_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self._scan_button.setObjectName("primaryButton")
        self._scan_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._scan_button.setEnabled(False)

        self._cancel_button.setObjectName("dangerButton")
        self._cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_button.setEnabled(False)

        layout.addWidget(self._folder_path_input)
        layout.addWidget(self._choose_folder_button)
        layout.addWidget(self._scan_button)
        layout.addWidget(self._cancel_button)

        return card

    def _build_results_header(self) -> QWidget:
        container = QWidget()

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self._page_title.setObjectName("pageTitle")

        self._search_input.setObjectName("searchInput")
        self._search_input.setPlaceholderText("Search files...")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.setMaximumWidth(320)

        self._trash_button.setObjectName("dangerButton")
        self._trash_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._trash_button.setEnabled(False)

        self._reveal_button.setObjectName("secondaryButton")
        self._reveal_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reveal_button.setEnabled(False)

        layout.addWidget(self._page_title)
        layout.addStretch()
        layout.addWidget(self._search_input)
        layout.addWidget(self._reveal_button)
        layout.addWidget(self._trash_button)

        return container

    def _build_status_bar(self) -> None:
        status_bar = QStatusBar()
        status_bar.setObjectName("statusBar")
        status_bar.showMessage("Ready")

        self.setStatusBar(status_bar)

    def _connect_signals(self) -> None:
        self._sidebar.page_selected.connect(self._handle_page_selected)
        self._choose_folder_button.clicked.connect(self._choose_folder)
        self._scan_button.clicked.connect(self._start_scan)
        self._cancel_button.clicked.connect(self._cancel_scan)
        self._search_input.textChanged.connect(self._refresh_current_view)
        self._reveal_button.clicked.connect(self._reveal_selected_file)

        self._trash_button.clicked.connect(self._move_selected_to_trash)

        selection_model = self._file_table.selectionModel()

        if selection_model is not None:
            selection_model.selectionChanged.connect(self._update_file_actions)

    def _choose_folder(self) -> None:
        initial_directory = (
            str(self._selected_folder) if self._selected_folder is not None else str(Path.home())
        )

        selected_path = QFileDialog.getExistingDirectory(
            self,
            "Choose a folder to scan",
            initial_directory,
            QFileDialog.Option.ShowDirsOnly,
        )

        if not selected_path:
            return

        folder = Path(selected_path)

        self._selected_folder = folder
        self._folder_path_input.setText(str(folder))
        self._folder_path_input.setToolTip(str(folder))
        self._scan_button.setEnabled(True)

        self.statusBar().showMessage(f"Selected folder: {folder.name}")

    def _start_scan(self) -> None:
        if self._duplicate_thread is not None:
            self.statusBar().showMessage("Wait for duplicate analysis to finish")
            return
        if self._selected_folder is None:
            return

        if self._scan_thread is not None:
            return

        self._scan_file_count = 0
        self._scan_results.clear()
        self._duplicate_groups.clear()
        self._duplicate_analysis_complete = False
        self._scan_cancel_requested = False
        self._file_table.clear_files()
        self._update_file_actions()

        self._choose_folder_button.setEnabled(False)
        self._scan_button.setEnabled(False)
        self._scan_button.setText("Scanning...")
        self._cancel_button.setEnabled(True)

        self.statusBar().showMessage("Scanning folder...")

        self._scan_thread = QThread(self)
        self._scan_worker = ScanWorker(self._selected_folder)

        self._scan_worker.moveToThread(self._scan_thread)

        self._scan_thread.started.connect(self._scan_worker.run)

        self._scan_worker.files_found.connect(self._handle_files_found)
        self._scan_worker.progress_updated.connect(self._handle_scan_progress)
        self._scan_worker.finished.connect(self._handle_scan_finished)
        self._scan_worker.failed.connect(self._handle_scan_failed)
        self._scan_worker.cancelled.connect(self._handle_scan_cancelled)

        self._scan_worker.finished.connect(self._scan_worker.deleteLater)
        self._scan_worker.failed.connect(self._scan_worker.deleteLater)
        self._scan_worker.cancelled.connect(self._scan_worker.deleteLater)

        self._scan_worker.finished.connect(self._scan_thread.quit)
        self._scan_worker.failed.connect(self._scan_thread.quit)
        self._scan_worker.cancelled.connect(self._scan_thread.quit)

        self._scan_thread.finished.connect(self._scan_thread.deleteLater)
        self._scan_thread.finished.connect(self._cleanup_scan)
        self._file_table.setSortingEnabled(False)

        self._scan_thread.start()

    def _handle_files_found(
        self,
        records: list[FileRecord],
    ) -> None:
        if self._scan_cancel_requested:
            return

        self._scan_results.extend(records)
        self._scan_file_count += len(records)

    def _handle_scan_progress(self, file_count: int) -> None:
        if self._scan_cancel_requested:
            return

        self.statusBar().showMessage(f"Scanning... {file_count:,} files found")

    def _handle_scan_finished(self) -> None:
        if self._selected_folder is not None:
            history_record = ScanHistoryRecord(
                folder=self._selected_folder,
                file_count=self._scan_file_count,
                scanned_at=datetime.now(),
            )

            self._history_repository.add(history_record)

        self._refresh_current_view()

        self.statusBar().showMessage(f"Scan complete — {self._scan_file_count:,} files found")

    def _handle_scan_failed(self, message: str) -> None:
        self.statusBar().showMessage(f"Scan failed: {message}")

    def _handle_scan_cancelled(self) -> None:
        self.statusBar().showMessage(f"Scan cancelled — {self._scan_file_count:,} files found")

    def _cleanup_scan(self) -> None:
        self._scan_worker = None
        self._scan_thread = None
        self._scan_cancel_requested = False
        self._file_table.setSortingEnabled(True)

        self._choose_folder_button.setEnabled(True)
        self._scan_button.setEnabled(self._selected_folder is not None)
        self._scan_button.setText("Scan Folder")
        self._cancel_button.setEnabled(False)

    def _cancel_scan(self) -> None:
        if self._scan_worker is None:
            return

        self._scan_cancel_requested = True

        self._cancel_button.setEnabled(False)
        self._scan_button.setText("Cancelling...")

        self.statusBar().showMessage(f"Cancelling scan... {self._scan_file_count:,} files found")

        self._scan_worker.request_cancel()

    def _show_files(self, records: list[FileRecord]) -> None:
        displayed_records = records[:MAX_DISPLAYED_FILES]

        self._file_table.set_files(displayed_records)
        self._update_file_actions()

        if len(records) > MAX_DISPLAYED_FILES:
            self.statusBar().showMessage(
                f"Showing {MAX_DISPLAYED_FILES:,} of {len(records):,} files"
            )
            return

        self.statusBar().showMessage(f"Showing {len(records):,} files")

    def _start_duplicate_analysis(self) -> None:
        if self._duplicate_thread is not None:
            self.statusBar().showMessage("Finding duplicate files...")
            return

        self._choose_folder_button.setEnabled(False)
        self._scan_button.setEnabled(False)
        self._cancel_button.setEnabled(False)

        self._file_table.clear_files()
        self._update_file_actions()
        self.statusBar().showMessage("Finding duplicate files...")

        self._duplicate_thread = QThread(self)
        self._duplicate_worker = DuplicateWorker(list(self._scan_results))

        self._duplicate_worker.moveToThread(self._duplicate_thread)

        self._duplicate_thread.started.connect(self._duplicate_worker.run)

        self._duplicate_worker.completed.connect(self._handle_duplicates_completed)
        self._duplicate_worker.failed.connect(self._handle_duplicates_failed)

        self._duplicate_worker.completed.connect(self._duplicate_worker.deleteLater)
        self._duplicate_worker.failed.connect(self._duplicate_worker.deleteLater)

        self._duplicate_worker.completed.connect(self._duplicate_thread.quit)
        self._duplicate_worker.failed.connect(self._duplicate_thread.quit)

        self._duplicate_thread.finished.connect(self._duplicate_thread.deleteLater)
        self._duplicate_thread.finished.connect(self._cleanup_duplicate_analysis)

        self._duplicate_thread.start()

    def _handle_duplicates_completed(
        self,
        groups: list[DuplicateGroup],
    ) -> None:
        self._duplicate_groups = groups
        self._duplicate_analysis_complete = True

        duplicate_file_count = sum(len(group.files) for group in groups)
        reclaimable_bytes = sum(group.reclaimable_bytes for group in groups)

        if self._current_page == "duplicates":
            duplicate_records = [record for group in groups for record in group.files]

            self._show_files(duplicate_records)

        self.statusBar().showMessage(
            f"Found {len(groups):,} duplicate groups — "
            f"{duplicate_file_count:,} files — "
            f"{format_file_size(reclaimable_bytes)} reclaimable"
        )

    def _handle_duplicates_failed(self, message: str) -> None:
        self.statusBar().showMessage(f"Duplicate detection failed: {message}")

    def _cleanup_duplicate_analysis(self) -> None:
        self._duplicate_worker = None
        self._duplicate_thread = None

        self._choose_folder_button.setEnabled(True)
        self._scan_button.setEnabled(self._selected_folder is not None)
        self._cancel_button.setEnabled(False)

    def _refresh_current_view(self) -> None:
        if self._current_page == "history":
            self._file_table.hide()
            self._history_table.show()

            history_records = self._history_repository.get_all()
            self._history_table.show_records(history_records)

            self._update_file_actions()
            self.statusBar().showMessage(f"Showing {len(history_records):,} previous scans")
            return

        if self._current_page == "duplicates":
            self._history_table.hide()
            self._file_table.show()

            if not self._scan_results:
                self._file_table.clear_files()
                self._update_file_actions()
                self.statusBar().showMessage("Scan a folder before finding duplicates")
                return

            if not self._duplicate_analysis_complete:
                self._start_duplicate_analysis()
                return

            duplicate_records = [
                record for group in self._duplicate_groups for record in group.files
            ]

            search_text = self._search_input.text().strip().lower()

            if search_text:
                duplicate_records = [
                    record
                    for record in duplicate_records
                    if search_text in record.name.lower()
                    or search_text in str(record.parent_folder).lower()
                    or search_text in record.extension.lower()
                ]

            self._show_files(duplicate_records)
            return

        self._history_table.hide()
        self._file_table.show()

        records = self._get_current_page_records()

        search_text = self._search_input.text().strip().lower()

        if search_text:
            records = [
                record
                for record in records
                if search_text in record.name.lower()
                or search_text in str(record.parent_folder).lower()
                or search_text in record.extension.lower()
            ]

        self._show_files(records)

    def _get_current_page_records(self) -> list[FileRecord]:
        if self._current_page == "duplicates":
            return [record for group in self._duplicate_groups for record in group.files]

        if self._current_page == "large_files":
            threshold_bytes = LARGE_FILE_THRESHOLD_MB * 1024 * 1024

            return [record for record in self._scan_results if record.size_bytes >= threshold_bytes]

        if self._current_page == "old_files":
            return [
                record
                for record in self._scan_results
                if record.age_days >= OLD_FILE_THRESHOLD_DAYS
            ]

        return list(self._scan_results)

    def _update_file_actions(self, *_: object) -> None:
        has_selection = bool(self._file_table.selected_records())

        background_job_running = self._scan_thread is not None or self._duplicate_thread is not None

        self._trash_button.setEnabled(
            has_selection and self._current_page != "history" and not background_job_running
        )

        self._reveal_button.setEnabled(
            has_selection and self._current_page != "history" and not background_job_running
        )

    def _reveal_selected_file(self) -> None:
        records = self._file_table.selected_records()

        if not records:
            return

        record = records[0]

        if self._file_reveal_service.reveal(record.path):
            self.statusBar().showMessage(f"Revealed {record.name}")
            return

        QMessageBox.warning(
            self,
            "Unable to Reveal File",
            "The selected file could not be found or opened.",
        )

    def _move_selected_to_trash(self) -> None:
        records = self._file_table.selected_records()

        if not records:
            return

        file_count = len(records)
        file_word = "file" if file_count == 1 else "files"

        response = QMessageBox.warning(
            self,
            "Move to Trash",
            (
                f"Move {file_count:,} selected {file_word} "
                "to the Trash?\n\n"
                "You can restore them from the system Trash."
            ),
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            QMessageBox.StandardButton.No,
        )

        if response != QMessageBox.StandardButton.Yes:
            return

        result = self._trash_service.move_files(record.path for record in records)

        moved_paths = set(result.moved)

        if moved_paths:
            self._scan_results = [
                record for record in self._scan_results if record.path not in moved_paths
            ]

            updated_groups: list[DuplicateGroup] = []

            for group in self._duplicate_groups:
                remaining_files = tuple(
                    record for record in group.files if record.path not in moved_paths
                )

                if len(remaining_files) >= 2:
                    updated_groups.append(
                        DuplicateGroup(
                            fingerprint=group.fingerprint,
                            files=remaining_files,
                        )
                    )

            self._duplicate_groups = updated_groups
            self._refresh_current_view()

        self._update_file_actions()

        if result.failed:
            QMessageBox.warning(
                self,
                "Some Files Were Not Moved",
                (
                    f"Moved {len(result.moved):,} files.\n"
                    f"Failed to move {len(result.failed):,} files."
                ),
            )
            return

        self.statusBar().showMessage(f"Moved {len(result.moved):,} files to Trash")

    def _handle_page_selected(self, page_name: str) -> None:
        if page_name == "scan_history":
            page_name = "history"

        self._current_page = page_name

        page_titles = {
            "all_files": "All Files",
            "duplicates": "Duplicates",
            "large_files": "Large Files",
            "old_files": "Old Files",
            "history": "Scan History",
        }

        self._page_title.setText(page_titles.get(page_name, "All Files"))

        self._refresh_current_view()
