import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterable, Set

from allennlp.common.params import Params

from mallennlp.domain.experiment import Experiment, Epoch, Meta, FileData


class ExperimentService:
    CONFIG_FNAME: str = "config.json"

    META_FNAME: str = "meta.json"

    METRICS_FNAME: str = "metrics.json"

    STDOUT_FNAME: str = "stdout.log"

    STDERR_FNAME: str = "stderr.log"

    EPOCH_METRICS_FNAME = "metrics_epoch_%d.json"

    DIRS_TO_IGNORE: Set[str] = {"vocabulary", "log"}

    def __init__(self, path: Path) -> None:
        self.e = Experiment(
            path=path,
            config=FileData(path / self.CONFIG_FNAME),
            meta=FileData(path / self.META_FNAME),
            metrics=FileData(path / self.METRICS_FNAME),
            stdout=FileData(path / self.STDOUT_FNAME),
            stderr=FileData(path / self.STDERR_FNAME),
            epochs=[],
        )

    def get_config(self) -> Params:
        fd = self.e.config
        if fd.should_read():
            fd.data = Params.from_file(fd.path)
        if fd.data is None:
            raise FileNotFoundError
        return fd.data

    def get_meta(self) -> Optional[Meta]:
        fd = self.e.meta
        if fd.should_read():
            with open(fd.path) as f:
                fd.data = Meta(**json.load(f))
        return fd.data

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        fd = self.e.metrics
        if fd.should_read():
            with open(fd.path) as f:
                fd.data = json.load(f)
        return fd.data

    def get_stdout(self) -> Optional[str]:
        fd = self.e.stdout
        if fd.should_read():
            with open(fd.path) as f:
                fd.data = f.read()
        return fd.data

    def get_stderr(self) -> Optional[str]:
        fd = self.e.stderr
        if fd.should_read():
            with open(fd.path) as f:
                fd.data = f.read()
        return fd.data

    def get_epochs(self) -> List[Epoch]:
        epoch_number = 0
        epoch_metric_path = self.e.path / (self.EPOCH_METRICS_FNAME % epoch_number)
        while epoch_metric_path.exists():
            try:
                epoch = self.e.epochs[epoch_number]
            except IndexError:
                epoch = Epoch(FileData(epoch_metric_path))
                self.e.epochs.append(epoch)
            if epoch.metrics.should_read():
                with open(epoch_metric_path) as f:
                    epoch.metrics.data = json.load(f)
            epoch_number += 1
            epoch_metric_path = self.e.path / (self.EPOCH_METRICS_FNAME % epoch_number)
        return self.e.epochs

    @classmethod
    def is_experiment(cls, path: Path) -> bool:
        # Just check if config exists.
        return (path / cls.CONFIG_FNAME).exists()

    @classmethod
    def find_experiments(
        cls, root: Path, ignore_root: bool = True
    ) -> Iterable["ExperimentService"]:
        root = root.resolve()
        for dirpath, dirnames, _ in os.walk(root):
            path = Path(dirpath).resolve()
            if cls.is_experiment(path) and (path != root or not ignore_root):
                # If `path` is an experiment, we can ignore all subdirectories
                # (experiments can't be nested).
                yield cls(path)
                continue
            # Ignore hidden directories or directories in the explicit ignore list.
            dirnames[:] = [
                d
                for d in dirnames
                if d not in cls.DIRS_TO_IGNORE or not d.startswith(".")
            ]
