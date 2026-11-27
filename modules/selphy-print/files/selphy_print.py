import os
import re
import sys
import time
import uuid
import shutil
import tempfile
import threading
import subprocess

from PySide6.QtCore import Qt, QPointF, QRectF, QRect, QSettings, QSize, QTimer, QObject, Signal
from PySide6.QtGui import (QImage, QImageReader, QPainter, QColor, QPen, QKeySequence, QShortcut,
                           QPainterPath, QIcon, QPixmap, QTransform, QFont, QBrush,
                           QLinearGradient, QGuiApplication)
from PySide6.QtPrintSupport import QPrinterInfo
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QComboBox, QPushButton,
                               QFileDialog, QDoubleSpinBox, QDialog, QFormLayout,
                               QDialogButtonBox, QToolButton, QHBoxLayout, QVBoxLayout, QLabel,
                               QFrame, QScrollArea, QGraphicsDropShadowEffect, QSizePolicy, QMenu)

DPI = 300
PAPER_MM = (148.0, 100.0)  # postcard, landscape
# Measured on a SELPHY CP1500 borderless postcard, tabs removed (mm cut from a landscape image).
CROP_DEFAULT = {"crop/top": 3.45, "crop/right": 5.7, "crop/bottom": 3.0, "crop/left": 4.0}
EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp", ".heic")
ACCENT = "#3b82f6"
WIN = sys.platform == "win32"

WIN_PRINT_PS1 = r'''
param([string]$Image,[string]$Printer,[int]$Copies=1,[string]$Name="SelphyPrint")
Add-Type -AssemblyName PresentationCore,PresentationFramework,ReachFramework,System.Printing
$q=New-Object System.Printing.PrintQueue((New-Object System.Printing.LocalPrintServer),$Printer)
$t=$q.UserPrintTicket.Clone()
$wDip=100.0/25.4*96; $hDip=148.0/25.4*96
$t.PageMediaSize=New-Object System.Printing.PageMediaSize([System.Printing.PageMediaSizeName]::JapanHagakiPostcard,$wDip,$hDip)
$t.PageBorderless=[System.Printing.PageBorderless]::Borderless
$t.PageMediaType=[System.Printing.PageMediaType]::Photographic
$t.PageOrientation=[System.Printing.PageOrientation]::Portrait
$t.CopyCount=$Copies
$t=$q.MergeAndValidatePrintTicket($q.UserPrintTicket,$t).ValidatedPrintTicket
$bmp=New-Object System.Windows.Media.Imaging.BitmapImage
$bmp.BeginInit(); $bmp.CacheOption='OnLoad'; $bmp.UriSource=New-Object Uri($Image); $bmp.EndInit()
$dv=New-Object System.Windows.Media.DrawingVisual
$dc=$dv.RenderOpen()
if ($bmp.PixelWidth -gt $bmp.PixelHeight) {
  $dc.PushTransform((New-Object System.Windows.Media.RotateTransform(90,0,0)))
  $dc.PushTransform((New-Object System.Windows.Media.TranslateTransform(0,-$wDip)))
  $dc.DrawImage($bmp,(New-Object System.Windows.Rect(0,0,$hDip,$wDip)))
  $dc.Pop(); $dc.Pop()
} else {
  $dc.DrawImage($bmp,(New-Object System.Windows.Rect(0,0,$wDip,$hDip)))
}
$dc.Close()
$q.CurrentJobSettings.Description=$Name
[System.Printing.PrintQueue]::CreateXpsDocumentWriter($q).Write($dv,$t)
'''


def mm2px(v):
    return v * DPI / 25.4


# --------------------------------------------------------------------- spooler

if WIN:
    import ctypes
    from ctypes import wintypes

    _ws = ctypes.WinDLL("winspool.drv")

    class _ST(ctypes.Structure):
        _fields_ = [(n, wintypes.WORD) for n in ("y", "m", "dw", "d", "h", "mi", "s", "ms")]

    class _JOB1(ctypes.Structure):
        _fields_ = [("JobId", wintypes.DWORD), ("pPrinterName", wintypes.LPWSTR),
                    ("pMachineName", wintypes.LPWSTR), ("pUserName", wintypes.LPWSTR),
                    ("pDocument", wintypes.LPWSTR), ("pDatatype", wintypes.LPWSTR),
                    ("pStatus", wintypes.LPWSTR), ("Status", wintypes.DWORD),
                    ("Priority", wintypes.DWORD), ("Position", wintypes.DWORD),
                    ("TotalPages", wintypes.DWORD), ("PagesPrinted", wintypes.DWORD),
                    ("Submitted", _ST)]

    _ws.OpenPrinterW.argtypes = [wintypes.LPWSTR, ctypes.POINTER(wintypes.HANDLE), ctypes.c_void_p]
    _ws.EnumJobsW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                              ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                              ctypes.POINTER(wintypes.DWORD)]
    _ws.SetJobW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                            wintypes.DWORD]
    _ws.ClosePrinter.argtypes = [wintypes.HANDLE]

    def _open(printer):
        h = wintypes.HANDLE()
        return h if _ws.OpenPrinterW(printer, ctypes.byref(h), None) else None

    def _win_state(st, txt):
        if st & 0x0104: return "cancelling", "Annulation…"
        if st & 0x1080: return "done", "Terminé"
        if st & 0x0040: return "error", txt or "Papier ou cassette"
        if st & 0x0020: return "error", txt or "Imprimante hors ligne"
        if st & 0x0602: return "error", txt or "Intervention requise"
        if st & 0x0001: return "paused", "En pause"
        if st & 0x0010: return "printing", "Impression…"
        if st & 0x0008: return "spooling", "Envoi…"
        return "queued", "En attente"

    def spool_jobs(printer):
        h = _open(printer)
        if not h:
            return None
        try:
            need, n = wintypes.DWORD(), wintypes.DWORD()
            _ws.EnumJobsW(h, 0, 128, 1, None, 0, ctypes.byref(need), ctypes.byref(n))
            if not need.value:
                return []
            buf = ctypes.create_string_buffer(need.value)
            if not _ws.EnumJobsW(h, 0, 128, 1, buf, need, ctypes.byref(need), ctypes.byref(n)):
                return None
            arr = ctypes.cast(buf, ctypes.POINTER(_JOB1))
            out = []
            for i in range(n.value):
                j = arr[i]
                state, label = _win_state(j.Status, j.pStatus or "")
                out.append({"id": str(j.JobId), "doc": j.pDocument or "", "state": state,
                            "label": label, "pos": j.Position})
            return out
        finally:
            _ws.ClosePrinter(h)

    def spool_cancel(printer, job_id):
        h = _open(printer)
        if not h:
            return False
        try:
            return bool(_ws.SetJobW(h, int(job_id), 0, None, 5))  # JOB_CONTROL_DELETE
        finally:
            _ws.ClosePrinter(h)
