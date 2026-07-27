import sys
from file_haven.presentation.theme import DARK_THEME

from PySide6.QtWidgets import QApplication

from file_haven.presentation.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)


    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()