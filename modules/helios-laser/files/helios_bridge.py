#!/usr/bin/env python3
"""
Helios Laser DAC bridge — reçoit les frames UDP depuis TouchDesigner (Wine)
et les envoie au DAC via libHeliosDacAPI.so (SDK officiel Helios, compilé Linux).

Protocol UDP (TD → bridge, loopback 127.0.0.1:45457):
  Header 8 bytes : magic "HLD\x00" + pps uint16 LE + num_points uint16 LE + flags uint8 + pad uint8
  Points N×8 bytes : x uint16, y uint16, r uint8, g uint8, b uint8, i uint8
  x,y : 0–4095 (12-bit), r/g/b/i : 0–255
"""

import socket
import struct
import ctypes
import time
import sys

LIB_PATH    = '/usr/local/lib/libHeliosDacAPI.so'
LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 45457
MAGIC       = b'HLD\x00'
MAX_POINTS  = 4095


class HeliosPoint(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_uint16),
        ('y', ctypes.c_uint16),
        ('r', ctypes.c_uint8),
        ('g', ctypes.c_uint8),
        ('b', ctypes.c_uint8),
        ('i', ctypes.c_uint8),
    ]


def load_sdk():
    lib = ctypes.CDLL(LIB_PATH)
    lib.OpenDevices.restype  = ctypes.c_int
    lib.CloseDevices.restype = ctypes.c_int
    lib.GetStatus.restype    = ctypes.c_int
    lib.WriteFrame.restype   = ctypes.c_int
    lib.SetShutter.restype   = ctypes.c_int
    lib.GetName.restype      = ctypes.c_int
    return lib


def main():
    print("=== Helios Bridge (SDK officiel) ===")
    lib = load_sdk()

    n_dacs = lib.OpenDevices()
    if n_dacs <= 0:
        raise RuntimeError("Aucun Helios DAC trouvé. Vérifie le câble USB.")
    print(f"{n_dacs} DAC(s) trouvé(s)")

    name = ctypes.create_string_buffer(32)
    lib.GetName(0, name)
    print(f"DAC 0 : {name.value.decode(errors='replace')}")

    lib.SetShutter(0, ctypes.c_bool(True))
    print("Shutter ouvert")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_HOST, LISTEN_PORT))
    sock.settimeout(2.0)
    print(f"En écoute sur UDP {LISTEN_HOST}:{LISTEN_PORT}")
    print("En attente de frames depuis TouchDesigner...\n", flush=True)

    frame_count = 0
    last_stat   = time.monotonic()

    while True:
        try:
            data, _ = sock.recvfrom(65535)
        except socket.timeout:
            continue

        if len(data) < 8 or data[:4] != MAGIC:
            continue

        pps, num_points, flags, _ = struct.unpack_from('<HHBB', data, 4)
        num_points = min(num_points, MAX_POINTS)
        expected   = 10 + num_points * 8   # header = 4 magic + 6 struct = 10 bytes
        if len(data) < expected or num_points == 0:
            continue

        # Construire le tableau de points
        pts = (HeliosPoint * num_points)()
        offset = 10
        for k in range(num_points):
            x, y, r, g, b, i = struct.unpack_from('<HHBBBBxx', data, offset) if False else \
                                (struct.unpack_from('<HH', data, offset) + struct.unpack_from('<BBBB', data, offset + 4))
            pts[k].x = min(x, 0xFFF)
            pts[k].y = min(y, 0xFFF)
            pts[k].r = r; pts[k].g = g; pts[k].b = b; pts[k].i = i
            offset += 8

        # Attendre que le DAC soit prêt puis envoyer
        for _ in range(40):
            if lib.GetStatus(0) == 1:
                break
            time.sleep(0.001)

        result = lib.WriteFrame(0, pps, flags, pts, num_points)
        if result == 1:
            frame_count += 1

        now = time.monotonic()
        if now - last_stat >= 5.0:
            fps = frame_count / (now - last_stat)
            print(f"[INFO] {frame_count} frames ({fps:.1f} fps, {num_points} pts/frame)", flush=True)
            frame_count = 0
            last_stat   = now


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt.")
    except Exception as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            ctypes.CDLL(LIB_PATH).CloseDevices()
        except Exception:
            pass
