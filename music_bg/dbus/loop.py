import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from loguru import logger

from music_bg.context import Context
from music_bg.dbus.handlers import player_exit_handler, player_signal_handler


def run_loop(context: Context) -> None:
    """
    Run dbus listener loop.

    :param context: current context.
    """
    logger.info("Setting up dbus connection.")
    dbus_loop = DBusGMainLoop()
    bus = dbus.SessionBus(mainloop=dbus_loop)
    bus.add_signal_receiver(
        player_signal_handler(context),
        dbus_interface="org.freedesktop.DBus.Properties",
        path="/org/mpris/MediaPlayer2",
        interface_keyword="org.freedesktop.DBus.Properti",
        arg0="org.mpris.MediaPlayer2.Player",
    )
    bus.add_signal_receiver(
        player_exit_handler(context),
        dbus_interface="org.freedesktop.DBus",
        signal_name="NameOwnerChanged",
        interface_keyword="dbus_interface",
    )
    logger.info("Loop is ready.")
    loop = GLib.MainLoop()
    loop.run()
