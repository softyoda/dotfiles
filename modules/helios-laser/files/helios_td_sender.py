# ============================================================
# Helios Bridge — Script CHOP pour TouchDesigner (Wine/Linux)
# ============================================================
# SETUP:
#   1. Ajoute un "Laser CHOP" dans ton patch TD
#   2. Ajoute un "Script CHOP", connecte le Laser CHOP en input[0]
#   3. Copie ce code dans l'onglet "onCook" du Script CHOP DAT
#   4. Lance helios_bridge.py sur Linux (terminal séparé)
#
# Channels attendus depuis le Laser CHOP : tx, ty, r, g, b, i
#   tx, ty  : positions   (-1.0 à +1.0)
#   r,g,b,i : couleurs/intensité (0.0 à 1.0)
# ============================================================

import socket as _socket
import struct  as _struct

_sock      = None
_BRIDGE    = ('127.0.0.1', 45457)
_MAGIC     = b'HLD\x00'

def _get_sock():
    global _sock
    if _sock is None:
        _sock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    return _sock


def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Helios Bridge')
    page.appendInt('Pps',   label='PPS (points/sec)')
    page.appendInt('Port',  label='Bridge UDP port')
    page.appendFloat('Xscale', label='X scale')
    page.appendFloat('Yscale', label='Y scale')
    scriptOp.par.Pps.val    = 30000
    scriptOp.par.Port.val   = 45457
    scriptOp.par.Xscale.val = 1.0
    scriptOp.par.Yscale.val = 1.0


def onCook(scriptOp):
    global _BRIDGE

    if not scriptOp.inputs:
        return

    laser = scriptOp.inputs[0]
    chans = {c.name: c for c in laser.chans}

    if 'tx' not in chans or 'ty' not in chans:
        return

    tx = list(chans['tx'].vals)
    ty = list(chans['ty'].vals)
    r  = list(chans['r'].vals)  if 'r'  in chans else [1.0] * len(tx)
    g  = list(chans['g'].vals)  if 'g'  in chans else [1.0] * len(tx)
    b  = list(chans['b'].vals)  if 'b'  in chans else [1.0] * len(tx)
    iv = list(chans['i'].vals)  if 'i'  in chans else [1.0] * len(tx)

    n   = min(len(tx), 0xFFF)   # max 4095 points
    pps = int(scriptOp.par.Pps.val)
    xs  = float(scriptOp.par.Xscale.val)
    ys  = float(scriptOp.par.Yscale.val)
    port = int(scriptOp.par.Port.val)
    _BRIDGE = ('127.0.0.1', port)

    buf = bytearray(_MAGIC)
    buf += _struct.pack('<HHBB', pps, n, 0, 0)   # pps, num_points, flags, pad

    for idx in range(n):
        xv = max(0, min(0xFFF, int((tx[idx] * xs + 1.0) * 0.5 * 0xFFF)))
        yv = max(0, min(0xFFF, int((ty[idx] * ys + 1.0) * 0.5 * 0xFFF)))
        rv = max(0, min(255, int(r[idx]  * 255)))
        gv = max(0, min(255, int(g[idx]  * 255)))
        bv = max(0, min(255, int(b[idx]  * 255)))
        iv_ = max(0, min(255, int(iv[idx] * 255)))

        buf.append(xv >> 4)
        buf.append(((xv & 0xF) << 4) | (yv >> 8))
        buf.append(yv & 0xFF)
        buf.append(rv)
        buf.append(gv)
        buf.append(bv)
        buf.append(iv_)

    try:
        _get_sock().sendto(bytes(buf), _BRIDGE)
    except Exception:
        pass
