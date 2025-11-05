from functools import partial
from operator import mul
from typing import Union

from PIL import Image


def pop_filter(
    image: Image.Image,
    offset_x: Union[str, int] = 60,
    offset_y: Union[str, int] = 60,
    increase_factor: Union[str, float] = 1.4,
    decrease_factor: Union[str, float] = 0.8,
) -> Image.Image:
    """
    Generate pop image.

    This filter splits image by color channels
    and creates three separate images.

    By changing offset you can control relative position
    of the channels.

    :param image: source image.
    :param offset_x: image offset by x axis, defaults to 40
    :param offset_y: image offset by y axis, defaults to 40
    :param increase_factor: color increase factor, defaults to 1.4
    :param decrease_factor: color decrease factor, defaults to 0.8
    :raises ValueError: if offset is less than zero or
        increase factor is less than 1 or decrease_factor is greater than 1.
    :return: new image.
    """
    image = image.convert("RGBA")

    offset_x = int(offset_x)
    offset_y = int(offset_y)

    if offset_y < 0 or offset_x < 0:
        raise ValueError("Offset can't be less than zero.")

    decrease_factor = float(decrease_factor)
    increase_factor = float(increase_factor)

    if increase_factor <= 1:
        raise ValueError("Increase factor must be greater than one.")

    if decrease_factor >= 1:
        raise ValueError("Decrease factor must be less than one.")

    increaser = partial(mul, increase_factor)
    decreaser = partial(mul, decrease_factor)

    red, green, blue, alpha = image.split()

    r_dec, r_inc = red.point(decreaser), red.point(increaser)
    g_dec, g_inc = green.point(decreaser), green.point(increaser)
    b_dec, b_inc = blue.point(decreaser), blue.point(increaser)

    r_img = Image.merge("RGBA", (r_inc, g_dec, b_dec, alpha))
    g_img = Image.merge("RGBA", (r_dec, g_inc, b_dec, alpha))
    b_img = Image.merge("RGBA", (r_dec, g_dec, b_inc, alpha))

    res = Image.new(  # noqa;
        "RGBA",
        (image.width + offset_x * 2, image.height + offset_y * 2),
        (0, 0, 0, 0),
    )

    res.alpha_composite(r_img, (0, 0))
    res.alpha_composite(g_img, (offset_x, offset_y))
    res.alpha_composite(b_img, (offset_x * 2, offset_y * 2))

    return res