else:
    def spool_jobs(printer):
        try:
            out = subprocess.run(["lpstat", "-o", printer], capture_output=True, text=True,
                                 timeout=5).stdout
        except Exception:
            return None
        jobs = []
        for i, line in enumerate(out.splitlines()):
            if line.strip():
                jid = line.split()[0]
                st, lb = ("printing", "Impression…") if i == 0 else ("queued", "En attente")
                jobs.append({"id": jid, "doc": jid, "state": st, "label": lb, "pos": i})
        return jobs

    def spool_cancel(printer, job_id):
        return subprocess.run(["cancel", job_id], capture_output=True).returncode == 0


def linux_media_opts(printer):
    """Pick a borderless 100x148 PageSize from the CUPS PPD when available."""
    try:
        out = subprocess.run(["lpoptions", "-p", printer, "-l"], capture_output=True,
                             text=True, timeout=5).stdout
    except Exception:
        out = ""
    for line in out.splitlines():
        if line.split("/")[0].strip() == "PageSize":
            choices = [c.lstrip("*") for c in line.split(":", 1)[1].split()]
            post = [c for c in choices if any(k in c.lower() for k in ("100x148", "hagaki", "postcard"))]
            bl = [c for c in post if any(k in c.lower() for k in ("borderless", "fb", "fullbleed"))]
            if bl or post:
                return ["-o", "PageSize=" + (bl or post)[0]]
    return ["-o", "media=jpn_hagaki_100x148mm"]


# ----------------------------------------------------------------------- icons

