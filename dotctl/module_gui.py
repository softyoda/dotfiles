"""Formulaire partagé : options de module, sous-parties et documentation."""
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QFileDialog,
                             QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QPlainTextEdit, QPushButton, QScrollArea,
                             QTabWidget, QTextBrowser, QVBoxLayout, QWidget)
from . import core, options


def agent_reference(module: core.Module) -> str:
    root_id = module.parent or module.id
    lines = [f'Identifiant Dotfiles : {module.id}',
             f'Inspecter : dotctl info {module.id} --json',
             f'Prévisualiser : dotctl plan {module.id} --json',
             f'Appliquer : dotctl apply {module.id}']
    if module.path:
        lines += [f'Manifeste : modules/{root_id}/module.toml',
                  f'README : https://github.com/softyoda/dotfiles/blob/master/modules/{root_id}/README.md']
    lines.append('Réglages privés : dossier indiqué dans ~/.config/dotfiles/private-path ; settings/<hostname>.json.')
    return '\n'.join(lines)


class ModuleDialog(QDialog):
    APPLY = 2

    def __init__(self, module: core.Module, parent=None):
        super().__init__(parent)
        self.module = module
        self.setWindowTitle(module.name)
        self.resize(850, 730)
        self.env = core.context_env()
        self.part_checks = {}
        self.editors = {}
        layout = QVBoxLayout(self)
        title = QLabel(module.description)
        title.setWordWrap(True)
        layout.addWidget(title)
        tools = QHBoxLayout()
        tools.addWidget(QLabel(module.id))
        copy = QPushButton('Copier la référence pour un agent')
        copy.clicked.connect(lambda: QApplication.clipboard().setText(agent_reference(module)))
        tools.addWidget(copy)
        layout.addLayout(tools)
        tabs = QTabWidget()
        layout.addWidget(tabs, 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        body = QVBoxLayout(content)
        body.addWidget(QLabel('Décocher signifie ne pas appliquer cette partie ; cela ne désinstalle rien.'))
        self.add_fields(module, body)
        selected = set(options.selected(module))
        for part in module.parts:
            group = QGroupBox()
            group_layout = QVBoxLayout(group)
            row = QHBoxLayout()
            check = QCheckBox(part.name)
            check.setChecked(part.id in selected)
            self.part_checks[part.id] = check
            row.addWidget(check, 1)
            copy_id = QPushButton('Copier ID')
            copy_id.setToolTip(part.id)
            copy_id.clicked.connect(lambda _=False, mid=part.id: QApplication.clipboard().setText(mid))
            row.addWidget(copy_id)
            agent = QPushButton('Pour un agent')
            agent.clicked.connect(lambda _=False, m=part: QApplication.clipboard().setText(agent_reference(m)))
            row.addWidget(agent)
            group_layout.addLayout(row)
            desc = QLabel(part.description + ('\nDépendances : ' + ', '.join(part.requires) if part.requires else ''))
            desc.setWordWrap(True)
            group_layout.addWidget(desc)
            fields = QWidget()
            field_layout = QVBoxLayout(fields)
            field_layout.setContentsMargins(0, 0, 0, 0)
            self.add_fields(part, field_layout)
            fields.setEnabled(check.isChecked())
            check.toggled.connect(fields.setEnabled)
            group_layout.addWidget(fields)
            body.addWidget(group)
        if not module.parts:
            note = QLabel('Ce module ne déclare pas de sous-parties. Les réglages ci-dessus concernent le module entier.')
            note.setWordWrap(True)
            body.addWidget(note)
        if module.manual:
            note = QLabel('Des étapes restent à faire dans l’application (connexion, appairage…). Voir l’onglet README.')
            note.setWordWrap(True)
            body.addWidget(note)
        body.addStretch()
        scroll.setWidget(content)
        tabs.addTab(scroll, 'Options et sous-parties')
        readme = QTextBrowser()
        readme.setOpenExternalLinks(True)
        readme.setMarkdown(module.readme() or 'Aucune documentation supplémentaire.')
        tabs.addTab(readme, 'README')
        self.preview = QPlainTextEdit(readOnly=True)
        tabs.addTab(self.preview, 'Aperçu')
        self.storage = QLabel(f'Réglages privés par machine : {options.path() or "dossier privé non configuré"}')
        self.storage.setWordWrap(True)
        layout.addWidget(self.storage)
        buttons = QHBoxLayout()
        preview = QPushButton('Voir ce qui sera appliqué')
        preview.clicked.connect(lambda: self.show_plan(tabs))
        buttons.addWidget(preview)
        save = QPushButton('Enregistrer les choix')
        save.clicked.connect(lambda: self.save(False))
        buttons.addWidget(save)
        apply = QPushButton('Appliquer cette sélection')
        apply.clicked.connect(lambda: self.save(True))
        buttons.addWidget(apply)
        cancel = QPushButton('Annuler')
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)

    def add_fields(self, module, layout):
        fields = options.fields(module)
        if not fields:
            return
        form = QFormLayout()
        values = core.module_env(module, self.env)
        for spec in fields:
            container = QWidget()
            row = QHBoxLayout(container)
            row.setContentsMargins(0, 0, 0, 0)
            initial = values.get(spec.key, '')
            if spec.type == 'bool':
                editor = QCheckBox()
                editor.setChecked(str(initial).lower() == 'true')
            elif spec.type == 'choice':
                editor = QComboBox()
                editor.addItem('— Choisir —', '')
                for choice in spec.choices:
                    editor.addItem(choice, choice)
                editor.setCurrentIndex(max(0, editor.findData(initial)))
            else:
                editor = QLineEdit(str(initial))
                if spec.type == 'secret':
                    editor.setEchoMode(QLineEdit.EchoMode.Password)
                if spec.type == 'path':
                    browse = QPushButton('Parcourir…')
                    browse.clicked.connect(lambda _=False, e=editor, s=spec: self.browse(e, s))
                    row.addWidget(browse)
            editor.setToolTip(spec.help + '\n' + spec.key)
            row.insertWidget(0, editor, 1)
            self.editors[(module.id, spec.key)] = (spec, editor, initial)
            label = (spec.label or spec.key) + (' *' if spec.required else '')
            form.addRow(label, container)
            if spec.help:
                help_label = QLabel(spec.help)
                help_label.setWordWrap(True)
                form.addRow('', help_label)
        layout.addLayout(form)

    def browse(self, editor, spec):
        if spec.path_kind == 'file':
            value, _ = QFileDialog.getOpenFileName(self, spec.label, str(Path(editor.text() or '~').expanduser()))
        else:
            value = QFileDialog.getExistingDirectory(self, spec.label, str(Path(editor.text() or '~').expanduser()))
        if value:
            editor.setText(value)

    def collect(self):
        parts = [mid for mid, check in self.part_checks.items() if check.isChecked()]
        active = {self.module.id, *parts}
        values, changed = {}, {}
        for (mid, key), (spec, editor, initial) in self.editors.items():
            if mid not in active:
                continue
            raw = editor.isChecked() if spec.type == 'bool' else editor.currentData() if spec.type == 'choice' else editor.text()
            value = spec.normalize(raw)
            values[key] = value
            try:
                original = spec.normalize(initial)
            except ValueError:
                original = None
            if value != original:
                changed[key] = value
        return parts, values, changed

    def show_plan(self, tabs):
        try:
            parts, values, _ = self.collect()
            overrides = {self.module.id: parts} if self.module.parts else None
            plan = core.application_plan([self.module.id], overrides, values)
            # Le plan contient les schémas et chemins déclarés, jamais les valeurs privées.
            self.preview.setPlainText(json.dumps(plan, indent=2, ensure_ascii=False))
            tabs.setCurrentIndex(2)
        except (ValueError, OSError, KeyError) as error:
            QMessageBox.warning(self, 'Réglages à compléter', str(error))

    def save(self, apply):
        try:
            parts, _, changed = self.collect()
            if apply and QMessageBox.question(self, 'Appliquer',
                    'Enregistrer ces choix puis appliquer cette sélection et ses dépendances ?') != QMessageBox.StandardButton.Yes:
                return
            if changed or self.module.parts:
                options.save(self.module, changed, parts if self.module.parts else None)
            self.done(self.APPLY if apply else QDialog.DialogCode.Accepted)
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, 'Enregistrement impossible', str(error))
