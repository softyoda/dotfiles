#!/usr/bin/env python3
"""Local URI handler. A link opens a confirmation, never an automatic update."""
from pathlib import Path
import subprocess
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

app = QApplication(sys.argv[:1])
answer = QMessageBox.question(None, 'Mettre à jour Immich',
    'Mettre à jour le NAS et les workers vers la dernière version stable ?\n'
    'La base sera sauvegardée et le correctif OCR vérifié.')
if answer == QMessageBox.StandardButton.Yes:
    subprocess.Popen(['konsole', '--hold', '-e', sys.executable, '-u',
                      str(Path.home() / '.local/bin/immich-update.py')])
