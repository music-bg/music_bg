from PIL import Image


def load_img(_image: Image.Image, path: str) -> Image.Image:
    """
    Load image from disk.

    :param _image: input image (ignored).
    :param path: path to image to load.
    :returns: loaded image.
    """
    return Image.open(path).convert("RGBA")
