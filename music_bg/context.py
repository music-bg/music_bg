from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Callable, Dict, List

import screeninfo
from loguru import logger
from PIL.Image import Image
from pydantic import BaseModel, Field

from music_bg.config import Config


class Metadata(BaseModel):
    """Music metadata."""

    track_id: str | None = Field(alias="mpris:trackid", default=None)
    art_url: str | None = Field(alias="mpris:artUrl", default=None)
    album: str | None = Field(alias="xesam:album", default=None)
    artists: List[str] | None = Field(alias="xesam:artist", default=None)
    title: str | None = Field(alias="xesam:title", default=None)
    track_number: int | None = Field(alias="xesam:trackNumber", default=None)
    url: str | None = Field(alias="xesam:url", default=None)


class Screen(BaseModel):
    """Screen dimensions model."""

    width: int = 1366
    height: int = 768


class Context:
    """music_bg context object."""

    def __init__(
        self,
        config_path: Path | None = None,
    ) -> None:
        """
        Method used to initialize class.

        This is a good topic to discuss, but I've decided to
        create this method, because __init__ method is called
        everytime you create a class instance. But this method
        is called only once in __new__ method.

        :param config_path: path to the config.
        """
        self.config_path = config_path or Path("~/.mbg.json")
        self.config = Config()
        self.last_status = ""
        self.screen = Screen()
        self.metadata = Metadata()
        self.src_image: Image | None = None
        self.previous_image: Image | None = None
        self.processors_map: Dict[str, Callable[..., Image]] = {}
        self.variables: Dict[str, Any] = {}
        self.variables_providers: Dict[str, Callable[..., Any]] = {
            "default_vars": Context.get_default_variables,
        }
        self.reload()

    def get_default_variables(self) -> dict[str, Any]:
        """Get default variables."""
        return {"screen": self.screen, "metadata": self.metadata}

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

        :raises ValueError: if can't get screen size or format is invalid.
        """
        logger.debug("Updating screen resolution")
        # Sort screens by their areas
        # and get the last one.
        biggest_screen = sorted(
            screeninfo.get_monitors(),
            key=lambda m: m.width * m.height,
        )[-1]

        self.screen = Screen(
            width=biggest_screen.width,
            height=biggest_screen.height,
        )

    def reload_processors(self) -> None:
        """Find and load in memory all image processors."""
        for entrypoint in entry_points(group="mbg_processors"):
            processor_func = entrypoint.load()
            self.processors_map[entrypoint.name] = processor_func

    def reload_variables_providers(self) -> None:
        """Find and load in memory all variables providers."""
        for entrypoint in entry_points(group="mbg_variables"):
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

        screen has two fields:
        * width
        * height

        You can use it as

        {screen.width} or {screen.height}

        :returns: a Screen object.
        """
        return self.screen

    def get_metadata(self) -> Metadata:
        """
        Get current track metadata.

        :return: metadata info.
        """
        return self.metadata

    def update_variables(self) -> None:
        """
        Get variables mapping.

        :return: mapping with variables.
        """
        self.variables.clear()
        for name, var_proc in self.variables_providers.items():
            logger.debug(f"Updating {name} variable")
            self.variables.update(var_proc(self))
