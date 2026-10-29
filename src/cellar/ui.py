"""Qt windows and dialogs."""
import sys
from pathlib import Path

from cryptography.exceptions import InvalidTag
from PySide6.QtCore import QEvent, QMimeData, QStandardPaths, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from cellar.theme import STYLE
from cellar.vault import Vault, generate_password

MIN_MASTER_LEN = 12
IDLE_LOCK_MS = 5 * 60 * 1000
CLIPBOARD_CLEAR_MS = 20 * 1000
PASSWORD = QLineEdit.EchoMode.Password


def button(label, slot, kind=None):
    b = QPushButton(label, objectName=kind or "", cursor=Qt.CursorShape.PointingHandCursor)
    b.clicked.connect(slot)
    return b


class UnlockDialog(QDialog):
    def __init__(self, vault, change=False):
        super().__init__()
        self.vault = vault
        self.creating = change or not vault.exists()
        self.setWindowTitle("Change master password" if change else "Create vault" if self.creating else "Unlock Cellar")
        self.pw = QLineEdit(echoMode=PASSWORD)
        self.confirm = QLineEdit(echoMode=PASSWORD)
        self.msg = QLabel(objectName="error")
        form = QFormLayout(self)
        form.setContentsMargins(36, 32, 36, 28)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.addRow(QLabel("◆  CELLAR", objectName="brand", alignment=Qt.AlignmentFlag.AlignCenter))
        tagline = "Choose a new master password" if change else "Create your vault" if self.creating else "Your vault is locked"
        form.addRow(QLabel(tagline, objectName="muted", alignment=Qt.AlignmentFlag.AlignCenter))
        form.addRow("New master password" if change else "Master password", self.pw)
        if self.creating:
            form.addRow("Confirm", self.confirm)
            form.addRow(QLabel(f"At least {MIN_MASTER_LEN} characters. It cannot be recovered if lost.", objectName="muted"))
        form.addRow(self.msg)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.submit)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self.setMinimumWidth(420)

    def submit(self):
        pw = self.pw.text()
        if self.creating and len(pw) < MIN_MASTER_LEN:
            return self.msg.setText(f"Use at least {MIN_MASTER_LEN} characters.")
        if self.creating and pw != self.confirm.text():
            return self.msg.setText("Passwords do not match.")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.vault.set_password(pw) if self.creating else self.vault.unlock(pw)
        except InvalidTag:
            self.pw.clear()
            return self.msg.setText("Wrong master password.")
        except (OSError, ValueError, KeyError) as e:
            return self.msg.setText(f"Could not open vault: {e}")
        finally:
            QApplication.restoreOverrideCursor()
        self.accept()


class EntryDialog(QDialog):
    def __init__(self, parent, entry=None):
        super().__init__(parent)
        entry = entry or {}
        self.setWindowTitle("Edit entry" if entry else "Add entry")
        self.site = QLineEdit(entry.get("site", ""))
        self.user = QLineEdit(entry.get("username", ""))
        self.pw = QLineEdit(entry.get("password", ""), echoMode=PASSWORD)
        self.notes = QPlainTextEdit(entry.get("notes", ""))
        show = QCheckBox("Show")
        show.toggled.connect(lambda on: self.pw.setEchoMode(QLineEdit.EchoMode.Normal if on else PASSWORD))
        gen = button("⟳ Generate", lambda: self.pw.setText(generate_password()), "brass")
        row = QHBoxLayout()
        for w in (self.pw, show, gen):
            row.addWidget(w)
        form = QFormLayout(self)
        form.setContentsMargins(28, 24, 28, 22)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.addRow(QLabel(self.windowTitle().upper(), objectName="title"))
        form.addRow("Site", self.site)
        form.addRow("Username", self.user)
        form.addRow("Password", row)
        form.addRow("Notes", self.notes)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.submit)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self.setMinimumWidth(480)

    def submit(self):
        if not self.site.text().strip() or not self.pw.text():
            return QMessageBox.warning(self, "Missing fields", "Site and password are required.")
        self.accept()

    def value(self):
        return {"site": self.site.text().strip(), "username": self.user.text().strip(),
                "password": self.pw.text(), "notes": self.notes.toPlainText()}


