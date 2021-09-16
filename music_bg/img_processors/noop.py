from PIL.Image import Image


def noop(image: Image) -> Image:
    """
    Dummy processor.

    It does nothing and returns the same image.

    :param image: input image
    :return: same image
    """
    return image
