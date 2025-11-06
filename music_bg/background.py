import subprocess

from loguru import logger

from music_bg.context import Context


def set_background(filename: str, context: Context) -> None:
    """
    Update current background.

    :param filename: path to background file.
    :param context: current mbg context.
    """
    logger.debug("Setting background")
    command = context.config.set_command.format_map(
        {
            "0": filename,  # for backward compatibility
            "out": filename,
            "output": filename,
            **context.variables,
        },
    )
    try:
        subprocess.run(["/bin/sh", "-c", command], check=False).check_returncode()  # noqa: S603
    except subprocess.CalledProcessError as exc:
        logger.exception(exc)


def reset_background(context: Context) -> None:
    """
    Return background to the default state.

    :param context: current mbg context.
    """
    logger.debug("Reseting background")
    command = context.config.reset_command
    try:
        subprocess.run(["/bin/sh", "-c", command], check=False).check_returncode()  # noqa: S603
    except subprocess.CalledProcessError as exc:
        logger.exception(exc)
