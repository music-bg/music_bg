import inspect
from importlib import metadata
from pathlib import Path

from loguru import logger
from PIL.Image import Image

from music_bg.argparse import parse_args
from music_bg.background import reset_background
from music_bg.config import Config
from music_bg.context import Context
from music_bg.dbus.loop import run_loop
from music_bg.logging import init_logger


def generate_config(config_path: Path) -> None:
    """
    Generate default config file.

    :param config_path: path to config.
    """
    if config_path.exists():
        logger.warning(f"Config {config_path} already exists")
        return
    Config().save(config_path)
    logger.info(f"Config successfully generated at {config_path}")


def show_version() -> None:
    """Show installed version of a Music Background."""
    version = metadata.version("music_bg")
    print(f"Music background v{version}")


def print_processors(context: Context) -> None:
    """
    Print information about available image processors.

    :param context: music_bg context.
    """
    print(" Processors ".center(80, "#"))

    for name, func in context.processors_map.items():
        print("-" * 80)
        print(f"name: {name}")
        print("type: processor")
        args = inspect.signature(func)
        custom_args = []
        for parameter in args.parameters.values():
            if parameter.annotation != Image:
                custom_args.append(parameter)
        if custom_args:
            print(" args ".center(20, "="))
            for arg in custom_args:
                arg_info = f"* {arg.name}"
                if arg.annotation != arg.empty:
                    arg_info = f"{arg_info}: {arg.annotation}"
                if arg.default == arg.empty:
                    arg_info = f"{arg_info} (required)"
                print(arg_info)
        doc = inspect.getdoc(func)
        if doc is not None:
            print(" doc ".center(20, "="))
            print(doc)


def print_variables(context: Context) -> None:
    """
    Print information about available variables.

    :param context: current mbg context.
    """
    print(" Variables ".center(80, "#"))

    context.update_variables()
    for name, value in context.variables.items():
        print("-" * 80)
        print(f"name: {name}")
        print(f"value: {value}")


def show_info(
    context: Context,
    show_processors: bool = False,
    show_variables: bool = False,
) -> None:
    """
    Show information about current context.

    This function shows available processors
    and variable providers.

    :param context: mbg context.
    :param show_processors: show information about processors.
    :param show_variables: show information about variables.
    """
    show_version()
    if show_processors:
        print_processors(context)
    if show_variables:
        print_variables(context)


def main() -> None:
    """The main entrypoint of a program."""
    logger.remove()
    args = parse_args()
    if args.version:
        show_version()
        return
    if args.subparser_name == "gen":
        generate_config(args.config_path)
        return
    context = Context(args.config_path)
    if args.subparser_name == "info":
        show_info(
            context,
            show_processors=args.show_processors,
            show_variables=args.show_vars,
        )
        return
    init_logger(context.config.log_level)
    logger.debug(f"Using config {args.config_path}")
    try:
        run_loop(context)
    except KeyboardInterrupt:
        logger.info("Goodbye!")
        reset_background(context)


if __name__ == "__main__":
    main()
