from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path

from xdg import xdg_config_home


def parse_args() -> Namespace:
    """
    Parse CLI arguments.

    :return: parsed Namespace.
    """
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Path to the configuration file",
        default=xdg_config_home() / ".mbg.json",
        type=Path,
        dest="config_path",
    )

    parser.add_argument(
        "-V",
        "--version",
        help="Show application version",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-r",
        "--reload",
        help="Reload configuration before setting background",
        action="store_true",
        default=False,
    )

    subparsers = parser.add_subparsers(dest="subparser_name")

    gen_parser = subparsers.add_parser(
        "gen",
        help="Generate config",
    )

    info_parser = subparsers.add_parser(
        "info",
        help="Get additional configuration information",
    )

    info_parser.add_argument(
        "-p",
        "--processors",
        action="store_true",
        help="Show available processors",
        dest="show_processors",
    )

    info_parser.add_argument(
        "-v",
        "--vars",
        action="store_true",
        help="Show available variables",
        dest="show_vars",
    )

    gen_parser.add_argument(
        "-f",
        "--format",
        default="json",
        choices=["json", "toml"],
        help="Config file format.",
    )

    gen_parser.add_argument(
        "-c",
        "--config",
        help="Path to the configuration file",
        default=xdg_config_home() / ".mbg.json",
        type=Path,
        dest="config_path",
    )

    return parser.parse_args()
