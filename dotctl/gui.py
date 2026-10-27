"""Interface graphique (PyQt6) : sélection des modules + icône de notification."""
from __future__ import annotations

import os
import shutil
import sys
import threading

from PyQt6.QtCore import QObject, QProcess, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QApplication, QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMenu, QMessageBox,
                             QPlainTextEdit, QPushButton, QScrollArea, QSystemTrayIcon,
                             QVBoxLayout, QWidget)

from . import core

BG, CARD, BORDER, FG, MUTED, ACCENT = "#1e1e2e", "#181825", "#313244", "#cdd6f4", "#6c7086", "#cba6f7"
BADGE = {core.OK: "#a6e3a1", core.UPDATE: "#f9e2af", core.DRIFT: "#f5c2e7", core.ABSENT: "#6c7086"}
NEW, UPDATES = "new", "updates"

STYLE = f"""
QWidget {{ background:{BG}; color:{FG}; font-size:13px; }}
QPushButton {{ background:{BORDER}; border:none; border-radius:8px; padding:8px 16px; }}
QPushButton:hover {{ background:#45475a; }}
QPushButton:checked, QPushButton#primary {{ background:{ACCENT}; color:{BG}; font-weight:bold; }}
QPushButton:disabled {{ background:{BORDER}; color:#585b70; }}
QListWidget {{ background:{CARD}; border:none; border-radius:10px; padding:6px; }}
QListWidget::item {{ padding:8px; border-radius:6px; }}
QListWidget::item:selected {{ background:{BORDER}; color:{ACCENT}; }}
QScrollArea {{ border:none; }}
QCheckBox::indicator {{ width:18px; height:18px; border-radius:5px; border:2px solid #585b70; background:{CARD}; }}
QCheckBox::indicator:checked {{ background:{ACCENT}; border-color:{ACCENT}; }}
QLineEdit {{ background:{CARD}; border:1px solid {BORDER}; border-radius:8px; padding:9px; }}
QPlainTextEdit {{ background:{CARD}; border-radius:8px; font-family:monospace; padding:8px; }}
"""


def dot_icon(color: str) -> QIcon:
    px = QPixmap(22, 22)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(3, 3, 16, 16, 5, 5)
    p.end()
    return QIcon(px)


def dotctl_cmd() -> list[str]:
    return [str(core.DOTFILES / "bin" / "dotctl")]


