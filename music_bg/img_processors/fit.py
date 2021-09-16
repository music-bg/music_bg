import math
from typing import Union

from PIL.Image import Image


def fit(  # noqa: WPS210
    image: Image,
    width: Union[str, int],
    height: Union[str, int],
) -> Image:
    """
    Fit image into given dimensions.

    This processor resizes image,
    and keep aspect ratio of an image.

    :param image: image to fit.
    :param width: desired width.
    :param height: desired height.
    :return: resized image.
    """
    width = int(width)
    height = int(height)

    width_factor = math.ceil(width / image.width)
    height_factor = math.ceil(height / image.height)

    scale_factor = max(width_factor, height_factor)

    resized = image.resize(
        (image.width * scale_factor, image.height * scale_factor),
    )

    return resized.crop(
        (
            (resized.width - width) // 2,
            (resized.height - height) // 2,
            (resized.width + width) // 2,
            (resized.height + height) // 2,
        ),
    )
