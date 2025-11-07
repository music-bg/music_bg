import uuid

from music_bg.context import Context


def uuid4(_context: Context) -> uuid.UUID:
    """
    Generate and return UUIDv4.

    :param _context: current context.
    :return: generated UUID.
    """
    return uuid.uuid4()
