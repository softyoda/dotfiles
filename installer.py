#!/usr/bin/env python3
import sys, os, subprocess, shutil, shlex
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QCheckBox, QFrame, QProgressBar,
    QPlainTextEdit, QStackedWidget, QMessageBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

DOTFILES = Path(__file__).parent
SECRETS_FILE = Path.home() / ".config" / "fish" / "secrets.fish"

APPS = {
    "Communication": [
        {"id": "discord",  "label": "Discord",   "desc": "Chat & gaming",           "method": "pacman",  "pkg": "discord",                               "default": True},
        {"id": "slack",    "label": "Slack",      "desc": "Chat pro",                "method": "flatpak", "pkg": "com.slack.Slack",                       "default": False},
        {"id": "element",  "label": "Element",    "desc": "Matrix / chiffré",        "method": "flatpak", "pkg": "im.riot.Riot",                          "default": False},
    ],
    "Productivité": [
        {"id": "obsidian",   "label": "Obsidian",    "desc": "Notes / knowledge base",  "method": "flatpak", "pkg": "md.obsidian.Obsidian",                  "default": True},
        {"id": "onlyoffice", "label": "OnlyOffice",  "desc": "Suite bureautique",        "method": "paru",    "pkg": "onlyoffice-bin",                        "default": True},
        {"id": "calibre",    "label": "Calibre",     "desc": "Gestion ebooks",           "method": "pacman",  "pkg": "calibre",                               "default": False},
        {"id": "librewolf",  "label": "LibreWolf",   "desc": "Firefox sans tracking",    "method": "paru",    "pkg": "librewolf-bin",                         "default": False},
        {"id": "dropbox",    "label": "Dropbox",     "desc": "Sync cloud",               "method": "pacman",  "pkg": "dropbox",                               "default": True},
        {"id": "variety",    "label": "Variety",     "desc": "Fond d'écran automatique", "method": "pacman",  "pkg": "variety",                               "default": True},
    ],
    "Développement": [
        {"id": "vscodium",      "label": "VSCodium",    "desc": "Éditeur de code",         "method": "pacman",  "pkg": "vscodium",                    "default": True},
        {"id": "git",           "label": "Git",         "desc": "Contrôle de version",     "method": "pacman",  "pkg": "git",                         "default": True},
        {"id": "meld",          "label": "Meld",        "desc": "Diff visuel",             "method": "pacman",  "pkg": "meld",                        "default": True},
        {"id": "alacritty",     "label": "Alacritty",   "desc": "Terminal GPU",            "method": "pacman",  "pkg": "alacritty",                   "default": False},
        {"id": "notepadqq",     "label": "Notepadqq",   "desc": "Éditeur texte avancé",    "method": "pacman",  "pkg": "notepadqq",                   "default": False},
        {"id": "sqlitebrowser", "label": "DB Browser",  "desc": "SQLite GUI",              "method": "pacman",  "pkg": "sqlitebrowser",               "default": False},
        {"id": "jan",           "label": "Jan",         "desc": "IA locale (LLM offline)", "method": "flatpak", "pkg": "ai.jan.Jan",                  "default": False},
        {"id": "claude-code",   "label": "Claude Code", "desc": "IA dans le terminal",     "method": "npm",     "pkg": "@anthropic-ai/claude-code",   "default": True},
    ],
    "Médias": [
        {"id": "vlc",           "label": "VLC",           "desc": "Lecteur vidéo universel",     "method": "pacman",  "pkg": "vlc",                             "default": True},
        {"id": "haruna",        "label": "Haruna",        "desc": "Lecteur vidéo KDE",           "method": "pacman",  "pkg": "haruna",                          "default": False},
        {"id": "smplayer",      "label": "SMPlayer",      "desc": "Lecteur vidéo avancé",        "method": "pacman",  "pkg": "smplayer",                        "default": False},
        {"id": "obs",           "label": "OBS Studio",    "desc": "Stream / enregistrement",     "method": "pacman",  "pkg": "obs-studio",                      "default": False},
        {"id": "spotify",       "label": "Spotify",       "desc": "Musique en streaming",        "method": "flatpak", "pkg": "com.spotify.Client",              "default": False},
        {"id": "spicetify",     "label": "Spicetify",     "desc": "Personnalise Spotify",        "method": "paru",    "pkg": "spicetify-cli",                   "default": False},
        {"id": "shotcut",       "label": "Shotcut",       "desc": "Montage vidéo",               "method": "pacman",  "pkg": "shotcut",                         "default": True},
        {"id": "mixxx",         "label": "Mixxx",         "desc": "DJ / mixage audio",           "method": "pacman",  "pkg": "mixxx",                           "default": False},
        {"id": "kid3",          "label": "Kid3",          "desc": "Éditeur tags audio",          "method": "pacman",  "pkg": "kid3",                            "default": False},
        {"id": "soundconverter","label": "SoundConverter","desc": "Convertisseur audio",         "method": "pacman",  "pkg": "soundconverter",                  "default": False},
        {"id": "freetube",      "label": "FreeTube",      "desc": "YouTube sans pub",            "method": "flatpak", "pkg": "io.freetubeapp.FreeTube",         "default": False},
        {"id": "tenacity",      "label": "Tenacity",      "desc": "Éditeur audio (Audacity)",    "method": "flatpak", "pkg": "org.tenacityaudio.Tenacity",      "default": False},
        {"id": "davinci",       "label": "DaVinci Resolve","desc": "Montage pro",               "method": "flatpak", "pkg": "com.blackmagicdesign.resolve",    "default": False},
    ],
    "3D / Graphisme": [
        {"id": "blender",      "label": "Blender Launcher", "desc": "Gère toutes versions Blender",  "method": "paru",    "pkg": "blender-launcher-v2-bin",       "default": True},
        {"id": "darktable",    "label": "Darktable",        "desc": "Développement RAW photo",        "method": "pacman",  "pkg": "darktable",                     "default": False},
        {"id": "gimp",         "label": "GIMP",             "desc": "Retouche image",                 "method": "pacman",  "pkg": "gimp",                          "default": False},
        {"id": "qgis",         "label": "QGIS",             "desc": "SIG / cartographie",             "method": "pacman",  "pkg": "qgis",                          "default": False},
        {"id": "cloudcompare", "label": "CloudCompare",     "desc": "Nuages de points 3D",            "method": "flatpak", "pkg": "org.cloudcompare.CloudCompare", "default": False},
        {"id": "orcaslicer",   "label": "OrcaSlicer",       "desc": "Slicer impression 3D",           "method": "flatpak", "pkg": "com.orcaslicer.OrcaSlicer",     "default": False},
    ],
    "Gaming": [
        {"id": "steam",       "label": "Steam",       "desc": "Plateforme de jeux",         "method": "pacman",  "pkg": "steam",       "default": True},
        {"id": "lutris",      "label": "Lutris",      "desc": "Launcher multi-plateformes", "method": "pacman",  "pkg": "lutris",      "default": False},
        {"id": "gamescope",   "label": "Gamescope",   "desc": "Compositeur Valve pour jeux","method": "pacman",  "pkg": "gamescope",   "default": False},
    ],
    "Outils": [
        {"id": "qbittorrent",   "label": "qBittorrent",    "desc": "Client BitTorrent",          "method": "pacman",  "pkg": "qbittorrent",                    "default": True},
        {"id": "kdeconnect",    "label": "KDE Connect",    "desc": "Téléphone <-> PC",           "method": "pacman",  "pkg": "kdeconnect",                     "default": True},
        {"id": "filezilla",     "label": "FileZilla",      "desc": "FTP / SFTP",                 "method": "pacman",  "pkg": "filezilla",                      "default": True},
        {"id": "scrcpy",        "label": "Scrcpy",         "desc": "Miroir écran Android",       "method": "pacman",  "pkg": "scrcpy",                         "default": False},
        {"id": "btop",          "label": "Btop",           "desc": "Moniteur système terminal",  "method": "pacman",  "pkg": "btop",                           "default": True},
        {"id": "gparted",       "label": "GParted",        "desc": "Gestion partitions",         "method": "pacman",  "pkg": "gparted",                        "default": False},
        {"id": "syncthing",     "label": "Syncthing",      "desc": "Sync P2P (alt. Dropbox)",    "method": "pacman",  "pkg": "syncthing",                      "default": False},
        {"id": "remmina",       "label": "Remmina",        "desc": "Bureau à distance RDP",      "method": "pacman",  "pkg": "remmina",                        "default": False},
        {"id": "rustdesk",      "label": "RustDesk",       "desc": "Bureau à distance moderne",  "method": "flatpak", "pkg": "com.rustdesk.RustDesk",          "default": False},
        {"id": "snapx",         "label": "SnapX",          "desc": "Screenshot / GIF (ShareX)",  "method": "flatpak", "pkg": "io.github.SnapXL.SnapX",         "default": True},
        {"id": "missioncenter", "label": "Mission Center", "desc": "Moniteur système GUI",       "method": "flatpak", "pkg": "io.missioncenter.MissionCenter", "default": True},
        {"id": "pavucontrol",   "label": "PavuControl",    "desc": "Contrôle volume PipeWire",   "method": "pacman",  "pkg": "pavucontrol",                    "default": True},
        {"id": "sigma",         "label": "Sigma",          "desc": "Gestionnaire de fichiers",   "method": "paru",    "pkg": "sigma-file-manager-bin",         "default": False},
    ],
}

