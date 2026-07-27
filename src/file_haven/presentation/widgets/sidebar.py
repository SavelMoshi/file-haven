from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class Sidebar(QWidget):
    page_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("sidebar")
        self.setFixedWidth(210)

        self._all_files_button = self._create_button("All Files", "all_files")
        self._duplicates_button = self._create_button("Duplicates", "duplicates")
        self._large_files_button = self._create_button("Large Files", "large_files")
        self._old_files_button = self._create_button("Old Files", "old_files")
        self._history_button = self._create_button("Scan History", "history")

        self._all_files_button.setProperty("active", True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(8)

        layout.addWidget(self._all_files_button)
        layout.addWidget(self._duplicates_button)
        layout.addWidget(self._large_files_button)
        layout.addWidget(self._old_files_button)
        layout.addStretch()
        layout.addWidget(self._history_button)

    def _create_button(self, text: str, page_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        button.setCursor(self.cursor())
        button.clicked.connect(
            lambda checked=False, name=page_name: self._select_page(name)
        )
        return button

    def _select_page(self, page_name: str) -> None:
        buttons = self.findChildren(QPushButton)

        for button in buttons:
            button.setProperty("active", False)
            button.style().unpolish(button)
            button.style().polish(button)

        selected_button = self.sender()

        if isinstance(selected_button, QPushButton):
            selected_button.setProperty("active", True)
            selected_button.style().unpolish(selected_button)
            selected_button.style().polish(selected_button)

        self.page_selected.emit(page_name)