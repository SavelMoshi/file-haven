from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

from file_haven.presentation.widgets.file_table import FileTable
from file_haven.presentation.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("File Haven")
        self.resize(1280, 760)
        self.setMinimumSize(1000, 620)

        self._sidebar = Sidebar()
        self._file_table = FileTable()

        self._page_title = QLabel("All Files")
        self._folder_path_input = QLineEdit()
        self._search_input = QLineEdit()

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

        subtitle = QLabel(
            "Find clutter, review files, and clean folders safely."
        )
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
        self._folder_path_input.setPlaceholderText(
            "Choose a folder to scan"
        )
        self._folder_path_input.setReadOnly(True)
        self._folder_path_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        choose_button = QPushButton("Choose Folder")
        choose_button.setObjectName("secondaryButton")
        choose_button.setCursor(Qt.CursorShape.PointingHandCursor)

        scan_button = QPushButton("Scan Folder")
        scan_button.setObjectName("primaryButton")
        scan_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self._folder_path_input)
        layout.addWidget(choose_button)
        layout.addWidget(scan_button)

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

    def _handle_page_selected(self, page_name: str) -> None:
        page_titles = {
            "all_files": "All Files",
            "duplicates": "Duplicates",
            "large_files": "Large Files",
            "old_files": "Old Files",
            "history": "Scan History",
        }

        self._page_title.setText(
            page_titles.get(page_name, "All Files")
        )