def icon(name, color="#e6e6ea", size=40):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(size / 24, size / 24)
    pen = QPen(QColor(color), 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    if name == "open":
        p.drawRoundedRect(QRectF(3.5, 4.5, 17, 15), 2.5, 2.5)
        path = QPainterPath(QPointF(3.5, 16.5))
        path.lineTo(8.5, 11.5); path.lineTo(12.5, 15.5); path.lineTo(15, 13); path.lineTo(20.5, 18)
        p.drawPath(path)
        p.drawEllipse(QPointF(15.5, 9), 1.5, 1.5)
    elif name in ("rotl", "rotr"):
        if name == "rotr":
            p.translate(24, 0); p.scale(-1, 1)
        path = QPainterPath()
        path.arcMoveTo(QRectF(5, 6, 14, 14), 90)
        path.arcTo(QRectF(5, 6, 14, 14), 90, -270)
        p.drawPath(path)
        a = QPainterPath(QPointF(14.2, 3.4)); a.lineTo(11.6, 6); a.lineTo(14.2, 8.6)
        p.drawPath(a)
    elif name.startswith("layout"):
        p.drawRoundedRect(QRectF(3, 6, 18, 12), 1.8, 1.8)
        k = name[6:]
        if k in ("2", "4"): p.drawLine(QPointF(12, 6), QPointF(12, 18))
        if k in ("2b", "4"): p.drawLine(QPointF(3, 12), QPointF(21, 12))
    elif name == "chevron":
        a = QPainterPath(QPointF(7, 10)); a.lineTo(12, 15); a.lineTo(17, 10)
        p.drawPath(a)
    elif name == "landscape":
        p.drawRoundedRect(QRectF(3, 7, 18, 11), 1.8, 1.8)
    elif name == "portrait":
        p.drawRoundedRect(QRectF(6.5, 3, 11, 18), 1.8, 1.8)
    elif name == "fit":
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            p.save(); p.translate(12, 12); p.scale(sx, sy)
            path = QPainterPath(QPointF(-8, -3.5)); path.lineTo(-8, -8); path.lineTo(-3.5, -8)
            p.drawPath(path); p.restore()
        p.drawRect(QRectF(8.5, 9.5, 7, 5))
    elif name == "calib":
        for y, x in ((7, 15), (12, 8), (17, 13)):
            p.drawLine(QPointF(4, y), QPointF(20, y))
            p.setBrush(QColor("#1c1c21")); p.drawEllipse(QPointF(x, y), 2, 2); p.setBrush(Qt.NoBrush)
    elif name == "close":
        p.drawLine(QPointF(7, 7), QPointF(17, 17)); p.drawLine(QPointF(17, 7), QPointF(7, 17))
    elif name == "print":
        p.drawRoundedRect(QRectF(3.5, 9, 17, 8), 2, 2)
        p.drawRect(QRectF(7, 4, 10, 5))
        p.setBrush(QColor(color)); p.drawRect(QRectF(7, 14, 10, 6.5))
    elif name == "paste":
        p.drawRoundedRect(QRectF(5, 5, 14, 16), 2, 2)
        p.drawRoundedRect(QRectF(9, 3, 6, 4), 1, 1)
    elif name == "image":
        p.drawRoundedRect(QRectF(2.5, 4.5, 19, 15), 2.5, 2.5)
        path = QPainterPath(QPointF(2.5, 16)); path.lineTo(8, 10.5); path.lineTo(12.5, 15)
        path.lineTo(15.5, 12); path.lineTo(21.5, 17.5)
        p.drawPath(path)
        p.drawEllipse(QPointF(16, 8.8), 1.6, 1.6)
    elif name == "app":
        g = QLinearGradient(0, 0, 24, 24)
        g.setColorAt(0, QColor("#60a5fa")); g.setColorAt(1, QColor("#7c3aed"))
        p.setPen(Qt.NoPen); p.setBrush(g)
        p.drawRoundedRect(QRectF(1, 1, 22, 22), 5.5, 5.5)
        p.setBrush(QColor(255, 255, 255, 235))
        p.drawRoundedRect(QRectF(5, 7, 14, 10), 1.2, 1.2)
        p.setBrush(QColor("#7c3aed"))
        path = QPainterPath(QPointF(5, 15.5)); path.lineTo(9.5, 11); path.lineTo(13, 14.5)
        path.lineTo(15, 12.5); path.lineTo(19, 16); path.lineTo(19, 17); path.lineTo(5, 17)
        p.drawPath(path)
    p.end()
    return QIcon(pm)


# ---------------------------------------------------------------------- canvas

GAP_MM = 2.0
LAYOUTS = {  # fractions of a landscape frame; transposed for portrait
    "1": [(0, 0, 1, 1)],
    "2": [(0, 0, .5, 1), (.5, 0, .5, 1)],
    "2b": [(0, 0, 1, .5), (0, .5, 1, .5)],
    "4": [(0, 0, .5, .5), (.5, 0, .5, .5), (0, .5, .5, .5), (.5, .5, .5, .5)],
}


class Cell:
    def __init__(self):
        self.img = None
        self.name = ""
        self.s = 1.0
        self.ox = self.oy = 0.0   # image top-left relative to cell rect, frame px
        self.rect = QRectF()

    def cover(self):
        return max(self.rect.width() / self.img.width(), self.rect.height() / self.img.height())

    def contain(self):
        return min(self.rect.width() / self.img.width(), self.rect.height() / self.img.height())

    def clamp(self):
        self.s = max(self.s, self.contain() * 0.2)
        rw, rh = self.rect.width(), self.rect.height()
        iw, ih = self.img.width() * self.s, self.img.height() * self.s
        # larger than the cell: no gaps; smaller: stays inside the cell
        self.ox = min(0, max(rw - iw, self.ox)) if iw >= rw else max(0, min(rw - iw, self.ox))
        self.oy = min(0, max(rh - ih, self.oy)) if ih >= rh else max(0, min(rh - ih, self.oy))

    def fit(self, mode="cover"):
        if not self.img:
            return
        self.s = self.cover() if mode == "cover" else self.contain()
        self.ox = (self.rect.width() - self.img.width() * self.s) / 2
        self.oy = (self.rect.height() - self.img.height() * self.s) / 2
        self.clamp()

    def is_cover(self):
        return abs(self.s - self.cover()) < 1e-6 * self.s + 1e-9


class Canvas(QWidget):
    changed = Signal()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setAcceptDrops(True)
        self.setMinimumSize(560, 420)
        self.setMouseTracking(True)
        self.landscape = True
        self.layout = "1"
        self.cells = [Cell()]
        self.active = 0
        self.drag = None
        self.hover = None
        self.relayout()

    # state ---------------------------------------------------------------
    @property
    def ready(self):
        return any(c.img for c in self.cells)

    @property
    def name(self):
        return "  ·  ".join(c.name for c in self.cells if c.img)

    @property
    def cell(self):
        return self.cells[self.active]

    def frame_size(self):
        w, h = round(mm2px(PAPER_MM[0])), round(mm2px(PAPER_MM[1]))
        return (w, h) if self.landscape else (h, w)

    def relayout(self, refit=True):
        fw, fh = self.frame_size()
        g = mm2px(GAP_MM) / 2
        specs = LAYOUTS[self.layout]
        while len(self.cells) < len(specs):
            self.cells.append(Cell())
        del self.cells[len(specs):]
        self.active = min(self.active, len(self.cells) - 1)
        for c, (x, y, w, h) in zip(self.cells, specs):
            if not self.landscape:
                x, y, w, h = y, x, h, w
            x0, y0, x1, y1 = x * fw, y * fh, (x + w) * fw, (y + h) * fh
            x0 += g if x > 0 else 0
            y0 += g if y > 0 else 0
            x1 -= g if x + w < 1 else 0
            y1 -= g if y + h < 1 else 0
            c.rect = QRectF(x0, y0, x1 - x0, y1 - y0)
            if refit and c.img:
                c.fit()
        self.update()

    def view(self):
        fw, fh = self.frame_size()
        mx, mtop, mbot = 56, 40, 100
        v = min((self.width() - 2 * mx) / fw, (self.height() - mtop - mbot) / fh)
        x0 = (self.width() - fw * v) / 2
        y0 = mtop + (self.height() - mtop - mbot - fh * v) / 2
        return v, x0, y0

    def hit(self, pos):
        v, x0, y0 = self.view()
        pt = QPointF((pos.x() - x0) / v, (pos.y() - y0) / v)
        g = mm2px(GAP_MM)
        for i, c in enumerate(self.cells):
            if c.rect.adjusted(-g, -g, g, g).contains(pt):
                return i
        return None

    def crop_mm(self):
        g = lambda k: float(self.settings.value(k, CROP_DEFAULT[k]))
        t, r, b, l = g("crop/top"), g("crop/right"), g("crop/bottom"), g("crop/left")
        return (t, r, b, l) if self.landscape else (l, t, r, b)

    # actions -------------------------------------------------------------
    def set_layout(self, name):
        if name == self.layout:
            return
        self.layout = name
        self.relayout()
        self.changed.emit()

    def set_landscape(self, on):
        if on == self.landscape:
            return
        self.landscape = on
        self.relayout()
        self.changed.emit()

    def load(self, path, idx=None):
        r = QImageReader(path)
        r.setAutoTransform(True)
        return self.set_image(r.read(), os.path.basename(path), idx)

    def set_image(self, img, name, idx=None):
        if img is None or img.isNull():
            return False
        i = self.active if idx is None else idx
        c = self.cells[i]
        c.img = img.convertToFormat(QImage.Format_RGB32)
        c.name = name
        if len(self.cells) == 1:
            self.landscape = c.img.width() >= c.img.height()
            self.relayout(refit=False)
        c.fit()
        empty = [j for j in range(len(self.cells)) if not self.cells[j].img]
        self.active = next((j for j in empty if j > i), empty[0] if empty else i)
        self.update()
        self.changed.emit()
        return True

    def clear_cell(self):
        c = self.cell
        c.img, c.name = None, ""
        self.update()
        self.changed.emit()

    def fit(self, mode="cover"):
        if self.cell.img:
            self.cell.fit(mode)
            self.update()

    def toggle_fit(self, idx):
        c = self.cells[idx]
        if c.img:
            c.fit("contain" if c.is_cover() else "cover")
            self.update()

    def rotate(self, deg):
        c = self.cell
        if not c.img:
            return
        c.img = c.img.transformed(QTransform().rotate(deg), Qt.SmoothTransformation)
        c.fit()
        self.update()

    # output --------------------------------------------------------------
    def render(self):
        """Paper-size image. The on-screen frame maps onto the part of the card that survives
        borderless overscan and tab removal; outer edges get bleed."""
        fw, fh = self.frame_size()
        t, r, b, l = (mm2px(v) for v in self.crop_mm())
        sx, sy = (fw - l - r) / fw, (fh - t - b) / fh
        out = QImage(fw, fh, QImage.Format_RGB32)
        out.fill(Qt.white)
        p = QPainter(out)
        e = 0.5
        for c in self.cells:
            if not c.img:
                continue
            R = c.rect
            X0, Y0 = l + R.left() * sx, t + R.top() * sy
            X1, Y1 = l + R.right() * sx, t + R.bottom() * sy
            if R.left() < e: X0 = 0
            if R.top() < e: Y0 = 0
            if R.right() > fw - e: X1 = fw
            if R.bottom() > fh - e: Y1 = fh
            E = QRect(round(X0), round(Y0), round(X1) - round(X0), round(Y1) - round(Y0))
            I = QRectF(R.x() + c.ox, R.y() + c.oy, c.img.width() * c.s, c.img.height() * c.s)
            kx, ky = c.s * sx, c.s * sy
            ix, iy = l + I.x() * sx, t + I.y() * sy
            src = QRectF((E.x() - ix) / kx, (E.y() - iy) / ky, E.width() / kx, E.height() / ky)
            sr = src.toAlignedRect().adjusted(-1, -1, 1, 1).intersected(c.img.rect())
            if sr.isEmpty():
                continue
            tw, th = max(1, round(sr.width() * kx)), max(1, round(sr.height() * ky))
            part = c.img.copy(sr).scaled(tw, th, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            cx, cy = round(ix + sr.x() * kx) - E.x(), round(iy + sr.y() * ky) - E.y()
            W, H = E.width(), E.height()
            patch = QImage(W, H, QImage.Format_RGB32)
            patch.fill(Qt.white)
            q = QPainter(patch)
            q.drawImage(cx, cy, part)
            # stretch edge pixels into the bleed only where the photo reaches the cell edge
            touch_l = I.left() <= R.left() + e
            touch_r = I.right() >= R.right() - e
            touch_t = I.top() <= R.top() + e
            touch_b = I.bottom() >= R.bottom() - e
            if touch_l and cx > 0:
                q.drawImage(QRectF(0, cy, cx, th), part, QRectF(0, 0, 1, th))
            if touch_r and cx + tw < W:
                q.drawImage(QRectF(cx + tw, cy, W - cx - tw, th), part, QRectF(tw - 1, 0, 1, th))
            q.end()
            q = QPainter(patch)
            if touch_t and cy > 0:
                q.drawImage(QRectF(0, 0, W, cy), patch.copy(0, cy, W, 1))
            if touch_b and cy + th < H:
                q.drawImage(QRectF(0, cy + th, W, H - cy - th), patch.copy(0, cy + th - 1, W, 1))
            q.end()
            p.drawImage(E.topLeft(), patch)
        p.end()
        return out

    def paint_cells(self, p, v, x0, y0):
        for c in self.cells:
            if not c.img:
                continue
            cr = QRectF(x0 + c.rect.x() * v, y0 + c.rect.y() * v, c.rect.width() * v, c.rect.height() * v)
            ir = QRectF(cr.x() + c.ox * v, cr.y() + c.oy * v,
                        c.img.width() * c.s * v, c.img.height() * c.s * v)
            p.save()
            p.setClipRect(cr)
            p.drawImage(ir, c.img)
            p.restore()

    def preview(self, h=96):
        fw, fh = self.frame_size()
        v = h / fh
        img = QImage(round(fw * v), h, QImage.Format_RGB32)
        img.fill(Qt.white)
        p = QPainter(img)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        self.paint_cells(p, v, 0, 0)
        p.end()
        return img

    # painting ------------------------------------------------------------
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setRenderHint(QPainter.Antialiasing)
        fw, fh = self.frame_size()
        v, x0, y0 = self.view()
        frame = QRectF(x0, y0, fw * v, fh * v)
        multi = len(self.cells) > 1

        if not self.ready and not multi:
            hov = self.hover is not None
            c = QColor(ACCENT) if hov else QColor(255, 255, 255, 46)
            p.setBrush(QColor(59, 130, 246, 22) if hov else QColor(255, 255, 255, 6))
            p.setPen(QPen(c, 1.5, Qt.DashLine))
            p.drawRoundedRect(frame, 12, 12)
            self.draw_glyph(p, frame, hov)
            return

        if self.drag and self.cell.img:  # ghost of the dragged photo around the card
            c = self.cell
            ir = QRectF(x0 + (c.rect.x() + c.ox) * v, y0 + (c.rect.y() + c.oy) * v,
                        c.img.width() * c.s * v, c.img.height() * c.s * v)
            p.setOpacity(0.16)
            p.drawImage(ir, c.img)
            p.setOpacity(1.0)
        for i in range(14):
            a = 3 + i * 1.6
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(0, 0, 0, 10))
            p.drawRoundedRect(frame.adjusted(-a / 2, -a / 2 + 6, a / 2, a / 2 + 6), 6, 6)
        p.fillRect(frame, Qt.white)
        self.paint_cells(p, v, x0, y0)
        for i, c in enumerate(self.cells):
            cr = QRectF(x0 + c.rect.x() * v, y0 + c.rect.y() * v, c.rect.width() * v, c.rect.height() * v)
            hov = self.hover == i
            if not c.img:
                p.fillRect(cr, QColor(219, 234, 254) if hov else QColor(236, 236, 240))
                self.draw_glyph(p, cr, hov, light=True)
            if multi and (i == self.active or hov):
                p.setBrush(Qt.NoBrush)
                p.setPen(QPen(QColor(ACCENT), 2))
                p.drawRect(cr.adjusted(1, 1, -1, -1))
        p.setPen(QPen(QColor(255, 255, 255, 40), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(frame.adjusted(0.5, 0.5, -0.5, -0.5))

    def draw_glyph(self, p, rect, hov, light=False):
        col = ACCENT if hov else ("#a1a1aa" if light else "#5a5a63")
        s = min(rect.width(), rect.height()) * (0.22 if light else 0.18)
        pm = icon("image", col, 96).pixmap(96, 96)
        p.drawPixmap(QRectF(rect.center().x() - s / 2, rect.center().y() - s / 2, s, s), pm,
                     QRectF(0, 0, 96, 96))

    # input ---------------------------------------------------------------
    def wheelEvent(self, e):
        i = self.hit(e.position())
        if i is None or not self.cells[i].img:
            return
        c = self.cells[i]
        v, x0, y0 = self.view()
        cx = (e.position().x() - x0) / v - c.rect.x()
        cy = (e.position().y() - y0) / v - c.rect.y()
        ns = max(c.s * 1.0015 ** e.angleDelta().y(), c.contain() * 0.2)
        k = ns / c.s
        c.ox = cx - (cx - c.ox) * k
        c.oy = cy - (cy - c.oy) * k
        c.s = ns
        c.clamp()
        self.update()

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        i = self.hit(e.position())
        if i is None:
            return
        if i != self.active:
            self.active = i
            self.changed.emit()
        c = self.cells[i]
        if c.img:
            self.drag = (e.position(), c.ox, c.oy)
            self.setCursor(Qt.ClosedHandCursor)
        else:
            self.window().open_file()
        self.update()

    def mouseMoveEvent(self, e):
        if self.drag:
            v = self.view()[0]
            start, ox, oy = self.drag
            d = (e.position() - start) / v
            c = self.cell
            c.ox, c.oy = ox + d.x(), oy + d.y()
            c.clamp()
            self.update()
        else:
            i = self.hit(e.position())
            if i is None:
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.OpenHandCursor if self.cells[i].img else Qt.PointingHandCursor)

    def mouseReleaseEvent(self, e):
        self.drag = None
        self.update()

    def mouseDoubleClickEvent(self, e):
        i = self.hit(e.position())
        if i is not None:
            self.toggle_fit(i)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() or e.mimeData().hasImage():
            e.acceptProposedAction()
            self.hover = self.hit(e.position()) if len(self.cells) > 1 else 0
            self.update()

    def dragMoveEvent(self, e):
        h = self.hit(e.position()) if len(self.cells) > 1 else 0
        if h != self.hover:
            self.hover = h
            self.update()
        e.acceptProposedAction()

    def dragLeaveEvent(self, e):
        self.hover = None
        self.update()

    def dropEvent(self, e):
        idx = self.hover if self.hover is not None else self.active
        self.hover = None
        self.window().load_mime(e.mimeData(), idx)
        self.update()


# ------------------------------------------------------------------ job queue

class JobCard(QFrame):
    def __init__(self, on_cancel):
        super().__init__()
        self.setObjectName("job")
        self.setFixedHeight(62)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 8, 6, 8)
        lay.setSpacing(10)
        self.thumb = QLabel()
        self.thumb.setFixedSize(64, 44)
        self.thumb.setObjectName("thumb")
        self.thumb.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.thumb)
        col = QVBoxLayout()
        col.setSpacing(2)
        self.title = QLabel()
        self.title.setObjectName("jobName")
        self.status = QLabel()
        self.status.setObjectName("jobStatus")
        col.addStretch()
        col.addWidget(self.title)
        col.addWidget(self.status)
        col.addStretch()
        lay.addLayout(col, 1)
        self.btn = QToolButton()
        self.btn.setObjectName("cancel")
        self.btn.setIcon(icon("close", "#a1a1aa"))
        self.btn.setIconSize(QSize(14, 14))
        self.btn.setToolTip("Annuler")
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(on_cancel)
        lay.addWidget(self.btn, 0, Qt.AlignVCenter)
        self._thumb_key = None

    def update_from(self, job):
        fm = self.title.fontMetrics()
        self.title.setText(fm.elidedText(job["name"], Qt.ElideMiddle, 150))
        self.title.setToolTip(job["name"])
        copies = f"  ·  ×{job['copies']}" if job.get("copies", 1) > 1 else ""
        self.status.setText(job["label"] + copies)
        col = {"printing": ACCENT, "spooling": ACCENT, "error": "#f87171", "done": "#4ade80",
               "paused": "#fbbf24"}.get(job["state"], "#9a9aa3")
        self.status.setStyleSheet(f"color:{col}")
        self.btn.setToolTip("Retirer" if job["state"] in ("done", "error_local") else "Annuler")
        if job.get("thumb") is not None and self._thumb_key is not job["thumb"]:
            self._thumb_key = job["thumb"]
            pm = QPixmap.fromImage(job["thumb"]).scaled(64, 44, Qt.KeepAspectRatioByExpanding,
                                                        Qt.SmoothTransformation)
            pm = pm.copy((pm.width() - 64) // 2, (pm.height() - 44) // 2, 64, 44)
            r = QPixmap(64, 44)
            r.fill(Qt.transparent)
            p = QPainter(r)
            p.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, 64, 44), 6, 6)
            p.setClipPath(path)
            p.drawPixmap(0, 0, pm)
            p.end()
            self.thumb.setPixmap(r)
        elif job.get("thumb") is None and self._thumb_key != "doc":
            self._thumb_key = "doc"
            self.thumb.setPixmap(icon("print", "#71717a", 44).pixmap(26, 26))


