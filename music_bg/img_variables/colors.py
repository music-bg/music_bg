from dataclasses import asdict, dataclass, field

from music_bg.context import Context
from music_bg.utils import (
    color_to_hexstr,
    colorstr_to_tuple,
    get_contrasting_accent_colors,
    invert_color,
    most_frequent_color,
)


@dataclass
class ColorsVars:
    """All available color-related vars."""

    least_frequent_color: str = "#000000"
    least_frequent_color_inverted: str = field(init=False)

    accent_color: str = "#FFFFFF"
    accent_color_inverted: str = field(init=False)

    second_accent_color: str = "#000000"
    second_accent_color_inverted: str = field(init=False)

    most_frequent_color: str = "#FFFFFF"
    most_frequent_color_inverted: str = field(init=False)

    def __post_init__(self) -> None:
        self.accent_color_inverted = color_to_hexstr(
            invert_color(colorstr_to_tuple(self.accent_color)),
        )
        self.second_accent_color_inverted = color_to_hexstr(
            invert_color(colorstr_to_tuple(self.second_accent_color)),
        )
        self.most_frequent_color_inverted = color_to_hexstr(
            invert_color(colorstr_to_tuple(self.most_frequent_color)),
        )
        self.least_frequent_color_inverted = color_to_hexstr(
            invert_color(colorstr_to_tuple(self.least_frequent_color)),
        )


def colors_var(context: Context) -> ColorsVars:
    """Setup color-related variables."""
    if context.src_image is None:
        return ColorsVars()

    mf_color = color_to_hexstr(most_frequent_color(context.src_image.copy()))
    bg_accent, fg_accent = get_contrasting_accent_colors(context.src_image.copy(), 4)

    return ColorsVars(
        most_frequent_color=mf_color,
        accent_color=color_to_hexstr(fg_accent),
        second_accent_color=color_to_hexstr(bg_accent),
    )
