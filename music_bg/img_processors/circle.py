from PIL import Image, ImageDraw


def circle(image: Image.Image) -> Image.Image:
    """
    Crop a circle from an image.

    :param image: Input image.
    :return: Circled image.
    """
    big_size = (image.width * 2, image.height * 2)
    mask = Image.new("L", big_size)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, *big_size), fill=255)
    mask = mask.resize(image.size)
    image.putalpha(mask)
    return image
