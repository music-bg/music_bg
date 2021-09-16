from sys import stdout

from loguru import logger

from music_bg.config import LogLevel


def init_logger(level: LogLevel) -> None:
    """Configure music_bg logging.

    :param level: New log level.
    """
    logger.remove()
    logger.add(
        sink=stdout,
        level=level.value,
        diagnose=True,
        backtrace=True,
    )
