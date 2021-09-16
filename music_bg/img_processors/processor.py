from functools import partial
from multiprocessing import Pool
from operator import attrgetter
from typing import Optional, Tuple, Union

from loguru import logger
from PIL import Image

from music_bg.config import Layer
from music_bg.context import Context


def process_layer(  # noqa: WPS210
    image: Image.Image,
    context: Context,
    layer: Layer,
) -> Tuple[Union[str, int], Image.Image]:
    """
    Process image layer.

    This function sequentially applies image processors
    from the configuration on an album cover.

    :param image: Album cover.
    :param context: Current MBG context.
    :param layer: Current layer.

    :raises ValueError: if unknown variable was used in config.

    :return: Name of the layer and processed image.
    """
    for processor in layer.processors:
        processor_func = context.get_processor(processor.name)
        logger.debug(f"Applying {processor.name} on layer {layer.name}")
        if not processor.args:
            image = processor_func(image)
            continue

        arguments = {}
        for arg, arg_value in processor.args.items():
            try:
                arguments[arg] = str(arg_value).format_map(context.variables())
            except KeyError as kerr:
                raise ValueError(f'Unknown variable "{{{kerr.args[0]}}}"') from kerr

        image = processor_func(image, **arguments)

    return layer.name, image


def process_image(  # noqa: WPS210
    image: Image.Image,
    context: Context,
) -> Optional[Image.Image]:  # : WPS210
    """
    Process album cover according to the config.

    This function processes every layer from configuration
    and merges it.

    :param image: album cover.
    :param context: current music_bg context.
    :raises ValueError: if layer image bigger than the screen.
    :returns: processed image.
    """
    if not context.config.layers:
        return None

    blender = context.config.blender
    if not blender:
        blender = list(map(attrgetter("name"), context.config.layers))

    layers = Pool().map(partial(process_layer, image, context), context.config.layers)
    layers_map = {layer_name: image for layer_name, image in layers}

    image = Image.new("RGBA", (context.screen.width, context.screen.height))
    for blend_index in blender:
        overlay_img = layers_map[blend_index]
        if overlay_img.height > image.height or overlay_img.width > image.width:
            raise ValueError("Layer image bigger than biggest screen.")
        image.alpha_composite(
            overlay_img,
            (
                (image.width - overlay_img.width) // 2,
                (image.height - overlay_img.height) // 2,
            ),
        )
    return image
