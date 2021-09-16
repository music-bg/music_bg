from pathlib import Path
from typing import Any, Callable, Dict, Optional

import requests
from loguru import logger
from PIL import Image

from music_bg.background import reset_background, set_background
from music_bg.context import Context, Metadata
from music_bg.img_processors.processor import process_image


def guard_metadata(context: Context, player_args: Dict[str, Any]) -> Optional[Metadata]:
    """
    This function constructs Metadata.

    If this request was already processed,
    None would be returned.

    :param context: current mbg context.
    :param player_args: arguents passed to dbus.
    :returns: metadata.
    """
    status = player_args.get("PlaybackStatus")
    raw_meta = player_args.get("Metadata")
    print(f"#### {raw_meta}")
    if raw_meta is None:
        return None
    metadata = Metadata(**raw_meta)
    if (  # noqa: WPS337
        str(metadata.track_id) == str(context.metdata.track_id)
        and str(status) == context.last_status
    ):
        return None
    if metadata.art_url is None:
        logger.debug("Can't get art_url")
        return None
    context.last_status = str(status)
    context.metdata = metadata
    return metadata


def player_signal_handler(  # noqa: WPS213, WPS210, C901
    context: Context,
) -> Callable[..., None]:
    """
    Dbus handler generator.

    :param context: current context.
    :return: dbus listener function.
    """

    def _player_signal_handler(  # noqa: WPS213, WPS210, C901
        _dbus_interface: str,
        player_args: Dict[str, Any],
        *_args: Any,
        **_kwargs: Dict[str, Any],
    ) -> None:
        """
        This signal is triggered when player's properties are changed.

        It checks for song's metadata and sets it as the wallpaper.

        :param _dbus_interface: name of the interface on which event apeared.
        :param player_args: current state of a player.
        :param _args: dbus additional arguments.
        :param _kwargs: additional dbus info.
        """
        status = player_args.get("PlaybackStatus")
        metadata = guard_metadata(context, player_args)
        if metadata is None:
            return
        if status != "Playing":
            reset_background(context)
            return
        bg_path = Path("/tmp/music_bg.png")  # noqa: S108
        logger.debug(f"Requesting {metadata.art_url}")
        response = requests.get(str(metadata.art_url), stream=True)
        if not response.ok:
            logger.debug(f"Image response returned status {response.status_code}")
            return
        context.reload_screen_size()

        if context.reloadable:
            context.reload()

        image = Image.open(response.raw).convert("RGBA")
        processed = process_image(image, context)
        if processed is not None:
            processed.save(bg_path)
            set_background(str(bg_path), context)

    return _player_signal_handler


def player_exit_handler(context: Context) -> Callable[..., None]:
    """
    Dbus handler generator.

    :param context: current context.
    :return: dbus listener function.
    """

    def _player_exit_handler(
        name: str,
        _old_name: str,
        new_name: str,
        **_kwargs: Dict[str, Any],
    ) -> None:
        """
        Function which called when someone leaves dbus.

        :param name: name of the interface.
        :param _old_name: old dbus name.
        :param new_name: new dbus name.
        :param _kwargs: different kwargs.
        """
        if str(name).startswith("org.mpris.MediaPlayer2") and str(new_name) == "":
            logger.info(f"Player {name} exited")
            reset_background(context)

    return _player_exit_handler
