import math
from typing import Union

import numpy as np
from PIL import Image

from music_bg.utils import colorstr_to_tuple


def radial_gradient(
    image: Image.Image,
    inner_color: str,
    outer_color: str,
    width: Union[str, int, None] = None,
    height: Union[str, int, None] = None,
) -> Image.Image:
    """

    Generate radial gradient.

    :param image: source image (ignored);
    :param inner_color: inner_color of a gradient.
    :param outer_color: outer color of a gradient.
    :param width: width of a resulting image,
        defaults to width of the source image.
    :param height: height of a resulting image,
        defaults to height of the source image.
    :return: image of a gradient.
    """
    if width is None:
        width = image.width

    if height is None:
        height = image.height

    width = int(width)
    height = int(height)

    inner_color_tup = colorstr_to_tuple(inner_color)
    outer_color_tup = colorstr_to_tuple(outer_color)

    sqrt2 = math.sqrt(2)

    result_img = Image.new("RGBA", (width, height))

    distances = np.full((width, height), None)

    for x in range(width):
        for y in range(height):
            if distances[x, y] is None:
                distance_to_center = math.sqrt(
                    (x - width / 2) ** 2 + (y - height / 2) ** 2,
                )

                # Make it on a scale from 0 to 1
                distance_to_center = distance_to_center / (sqrt2 * width / 2)
                distances[x, y] = distance_to_center
                distances[width - x - 1, y] = distance_to_center
                distances[x, height - y - 1] = distance_to_center
                distances[
                    width - x - 1,
                    height - y - 1,
                ] = distance_to_center

            distance_to_center = distances[x, y]

            # Calculate r, g, b values
            red = outer_color_tup[0] * distance_to_center + inner_color_tup[0] * (
                1 - distance_to_center
            )
            green = outer_color_tup[1] * distance_to_center + inner_color_tup[1] * (
                1 - distance_to_center
            )
            blue = outer_color_tup[2] * distance_to_center + inner_color_tup[2] * (
                1 - distance_to_center
            )

            result_img.putpixel(
                (x, y),
                (int(red), int(green), int(blue)),
            )
    return result_img
