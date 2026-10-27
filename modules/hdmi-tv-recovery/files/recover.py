#!/usr/bin/python
"""Relance le signal d'une TV HDMI après ses événements hotplug DRM (anti-rebond).

La TV est reconnue par une sous-chaîne de son EDID : variable HDMI_TV_EDID_MATCH
(ex. « Panasonic »), fournie par le service systemd utilisateur.
"""
import logging
import os
from pathlib import Path
import subprocess
import time
import pyudev

LOG = logging.getLogger('hdmi-recovery')
EDID_MATCH = os.environ.get('HDMI_TV_EDID_MATCH', '').encode()

class Debounce:
    def __init__(self):
        self.deadline = None
        self.ignore_until = 0.0
    def event(self, now):
        if now >= self.ignore_until:
            self.deadline = now + 3.0
    def ready(self, now, connected):
        if self.deadline is None or now < self.deadline:
            return False
        self.deadline = None
        if not connected:
            return False
        self.ignore_until = now + 12.0
        return True

def connector():
    for path in Path('/sys/class/drm').glob('card*-HDMI-A-*'):
        try:
            if EDID_MATCH in (path/'edid').read_bytes():
                return path
        except OSError:
            pass
    return None

def recover():
    # Always attempt ON, including if OFF fails or times out.
    try:
        subprocess.run(['/usr/bin/kscreen-doctor', '--dpms', 'off'], check=True, timeout=6)
        time.sleep(1.5)
    finally:
        subprocess.run(['/usr/bin/kscreen-doctor', '--dpms', 'on'], check=True, timeout=6)
    # A lost output can leave the XScreenSaver graphics child crashed.
    active = subprocess.run(['/usr/bin/systemctl', '--user', 'is-active', '--quiet', 'retro-screensaver.service']).returncode == 0
    if active:
        subprocess.run(['/usr/bin/systemctl', '--user', 'restart', 'retro-screensaver.service'], check=True, timeout=10)

def main():
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    if not EDID_MATCH:
        raise SystemExit('HDMI_TV_EDID_MATCH non défini')
    monitor = pyudev.Monitor.from_netlink(pyudev.Context())
    monitor.filter_by(subsystem='drm')
    monitor.start()
    debounce = Debounce()
    # Resolve at startup when available; otherwise resolve when the TV reconnects.
    target = connector()
    LOG.info('Watching %s HDMI hotplug events; no display change on startup', EDID_MATCH.decode())
    while True:
        event = monitor.poll(timeout=0.5)
        now = time.monotonic()
        if event is not None and event.action == 'change' and event.get('HOTPLUG') == '1':
            target = target or connector()
            if target is not None:
                card = target.name.split('-HDMI-', 1)[0]
                if Path(event.sys_path).name in (card, target.name):
                    debounce.event(now)
        if target is None:
            continue
        try:
            connected = (target/'status').read_text().strip() == 'connected'
        except OSError:
            connected = False
        if debounce.ready(now, connected):
            LOG.info('HDMI hotplug settled; restarting video signal')
            try:
                recover()
                LOG.info('Video signal enabled again')
            except (subprocess.SubprocessError, OSError):
                LOG.exception('Video signal recovery failed')

if __name__ == '__main__':
    main()