class Scan(QObject):
    """Calcule les statuts en arrière-plan (check.sh peut être lent)."""
    done = pyqtSignal(dict, dict, dict)

    def run(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        core.invalidate_cache()
        mods = core.load_modules()
        prof = core.load_profile()
        env = core.context_env(prof)
        state = core.load_state()
        st = {}
        for mid, m in mods.items():
            # Les applis du catalogue : statut paquet seulement (rapide)
            st[mid] = core.status(m, env, state)
        self.done.emit(mods, prof, st)


class ModuleCard(QFrame):
    def __init__(self, m: core.Module, status: str, checked: bool):
        super().__init__()
        self.m = m
        self.setStyleSheet(f"QFrame{{background:{CARD};border:1px solid {BORDER};border-radius:10px;}}"
                           f"QLabel{{background:transparent;border:none;}}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        self.cb = QCheckBox()
        self.cb.setChecked(checked)
        lay.addWidget(self.cb)
        col = QVBoxLayout()
        col.setSpacing(2)
        name = QLabel(f"<b>{m.name}</b>  <span style='color:{MUTED};font-size:11px'>{m.id}</span>")
        desc = QLabel(m.description)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{MUTED};font-size:12px;")
        col.addWidget(name)
        col.addWidget(desc)
        lay.addLayout(col, 1)
        if m.manual:
            lay.addWidget(QLabel("<span style='color:#fab387;font-size:11px'>étapes manuelles</span>"))
        badge = QLabel(core.STATUS_LABEL[status])
        badge.setStyleSheet(f"color:{BADGE[status]};border:1px solid {BADGE[status]};border-radius:5px;"
                            f"padding:1px 6px;font-size:11px;")
        lay.addWidget(badge)
        if m.path:
            info = QPushButton("?")
            info.setFixedSize(30, 30)
            info.setStyleSheet("padding:0; font-weight:bold;")
            info.clicked.connect(self.show_info)
            lay.addWidget(info)

    def show_info(self):
        d = QDialog(self)
        d.setWindowTitle(self.m.name)
        d.resize(700, 520)
        v = QVBoxLayout(d)
        t = QPlainTextEdit(readOnly=True)
        pk = "  ".join(f"{k}: {' '.join(p)}" for k, p in (("pacman", self.m.pacman), ("AUR", self.m.aur),
                                                          ("flatpak", self.m.flatpak)) if p)
        files = "\n".join(f"  → {f.dst}" for f in self.m.files)
        t.setPlainText(f"{self.m.description}\n\n{pk}\n{files}\n\n{self.m.readme()}")
        v.addWidget(t)
        d.exec()


class LogDialog(QDialog):
    finished = pyqtSignal(int)

    def __init__(self, args: list[str], title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(780, 500)
        v = QVBoxLayout(self)
        self.out = QPlainTextEdit(readOnly=True)
        v.addWidget(self.out)
        self.btn = QPushButton("Fermer", enabled=False)
        self.btn.clicked.connect(self.accept)
        v.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.p = QProcess(self)
        env = self.p.processEnvironment()
        env.insert("PYTHONUNBUFFERED", "1")
        if not env.contains("SUDO_ASKPASS") and shutil.which("ksshaskpass"):
            env.insert("SUDO_ASKPASS", shutil.which("ksshaskpass"))
        self.p.setProcessEnvironment(env)
        self.p.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.p.setStandardInputFile(QProcess.nullDevice())  # pas de tty → sudo -A (fenêtre de mot de passe)
        self.p.readyReadStandardOutput.connect(
            lambda: self.out.appendPlainText(bytes(self.p.readAllStandardOutput()).decode(errors="replace").rstrip()))
        self.p.finished.connect(self._done)
        self.p.start(args[0], args[1:])

    def _done(self, rc, _status):
        self.out.appendPlainText("\n✅ Terminé." if rc == 0 else f"\n⚠ Terminé avec des erreurs (code {rc}).")
        self.btn.setEnabled(True)
        self.finished.emit(rc)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dotfiles")
        self.resize(1080, 760)
        self.mode = UPDATES if core.load_state() else NEW
        self.mods, self.prof, self.st = {}, {}, {}
        self.cards: dict[str, ModuleCard] = {}
        self.checked: dict[str, bool] = {}

        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(18, 18, 18, 18)

        top = QHBoxLayout()
        self.title = QLabel("<span style='font-size:20px;font-weight:bold'>Dotfiles</span>")
        top.addWidget(self.title)
        top.addStretch()
        self.b_new = QPushButton("Tous les modules", checkable=True)
        self.b_upd = QPushButton("Mises à jour", checkable=True)
        for b, mode in ((self.b_new, NEW), (self.b_upd, UPDATES)):
            b.setMinimumWidth(190)
            b.clicked.connect(lambda _=False, m=mode: self.set_mode(m))
            top.addWidget(b)
        top.addSpacing(16)
        self.b_sync = QPushButton("⟳ Synchroniser")
        self.b_sync.clicked.connect(self.sync)
        top.addWidget(self.b_sync)
        self.b_firefox = QPushButton("Firefox…")
        self.b_firefox.clicked.connect(self.firefox_settings)
        top.addWidget(self.b_firefox)
        v.addLayout(top)

        self.subtitle = QLabel()
        self.subtitle.setStyleSheet(f"color:{MUTED};")
        v.addWidget(self.subtitle)
        self.private_status = QLabel()
        self.private_status.setWordWrap(True)
        self.private_status.setStyleSheet(f"color:{MUTED};")
        v.addWidget(self.private_status)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher dans tous les modules… (Ctrl+F)")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(lambda _: self.set_mode(self.mode))
        v.addWidget(self.search)
        self.search_shortcut = QShortcut(QKeySequence.StandardKey.Find, self)
        self.search_shortcut.activated.connect(self.search.setFocus)

        body = QHBoxLayout()
        self.cats = QListWidget()
        self.cats.setFixedWidth(210)
        self.cats.currentRowChanged.connect(lambda _: self.fill())
        body.addWidget(self.cats)
        self.area = QScrollArea()
        self.area.setWidgetResizable(True)
        body.addWidget(self.area, 1)
        v.addLayout(body, 1)

        bottom = QHBoxLayout()
        self.b_all = QPushButton("Tout cocher")
        self.b_all.clicked.connect(lambda: self.check_visible(True))
        self.b_none = QPushButton("Tout décocher")
        self.b_none.clicked.connect(lambda: self.check_visible(False))
        bottom.addWidget(self.b_all)
        bottom.addWidget(self.b_none)
        bottom.addStretch()
        self.b_apply = QPushButton("Appliquer", objectName="primary")
        self.b_apply.clicked.connect(self.apply)
        bottom.addWidget(self.b_apply)
        v.addLayout(bottom)

        self.scan = Scan()
        self.scan.done.connect(self.loaded)
        self.refresh()

    # ── données ──
    def refresh(self):
        self.subtitle.setText("Analyse de la machine…")
        self.b_apply.setEnabled(False)
        self.scan.run()

    def loaded(self, mods, prof, st):
        self.mods, self.prof, self.st = mods, prof, st
        self.private_status.setText(core.private_sync_label())
        self.reset_checks()
        self.set_mode(self.mode)

    def reset_checks(self):
        wanted = set(self.prof.get("modules", []))
        state = core.load_state()
        self.checked = {}
        for mid, s in self.st.items():
            if self.mode == NEW:
                self.checked[mid] = mid in wanted
            else:  # mises à jour : ce qui est dans le profil (ou déjà appliqué) et pas à jour
                self.checked[mid] = (mid in wanted or mid in state) and s in (core.UPDATE, core.ABSENT) \
                    and not (s == core.ABSENT and mid not in wanted)

    def visible_ids(self) -> list[str]:
        order = list(core.CATEGORIES)
        ids = sorted(self.mods, key=lambda i: (order.index(self.mods[i].category) if self.mods[i].category in order
                                                else 99, getattr(self.mods[i], "group", ""), self.mods[i].name.lower()))
        query = self.search.text().strip().casefold()
        if self.mode == UPDATES and not query:
            wanted = set(self.prof.get("modules", [])) | set(core.load_state())
            ids = [i for i in ids if self.st[i] != core.OK and (i in wanted or self.st[i] == core.DRIFT)]
        if query:
            ids = [i for i in ids if all(word in " ".join((self.mods[i].name, i,
                   self.mods[i].description, core.CATEGORIES.get(self.mods[i].category, ""),
                   getattr(self.mods[i], "group", ""))).casefold() for word in query.split())]
        return ids

    def set_mode(self, mode):
        changed = mode != self.mode
        self.mode = mode
        self.b_new.setChecked(mode == NEW)
        self.b_upd.setChecked(mode == UPDATES)
        if changed:
            self.cards = {}
            self.reset_checks()
        ids = self.visible_ids()
        cur = self.cats.currentItem().data(Qt.ItemDataRole.UserRole) if self.cats.currentItem() else None
        self.cats.blockSignals(True)
        self.cats.clear()
        counts = {}
        for i in ids:
            counts[self.mods[i].category] = counts.get(self.mods[i].category, 0) + 1
        item = QListWidgetItem(f"Tout  ({len(ids)})")
        item.setData(Qt.ItemDataRole.UserRole, None)
        self.cats.addItem(item)
        for cat, label in core.CATEGORIES.items():
            if counts.get(cat):
                it = QListWidgetItem(f"{label}  ({counts[cat]})")
                it.setData(Qt.ItemDataRole.UserRole, cat)
                self.cats.addItem(it)
        if self.search.text().strip():
            cur = None
        row = next((r for r in range(self.cats.count())
                    if self.cats.item(r).data(Qt.ItemDataRole.UserRole) == cur), 0)
        self.cats.setCurrentRow(row)
        self.cats.blockSignals(False)
        prof = self.prof.get("_name") or "aucun profil (dossier privé introuvable)"
        n_upd = sum(1 for i in ids if self.st[i] in (core.UPDATE, core.ABSENT, core.DRIFT))
        self.subtitle.setText(
            f"Machine : {prof}  ·  " + ("Tous les modules disponibles ; le profil est présélectionné."
                                       if mode == NEW else f"{n_upd} module(s) à traiter."))
        if self.search.text().strip():
            self.subtitle.setText(f"{len(ids)} résultat(s) dans tous les modules, y compris ceux à jour.")
        self.b_apply.setEnabled(True)
        self.fill()

    def fill(self):
        for mid, c in self.cards.items():
            self.checked[mid] = c.cb.isChecked()
        it = self.cats.currentItem()
        cat = it.data(Qt.ItemDataRole.UserRole) if it else None
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(6)
        self.cards = {}
        last_group = None
        for mid in self.visible_ids():
            m = self.mods[mid]
            if cat and m.category != cat:
                continue
            group = getattr(m, "group", None) if m.category == "apps" and not m.path else None
            if cat == "apps" and group and group != last_group:
                lay.addWidget(QLabel(f"<b style='color:{ACCENT}'>{group}</b>"))
                last_group = group
            card = ModuleCard(m, self.st[mid], self.checked.get(mid, False))
            self.cards[mid] = card
            lay.addWidget(card)
        if not self.cards:
            lay.addWidget(QLabel("✓ Rien à faire ici." if self.mode == UPDATES else "Aucun module."))
        lay.addStretch()
        self.area.setWidget(w)

    def check_visible(self, on):
        for c in self.cards.values():
            c.cb.setChecked(on)

    # ── actions ──
    def selection(self) -> list[str]:
        for mid, c in self.cards.items():
            self.checked[mid] = c.cb.isChecked()
        return [m for m, on in self.checked.items() if on]

    def apply(self):
        ids = self.selection()
        if not ids:
            QMessageBox.information(self, "Dotfiles", "Aucun module coché.")
            return
        names = "\n".join(f"• {self.mods[i].name}" for i in ids[:25]) + ("\n…" if len(ids) > 25 else "")
        if QMessageBox.question(self, "Appliquer", f"Appliquer {len(ids)} module(s) ?\n\n{names}") \
                != QMessageBox.StandardButton.Yes:
            return
        d = LogDialog(dotctl_cmd() + ["apply", *ids], f"Application de {len(ids)} module(s)", self)
        d.finished.connect(lambda _rc: self.refresh())
        d.show()

    def firefox_settings(self):
        from .firefox_gui import FirefoxDialog
        FirefoxDialog(self).exec()

    def sync(self):
        d = LogDialog(dotctl_cmd() + ["sync"], "Synchronisation", self)
        d.finished.connect(lambda _rc: self.refresh())
        d.show()


class Tray(QObject):
    """Icône de notification : synchro périodique, nouvelles versions, secrets qui expirent."""
    result = pyqtSignal(int, list, list)

    def __init__(self, app):
        super().__init__()
        self.win = None
        self.tray = QSystemTrayIcon(dot_icon(ACCENT))
        self.tray.setToolTip("Dotfiles")
        menu = QMenu()
        menu.addAction("Ouvrir", self.open)
        menu.addAction("Synchroniser maintenant", lambda: self.check(pull=True))
        menu.addSeparator()
        menu.addAction("Quitter", app.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda r: r == QSystemTrayIcon.ActivationReason.Trigger and self.open())
        self.result.connect(self.show_result)
        self.tray.show()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check)
        self.timer.start(6 * 3600 * 1000)
        QTimer.singleShot(20_000, self.check)
        self.last_msg = None

    def open(self):
        if not self.win:
            self.win = MainWindow()
        else:
            self.win.refresh()
        self.win.show()
        self.win.raise_()
        self.win.activateWindow()

    def check(self, pull=False):
        threading.Thread(target=self._check, args=(pull,), daemon=True).start()

    def _check(self, pull):
        if pull:
            core.sync(log=lambda *_: None)
        behind = sum(core.behind_count(r) for r in core.repos())
        prof = core.load_profile()
        env = core.context_env(prof)
        state = core.load_state()
        mods = core.load_modules()
        todo = [m for m in prof.get("modules", []) + list(state)
                if m in mods and core.status(mods[m], env, state) == core.UPDATE]
        self.result.emit(behind, sorted(set(todo)), core.expiring_secrets())

    def show_result(self, behind, todo, expiring):
        lines = []
        if behind:
            lines.append(f"{behind} nouveau(x) commit(s) à synchroniser")
        if todo:
            lines.append(f"{len(todo)} module(s) à mettre à jour : {', '.join(todo[:5])}")
        for key, date, left in expiring:
            lines.append(f"Secret {key} : {'expiré' if left < 0 else f'expire dans {left} j'} ({date})")
        color = "#f38ba8" if expiring else "#f9e2af" if (behind or todo) else ACCENT
        self.tray.setIcon(dot_icon(color))
        tip = "\n".join(lines) or "Dotfiles : tout est à jour"
        self.tray.setToolTip(tip)
        if lines and tip != self.last_msg:
            self.last_msg = tip
            self.tray.showMessage("Dotfiles", tip, QSystemTrayIcon.MessageIcon.Information, 10000)


def main(tray: bool = False):
    app = QApplication(sys.argv)
    app.setApplicationName("dotfiles")
    app.setDesktopFileName("dotfiles")
    app.setStyleSheet(STYLE)
    if tray:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            sys.exit("Pas de zone de notification disponible")
        app.setQuitOnLastWindowClosed(False)
        t = Tray(app)  # noqa: F841
    else:
        w = MainWindow()
        w.show()
    sys.exit(app.exec())
