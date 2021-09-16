from typing import Optional

from PIL.Image import Image


def resize(
    image: Image,
    width: Optional[str] = None,
    height: Optional[str] = None,
    factor: Optional[str] = None,
) -> Image:
    """
    Resize image with given size.

    :param image: target image to resize.
    :param width: new image's width
    :param height: new image's height
    :param factor: scale factor.
        Image dimensions will be multiplied by this parameter.
        if passed, width and heigh parameters are ignored.
    :return: resized image.
    """
    new_width = int(width or image.width)
    new_height = int(height or image.height)

    if factor is not None:
        new_width = int(image.width * float(factor))
        new_height = int(image.height * float(factor))

    return image.resize((new_width, new_height))
