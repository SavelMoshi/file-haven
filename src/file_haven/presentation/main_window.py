from pathlib import Path

from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from file_haven.domain import FileRecord
from file_haven.presentation.widgets.file_table import FileTable
from file_haven.presentation.widgets.sidebar import Sidebar
from file_haven.presentation.workers.scan_worker import ScanWorker


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
        self._scan_cancel_requested = False

        self._sidebar = Sidebar()
        self._file_table = FileTable()

        self._page_title = QLabel("All Files")
        self._folder_path_input = QLineEdit()
        self._search_input = QLineEdit()

        self._choose_folder_button = QPushButton("Choose Folder")
        self._scan_button = QPushButton("Scan Folder")
        self._cancel_button = QPushButton("Cancel")

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

        layout.addWidget(self._page_title)
        layout.addStretch()
        layout.addWidget(self._search_input)

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
        if self._selected_folder is None:
            return

        if self._scan_thread is not None:
            return

        self._scan_file_count = 0
        self._scan_cancel_requested = False
        self._file_table.clear_files()

        self._choose_folder_button.setEnabled(False)
        self._scan_button.setEnabled(False)
        self._scan_button.setText("Scanning...")
        self._cancel_button.setEnabled(True)

        self.statusBar().showMessage("Scanning folder...")

        self._scan_thread = QThread(self)
        self._scan_worker = ScanWorker(self._selected_folder)

        self._scan_worker.moveToThread(self._scan_thread)

        self._scan_thread.started.connect(self._scan_worker.run)

        self._scan_worker.file_found.connect(self._handle_file_found)
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

        self._scan_thread.start()

    def _handle_file_found(self, record: FileRecord) -> None:
        if self._scan_cancel_requested:
            return

        self._scan_file_count += 1
        self._file_table.add_file(record)

    def _handle_scan_progress(self, file_count: int) -> None:
        if self._scan_cancel_requested:
            return

        self.statusBar().showMessage(f"Scanning... {file_count:,} files found")

    def _handle_scan_finished(self) -> None:
        self.statusBar().showMessage(f"Scan complete — {self._scan_file_count:,} files found")

    def _handle_scan_failed(self, message: str) -> None:
        self.statusBar().showMessage(f"Scan failed: {message}")

    def _handle_scan_cancelled(self) -> None:
        self.statusBar().showMessage(f"Scan cancelled — {self._scan_file_count:,} files found")

    def _cleanup_scan(self) -> None:
        self._scan_worker = None
        self._scan_thread = None
        self._scan_cancel_requested = False

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

    def _handle_page_selected(self, page_name: str) -> None:
        page_titles = {
            "all_files": "All Files",
            "duplicates": "Duplicates",
            "large_files": "Large Files",
            "old_files": "Old Files",
            "history": "Scan History",
        }

        self._page_title.setText(page_titles.get(page_name, "All Files"))
