from music_bg.context import Context
from music_bg.utils import (
    colorstr_to_tuple,
    get_accent_colors,
    get_contrasting_accent_colors,
    most_frequent_color,
)


def most_frequent_color_var(context: Context) -> str:
    """
    The most frequent color of an album cover.

    returns color in format like "#FFFFFF".

    :param context: current context.
    :return: hex color.
    """
    if context.src_image is None:
        return "#000000"
    dominant_color = most_frequent_color(context.src_image.copy())
    return "#%02X%02X%02X" % dominant_color


def most_frequent_color_inverted_var(context: Context) -> str:
    """
    The most frequent color of an album cover.

    returns color in format like "#FFFFFF".

    :param context: current context.
    :return: hex color.
    """
    if context.src_image is None:
        return "#000000"
    red, green, blue = most_frequent_color(context.src_image.copy())
    return "#%02X%02X%02X" % (
        255 - red,
        255 - green,
        255 - blue,
    )


def accent_color_var(context: Context) -> str:
    if context.src_image is None:
        return "#000000"
    _, fg = get_contrasting_accent_colors(context.src_image, 2)
    return "#%02X%02X%02X" % fg


def accent_color_inv_var(context: Context) -> str:
    r, g, b = colorstr_to_tuple(accent_color_var(context))
    return "#%02X%02X%02X" % (255 - r, 255 - g, 255 - b)


def second_accent_color_var(context: Context) -> str:
    if context.src_image is None:
        return "#000000"
    bg, _ = get_contrasting_accent_colors(context.src_image, 2)
    return "#%02X%02X%02X" % bg


def second_accent_color_inv_var(context: Context) -> str:
    r, g, b = colorstr_to_tuple(second_accent_color_var(context))
    return "#%02X%02X%02X" % (255 - r, 255 - g, 255 - b)


def least_frequent_color_var(context: Context) -> str:
    """
    The most frequent color of an album cover.

    returns color in format like "#FFFFFF".

    :param context: current context.
    :return: hex color.
    """
    if context.src_image is None:
        return "#000000"
    red, green, blue = most_frequent_color(context.src_image.copy())
    return "#%02X%02X%02X" % (
        255 - red,
        255 - green,
        255 - blue,
    )