class Bus(QObject):
    sent = Signal(str, bool, str, str)  # key, ok, error, spool id (linux)


# ---------------------------------------------------------------------- window

class CalibDialog(QDialog):
    def __init__(self, settings, parent):
        super().__init__(parent)
        self.setWindowTitle("Calibration")
        self.settings = settings
        f = QFormLayout(self)
        f.setContentsMargins(22, 20, 22, 18)
        f.setSpacing(10)
        self.boxes = {}
        for key, label in (("top", "Haut"), ("right", "Droite"), ("bottom", "Bas"), ("left", "Gauche")):
            b = QDoubleSpinBox()
            b.setRange(0, 15)
            b.setSingleStep(0.25)
            b.setDecimals(2)
            b.setSuffix(" mm")
            b.setValue(float(settings.value(f"crop/{key}", CROP_DEFAULT[f"crop/{key}"])))
            self.boxes[key] = b
            f.addRow(label, b)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        bb.button(QDialogButtonBox.RestoreDefaults).clicked.connect(
            lambda: [b.setValue(CROP_DEFAULT[f"crop/{k}"]) for k, b in self.boxes.items()])
        f.addRow(bb)

    def accept(self):
        for k, b in self.boxes.items():
            self.settings.setValue(f"crop/{k}", b.value())
        super().accept()


