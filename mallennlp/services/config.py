from collections import OrderedDict
from pathlib import Path
from typing import ClassVar

import attr
import toml

from mallennlp.domain.config import ProjectConfig, ServerConfig
from mallennlp.domain.dataclass import dataclass
from mallennlp.exceptions import NotInProjectError


@dataclass
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
