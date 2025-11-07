import os
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def xdg_config_home() -> Path:
    """
    Return a Path corresponding to XDG_CONFIG_HOME.

    :return: xdg_config_home path.
    """
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if not config_home:
        return Path.home() / ".config"
    return Path(config_home)


def most_frequent_color(
    image: Image.Image,
) -> Tuple[int, int, int]:
    """
    Find the most frequent color of the image.

    :param image: input image.
    :param reverse: whether to return the most (False) or least (True) frequent color.
    :return: color tuple.
    """
    image.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=3)
    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)  # type: ignore
    palette_index = color_counts[0][1]

    dominant_color = palette[palette_index * 3 : palette_index * 3 + 3]  # type: ignore

    return tuple(dominant_color)


def get_accent_colors(
    image: Image.Image,
    num_colors: int = 5,
) -> list[Tuple[int, int, int]]:
    """Get accent colors."""
    image.thumbnail((100, 100))
    image = image.convert("RGB")

    img_np = np.array(image).reshape((-1, 3))
    kmeans = KMeans(n_clusters=num_colors, init="k-means++", n_init=10, random_state=42)
    kmeans.fit(img_np)

    accent_colors = kmeans.cluster_centers_.astype(int)

    return [tuple(color) for color in accent_colors]


def luminance(color: Tuple[int, int, int]) -> float:
    """
    Calculate the luminance of a color.

    :param color: color tuple (red, green, blue).
    :return: luminance value.
    """
    red, green, blue = color
    # Using the Rec. 709 formula for luminance
    # return 0.299 * red + 0.587 * green + 0.114 * blue  # noqa: ERA001
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(
    color1: Tuple[int, int, int],
    color2: Tuple[int, int, int],
) -> float:
    """
    Calculate the contrast ratio between two colors.

    :param color1: first color tuple (red, green, blue).
    :param color2: second color tuple (red, green, blue).
    :return: contrast ratio.
    """
    lum1 = luminance(color1)
    lum2 = luminance(color2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


def get_contrasting_accent_colors(
    image: Image.Image,
    min_contrast_ratio: float = 5.5,
    num_colors: int = 5,
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Get accent colors from the image that have sufficient contrast score.

    :param image: input image.
    :param background_color: background color tuple (red, green, blue).
    :param min_contrast_ratio: minimum contrast ratio required.
    :param num_colors: number of accent colors to extract.
    :return: list of accent colors with sufficient contrast.
    """
    accent_colors = get_accent_colors(image, num_colors)
    fg = accent_colors[0]
    bg = (255 - fg[0], 255 - fg[1], 255 - fg[1])  # Default to inversed fg
    for color in accent_colors[1:]:
        if contrast_ratio(color, fg) >= min_contrast_ratio:
            bg = color
            break
    return (bg, fg)


def colorstr_to_tuple(color: str) -> Tuple[int, int, int]:
    """
    Convert color hex to tuple of ints.

    :param color: color hex.
    :raises ValueError: if string has unknown format.
    :return: color tuple (red, green, blue).
    """
    color_hex = color.lstrip("#")
    if len(color_hex) != 6:
        raise ValueError(f"Badly formatted color string: '{color_hex}'")

    red = int(color_hex[:2], base=16)
    green = int(color_hex[2:4], base=16)
    blue = int(color_hex[4:], base=16)

    return red, green, blue


def invert_color(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Find the inverted color."""
    return (255 - color[0], 255 - color[1], 255 - color[2])


def color_to_hexstr(clr: Tuple[int, int, int]) -> str:
    """Convert a color tuple to an hex string."""
    return "#%02X%02X%02X" % clr
