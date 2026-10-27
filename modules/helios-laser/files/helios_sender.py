import socket, struct

_sock  = None
_MAGIC = b'HLD\x00'

def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Helios')
    page.appendInt('Pps', label='PPS (pts/sec)')
    scriptOp.par.Pps.val = 30000

def onCook(scriptOp):
    global _sock
    if _sock is None:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if not scriptOp.inputs:
        return

    laser = scriptOp.inputs[0]
    chans = {c.name: c for c in laser.chans()}

    if 'tx' not in chans or 'ty' not in chans:
        return

    tx = list(chans['tx'].vals)
    ty = list(chans['ty'].vals)
    r  = list(chans['r'].vals)  if 'r'  in chans else [1.0] * len(tx)
    g  = list(chans['g'].vals)  if 'g'  in chans else [0.0] * len(tx)
    b  = list(chans['b'].vals)  if 'b'  in chans else [0.0] * len(tx)
    iv = list(chans['i'].vals)  if 'i'  in chans else [1.0] * len(tx)

    n   = min(len(tx), 4095)
    pps = int(scriptOp.par.Pps.val)

    buf = bytearray(_MAGIC)
    buf += struct.pack('<HHBB', pps, n, 0, 0)

    for idx in range(n):
        xv  = max(0, min(4095, int((tx[idx]  + 1.0) * 0.5 * 4095)))
        yv  = max(0, min(4095, int((ty[idx]  + 1.0) * 0.5 * 4095)))
        rv  = max(0, min(255,  int(r[idx]  * 255)))
        gv  = max(0, min(255,  int(g[idx]  * 255)))
        bv  = max(0, min(255,  int(b[idx]  * 255)))
        iv_ = max(0, min(255,  int(iv[idx] * 255)))
        buf += struct.pack('<HHBBBB', xv, yv, rv, gv, bv, iv_)

    _sock.sendto(bytes(buf), ('127.0.0.1', 45457))