QSS = f"""
* {{ font-family: "Segoe UI Variable Text", "Segoe UI", "Inter", "Cantarell", sans-serif;
     font-size: 13px; color: #e7e7ea; }}
QMainWindow, #main {{ background: #0f0f12; }}
#sidebar {{ background: #16161a; border-right: 1px solid #232329; }}
#sideTitle {{ font-size: 15px; font-weight: 600; }}
#count {{ color: #a1a1aa; background: #25252b; border-radius: 9px; padding: 1px 8px; font-size: 12px; }}
#job {{ background: #1e1e23; border: 1px solid #26262d; border-radius: 12px; }}
#job:hover {{ border-color: #34343c; background: #212127; }}
#thumb {{ background: #26262c; border-radius: 6px; }}
#jobName {{ font-weight: 600; }}
#jobStatus {{ font-size: 12px; }}
QToolButton#cancel {{ border: none; border-radius: 8px; padding: 6px; background: transparent; }}
QToolButton#cancel:hover {{ background: #3a1f24; }}
#topbar {{ background: transparent; }}
#docName {{ color: #a1a1aa; font-size: 13px; }}
#pill {{ background: rgba(26, 26, 31, 242); border: 1px solid #2c2c34; border-radius: 16px; }}
QToolButton#tool {{ border: none; border-radius: 10px; padding: 8px; background: transparent; }}
QToolButton#tool:hover {{ background: #2b2b32; }}
QToolButton#tool:pressed {{ background: #34343c; }}
#sep {{ background: #2c2c34; }}
QComboBox {{ background: #1b1b20; border: 1px solid #2a2a31; border-radius: 10px; padding: 7px 12px;
             min-width: 190px; }}
QComboBox:hover {{ border-color: #3a3a43; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox::down-arrow {{ image: url("CHEVRON"); width: 12px; height: 12px; }}
QComboBox QAbstractItemView {{ background: #1b1b20; border: 1px solid #2a2a31; outline: 0; padding: 4px;
                               selection-background-color: #2a2a31; }}
#stepper {{ background: #1b1b20; border: 1px solid #2a2a31; border-radius: 10px; }}
#stepper QToolButton {{ border: none; border-radius: 8px; padding: 3px 10px; font-size: 16px; color: #c4c4cc; }}
#stepper QToolButton:hover {{ background: #2b2b32; }}
#stepVal {{ min-width: 26px; font-weight: 600; }}
QPushButton#printBtn {{ background: {ACCENT}; border: none; border-radius: 10px; padding: 9px 20px;
                        font-weight: 600; color: white; }}
QPushButton#printBtn:hover {{ background: #4f8ff7; }}
QPushButton#printBtn:pressed {{ background: #2f6fde; }}
QPushButton#printBtn:disabled {{ background: #24242a; color: #5f5f68; }}
QMenu {{ background: #1e1e23; border: 1px solid #2c2c34; border-radius: 10px; padding: 6px; }}
QMenu::item {{ padding: 7px 16px 7px 10px; border-radius: 6px; }}
QMenu::item:selected {{ background: #2b2b32; }}
QMenu::item:checked {{ color: {ACCENT}; }}
QMenu::indicator {{ width: 0; }}
QToolTip {{ background: #24242a; color: #e7e7ea; border: 1px solid #33333b; padding: 5px 8px; }}
QScrollArea, #jobList {{ border: none; background: transparent; }}
QScrollBar:vertical {{ width: 8px; background: transparent; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #2e2e36; border-radius: 3px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QDialog {{ background: #16161a; }}
QDoubleSpinBox {{ background: #1b1b20; border: 1px solid #2a2a31; border-radius: 8px; padding: 5px 8px; }}
QDialogButtonBox QPushButton {{ background: #25252b; border: 1px solid #2f2f37; border-radius: 8px;
                                padding: 6px 14px; min-width: 70px; }}
QDialogButtonBox QPushButton:hover {{ background: #2d2d34; }}
"""


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selphy Print")
        self.setWindowIcon(icon("app", size=64))
        self.settings = QSettings("SelphyPrint", "SelphyPrint")
        self.jobs = {}     # key -> job dict
        self.cards = {}    # key -> JobCard
        self.bus = Bus()
        self.bus.sent.connect(self.on_sent)

        root = QWidget()
        root.setObjectName("main")
        self.setCentralWidget(root)
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # sidebar
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(290)
        sv = QVBoxLayout(side)
        sv.setContentsMargins(16, 18, 12, 16)
        sv.setSpacing(12)
        head = QHBoxLayout()
        t = QLabel("Impressions")
        t.setObjectName("sideTitle")
        self.count = QLabel("0")
        self.count.setObjectName("count")
        head.addWidget(t)
        head.addWidget(self.count)
        head.addStretch()
        sv.addLayout(head)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.job_list = QWidget()
        self.job_list.setObjectName("jobList")
        self.job_lay = QVBoxLayout(self.job_list)
        self.job_lay.setContentsMargins(0, 0, 4, 0)
        self.job_lay.setSpacing(8)
        self.job_lay.addStretch()
        scroll.setWidget(self.job_list)
        sv.addWidget(scroll, 1)
        h.addWidget(side)

        # main column
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        top = QWidget()
        top.setObjectName("topbar")
        tl = QHBoxLayout(top)
        tl.setContentsMargins(24, 14, 18, 6)
        tl.setSpacing(10)
        self.doc = QLabel()
        self.doc.setObjectName("docName")
        tl.addWidget(self.doc, 1)
        self.printers = QComboBox()
        names = [i.printerName() for i in QPrinterInfo.availablePrinters()]
        self.printers.addItems(names)
        saved = self.settings.value("printer", "")
        pick = saved if saved in names else next((n for n in names if "selphy" in n.lower()), None)
        if pick:
            self.printers.setCurrentText(pick)
        self.printers.currentTextChanged.connect(lambda n: self.settings.setValue("printer", n))
        tl.addWidget(self.printers)
        tl.addWidget(self.make_stepper())
        self.print_btn = QPushButton("  Imprimer")
        self.print_btn.setObjectName("printBtn")
        self.print_btn.setIcon(icon("print", "#ffffff"))
        self.print_btn.setIconSize(QSize(16, 16))
        self.print_btn.setCursor(Qt.PointingHandCursor)
        self.print_btn.clicked.connect(self.do_print)
        tl.addWidget(self.print_btn)
        col.addWidget(top)

        self.canvas = Canvas(self.settings)
        self.canvas.changed.connect(self.on_canvas_changed)
        col.addWidget(self.canvas, 1)
        h.addLayout(col, 1)

        # floating tool pill
        self.pill = QFrame(self.canvas)
        self.pill.setObjectName("pill")
        pl = QHBoxLayout(self.pill)
        pl.setContentsMargins(6, 5, 6, 5)
        pl.setSpacing(2)
        shadow = QGraphicsDropShadowEffect(self.pill)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.pill.setGraphicsEffect(shadow)

        def tool(name, tip, slot):
            b = QToolButton()
            b.setObjectName("tool")
            b.setIcon(icon(name))
            b.setIconSize(QSize(20, 20))
            b.setToolTip(tip)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(slot)
            pl.addWidget(b)
            return b

        def sep():
            s = QFrame()
            s.setObjectName("sep")
            s.setFixedSize(1, 22)
            pl.addSpacing(4)
            pl.addWidget(s)
            pl.addSpacing(4)

        tool("open", "Ouvrir  (Ctrl+O)", self.open_file)
        tool("paste", "Coller  (Ctrl+V)", self.paste)
        sep()
        tool("rotl", "Pivoter à gauche", lambda: self.canvas.rotate(-90))
        tool("rotr", "Pivoter à droite", lambda: self.canvas.rotate(90))
        self.orient_btn = tool("landscape", "Paysage / portrait",
                               lambda: self.canvas.set_landscape(not self.canvas.landscape))
        tool("fit", "Remplir / photo entière  (double-clic)",
             lambda: self.canvas.toggle_fit(self.canvas.active))
        self.layout_btn = tool("layout1", "Mise en page", self.layout_menu)
        sep()
        tool("calib", "Calibration", self.calibrate)
        self.pill.adjustSize()
        self.canvas.installEventFilter(self)

        QShortcut(QKeySequence.Open, self, self.open_file)
        QShortcut(QKeySequence.Paste, self, self.paste)
        QShortcut(QKeySequence.Print, self, self.do_print)
        QShortcut(QKeySequence("Ctrl+S"), self, self.export)
        QShortcut(QKeySequence("Ctrl+0"), self, self.canvas.fit)
        QShortcut(QKeySequence.Delete, self, self.canvas.clear_cell)
        QShortcut(QKeySequence("R"), self, lambda: self.canvas.rotate(90))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(1000)
        self.on_canvas_changed()
        self.resize(1280, 820)

    # ui helpers -----------------------------------------------------------
    def make_stepper(self):
        w = QFrame()
        w.setObjectName("stepper")
        l = QHBoxLayout(w)
        l.setContentsMargins(3, 3, 3, 3)
        l.setSpacing(0)
        self.n = 1
        minus, plus = QToolButton(), QToolButton()
        minus.setText("−")
        plus.setText("+")
        self.n_lbl = QLabel("1")
        self.n_lbl.setObjectName("stepVal")
        self.n_lbl.setAlignment(Qt.AlignCenter)
        self.n_lbl.setToolTip("Copies")

        def step(d):
            self.n = max(1, min(50, self.n + d))
            self.n_lbl.setText(str(self.n))
        minus.clicked.connect(lambda: step(-1))
        plus.clicked.connect(lambda: step(1))
        for x in (minus, self.n_lbl, plus):
            l.addWidget(x)
        return w

    def eventFilter(self, obj, ev):
        if obj is self.canvas and ev.type() == ev.Type.Resize:
            self.pill.adjustSize()
            self.pill.move((self.canvas.width() - self.pill.width()) // 2,
                           self.canvas.height() - self.pill.height() - 26)
        return super().eventFilter(obj, ev)

    def showEvent(self, e):
        super().showEvent(e)
        if WIN:
            try:  # dark title bar
                v = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(int(self.winId()), 20, ctypes.byref(v), 4)
            except Exception:
                pass

    def on_canvas_changed(self):
        c = self.canvas
        self.orient_btn.setIcon(icon("landscape" if c.landscape else "portrait"))
        self.layout_btn.setIcon(icon("layout" + c.layout))
        self.doc.setText(c.name)
        self.print_btn.setEnabled(c.ready)

    def layout_menu(self):
        m = QMenu(self)
        for k, label in (("1", "Une photo"), ("2", "Deux côte à côte"), ("2b", "Deux superposées"),
                         ("4", "Quatre")):
            act = m.addAction(icon("layout" + k), label)
            act.setCheckable(True)
            act.setChecked(self.canvas.layout == k)
            act.triggered.connect(lambda _=False, k=k: self.canvas.set_layout(k))
        b = self.layout_btn
        m.exec(b.mapToGlobal(QPointF(0, -m.sizeHint().height() - 6).toPoint()))

    # input ---------------------------------------------------------------
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Photo", self.settings.value("dir", ""),
            "Images (" + " ".join("*" + e for e in EXTS) + ")")
        if path:
            self.settings.setValue("dir", os.path.dirname(path))
            self.canvas.load(path)

    def load_mime(self, md, idx=None):
        c = self.canvas
        i = c.active if idx is None else idx
        done = False
        for u in md.urls() if md.hasUrls() else []:
            if i is not None and u.isLocalFile() and c.load(u.toLocalFile(), i):
                done = True
                i = c.active if c.active > i and not c.cells[c.active].img else None
        if done:
            return True
        if md.hasImage():
            img = md.imageData()
            if isinstance(img, QPixmap):
                img = img.toImage()
            if isinstance(img, QImage) and c.set_image(img, "Presse-papiers", idx):
                return True
        return False

    def paste(self):
        cb = QGuiApplication.clipboard()
        if not self.load_mime(cb.mimeData()):
            img = cb.image()
            if not img.isNull():
                self.canvas.set_image(img, "Presse-papiers")

    def calibrate(self):
        if CalibDialog(self.settings, self).exec():
            self.canvas.update()

    def export(self):
        if not self.canvas.ready:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exporter", "", "PNG (*.png)")
        if path:
            self.canvas.render().save(path)

    # printing ------------------------------------------------------------
    def do_print(self):
        c = self.canvas
        if not c.ready:
            return
        printer = self.printers.currentText()
        key = uuid.uuid4().hex[:8]
        base = " + ".join(os.path.splitext(x.name)[0] for x in c.cells if x.img) or "Photo"
        spool_name = f"SelphyPrint {key} {base}"
        tmp = tempfile.mkdtemp(prefix="selphy_")
        png = os.path.join(tmp, "print.png")
        c.render().save(png)
        job = {"key": key, "name": base, "spool": spool_name, "printer": printer, "copies": self.n,
               "thumb": c.preview(), "state": "spooling", "label": "Envoi…", "id": None,
               "t": time.time(), "proc": None, "seen": False}
        self.jobs[key] = job
        self.refresh_cards()
        threading.Thread(target=self.send, args=(job, png, tmp), daemon=True).start()

    def send(self, job, png, tmp):
        err, sid = "", ""
        try:
            if WIN:
                ps1 = os.path.join(tmp, "print.ps1")
                with open(ps1, "w", encoding="utf-8-sig") as f:
                    f.write(WIN_PRINT_PS1)
                cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1,
                       "-Image", png, "-Printer", job["printer"], "-Copies", str(job["copies"]),
                       "-Name", job["spool"]]
                kw = {"creationflags": 0x08000000}
            else:
                cmd = ["lp", "-d", job["printer"], "-n", str(job["copies"]), "-t", job["spool"],
                       "-o", "print-scaling=fill"] + linux_media_opts(job["printer"]) + [png]
                kw = {}
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kw)
            job["proc"] = proc
            out, e = proc.communicate()
            ok = proc.returncode == 0
            if not ok:
                err = (e or out).strip().splitlines()[-1][:160] if (e or out).strip() else "Échec de l'envoi"
            m = re.search(r"request id is (\S+)", out or "")
            sid = m.group(1) if m else ""
        except Exception as ex:
            ok, err = False, str(ex)[:160]
        shutil.rmtree(tmp, ignore_errors=True)
        self.bus.sent.emit(job["key"], ok, err, sid)

    def on_sent(self, key, ok, err, sid):
        job = self.jobs.get(key)
        if not job:
            return
        job["proc"] = None
        if job["state"] == "cancelling":
            if job["id"]:
                spool_cancel(job["printer"], job["id"])
            else:
                self.drop(key)
            return
        if not ok:
            job.update(state="error_local", label=err or "Erreur")
        else:
            if sid:
                job["id"] = sid
            job["sent_at"] = time.time()
            if job["state"] == "spooling" and not job["seen"]:
                job.update(state="queued", label="En attente")
        self.refresh_cards()

    def cancel(self, key):
        job = self.jobs.get(key)
        if not job:
            return
        if job["state"] in ("done", "error_local"):
            self.drop(key)
            return
        if job.get("id"):
            spool_cancel(job["printer"], job["id"])
            job.update(state="cancelling", label="Annulation…")
        elif job.get("proc"):
            job.update(state="cancelling", label="Annulation…")
            try:
                job["proc"].kill()
            except Exception:
                pass
        else:
            job.update(state="cancelling", label="Annulation…")
        self.refresh_cards()

    def drop(self, key):
        self.jobs.pop(key, None)
        self.refresh_cards()

    def poll(self):
        printer = self.printers.currentText()
        if not printer:
            return
        spool = spool_jobs(printer)
        if spool is None:
            return
        now = time.time()
        by_id = {j["id"]: j for j in spool}
        by_doc = {j["doc"]: j for j in spool}
        # attach / update our jobs
        for key, job in list(self.jobs.items()):
            if job["printer"] != printer:
                continue
            sj = by_id.get(job["id"]) if job["id"] else by_doc.get(job["spool"])
            if sj:
                job["id"] = sj["id"]
                job["seen"] = True
                if job["state"] != "cancelling" or sj["state"] == "cancelling":
                    job.update(state=sj["state"], label=sj["label"])
                if sj["state"] == "done":
                    job.setdefault("done_at", now)
            elif job["state"] in ("spooling",) and not job.get("proc") and now - job["t"] > 60:
                job.update(state="error_local", label="Introuvable dans la file")
            elif job.get("seen") or (job.get("sent_at") and now - job["sent_at"] > 8):
                if job["state"] == "cancelling":
                    self.jobs.pop(key)
                    continue
                if job["state"] not in ("done", "error_local"):
                    job.update(state="done", label="Terminé")
                    job["done_at"] = now
            if job["state"] == "done" and now - job.get("done_at", now) > 6:
                self.jobs.pop(key)
        # foreign jobs
        ours = {j["id"] for j in self.jobs.values() if j["id"]} | {j["spool"] for j in self.jobs.values()}
        for sj in spool:
            fkey = "spool:" + sj["id"]
            if sj["id"] in ours or sj["doc"] in ours:
                continue
            if sj["state"] == "done":
                self.jobs.pop(fkey, None)
                continue
            j = self.jobs.setdefault(fkey, {"key": fkey, "name": sj["doc"] or f"Tâche {sj['id']}",
                                            "printer": printer, "copies": 1, "thumb": None,
                                            "id": sj["id"], "spool": "", "t": now, "proc": None,
                                            "seen": True, "foreign": True})
            if j.get("state") != "cancelling" or sj["state"] == "cancelling":
                j.update(state=sj["state"], label=sj["label"])
        live = set(by_id)
        for key in [k for k, j in self.jobs.items() if j.get("foreign") and j["id"] not in live]:
            self.jobs.pop(key)
        self.refresh_cards()

    def refresh_cards(self):
        for key in list(self.cards):
            if key not in self.jobs:
                card = self.cards.pop(key)
                self.job_lay.removeWidget(card)
                card.deleteLater()
        order = sorted(self.jobs.values(), key=lambda j: j["t"])
        for i, job in enumerate(order):
            card = self.cards.get(job["key"])
            if not card:
                card = JobCard(lambda _=False, k=job["key"]: self.cancel(k))
                self.cards[job["key"]] = card
                self.job_lay.insertWidget(i, card)
            card.update_from(job)
        active = sum(1 for j in self.jobs.values() if j["state"] not in ("done", "error_local"))
        self.count.setText(str(active))


if __name__ == "__main__":
    QImageReader.setAllocationLimit(1024)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setDesktopFileName("selphy-print")
    app.setStyle("Fusion")
    chev = os.path.join(tempfile.gettempdir(), "selphyprint_chevron.png")
    icon("chevron", "#a1a1aa", 48).pixmap(48, 48).save(chev)
    app.setStyleSheet(QSS.replace("CHEVRON", chev.replace("\\", "/")))
    w = Main()
    w.show()
    if len(sys.argv) > 1:
        w.canvas.load(sys.argv[1])
    sys.exit(app.exec())
