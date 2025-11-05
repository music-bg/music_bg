from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFont

from music_bg.utils import most_frequent_color


def img_print(
    image: Image.Image,
    text: str,
    color: Optional[str] = None,
    font: str = "DejaVuSans",
    font_size: Union[str, int] = 30,
    start_x: Union[str, int, None] = None,
    start_y: Union[str, int, None] = None,
) -> Image.Image:
    """
    Render a text on the image.

    if start_x and start_y are equal to None,
    text is rendered in the center of an image.

    :param image: input image.
    :param text: text to render.
    :param color: text color
        if color is None, inverted to the most common one is chosen.
    :param font: font to use, defaults to "DejaVuSans"
    :param font_size: size of a font, defaults to 30
    :param start_x: where to start rendering text on the x axis,
        if start_x is None, center of the image is chosen.
    :param start_y: where to start rendering text on the y axis,
        if start_y is None, center of the image is chosen.
    :return: image with text on it.
    """
    img_font = ImageFont.truetype(font, int(font_size))
    draw = ImageDraw.Draw(image)
    # left, top, right, bottom
    _, _, text_w, text_h = draw.textbbox((0, 0), text, font=img_font)

    if start_x is None:
        start_x = int((image.width - text_w) // 2)

    if start_y is None:
        start_y = int((image.height - text_h) // 2)

    if color is None:
        red, green, blue = most_frequent_color(image.copy())
        color = (255 - red, 255 - green, 255 - blue)  # type: ignore

    draw.text(
        xy=(int(start_x), int(start_y)),
        text=text,
        fill=color,
        font=img_font,
    )
    return image
