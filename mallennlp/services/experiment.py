import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterable, Set, Tuple

from allennlp.common.params import Params

from mallennlp.domain.experiment import Experiment, Epoch, Meta, FileData
from mallennlp.services.db import Tables, get_db_from_app


def with_db_update(method):
    def wrapped(self, *args, **kwargs):
        out = method(self, *args, **kwargs)
        self.update_db_entry()
        return out

    return wrapped


class ExperimentService:
    CONFIG_FNAME: str = "config.json"

    META_FNAME: str = "meta.json"

    METRICS_FNAME: str = "metrics.json"

    STDOUT_FNAME: str = "stdout.log"

    STDERR_FNAME: str = "stderr.log"

    EPOCH_METRICS_FNAME = "metrics_epoch_%d.json"

    DIRS_TO_IGNORE: Set[str] = {"vocabulary", "log"}

    DB_FIELD_NAMES: Tuple[str, str] = ("path", "tags")

    def __init__(self, path: Path, db=None) -> None:
        self._db = db
        self.e = Experiment(
            path=path,
            config=FileData(path / self.CONFIG_FNAME),
            meta=FileData(path / self.META_FNAME),
            metrics=FileData(path / self.METRICS_FNAME),
            stdout=FileData(path / self.STDOUT_FNAME),
            stderr=FileData(path / self.STDERR_FNAME),
            epochs=[],
        )

    @property
    def db(self):
        return self._db or get_db_from_app()

    def get_db_fields(self) -> Tuple[str, str]:
        return str(self.get_path()), " ".join(self.get_tags())

    def get_path(self) -> Path:
        return self.e.path

    def get_config(self) -> Params:
        fd = self.e.config
        if fd.should_read():
            fd.data = Params.from_file(fd.path)
        if fd.data is None:
            raise FileNotFoundError
        return fd.data

    def get_meta(self) -> Meta:
        fd = self.e.meta
        if fd.should_read():
            with open(fd.path) as f:
                fd.data = Meta(**json.load(f))
        if not fd.data:
            fd.data = Meta([])
        return fd.data

    def get_tags(self) -> List[str]:
        meta = self.get_meta()
        return meta.tags

    @with_db_update
    def set_tags(self, tags: List[str]) -> None:
        meta = self.get_meta()
        meta.tags = tags
        with open(self.e.meta.path, "w") as f:
            f.write(meta.serialize())  # type: ignore

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
        cls, root: Path = None, ignore_root: bool = True
    ) -> Iterable["ExperimentService"]:
        root = root or Path("./")
        root = root.resolve()
        for dirpath, dirnames, _ in os.walk(root):
            path = Path(dirpath)
            if cls.is_experiment(path) and (path != root or not ignore_root):
                # If `path` is an experiment, we can ignore all subdirectories
                # (experiments can't be nested).
                yield cls(path.relative_to(root))
                continue
            # Ignore hidden directories or directories in the explicit ignore list.
            dirnames[:] = [
                d
                for d in dirnames
                if d not in cls.DIRS_TO_IGNORE or not d.startswith(".")
            ]

    def update_db_entry(self, db=None):
        field_names = self.DB_FIELD_NAMES
        fields = self.get_db_fields()
        c = self.db.cursor()
        insert_stmnt = (
            f"INSERT OR REPLACE INTO {Tables.EXPERIMENTS.value} "
            f"({', '.join(field_names)}) VALUES "
            f"({','.join('?' for _ in field_names)})"
        )
        c.execute(insert_stmnt, fields)
        self.db.commit()

    @classmethod
    def init_db_table(cls, db=None, entries: List[Tuple[str, str]] = None):
        db = db or get_db_from_app()
        entries = entries or [
            experiment.get_db_fields() for experiment in cls.find_experiments()
        ]
        c = db.cursor()
        c.execute(f"DELETE FROM {Tables.EXPERIMENTS.value}")
        field_names = cls.DB_FIELD_NAMES
        insert_stmnt = (
            f"INSERT OR REPLACE INTO {Tables.EXPERIMENTS.value} "
            f"({', '.join(field_names)}) VALUES "
            f"({','.join('?' for _ in field_names)})"
        )
        c.executemany(insert_stmnt, entries)
        db.commit()
