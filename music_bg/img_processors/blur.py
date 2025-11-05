from typing import Union

from PIL.Image import Image
from PIL.ImageFilter import BoxBlur, GaussianBlur


def box_blur(image: Image, strength: Union[str, int] = 5) -> Image:
    """
    Apply BoxBlur filter onto an image.

    :param image: Input image.
    :param strength: Blur strength.
    :return: Blurred image.
    """
    return image.filter(BoxBlur(int(strength)))


def gaussian_blur(image: Image, radius: Union[float, str] = 5.0) -> Image:
    """
    Apply Gaussian blur to an image.

    :param image: Input image.
    :param radius: Blur radius (float).
    :return: Blurred image.
    """
    return image.filter(GaussianBlur(float(radius)))