BTN = """
    QPushButton {{ background:{bg}; color:{fg}; border-radius:10px; font-size:14px;
        font-weight:bold; border:none; padding:0 24px; }}
    QPushButton:hover {{ background:{hv}; }}
    QPushButton:disabled {{ background:#313244; color:#585b70; }}
"""

# ─── Helpers ────────────────────────────────────────────────────────────────

def is_installed(app):
    m, pkg = app["method"], app["pkg"]
    if m in ("pacman", "paru"):
        return subprocess.run(["pacman", "-Qq", pkg], capture_output=True).returncode == 0
    if m == "flatpak":
        r = subprocess.run(["flatpak", "list", "--app", "--columns=application"],
                           capture_output=True, text=True)
        return pkg in r.stdout
    if m == "npm":
        return shutil.which("claude") is not None
    return False

def read_existing_api_key():
    if SECRETS_FILE.exists():
        for line in SECRETS_FILE.read_text().splitlines():
            if "ANTHROPIC_API_KEY" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    return parts[1].strip().strip('"').strip("'")
    return ""

def save_api_key(key):
    SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if SECRETS_FILE.exists():
        lines = [l for l in SECRETS_FILE.read_text().splitlines()
                 if "ANTHROPIC_API_KEY" not in l]
    lines.append(f'set -gx ANTHROPIC_API_KEY "{key}"')
    SECRETS_FILE.write_text("\n".join(lines) + "\n")

