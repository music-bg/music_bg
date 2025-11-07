from tempfile import NamedTemporaryFile
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
    raw_meta = player_args.get("Metadata")
    if raw_meta is None:
        return None
    metadata = Metadata(**raw_meta)
    if str(metadata.track_id) == str(context.metadata.track_id):
        return None
    if metadata.art_url is None:
        logger.debug("Can't get art_url")
        return None
    return metadata


def player_signal_handler(
    context: Context,
) -> Callable[..., None]:
    """
    Dbus handler generator.

    :param context: current context.
    :return: dbus listener function.
    """

    def _player_signal_handler(
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

        if status:
            context.last_status = str(status).lower()

        if metadata:
            context.metadata = metadata

        if context.last_status != "playing":
            logger.info("Resetting background")
            reset_background(context)
            return

        if not context.metadata.art_url:
            logger.warning("No art url")
            return

        logger.debug(f"Requesting {context.metadata.art_url}")
        response = requests.get(context.metadata.art_url, stream=True, timeout=5)
        if not response.ok:
            logger.debug(f"Image response returned status {response.status_code}")
            return

        context.reload()

        image = Image.open(response.raw).convert("RGBA")  # type: ignore
        context.src_image = image.copy()
        context.update_variables()
        processed = process_image(image, context)
        context.previous_image = processed
        if processed is not None:
            with NamedTemporaryFile(mode="wb", delete=True) as temp_file:
                processed.save(temp_file, format="png")
                logger.debug(f"Background saved at {temp_file.name}")
                set_background(temp_file.name, context)

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
