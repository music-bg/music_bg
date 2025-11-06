import enum
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Union

import toml
from pydantic import BaseModel


class ImageProcessor(BaseModel):
    """Image processor config."""

    name: str
    args: dict[str, Any] | None = None


class Layer(BaseModel):
    """Mergeable layer."""

    name: Union[str, int]
    processors: List[ImageProcessor]


class LogLevel(enum.Enum):
    """Possible log levels."""

    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class Config(BaseModel):
    """User configuration object."""

    blender: list[str | int] = []
    log_level: LogLevel = LogLevel.INFO

    set_command: str = 'feh --bg-fill "{0}"'
    reset_command: str = "nitrogen --restore"

    screen_resolution_command: str = "xrandr | grep '*' | cut -d' ' -f4 | sort --human-numeric-sort --reverse | head -n 1"  # noqa: E501
    layers: list[Layer] = []

    @classmethod
    def get_serde_by_extension(
        cls,
        ext: str,
    ) -> Iterable[Callable[..., Dict[str, Any]]]:
        """
        Get serializer and deserializer for the given file extension.

        :param ext: file extension.
        :raises ValueError: if unknown extension was passed.
        :return: serializer and deserializer.
        """
        extension_map = {
            "json": (json.dump, json.load),
            "toml": (toml.dump, toml.load),
        }
        if ext not in extension_map:
            known_formats = ",".join(extension_map.keys())
            raise ValueError(
                f"Unknown config format. Supported formats: {known_formats}",
            )
        return extension_map[ext]  # type: ignore

    @classmethod
    def from_file(
        cls,
        config_path: Path,
    ) -> "Config":
        """
        Load config from a given path.

        :param config_path: path to the configuration file.
        :return: Config instance.
        """
        extension = config_path.name.split(".")[-1]

        _, des = cls.get_serde_by_extension(extension)

        with Path(config_path).open("r") as config_io:
            deserialized = des(config_io)
        return cls(**deserialized)

    def save(self, config_path: Path) -> None:
        """Write config to file.

        :param config_path: path to file.
        """
        extension = config_path.name.split(".")[-1]

        ser, _ = self.get_serde_by_extension(extension)

        with Path(config_path).open("w") as config_io:
            ser(self.model_dump_json(exclude={"log_level"}), config_io)
