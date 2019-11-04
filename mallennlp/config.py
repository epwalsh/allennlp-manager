from pathlib import Path
from typing import ClassVar

import attr
import toml

from mallennlp.exceptions import NotInProjectError


@attr.s(slots=True, auto_attribs=True)
class ProjectConfig:
    name: str


@attr.s(slots=True, auto_attribs=True)
class ServerConfig:
    port: int


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
