DARK_THEME = """
* {
    font-family: "Inter", "SF Pro Display", "Segoe UI", sans-serif;
    font-size: 14px;
}

QMainWindow,
QWidget#rootWidget,
QWidget#contentArea {
    background-color: #111318;
    color: #F4F6FA;
}

QWidget#sidebar {
    background-color: #181B22;
    border-right: 1px solid #292D36;
}

QPushButton#sidebarButton {
    min-height: 44px;
    padding: 0 14px;
    border: none;
    border-radius: 8px;
    background-color: transparent;
    color: #A9AFBC;
    text-align: left;
    font-weight: 500;
}

QPushButton#sidebarButton:hover {
    background-color: #222630;
    color: #FFFFFF;
}

QPushButton#sidebarButton[active="true"] {
    background-color: #2D3443;
    color: #FFFFFF;
    font-weight: 600;
}

QLabel#appTitle {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 700;
}

QLabel#appSubtitle {
    color: #8E95A3;
    font-size: 14px;
}

QLabel#pageTitle {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 650;
}

QFrame#controlCard {
    background-color: #181B22;
    border: 1px solid #292D36;
    border-radius: 12px;
}

QLineEdit {
    min-height: 40px;
    padding: 0 12px;
    border: 1px solid #323743;
    border-radius: 8px;
    background-color: #20242D;
    color: #F4F6FA;
    selection-background-color: #6278FF;
}

QLineEdit:hover {
    border-color: #454C5C;
}

QLineEdit:focus {
    border: 1px solid #7185FF;
}

QLineEdit:read-only {
    color: #A9AFBC;
}

QPushButton#primaryButton,
QPushButton#secondaryButton {
    min-height: 40px;
    padding: 0 18px;
    border-radius: 8px;
    font-weight: 600;
}

QPushButton#primaryButton {
    border: none;
    background-color: #6D7CFF;
    color: #FFFFFF;
}

QPushButton#primaryButton:hover {
    background-color: #7E8BFF;
}

QPushButton#primaryButton:pressed {
    background-color: #5D6BE8;
}

QPushButton#secondaryButton {
    border: 1px solid #383E4B;
    background-color: #242832;
    color: #E8EAF0;
}

QPushButton#secondaryButton:hover {
    background-color: #2C313D;
    border-color: #4B5262;
}

QPushButton:disabled {
    background-color: #2A2E37;
    border-color: #30343E;
    color: #666D7A;
}

QTableWidget#fileTable {
    border: 1px solid #292D36;
    border-radius: 10px;
    background-color: #181B22;
    alternate-background-color: #1C2028;
    color: #E8EAF0;
    gridline-color: transparent;
    outline: none;
}

QTableWidget#fileTable::item {
    min-height: 42px;
    padding: 8px;
    border-bottom: 1px solid #252932;
}

QTableWidget#fileTable::item:selected {
    background-color: #303A58;
    color: #FFFFFF;
}

QHeaderView::section {
    min-height: 42px;
    padding: 0 10px;
    border: none;
    border-bottom: 1px solid #30343E;
    background-color: #20242D;
    color: #AEB4C0;
    font-weight: 600;
    text-align: left;
}

QTableCornerButton::section {
    background-color: #20242D;
    border: none;
    border-bottom: 1px solid #30343E;
}

QScrollBar:vertical {
    width: 10px;
    margin: 4px;
    border: none;
    background-color: transparent;
}

QScrollBar::handle:vertical {
    min-height: 30px;
    border-radius: 5px;
    background-color: #3A404D;
}

QScrollBar::handle:vertical:hover {
    background-color: #4A5262;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QStatusBar#statusBar {
    border-top: 1px solid #292D36;
    background-color: #181B22;
    color: #8E95A3;
}
"""