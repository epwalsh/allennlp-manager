from collections import OrderedDict
import os
from pathlib import Path
from typing import ClassVar, Optional

import attr
import toml

from mallennlp import VERSION
from mallennlp.exceptions import NotInProjectError


@attr.s(slots=True, auto_attribs=True)
class ProjectConfig:
    _path: Path
    name: str = "my-project"
    display_name: Optional[str] = None
    loglevel: str = "INFO"


@attr.s(slots=True, auto_attribs=True)
class ServerConfig:
    _path: Path
    image: str = f"epwalsh/allennlp-manager:{VERSION}"
    port: int = 5000
    secret: str = attr.ib(
        default=None, converter=lambda s: s or os.urandom(24).hex()  # type: ignore
    )
    concurrency: int = 10
    memory: int = 1024
    cpus: float = 0.5

    """
    Uppercase properties are mapped to the Flask config.
    """

    @property
    def SECRET_KEY(self):
        return self.secret

    @property
    def instance_path(self):
        return self._path / ".instance/"

    @property
    def DATABASE(self):
        return str(self.instance_path / "mallennlp.sqlite")


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
        full_path = config_path.resolve().parent
        config_dict["project"] = ProjectConfig(
            full_path, **config_dict.get("project", {})
        )
        config_dict["server"] = ServerConfig(full_path, **config_dict.get("server", {}))
        return cls(**config_dict)

    def to_toml(self, project_directory: Path = None):
        config_path = Path(self.CONFIG_PATH)
        if project_directory is not None:
            config_path = project_directory / config_path
        with open(config_path, "w") as config_file:
            config_dict = attr.asdict(
                self,
                recurse=True,
                dict_factory=OrderedDict,
                filter=lambda attribute, value: not attribute.name.startswith("_"),
            )
            toml.dump(config_dict, config_file)
