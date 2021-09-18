from typing import Union

from PIL import Image


def blank_image(
    _image: Image.Image,
    width: Union[str, int],
    height: Union[str, int],
    color: str = "#000000",
) -> Image.Image:
    """
    Generate blank image with one color.

    :param _image: imnput image (ignored)
    :param width: width of a new image.
    :param height: height of a new image.
    :param color: color of an image, defaults to "#000000"
    :returns: created image.
    """
    width = int(width)
    height = int(height)
    return Image.new("RGBA", (width, height), color)
