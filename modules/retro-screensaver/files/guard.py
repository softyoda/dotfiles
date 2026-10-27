#!/usr/bin/python
"""Extra XScreenSaver protection for games, fullscreen apps and MPRIS players."""
import configparser
import subprocess
from pathlib import Path
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
class Guard(dbus.service.Object):
    fullscreen = False
    @dbus.service.method('local.RetroSaver', in_signature='b', out_signature='')
    def SetFullscreen(self, value):
        self.fullscreen = bool(value)
        tick()
name = dbus.service.BusName('local.RetroSaver', bus)
guard = Guard(bus, '/RetroSaver')
def protection_enabled():
    config = configparser.ConfigParser()
    config.read(Path.home()/'.config/retro-saver/preferences.conf')
    return config.getboolean('General', 'protect', fallback=True)
def blocked():
    if guard.fullscreen:
        return True
    try:
        obj = bus.get_object('com.feralinteractive.GameMode', '/com/feralinteractive/GameMode')
        if obj.ListGames(dbus_interface='com.feralinteractive.GameMode', timeout=2):
            return True
    except dbus.DBusException:
        pass
    for service in bus.list_names():
        if not service.startswith('org.mpris.MediaPlayer2.'):
            continue
        try:
            obj = bus.get_object(service, '/org/mpris/MediaPlayer2')
            if obj.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus', dbus_interface='org.freedesktop.DBus.Properties', timeout=2) == 'Playing':
                return True
        except dbus.DBusException:
            pass
    return False
def tick():
    if protection_enabled() and blocked():
        subprocess.run(['/usr/bin/xscreensaver-command', '-deactivate'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
    return True
GLib.timeout_add_seconds(10, tick)
GLib.MainLoop().run()
