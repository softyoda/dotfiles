"""Choix explicite du profil et des données Firefox à transporter."""
from pathlib import Path
import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout)
from . import firefox


class FirefoxDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Firefox — sauvegarde et restauration sélectives')
        self.resize(780, 670)
        layout = QVBoxLayout(self)
        help_text = QLabel('Fermez le profil Firefox concerné avant une sauvegarde ou une restauration.\n'
                          'Choisissez les éléments à transporter ; les autres restent inchangés.')
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        layout.addWidget(QLabel('Profil Firefox sur cet ordinateur :'))
        self.profile = QComboBox()
        for name, path in firefox.profiles().items():
            self.profile.addItem(name, str(path))
        layout.addWidget(self.profile)
        layout.addWidget(QLabel('Sauvegarde privée à restaurer :'))
        self.archive = QComboBox()
        layout.addWidget(self.archive)
        self.parts = {}
        for part, label in firefox.LABELS.items():
            cb = QCheckBox(label)
            cb.setChecked(part == 'prefs')
            self.parts[part] = cb
            layout.addWidget(cb)
        self.source = QComboBox()
        self.source.addItems(['Préférences du profil local (sauvegarder)',
                              'Préférences de la sauvegarde (restaurer)'])
        layout.addWidget(self.source)
        self.advanced = QCheckBox('Afficher aussi les autres préférences (décochées par défaut)')
        self.advanced.setToolTip('Certaines préférences internes contiennent des valeurs propres à cette machine ou à un compte.')
        layout.addWidget(self.advanced)
        layout.addWidget(QLabel('Préférences sélectionnables individuellement :'))
        self.prefs = QListWidget()
        layout.addWidget(self.prefs, 1)
        pref_buttons = QHBoxLayout()
        for label, checked in [('Tout cocher', True), ('Tout décocher', False)]:
            b = QPushButton(label)
            b.clicked.connect(lambda _=False, state=checked: self.select_prefs(state))
            pref_buttons.addWidget(b)
        layout.addLayout(pref_buttons)
        self.location = QLabel()
        self.location.setWordWrap(True)
        self.location.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.location)
        row = QHBoxLayout()
        self.save_button = QPushButton('Sauvegarder la sélection')
        self.save_button.clicked.connect(self.capture)
        row.addWidget(self.save_button)
        self.restore_button = QPushButton('Restaurer la sélection')
        self.restore_button.clicked.connect(self.restore)
        row.addWidget(self.restore_button)
        close = QPushButton('Fermer')
        close.clicked.connect(self.accept)
        row.addWidget(close)
        layout.addLayout(row)
        self.profile.currentIndexChanged.connect(self.load_prefs)
        self.archive.currentIndexChanged.connect(self.load_prefs)
        self.source.currentIndexChanged.connect(self.load_prefs)
        self.advanced.toggled.connect(self.load_prefs)
        self.refresh_archives()
        self.load_prefs()
        if not self.profile.count():
            self.location.setText('Aucun profil : lancez Firefox une première fois, fermez-le, puis rouvrez cet écran.')
            self.save_button.setEnabled(False)
            self.restore_button.setEnabled(False)

    def refresh_archives(self):
        self.archive.clear()
        for path in firefox.snapshots():
            try:
                info = json.loads(path.read_text())
                self.archive.addItem(f"{info['created']} — {info['profile']}", str(path.parent))
            except (OSError, ValueError, KeyError):
                continue
        try:
            self.location.setText(f'Destination : {firefox.archive_root()}\n'
                                  'Le transfert vers un autre ordinateur dépend de la synchronisation de ce dossier privé. '
                                  'Ces données ne sont jamais publiées sur GitHub.')
        except RuntimeError as e:
            self.location.setText(str(e))
        self.restore_button.setEnabled(self.archive.count() > 0 and self.profile.count() > 0)

    def load_prefs(self, *_):
        self.prefs.clear()
        try:
            if self.source.currentIndex() == 1:
                source = self.archive.currentData()
                p = Path(source) / 'prefs.json' if source else None
                values = json.loads(p.read_text()) if p and p.exists() else {}
            else:
                source = self.profile.currentData()
                values = (firefox.preferences(Path(source) / 'prefs.js') if self.advanced.isChecked()
                          else firefox.candidates(Path(source))) if source else {}
                values.pop('extensions.webextensions.uuids', None)
            for key, value in sorted(values.items()):
                item = QListWidgetItem(f'{key} = {json.dumps(value, ensure_ascii=False)[:160]}')
                item.setData(Qt.ItemDataRole.UserRole, key)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                selected = self.source.currentIndex() == 1 or key.startswith(firefox.PREF_PREFIXES)
                item.setCheckState(Qt.CheckState.Checked if selected else Qt.CheckState.Unchecked)
                self.prefs.addItem(item)
        except (OSError, ValueError) as e:
            QMessageBox.warning(self, 'Lecture des préférences', str(e))

    def select_prefs(self, checked):
        for i in range(self.prefs.count()):
            self.prefs.item(i).setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def selection(self):
        return [part for part, cb in self.parts.items() if cb.isChecked()]

    def keys(self):
        return [self.prefs.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.prefs.count())
                if self.prefs.item(i).checkState() == Qt.CheckState.Checked]

    def capture(self):
        if 'prefs' in self.selection() and self.source.currentIndex() != 0:
            self.source.setCurrentIndex(0)
            QMessageBox.information(self, 'Préférences', 'Sélectionnez les préférences locales à sauvegarder, puis réessayez.')
            return
        try:
            path = firefox.capture(Path(self.profile.currentData()), self.profile.currentText(),
                                   self.selection(), self.keys())
            self.refresh_archives()
            QMessageBox.information(self, 'Sauvegarde créée', f'Sauvegarde privée créée :\n{path}\n\n'
                                    'Vérifiez que votre outil de synchronisation a transféré ce dossier.')
        except (OSError, ValueError, RuntimeError, KeyError) as e:
            QMessageBox.warning(self, 'Sauvegarde impossible', str(e))

    def restore(self):
        if 'prefs' in self.selection() and self.source.currentIndex() != 1:
            self.source.setCurrentIndex(1)
            QMessageBox.information(self, 'Préférences', 'Sélectionnez les préférences sauvegardées à restaurer, puis réessayez.')
            return
        selected = self.selection()
        if not selected:
            QMessageBox.information(self, 'Firefox', 'Choisissez au moins un élément.')
            return
        if QMessageBox.question(self, 'Restaurer la sélection',
                f"Remplacer les éléments sélectionnés dans « {self.profile.currentText()} » ?\n\n"
                'Une copie des fichiers remplacés sera conservée dans le profil.\n'
                'Pour les extensions, utilisez une version de Firefox au moins aussi récente que la source.') \
                != QMessageBox.StandardButton.Yes:
            return
        try:
            backup = firefox.restore(Path(self.archive.currentData()), Path(self.profile.currentData()),
                                     selected, self.keys())
            QMessageBox.information(self, 'Restauration terminée',
                                    f'Copie de sécurité :\n{backup}\n\nRelancez Firefox. '
                                    'Si Firefox le demande, activez les extensions restaurées dans about:addons.')
        except (OSError, ValueError, RuntimeError, KeyError) as e:
            QMessageBox.warning(self, 'Restauration impossible', str(e))


def main():
    app = QApplication.instance() or QApplication([])
    dialog = FirefoxDialog()
    dialog.exec()
