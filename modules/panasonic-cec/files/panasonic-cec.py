#!/usr/bin/python3
"""Bridge the Plasma launcher and logind power-off to a Pico-CEC adapter."""

import fcntl
import logging
import os
from pathlib import Path
import re
import signal
import struct
import termios
import time
import tty

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib, GLibUnix

DEVICE = "/dev/panasonic-cec"
LOGIN = "org.freedesktop.login1"
LOGIN_PATH = "/org/freedesktop/login1"
LOGIN_MANAGER = LOGIN + ".Manager"
FRAME = re.compile(r"\[\s*\d+\]\s+([\da-f]{2}) (->|~>|<-|<~) ([\da-f]{2}): "
                   r"\[([^\]]+)\](?:\[([^\]]*)\])?", re.I)
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

log = logging.getLogger("panasonic-cec")


class Controller:
    def __init__(self, system_bus):
        self.manager = dbus.Interface(system_bus.get_object(LOGIN, LOGIN_PATH), LOGIN_MANAGER)
        self.inhibitor = None
        self.stopping = False
        self.fd = None
        self.watch = None
        self.serial_buffer = b""
        self.physical = None
        self.logical = None
        self.streaming = False
        self.active = None
        self.power = None
        self.wake_timer = None
        self.announcement_deadline = 0.0
        self.last_shortcut = 0.0
        self.boot_checked = False
        self.boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        state_home = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
        self.boot_marker = state_home / "panasonic-cec" / "boot-id"

    def inhibit(self):
        try:
            self.inhibitor = self.manager.Inhibit(
                "shutdown", "Panasonic HDMI-CEC", "Envoyer la veille HDMI-CEC si le PC est la source", "delay"
            ).take()
        except dbus.DBusException as error:
            log.warning("Surveillance de l’arrêt indisponible (%s)", error.get_dbus_name())

    def release_inhibitor(self):
        if self.inhibitor is not None:
            os.close(self.inhibitor)
            self.inhibitor = None
        return GLib.SOURCE_REMOVE

    def connect(self):
        if self.stopping:
            return GLib.SOURCE_CONTINUE
        if self.fd is not None:
            if not self.streaming:
                self.write("show cec")
            return GLib.SOURCE_CONTINUE

        try:
            fd = os.open(DEVICE, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK | os.O_CLOEXEC)
        except (FileNotFoundError, PermissionError):
            return GLib.SOURCE_CONTINUE
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            tty.setraw(fd)
            fcntl.ioctl(fd, termios.TIOCMBIS, struct.pack("I", termios.TIOCM_DTR))
            self.fd = fd
            self.watch = GLib.io_add_watch(
                fd, GLib.PRIORITY_DEFAULT, GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP, self.read_ready
            )
            log.info("RP2040 ouverte sur %s", DEVICE)
        except OSError as error:
            os.close(fd)
            log.warning("Port CEC indisponible (%s)", error)
        return GLib.SOURCE_CONTINUE

    def disconnect(self):
        if self.watch is not None:
            GLib.source_remove(self.watch)
            self.watch = None
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        self.physical = self.logical = self.active = self.power = None
        self.streaming = False
        self.announcement_deadline = 0.0
        self.serial_buffer = b""
        self.cancel_wake()

    def read_ready(self, fd, condition):
        try:
            data = os.read(fd, 4096) if condition & GLib.IO_IN else b""
        except BlockingIOError:
            return GLib.SOURCE_CONTINUE
        except OSError:
            data = b""
        if not data:
            self.watch = None
            self.disconnect()
            log.info("Port CEC déconnecté")
            return GLib.SOURCE_REMOVE

        *lines, self.serial_buffer = (self.serial_buffer + data).split(b"\r")
        if len(self.serial_buffer) > 4096:
            self.serial_buffer = b""
        for line in lines:
            self.parse(ANSI.sub("", line.decode(errors="replace")))
            if self.fd != fd:
                break
        return self.fd is not None

    def write(self, command):
        if self.fd is None:
            return False
        message = (command + "\r").encode("ascii")
        try:
            if os.write(self.fd, message) == len(message):
                return True
        except OSError:
            pass
        log.warning("Écriture interrompue sur le port CEC")
        self.disconnect()
        return False

    def set_active(self, path):
        self.announcement_deadline = 0.0
        if path != self.active:
            self.active = path
            if path is None:
                log.info("Source CEC indéterminée")
            else:
                log.info("Source CEC observée %s%s", format(path, "04x"),
                         " (PC)" if path == self.physical else "")

    def parse(self, line):
        address = re.search(r"Physical address\s*:\s*0x([\da-f]{4})", line, re.I)
        if address:
            self.physical = int(address[1], 16) or None
        address = re.search(r"Logical address\s*:\s*0x0([1-9a-e])", line, re.I)
        if address:
            self.logical = int(address[1], 16)
        address = re.search(r"Active address\s*:\s*0x([\da-f]{4})", line, re.I)
        if address and self.streaming:
            path = int(address[1], 16)
            self.set_active(None if path == 0xffff else path)
            return
        if self.physical and self.logical and not self.streaming:
            self.streaming = self.write("debug on")
            if self.streaming:
                log.info("CEC prêt, adresse PC %04x et adresse logique %x", self.physical, self.logical)
                if not self.stopping and not self.boot_checked:
                    self.check_boot()
                GLib.timeout_add(2600, self.discover_source)
            return

        frame = FRAME.search(line)
        if not frame:
            return
        initiator, arrow, _destination, event, detail = frame.groups()
        if arrow in ("<-", "<~"):
            if event in ("Image View On", "Active Source", "Standby"):
                log.info("CEC émis %s%s%s", event, f" {detail}" if detail else "",
                         " (ACK)" if arrow == "<-" else "")
            if (event == "Active Source" and detail and self.power == "On"
                    and time.monotonic() < self.announcement_deadline
                    and int(detail.split()[0], 16) == self.physical):
                # This TV follows One Touch Play. Any subsequent routing frame
                # takes precedence over the source we just announced.
                self.set_active(self.physical)
            return

        if event == "Report Power Status" and initiator == "00":
            self.power = detail
            log.info("État CEC de la TV %s", detail)
            if detail == "Standby":
                self.set_active(None)
        elif event == "Routing Change" and detail and initiator == "00":
            self.set_active(int(detail.split(" -> ")[-1], 16))
        elif event in ("Set Stream Path", "Routing Information"):
            self.set_active(int(detail, 16) if detail and initiator == "00" else None)
        elif event == "Active Source" and detail:
            path = int(detail.split()[0], 16)
            if path != self.physical or initiator == "00":
                self.set_active(path)
        elif event in ("Standby", "Inactive Source", "81"):
            self.set_active(None)

    def check_boot(self):
        self.boot_checked = True
        try:
            if self.boot_marker.read_text().strip() == self.boot_id:
                return
        except FileNotFoundError:
            pass
        except OSError as error:
            log.warning("État du démarrage illisible (%s)", error)

        self.power = None
        if self.write("send 0 8f"):
            GLib.timeout_add(900, self.finish_boot_wake)
        else:
            self.boot_checked = False

    def finish_boot_wake(self):
        if not self.stopping and self.streaming:
            if time.monotonic() - self.last_shortcut < 2:
                log.info("Réveil au démarrage déjà demandé par le raccourci")
            elif self.power not in ("On", "In transition Standby to On"):
                log.info("Réveil au démarrage")
                if not self.write("send 0 04"):
                    self.boot_checked = False
                    return GLib.SOURCE_REMOVE
            else:
                log.info("TV déjà allumée au démarrage")
            try:
                self.boot_marker.parent.mkdir(parents=True, exist_ok=True)
                self.boot_marker.write_text(self.boot_id + "\n")
            except OSError as error:
                log.warning("État du démarrage non enregistré (%s)", error)
        elif not self.stopping:
            self.boot_checked = False
        return GLib.SOURCE_REMOVE

    def cancel_wake(self):
        if self.wake_timer is not None:
            GLib.source_remove(self.wake_timer)
            self.wake_timer = None

    def discover_source(self):
        if self.streaming and self.active is None:
            # The TV can confirm its current path with Set Stream Path when
            # rediscovering the device already connected to that input.
            self.write(f"send f 84 {self.physical >> 8:02x} {self.physical & 255:02x} 04")
        return GLib.SOURCE_REMOVE

    def launcher_pressed(self, component, shortcut, _timestamp):
        if component != "plasmashell" or shortcut != "activate application launcher" or self.stopping:
            return
        now = time.monotonic()
        if now - self.last_shortcut < 0.8:
            return
        self.last_shortcut = now
        if not self.streaming:
            log.info("Raccourci du lanceur reçu, carte CEC indisponible")
            return
        log.info("Raccourci du lanceur reçu, réveil et sélection HDMI du PC")
        if self.active != self.physical:
            self.set_active(None)
        self.cancel_wake()
        self.power = None
        self.write("send 0 8f")
        if self.write("send 0 04"):
            self.wake_timer = GLib.timeout_add(350, self.announce_pc, True)

    def announce_pc(self, allow_retry):
        self.wake_timer = None
        if not self.stopping and self.streaming:
            self.announcement_deadline = time.monotonic() + 1.5
            announced = self.write(f"send f 82 {self.physical >> 8:02x} {self.physical & 255:02x}")
            if announced and allow_retry and self.power != "On" and self.active != self.physical:
                self.wake_timer = GLib.timeout_add(1800, self.announce_pc, False)
        return GLib.SOURCE_REMOVE

    def prepare_shutdown(self, preparing, metadata):
        if not preparing:
            self.stopping = False
            if self.inhibitor is None:
                self.inhibit()
            return
        self.stopping = True
        self.cancel_wake()
        self.announcement_deadline = 0.0
        shutdown_type = str(metadata.get("type", ""))
        log.info("Signal logind reçu, arrêt de type %s", shutdown_type or "inconnu")
        if self.inhibitor is None:
            log.warning("Délai d’arrêt indisponible, veille CEC ignorée")
            return
        if shutdown_type not in ("poweroff", "power-off"):
            return self.release_inhibitor()
        if not self.streaming:
            log.info("Carte CEC indisponible, veille ignorée")
            self.release_inhibitor()
            return
        self.power = None
        self.write("send 0 8f")
        GLib.timeout_add(330, self.request_shutdown_source)
        GLib.timeout_add(1850, self.read_shutdown_route)
        GLib.timeout_add(2150, self.finish_shutdown)

    def request_shutdown_source(self):
        if self.stopping and self.streaming:
            self.write("send f 85")
            if self.active is None and self.power == "On":
                GLib.timeout_add(450, self.discover_source)
        return GLib.SOURCE_REMOVE

    def read_shutdown_route(self):
        if self.stopping and self.streaming:
            self.write("show cec")
        return GLib.SOURCE_REMOVE

    def finish_shutdown(self):
        if not self.stopping or self.inhibitor is None:
            return GLib.SOURCE_REMOVE
        if self.streaming and self.active == self.physical and self.power == "On":
            log.info("Arrêt du PC, entrée PC observée, envoi de la veille")
            if self.write("send 0 36"):
                GLib.timeout_add(550, self.release_inhibitor)
                return GLib.SOURCE_REMOVE
        source = f"{self.active:04x}" if self.active is not None else "inconnue"
        log.info("Arrêt du PC, veille ignorée (source %s, TV %s)", source, self.power or "inconnue")
        return self.release_inhibitor()


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    system_bus = dbus.SystemBus()
    loop = GLib.MainLoop()
    controller = Controller(system_bus)
    session_bus.add_signal_receiver(
        controller.launcher_pressed, signal_name="globalShortcutPressed",
        dbus_interface="org.kde.kglobalaccel.Component", bus_name="org.kde.kglobalaccel",
        path="/component/plasmashell",
    )
    system_bus.add_signal_receiver(
        controller.prepare_shutdown, signal_name="PrepareForShutdownWithMetadata",
        dbus_interface=LOGIN_MANAGER, bus_name=LOGIN, path=LOGIN_PATH,
    )
    controller.inhibit()
    controller.connect()
    GLib.timeout_add(1000, controller.connect)
    for sig in (signal.SIGINT, signal.SIGTERM):
        GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, sig, loop.quit)
    try:
        loop.run()
    finally:
        controller.write("debug off")
        controller.disconnect()
        controller.release_inhibitor()


if __name__ == "__main__":
    main()
