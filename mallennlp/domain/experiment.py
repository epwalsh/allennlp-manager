from enum import Enum
from pathlib import Path
from typing import Optional, Any, Dict, List, Generic, TypeVar

import attr
from allennlp.common.params import Params

from mallennlp.services.serialization import serializable


T = TypeVar("T")


class FileData(Generic[T]):
    """
    Wraps experiment data that comes from a file that might be updated frequently.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lastmod: Optional[float] = path.stat().st_mtime if path.exists() else None
        self.data: Optional[T] = None

    def should_read(self) -> bool:
        if self.path.exists():
            actual_lastmod = self.path.stat().st_mtime
            if not self.data or not self.lastmod or self.lastmod < actual_lastmod:
                self.lastmod = actual_lastmod
                return True
        return False


class Status(Enum):
    UNKNOWN = "UNKNOWN"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


@attr.s(auto_attribs=True)
class Epoch:
    metrics: FileData[Dict[str, Any]]
    """
    Metrics reported for this epoch.
    """


@serializable
class Meta:
    tags: List[str]


@attr.s(auto_attribs=True)
class Experiment:
    path: Path
    """
    Path to experiment directory.
    """

    config: FileData[Params]
    """
    Experiment configuration file.
    """

    meta: FileData[Meta]
    """
    Meta data about experiment.
    """

    metrics: FileData[Dict[str, Any]]
    """
    Final reported metrics, if the experiment completed successfully.
    """

    stdout: FileData[str]
    """
    STDOUT logs, if they exists.
    """

    stderr: FileData[str]
    """
    STDERR logs, if they exists.
    """

    epochs: List[Epoch]
    """
    Data for each epoch.
    """
