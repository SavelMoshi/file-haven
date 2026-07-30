DARK_THEME = """
* {
    font-family: "Helvetica Neue";
    font-size: 14px;
}

QMainWindow,
QWidget#rootWidget,
QWidget#contentArea {
    background-color: #0B111C;
    color: #F1F5F9;
}

QWidget#sidebar {
    background-color: #0E1724;
    border-right: 1px solid #223044;
}

QPushButton#sidebarButton {
    min-height: 44px;
    padding: 0 14px;
    border: none;
    border-radius: 8px;
    background-color: transparent;
    color: #94A3B8;
    text-align: left;
    font-weight: 500;
}

QPushButton#sidebarButton:hover {
    background-color: #142033;
    color: #F1F5F9;
}

QPushButton#sidebarButton[active="true"] {
    background-color: #17323B;
    color: #CCFBF1;
    font-weight: 600;
}

QLabel#appTitle {
    color: #F8FAFC;
    font-size: 28px;
    font-weight: 700;
}

QLabel#appSubtitle {
    color: #94A3B8;
    font-size: 14px;
}

QLabel#pageTitle {
    color: #F1F5F9;
    font-size: 20px;
    font-weight: 650;
}

QLabel#emptyState {
    color: #94A3B8;
    font-size: 15px;
    padding: 28px;
}

QFrame#controlCard {
    background-color: #142033;
    border: 1px solid #243246;
    border-radius: 12px;
}

QLineEdit {
    min-height: 40px;
    padding: 0 12px;
    border: 1px solid #243246;
    border-radius: 8px;
    background-color: #101827;
    color: #F1F5F9;
    selection-background-color: #0F766E;
}

QLineEdit:hover {
    border-color: #345061;
}

QLineEdit:focus {
    border: 1px solid #5EEAD4;
}

QLineEdit:read-only {
    color: #CBD5E1;
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
    background-color: #2DD4BF;
    color: #06211E;
}

QPushButton#primaryButton:hover {
    background-color: #5EEAD4;
}

QPushButton#primaryButton:pressed {
    background-color: #14B8A6;
}

QPushButton#secondaryButton {
    border: 1px solid #243246;
    background-color: #142033;
    color: #E2E8F0;
}

QPushButton#secondaryButton:hover {
    background-color: #1A2A3E;
    border-color: #4DB6AC;
}

QPushButton:disabled {
    background-color: #151E2B;
    border-color: #223044;
    color: #64748B;
}

QPushButton#dangerButton {
    background-color: #C76666;
    color: #FFFFFF;
    border: 1px solid #D27A7A;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}

QPushButton#dangerButton:hover {
    background-color: #D27A7A;
    border-color: #DE8F8F;
}

QPushButton#dangerButton:pressed {
    background-color: #A94F4F;
    border-color: #B85C5C;
}

QPushButton#dangerButton:disabled {
    background-color: #332126;
    color: #94A3B8;
    border-color: #4A2B31;
}

QTableView#fileTable {
    border: 1px solid #243246;
    border-radius: 10px;
    background-color: #142033;
    alternate-background-color: #101827;
    color: #E2E8F0;
    gridline-color: transparent;
    outline: none;
}

QTableView#fileTable::item {
    min-height: 42px;
    padding: 8px;
    border-bottom: 1px solid #223044;
}

QTableView#fileTable::item:selected {
    background-color: #166B68;
    color: #F8FAFC;
}

QHeaderView::section {
    min-height: 42px;
    padding: 0 10px;
    border: none;
    border-bottom: 1px solid #243246;
    background-color: #101827;
    color: #CBD5E1;
    font-weight: 600;
    text-align: left;
}

QTableCornerButton::section {
    background-color: #101827;
    border: none;
    border-bottom: 1px solid #243246;
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
    background-color: #2A3B4F;
}

QScrollBar::handle:vertical:hover {
    background-color: #4DB6AC;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QStatusBar#statusBar {
    border-top: 1px solid #223044;
    background-color: #0E1724;
    color: #94A3B8;
}
"""