def get_available_sessions():
    sessions = []
    for d in ("/usr/share/wayland-sessions", "/usr/share/xsessions"):
        try:
            for f in sorted(Path(d).glob("*.desktop")):
                name = f.stem
                for line in f.read_text().splitlines():
                    if line.startswith("Name="):
                        name = line[5:]
                        break
                sessions.append((f.stem, f"{name}  ({Path(d).name})"))
        except Exception:
            pass
    return sessions

def get_current_session():
    try:
        for line in Path("/etc/sddm.conf.d/autologin.conf").read_text().splitlines():
            if line.startswith("Session="):
                return line[8:].strip()
    except Exception:
        pass
    return "plasma"


# ─── Workers ────────────────────────────────────────────────────────────────

class ShellWorker(QThread):
    log = pyqtSignal(str)
    done = pyqtSignal(int)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        proc = subprocess.Popen(self.cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            self.log.emit(line.rstrip())
        proc.wait()
        self.done.emit(proc.returncode)


class InstallWorker(QThread):
    log = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, apps):
        super().__init__()
        self.apps = apps

    def _stream(self, cmd):
        proc = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            self.log.emit(line.rstrip())
        proc.wait()
        return proc.returncode

    def run(self):
        by = {}
        for a in self.apps:
            by.setdefault(a["method"], []).append(a)

        # ── pacman + npm → un seul pkexec ──────────────────────────────────
        privileged = []
        if "pacman" in by:
            pkgs = " ".join(a["pkg"] for a in by["pacman"])
            self.log.emit(f"\n▶ Pacman : {pkgs}")
            privileged.append(f"pacman -S --needed --noconfirm {pkgs}")
        if "npm" in by:
            npm_pkgs = " ".join(a["pkg"] for a in by["npm"])
            self.log.emit(f"▶ npm : {npm_pkgs}")
            privileged.append("command -v node || pacman -S --needed --noconfirm nodejs npm")
            privileged.append(f"npm install -g {npm_pkgs}")
        if privileged:
            rc = self._stream("pkexec bash -c " + shlex.quote("; ".join(privileged)))
            self.log.emit("✓ Packages système installés" if rc == 0
                          else f"✗ Erreur pacman/npm (code {rc})")

        # ── paru (AUR) → une seule invocation, paru gère sudo lui-même ──────
        if "paru" in by:
            pkgs = " ".join(a["pkg"] for a in by["paru"])
            self.log.emit(f"\n▶ AUR : {pkgs}")
            rc = self._stream(f"paru -S --needed --noconfirm {pkgs}")
            self.log.emit("✓ AUR installé" if rc == 0 else f"✗ Erreur paru (code {rc})")

        # ── flatpak --system (pkexec, une seule auth pour tout) ─────────────
        if "flatpak" in by:
            flatpak_parts = [
                "flatpak remote-add --system --if-not-exists flathub "
                "https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true"
            ]
            for app in by["flatpak"]:
                flatpak_parts.append(
                    f"flatpak install --system -y --noninteractive flathub {app['pkg']}"
                )
            labels = ", ".join(a["label"] for a in by["flatpak"])
            self.log.emit(f"\n▶ Flatpak : {labels}")
            rc = self._stream("pkexec bash -c " + shlex.quote("; ".join(flatpak_parts)))
            self.log.emit("✓ Flatpak installé" if rc == 0 else f"✗ Erreur flatpak (code {rc})")

        self.done.emit()


