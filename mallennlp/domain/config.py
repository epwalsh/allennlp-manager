from multiprocessing import cpu_count
import os
from pathlib import Path
from typing import Optional, List

import attr


@attr.s(slots=True, auto_attribs=True)
class ProjectConfig:
    _path: Path
    """
    Root experiment directory.
    """

    name: str = "my-project"
    """
    Name of directory / name of project.
    """

    display_name: Optional[str] = None
    """
    Name to display in dashboard. Defaults to `name`.
    """

    loglevel: str = "INFO"
    """
    Log level across CLI and dashboard.
    """


@attr.s(slots=True, auto_attribs=True)
class ServerConfig:
    _path: Path
    """
    Root experiment directory.
    """

    port: int = 5000
    """
    Port to bind to the server.
    """

    secret: str = attr.ib(
        default=None, converter=lambda s: s or os.urandom(24).hex()  # type: ignore
    )
    """
    Used for security in the server.
    """

    workers: int = attr.ib(default=cpu_count())
    """
    Number of worker processes for handling requests. Defaults to CPU count.
    """

    worker_connections: int = 10000
    """
    Maximum number of simultaneous connections.
    """

    imports: Optional[List[str]] = None
    """
    Additional packages to import.
    """

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
