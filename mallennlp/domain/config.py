import os
from pathlib import Path
from typing import Optional, List

import attr


@attr.s(slots=True, auto_attribs=True)
class ProjectConfig:
    _path: Path
    name: str = "my-project"
    display_name: Optional[str] = None
    loglevel: str = "INFO"


@attr.s(slots=True, auto_attribs=True)
class ServerConfig:
    _path: Path
    port: int = 5000
    secret: str = attr.ib(
        default=None, converter=lambda s: s or os.urandom(24).hex()  # type: ignore
    )
    concurrency: int = 100
    imports: Optional[List[str]] = None

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
    def cache_path(self):
        return self.instance_path / "cache/"

    @property
    def DATABASE(self):
        return str(self.instance_path / "mallennlp.sqlite")