class MainWindow(QMainWindow):
    def __init__(self, vault):
        super().__init__()
        self.vault = vault
        self.setWindowTitle("Cellar")
        self.resize(880, 560)
        self.search = QLineEdit(placeholderText="⌕  Search site or username…", objectName="search")
        self.search.textChanged.connect(self.refresh)
        self.count = QLabel(objectName="muted")
        self.table = QTableWidget(0, 2, alternatingRowColors=True, showGrid=False)
        self.table.setHorizontalHeaderLabels(["SITE", "USERNAME"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setColumnWidth(0, 360)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self.edit)
        header = QHBoxLayout()
        titles = QVBoxLayout(spacing=2)
        titles.addWidget(QLabel("◆ CELLAR", objectName="title"))
        titles.addWidget(self.count)
        header.addLayout(titles)
        header.addStretch()
        header.addWidget(self.search)
        buttons = QHBoxLayout(spacing=8)
        buttons.addWidget(button("＋  New entry", self.add, "primary"))
        buttons.addWidget(button("Edit", self.edit))
        buttons.addWidget(button("Delete", self.delete, "danger"))
        buttons.addStretch()
        buttons.addWidget(button("Copy username", lambda: self.copy("username")))
        buttons.addWidget(button("Copy password", lambda: self.copy("password")))
        buttons.addStretch()
        buttons.addWidget(button("Master password…", self.change_master))
        buttons.addWidget(button("Lock", self.lock, "brass"))
        layout = QVBoxLayout(spacing=16)
        layout.setContentsMargins(24, 22, 24, 18)
        layout.addLayout(header)
        layout.addWidget(self.table)
        layout.addLayout(buttons)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.idle = QTimer(self, singleShot=True, interval=IDLE_LOCK_MS)
        self.idle.timeout.connect(self.lock)
        QApplication.instance().installEventFilter(self)
        self.refresh()
        self.idle.start()

    def eventFilter(self, obj, event):
        if self.isVisible() and event.type() in (QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress, QEvent.Type.MouseMove):
            self.idle.start()
        return False

    def refresh(self, *_):
        q = self.search.text().lower()
        self.table.setRowCount(0)
        for i, e in sorted(enumerate(self.vault.entries), key=lambda ie: ie[1]["site"].lower()):
            if q in e["site"].lower() or q in e["username"].lower():
                r = self.table.rowCount()
                self.table.insertRow(r)
                site = QTableWidgetItem(e["site"])
                site.setData(Qt.ItemDataRole.UserRole, i)
                self.table.setItem(r, 0, site)
                self.table.setItem(r, 1, QTableWidgetItem(e["username"]))
        n = len(self.vault.entries)
        self.count.setText(f"{self.table.rowCount()} of {n} entries" if q else f"{n} {'entry' if n == 1 else 'entries'} under lock")

    def selected(self):
        row = self.table.currentRow()
        return None if row < 0 else self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def commit(self):
        try:
            self.vault.save()
        except OSError as e:
            QMessageBox.critical(self, "Save failed", f"Changes are NOT saved to disk:\n{e}")
        self.refresh()

    def add(self, *_):
        d = EntryDialog(self)
        if d.exec():
            self.vault.entries.append(d.value())
            self.commit()

    def edit(self, *_):
        i = self.selected()
        if i is None:
            return
        d = EntryDialog(self, self.vault.entries[i])
        if d.exec():
            self.vault.entries[i] = d.value()
            self.commit()

    def delete(self, *_):
        i = self.selected()
        if i is None:
            return
        site = self.vault.entries[i]["site"]
        if QMessageBox.question(self, "Delete", f"Delete entry for {site}?") == QMessageBox.StandardButton.Yes:
            del self.vault.entries[i]
            self.commit()

    def copy(self, field):
        i = self.selected()
        if i is None:
            return
        text = self.vault.entries[i][field]
        md = QMimeData()
        md.setText(text)
        # Ask clipboard managers not to keep it in history (KDE Klipper, Windows Win+V).
        md.setData("x-kde-passwordManagerHint", b"secret")
        md.setData('application/x-qt-windows-mime;value="ExcludeClipboardContentFromMonitorProcessing"', b"\0")
        cb = QApplication.clipboard()
        cb.setMimeData(md)
        QTimer.singleShot(CLIPBOARD_CLEAR_MS, lambda: cb.text() == text and cb.clear())
        self.statusBar().showMessage(f"Copied {field}. Clipboard clears in {CLIPBOARD_CLEAR_MS // 1000}s.", 4000)

    def change_master(self, *_):
        UnlockDialog(self.vault, change=True).exec()

    def lock(self, *_):
        self.idle.stop()
        if modal := QApplication.activeModalWidget():
            modal.reject()
        if QApplication.clipboard().ownsClipboard():
            QApplication.clipboard().clear()
        self.vault.lock()
        self.search.clear()
        self.refresh()
        self.hide()
        if UnlockDialog(self.vault).exec():
            self.refresh()
            self.show()
            self.idle.start()
        else:
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cellar")
    app.setDesktopFileName("cellar")  # Wayland app_id → matches cellar.desktop for dock icon
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    vault = Vault(Path(data_dir) / "vault.json")
    if not UnlockDialog(vault).exec():
        return
    win = MainWindow(vault)
    win.show()
    sys.exit(app.exec())
