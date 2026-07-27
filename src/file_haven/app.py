import sys

from PySide6.QtWidgets import QApplication

from file_haven.presentation.main_window import MainWindow
from file_haven.presentation.theme import DARK_THEME


def create_application() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName("File Haven")
    app.setOrganizationName("File Haven")
    app.setStyleSheet(DARK_THEME)

    return app


def main() -> None:
    app = create_application()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
