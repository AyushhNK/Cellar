"""Qt stylesheet for the Cellar UI."""

# Wine-cellar theme: aubergine dark, burgundy actions, brass accents, serif display type.
STYLE = """
* { font-family: "Inter", "Segoe UI", "Cantarell", sans-serif; font-size: 13px; color: #efe6da; }
QWidget { background: #17121a; }
QDialog, QMainWindow { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1d1520, stop:1 #120e14); }
QLabel { background: transparent; }
QLabel#brand { font-family: "Georgia", "Noto Serif", "DejaVu Serif", serif; font-size: 30px; color: #d4af6a; letter-spacing: 6px; }
QLabel#title { font-family: "Georgia", "Noto Serif", "DejaVu Serif", serif; font-size: 22px; color: #d4af6a; letter-spacing: 3px; }
QLabel#muted { color: #8f8094; font-size: 12px; }
QLabel#error { color: #e0607a; }
QLineEdit, QPlainTextEdit {
    background: #221a25; border: 1px solid #3a2d3e; border-radius: 9px; padding: 9px 12px;
    selection-background-color: #8e2b3f;
}
QLineEdit:focus, QPlainTextEdit:focus { border: 1px solid #b0384f; background: #281e2b; }
QLineEdit#search { border-radius: 17px; padding-left: 16px; min-width: 260px; }
QPushButton {
    background: transparent; border: 1px solid #3f3043; border-radius: 9px; padding: 8px 16px; color: #d9cbbb;
}
QPushButton:hover { background: #2a2030; border-color: #5a4560; }
QPushButton:pressed { background: #1c151f; }
QPushButton#primary, QDialogButtonBox QPushButton:default {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a8364c, stop:1 #7d2437);
    border: 1px solid #b8445a; color: #fff4ea; font-weight: 600;
}
QPushButton#primary:hover, QDialogButtonBox QPushButton:default:hover { background: #b23d54; }
QPushButton#danger { color: #e0607a; }
QPushButton#danger:hover { background: #3a1a24; border-color: #8e2b3f; }
QPushButton#brass { color: #d4af6a; border-color: #6b5530; }
QPushButton#brass:hover { background: #2c2418; }
QTableWidget {
    background: #1c161f; alternate-background-color: #201923; border: 1px solid #2f2533;
    border-radius: 12px; gridline-color: transparent; outline: 0;
}
QTableWidget::item { padding: 0 14px; border: none; }
QTableWidget::item:selected { background: #4a1d2a; color: #fff4ea; }
QHeaderView::section {
    background: #1c161f; color: #a08a6a; border: none; border-bottom: 1px solid #3a2d3e;
    padding: 10px 14px; font-size: 11px; font-weight: 600; letter-spacing: 2px;
}
QScrollBar:vertical { background: transparent; width: 10px; margin: 4px; }
QScrollBar::handle:vertical { background: #3f3043; border-radius: 3px; min-height: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QCheckBox { background: transparent; spacing: 6px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #5a4560; border-radius: 4px; background: #221a25; }
QCheckBox::indicator:checked { background: #a8364c; border-color: #b8445a; }
QStatusBar { background: #120e14; color: #d4af6a; border-top: 1px solid #2a2030; }
QToolTip { background: #2a2030; color: #efe6da; border: 1px solid #5a4560; }
"""