# ─── Widgets réutilisables ──────────────────────────────────────────────────

class CategoryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton { text-align:left; padding:0 16px; border:none; border-radius:8px;
                font-size:14px; color:#cdd6f4; background:transparent; }
            QPushButton:hover  { background:#313244; }
            QPushButton:checked{ background:#45475a; color:#cba6f7; font-weight:bold; }
        """)


class AppCard(QFrame):
    def __init__(self, app, installed, parent=None):
        super().__init__(parent)
        self.app = app
        self.setStyleSheet("""
            QFrame { background:#1e1e2e; border-radius:10px; border:1px solid #313244; }
            QFrame:hover { border:1px solid #45475a; }
        """)
        self.setFixedHeight(68)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(app["default"] or installed)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator { width:20px; height:20px; border-radius:6px;
                border:2px solid #585b70; background:#181825; }
            QCheckBox::indicator:checked { background:#cba6f7; border-color:#cba6f7; }
            QCheckBox::indicator:hover   { border-color:#89b4fa; }
        """)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        name = QLabel(app["label"])
        name.setStyleSheet("color:#cdd6f4; font-size:14px; font-weight:600; background:transparent; border:none;")
        desc = QLabel(app["desc"])
        desc.setStyleSheet("color:#6c7086; font-size:12px; background:transparent; border:none;")
        text_col.addWidget(name)
        text_col.addWidget(desc)

        badge_text  = {"pacman":"pacman","paru":"AUR","flatpak":"Flatpak","npm":"npm"}.get(app["method"],"")
        badge_color = {"pacman":"#89dceb","paru":"#f38ba8","flatpak":"#a6e3a1","npm":"#f9e2af"}.get(app["method"],"#cdd6f4")
        badge = QLabel(badge_text)
        badge.setFixedHeight(22)
        badge.setStyleSheet(f"QLabel{{color:{badge_color};font-size:11px;font-weight:bold;"
                            f"background:transparent;border:1px solid {badge_color};"
                            f"border-radius:4px;padding:0 6px;}}")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.checkbox)
        layout.addLayout(text_col, 1)
        if installed:
            inst = QLabel("✓ installé")
            inst.setStyleSheet("color:#a6e3a1;font-size:11px;background:transparent;border:none;")
            layout.addWidget(inst)
        layout.addWidget(badge)

    def is_checked(self):
        return self.checkbox.isChecked()


class LogWindow(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle(title or "En cours…")
        self.setMinimumSize(700, 450)
        self.setStyleSheet("background:#1e1e2e;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QPlainTextEdit{background:#181825;color:#cdd6f4;border-radius:8px;
                font-family:monospace;font-size:13px;padding:10px;border:none;}
        """)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setStyleSheet("""
            QProgressBar{border-radius:4px;background:#313244;height:6px;text-align:center;}
            QProgressBar::chunk{background:#cba6f7;border-radius:4px;}
        """)

        self.close_btn = QPushButton("Fermer")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet(BTN.format(bg="#cba6f7", fg="#1e1e2e", hv="#d0bcff"))

        layout.addWidget(self.log)
        layout.addWidget(self.progress)
        layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def append(self, text):
        self.log.appendPlainText(text)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def finish(self, rc=0):
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.close_btn.setEnabled(True)
        self.append("\n✅ Terminé !" if rc == 0 else f"\n⚠ Terminé avec erreurs (code {rc})")


# ─── Pages ──────────────────────────────────────────────────────────────────

class ApiKeyPage(QWidget):
    confirmed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(0)
        layout.addStretch()

        title = QLabel("Clé API Anthropic")
        title.setStyleSheet("color:#cdd6f4;font-size:24px;font-weight:bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel(
            "Nécessaire pour Claude Code.\n"
            "Obtiens ta clé sur console.anthropic.com → API Keys.\n"
            "Elle sera sauvegardée dans ~/.config/fish/secrets.fish"
        )
        subtitle.setStyleSheet("color:#6c7086;font-size:13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        self.field = QLineEdit()
        self.field.setPlaceholderText("sk-ant-api03-…")
        self.field.setEchoMode(QLineEdit.EchoMode.Password)
        self.field.setFixedHeight(48)
        self.field.setStyleSheet("""
            QLineEdit{background:#1e1e2e;color:#cdd6f4;border:1px solid #313244;
                border-radius:10px;font-size:14px;padding:0 16px;}
            QLineEdit:focus{border-color:#cba6f7;}
        """)
        existing = read_existing_api_key()
        if existing:
            self.field.setText(existing)

        show_btn = QPushButton("Afficher / masquer")
        show_btn.setCheckable(True)
        show_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        show_btn.setStyleSheet("QPushButton{background:transparent;color:#6c7086;border:none;font-size:12px;}"
                               "QPushButton:hover{color:#cdd6f4;}")
        show_btn.toggled.connect(lambda on: self.field.setEchoMode(
            QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password))

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("font-size:12px;")

        btn_row = QHBoxLayout()
        skip_btn = QPushButton("Passer (configurer plus tard)")
        skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        skip_btn.setFixedHeight(44)
        skip_btn.setStyleSheet(BTN.format(bg="#313244", fg="#cdd6f4", hv="#45475a"))
        skip_btn.clicked.connect(self.confirmed.emit)

        save_btn = QPushButton("Sauvegarder et continuer  →")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet(BTN.format(bg="#cba6f7", fg="#1e1e2e", hv="#d0bcff"))
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(skip_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)

        layout.addWidget(title)
        layout.addSpacing(12)
        layout.addWidget(subtitle)
        layout.addSpacing(32)
        layout.addWidget(self.field)
        layout.addSpacing(6)
        layout.addWidget(show_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(8)
        layout.addWidget(self.status)
        layout.addSpacing(24)
        layout.addLayout(btn_row)
        layout.addStretch()

    def _save(self):
        key = self.field.text().strip()
        if not key:
            self.status.setText("Clé vide — utilise 'Passer' pour configurer plus tard.")
            self.status.setStyleSheet("color:#f38ba8;font-size:12px;")
            return
        save_api_key(key)
        self.status.setText("✓ Clé sauvegardée dans ~/.config/fish/secrets.fish")
        self.status.setStyleSheet("color:#a6e3a1;font-size:12px;")
        self.confirmed.emit()


class KdeEnvPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Environnement KDE Plasma")
        title.setStyleSheet("color:#cdd6f4;font-size:20px;font-weight:bold;")
        layout.addWidget(title)

        desc = QLabel(
            "Sauvegarde et restaure ta configuration KDE complète : thème, icônes, "
            "raccourcis, panels, splash screen Watch_Dogs et paramètres système."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#6c7086;font-size:13px;")
        layout.addWidget(desc)

        # ── Ce qui est sauvegardé ──
        saved_frame = self._section("Ce qui est sauvegardé / restauré", [
            ("Config KDE",    "kdeglobals, kwinrc, plasmarc, plasmashellrc, kglobalshortcutsrc…"),
            ("Splash screen", "Watch_Dogs_Theme → kde/look-and-feel/"),
            ("Icônes",        "papirus-icon-theme (pacman)  +  we10x-icon-theme-git (AUR)"),
            ("Thème CachyOS", "cachyos-emerald-kde-theme-git, cachyos-iridescent-kde"),
        ])
        layout.addWidget(saved_frame)

        # ── Session SDDM ──
        sessions = get_available_sessions()
        if sessions:
            sess_frame = self._section("Session par défaut (autologin SDDM)", [])
            sess_layout = sess_frame.layout()

            self.session_combo = QComboBox()
            self.session_combo.setFixedHeight(36)
            self.session_combo.setStyleSheet("""
                QComboBox{background:#313244;color:#cdd6f4;border:1px solid #45475a;
                    border-radius:8px;padding:0 12px;font-size:13px;}
                QComboBox::drop-down{border:none;}
                QComboBox QAbstractItemView{background:#313244;color:#cdd6f4;border:1px solid #45475a;}
            """)
            current = get_current_session()
            for sid, sname in sessions:
                self.session_combo.addItem(sname, sid)
                if sid == current:
                    self.session_combo.setCurrentIndex(self.session_combo.count() - 1)

            apply_sess = QPushButton("Appliquer")
            apply_sess.setFixedHeight(36)
            apply_sess.setCursor(Qt.CursorShape.PointingHandCursor)
            apply_sess.setStyleSheet(BTN.format(bg="#45475a", fg="#cdd6f4", hv="#585b70"))
            apply_sess.clicked.connect(self._apply_session)

            row = QHBoxLayout()
            row.addWidget(self.session_combo, 1)
            row.addWidget(apply_sess)
            sess_layout.addLayout(row)
            layout.addWidget(sess_frame)

        # ── Boutons backup / restore ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        backup_btn = QPushButton("⬆  Sauvegarder env actuel → repo")
        backup_btn.setFixedHeight(48)
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.setStyleSheet(BTN.format(bg="#89b4fa", fg="#1e1e2e", hv="#74c7ec"))
        backup_btn.clicked.connect(self._backup)

        restore_btn = QPushButton("⬇  Restaurer depuis repo")
        restore_btn.setFixedHeight(48)
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.setStyleSheet(BTN.format(bg="#a6e3a1", fg="#1e1e2e", hv="#94e2d5"))
        restore_btn.clicked.connect(self._restore)

        btn_row.addWidget(backup_btn)
        btn_row.addWidget(restore_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

    def _section(self, title, rows):
        frame = QFrame()
        frame.setStyleSheet("QFrame{background:#1e1e2e;border-radius:10px;border:1px solid #313244;}")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(8)

        lbl = QLabel(title)
        lbl.setStyleSheet("color:#cba6f7;font-size:13px;font-weight:bold;border:none;background:transparent;")
        fl.addWidget(lbl)

        for key, val in rows:
            row = QHBoxLayout()
            k = QLabel(key)
            k.setFixedWidth(120)
            k.setStyleSheet("color:#cdd6f4;font-size:12px;font-weight:600;border:none;background:transparent;")
            v = QLabel(val)
            v.setStyleSheet("color:#6c7086;font-size:12px;border:none;background:transparent;")
            v.setWordWrap(True)
            row.addWidget(k)
            row.addWidget(v, 1)
            fl.addLayout(row)

        return frame

    def _backup(self):
        self._run(f"bash {DOTFILES}/scripts/kde-backup.sh", "Sauvegarde KDE")

    def _restore(self):
        self._run(f"bash {DOTFILES}/scripts/kde-restore.sh", "Restauration KDE")

    def _apply_session(self):
        sid = self.session_combo.currentData()
        user = os.environ.get("USER", "")
        conf = f"[Autologin]\\nUser={user}\\nSession={sid}\\n"
        cmd = (f"pkexec bash -c 'mkdir -p /etc/sddm.conf.d && "
               f"printf \"{conf}\" > /etc/sddm.conf.d/autologin.conf'")
        self._run(cmd, f"Session SDDM → {sid}")

    def _run(self, cmd, title):
        self._log_win = LogWindow(title, self.window())
        self._log_win.show()
        self._worker = ShellWorker(cmd)
        self._worker.log.connect(self._log_win.append)
        self._worker.done.connect(self._log_win.finish)
        self._worker.start()


class AppsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = {}
        self._cat_index = {}
        self._current_cat = "__kde__"
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background:#11111b;border-right:1px solid #1e1e2e;")
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(10, 20, 10, 20)
        sb.setSpacing(4)

        logo = QLabel("✦  Dotfiles")
        logo.setStyleSheet("color:#cba6f7;font-size:17px;font-weight:bold;padding:0 6px 12px 6px;")
        sb.addWidget(logo)

        self.cat_buttons = {}

        # Bouton spécial KDE
        kde_btn = CategoryButton("  KDE Plasma")
        kde_btn.clicked.connect(lambda: self._select("__kde__"))
        kde_btn.setChecked(True)
        self.cat_buttons["__kde__"] = kde_btn
        sb.addWidget(kde_btn)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#313244;border:none;max-height:1px;margin:6px 6px;")
        sb.addWidget(sep)

        # Catégories apps
        for cat in APPS:
            btn = CategoryButton(cat)
            btn.clicked.connect(lambda _, c=cat: self._select(c))
            sb.addWidget(btn)
            self.cat_buttons[cat] = btn

        sb.addStretch()

        self.install_btn = QPushButton("⬇  Installer")
        self.install_btn.setFixedHeight(44)
        self.install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_btn.setStyleSheet(BTN.format(bg="#cba6f7", fg="#1e1e2e", hv="#d0bcff"))
        self.install_btn.clicked.connect(self._install)
        sb.addWidget(self.install_btn)

        # ── Content ───────────────────────────────────────────────────────────
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 24, 28, 24)
        cl.setSpacing(16)

        # Sel all/none (caché sur la page KDE)
        self.sel_row = QWidget()
        sel_layout = QHBoxLayout(self.sel_row)
        sel_layout.setContentsMargins(0, 0, 0, 0)
        sel_all  = QPushButton("Tout cocher")
        sel_none = QPushButton("Tout décocher")
        for b in (sel_all, sel_none):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("QPushButton{background:#313244;color:#cdd6f4;border-radius:6px;"
                            "padding:5px 14px;font-size:12px;border:none;}"
                            "QPushButton:hover{background:#45475a;}")
        sel_all.clicked.connect(lambda: self._select_all(True))
        sel_none.clicked.connect(lambda: self._select_all(False))
        sel_layout.addWidget(sel_all)
        sel_layout.addWidget(sel_none)
        sel_layout.addStretch()

        self.stack = QStackedWidget()

        # Page 0 : KDE env
        self.kde_page = KdeEnvPage()
        self.stack.addWidget(self.kde_page)

        # Pages apps (index 1…)
        for i, (cat, apps) in enumerate(APPS.items()):
            page = QWidget()
            pl = QVBoxLayout(page)
            pl.setSpacing(8)
            pl.setContentsMargins(0, 0, 0, 0)
            self.cards[cat] = []
            for app in apps:
                card = AppCard(app, is_installed(app))
                pl.addWidget(card)
                self.cards[cat].append(card)
            pl.addStretch()

            scroll = QScrollArea()
            scroll.setWidget(page)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background:transparent;")
            self.stack.addWidget(scroll)
            self._cat_index[cat] = i + 1

        cl.addWidget(self.sel_row)
        cl.addWidget(self.stack, 1)

        root.addWidget(sidebar)
        root.addWidget(content, 1)

        # Démarre sur la page KDE, sel_row caché
        self.stack.setCurrentIndex(0)
        self.sel_row.setVisible(False)
        self.install_btn.setVisible(False)

    def _select(self, cat):
        for c, btn in self.cat_buttons.items():
            btn.setChecked(c == cat)
        if cat == "__kde__":
            self.stack.setCurrentIndex(0)
            self.sel_row.setVisible(False)
            self.install_btn.setVisible(False)
        else:
            self.stack.setCurrentIndex(self._cat_index[cat])
            self.sel_row.setVisible(True)
            self.install_btn.setVisible(True)
        self._current_cat = cat

    def _select_all(self, state):
        for card in self.cards.get(self._current_cat, []):
            card.checkbox.setChecked(state)

    def _install(self):
        to_install = [
            card.app
            for cards in self.cards.values()
            for card in cards
            if card.is_checked() and not is_installed(card.app)
        ]
        if not to_install:
            QMessageBox.information(self, "Rien à faire",
                "Toutes les apps cochées sont déjà installées.")
            return

        names = "\n".join(f"  • {a['label']}" for a in to_install)
        reply = QMessageBox.question(self, "Confirmer l'installation",
            f"Installer {len(to_install)} app(s) ?\n\n{names}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._log_win = LogWindow("Installation en cours…", self.window())
        self._log_win.show()
        self._worker = InstallWorker(to_install)
        self._worker.log.connect(self._log_win.append)
        self._worker.done.connect(lambda: self._log_win.finish(0))
        self._worker.start()


# ─── Fenêtre principale ─────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dotfiles Installer")
        self.setMinimumSize(960, 660)
        self.setStyleSheet("""
            QMainWindow,QWidget{background:#181825;color:#cdd6f4;font-family:sans-serif;}
            QScrollArea{border:none;background:transparent;}
            QScrollBar:vertical{background:#181825;width:8px;border-radius:4px;}
            QScrollBar::handle:vertical{background:#313244;border-radius:4px;}
        """)

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.api_page = ApiKeyPage()
        self.api_page.confirmed.connect(self._show_apps)
        self.pages.addWidget(self.api_page)

        self.apps_page = AppsPage()
        self.pages.addWidget(self.apps_page)

        self.pages.setCurrentIndex(0)

    def _show_apps(self):
        self.pages.setCurrentIndex(1)


if __name__ == "__main__":
    os.chdir(DOTFILES)
    app = QApplication(sys.argv)
    app.setApplicationName("Dotfiles Installer")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
