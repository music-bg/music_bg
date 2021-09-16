import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import entrypoints
from loguru import logger
from PIL.Image import Image
from pydantic import BaseModel, Field

from music_bg.config import Config


class Metadata(BaseModel):
    """Music metadata."""

    track_id: Optional[str] = Field(alias="mpris:track_id")
    art_url: Optional[str] = Field(alias="mpris:art_url")
    album: Optional[str] = Field(alias="xesam:album")
    artists: Optional[List[str]] = Field(alias="xesam:artist")
    title: Optional[str] = Field(alias="xesam:title")
    track_number: Optional[int] = Field(alias="xesam:track_number")
    url: Optional[str] = Field(alias="xesam:url")


class Screen(BaseModel):
    """Screen dimensions model."""

    width: int = 1366
    height: int = 768


class Context:  # noqa: WPS230
    """music_bg context object."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        reloadable: Optional[bool] = None,
    ):
        """
        Method used to initialize class.

        This is a good topic to discuss, but I've decided to
        create this method, because __init__ method is called
        everytime you create a class instance. But this method
        is called only once in __new__ method.

        :param config_path: path to the config.
        :param reloadable: if config must be reloadable.
        """
        self.config_path = config_path or Path("~/.mbg.json")
        self.config = Config()
        self.reloadable = reloadable or False
        self.last_status = ""
        self.screen = Screen()
        self.metdata = Metadata()
        self.processors_map: Dict[str, Callable[..., Image]] = {}
        self.variables_providers: Dict[str, Callable[..., Any]] = {
            "screen": self.get_screen_size,
            "metadata": self.get_metadata,
        }
        self.reload()

    def reload(self) -> None:
        """Perform full context reload."""
        self.reload_config()
        self.reload_processors()
        self.reload_screen_size()
        self.reload_variables_providers()

    def reload_config(self) -> None:
        """Update configuration from file."""
        self.config = Config.from_file(self.config_path.expanduser())

    def reload_screen_size(self) -> None:
        """
        Update biggest screen size.

        :raises ValueError: if can't get screen size
            or format is invalid.
        """
        logger.debug("Updating screen resolution")
        try:
            run_result = subprocess.run(  # noqa: S603
                ["/bin/sh", "-c", self.config.screen_resolution_command],
                stdout=subprocess.PIPE,
            )
            run_result.check_returncode()
        except subprocess.CalledProcessError:
            raise ValueError("Can't read screen resolution.")

        resolution = run_result.stdout.decode().strip()
        logger.debug(f"Found resolution: {resolution}")
        try:
            width, height = map(int, resolution.split("x"))
        except ValueError:
            raise ValueError(f"Invalid resolution format: '{resolution}'.")

        self.screen = Screen(
            width=width,
            height=height,
        )

    def reload_processors(self) -> None:
        """Find and load in memory all image processors."""
        for entrypoint in entrypoints.get_group_all("mbg_processors"):
            processor_func = entrypoint.load()
            self.processors_map[entrypoint.name] = processor_func

    def reload_variables_providers(self) -> None:
        """Find and load in memory all variables providers."""
        for entrypoint in entrypoints.get_group_all("mbg_variables"):
            variable_func = entrypoint.load()
            self.variables_providers[entrypoint.name] = variable_func

    def get_processor(self, processor_name: str) -> Callable[..., Image]:
        """
        Get processor function by name.

        :param processor_name: name of processor.
        :raises ValueError: if processor is not found.
        :return: processor function.
        """
        if processor_name not in self.processors_map:
            logger.error(f"Processor {processor_name} is not found.")
            raise ValueError(f"Unknown processor {processor_name}")
        return self.processors_map[processor_name]

    def get_screen_size(self) -> Screen:
        """
        Get dimensions of the biggest screen.

        :return: Tuple[width, height]
        """
        return self.screen

    def get_metadata(self) -> Metadata:
        """
        Get current track metadata.

        :return: metadata info.
        """
        return self.metdata

    def variables(self) -> Dict[str, Any]:
        """
        Get variables mapping.

        :return: [description]
        :rtype: [type]
        """
        return {name: var_proc() for name, var_proc in self.variables_providers.items()}
