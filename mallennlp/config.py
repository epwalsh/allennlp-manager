from collections import OrderedDict
import os
from pathlib import Path
from typing import ClassVar

import attr
import toml

from mallennlp import VERSION
from mallennlp.exceptions import NotInProjectError


@attr.s(slots=True, auto_attribs=True)
class ProjectConfig:
    name: str = "my-project"


@attr.s(slots=True, auto_attribs=True)
class ServerConfig:
    image: str = f"epwalsh/allennlp-manager:{VERSION}"
    port: int = 5000
    secret: str = attr.ib(
        default=None, converter=lambda s: s or os.urandom(24).hex()  # type: ignore
    )


@attr.s(slots=True, auto_attribs=True)
class Config:
    CONFIG_PATH: ClassVar[str] = "Project.toml"

    project: ProjectConfig
    server: ServerConfig

    @classmethod
    def from_toml(cls, project_directory: Path = None) -> "Config":
        config_path = Path(cls.CONFIG_PATH)
        if project_directory is not None:
            config_path = project_directory / config_path
        if not config_path.exists():
            raise NotInProjectError
        with open(config_path) as config_file:
            config_dict = toml.load(config_file)
        config_dict["project"] = ProjectConfig(**config_dict.get("project", {}))
        config_dict["server"] = ServerConfig(**config_dict.get("server", {}))
        return cls(**config_dict)

    def to_toml(self, project_directory: Path = None):
        config_path = Path(self.CONFIG_PATH)
        if project_directory is not None:
            config_path = project_directory / config_path
        with open(config_path, "w") as config_file:
            config_dict = attr.asdict(self, recurse=True, dict_factory=OrderedDict)
            toml.dump(config_dict, config_file)
