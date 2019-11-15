from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile

from allennlp.common.params import Params
import pytest

from mallennlp.domain.config import ProjectConfig, ServerConfig
from mallennlp.domain.experiment import Meta
from mallennlp.services.config import Config
from mallennlp.services.db import Tables, init_tables
from mallennlp.services.experiment import ExperimentService


@pytest.fixture(scope="module")
def project_path():
    with tempfile.TemporaryDirectory() as _tmpdirname:
        yield Path(_tmpdirname)


@pytest.fixture(scope="module")
def project(project_path):
    # Save this so we can change back when fixture is taken down.
    originalwd = os.getcwd()

    # Copy fixtures.
    shutil.copytree(
        "mallennlp/tests/fixtures/test_experiment", project_path / "test_experiment"
    )

    # Write config.
    config = Config(
        ProjectConfig(project_path, name="my-test-project"), ServerConfig(project_path)
    )
    config.to_toml(project_path)

    # Move wd to project.
    os.chdir(project_path)

    yield project_path

    # Change back to original wd.
    os.chdir(originalwd)


def test_experiment_files_present(project):
    assert "test_experiment" in os.listdir(project)
    assert "config.json" in os.listdir(project / "test_experiment")


@pytest.fixture(scope="module")
def experiment_service(project, db):
    return ExperimentService(project / "test_experiment", db)


def initial_check(file_data):
    # file should not have been read yet.
    assert file_data.data is None
    assert file_data.should_read()


def touch_and_check_again(file_data):
    # now the file data is cached, so `should_read` should return False.
    assert not file_data.should_read()

    # until the file is changed...
    file_data.path.touch()
    assert file_data.should_read()


def test_get_config(experiment_service):
    initial_check(experiment_service.e.config)
    config = experiment_service.get_config()
    assert isinstance(config, Params)
    assert config["dataset_reader"]["type"] == "copynet_seq2seq"
    touch_and_check_again(experiment_service.e.config)


def test_get_meta(experiment_service):
    meta = experiment_service.get_meta()
    assert isinstance(meta, Meta)
    assert meta.tags == []


def test_get_tags(experiment_service):
    assert experiment_service.get_tags() == []


def test_set_tags(experiment_service, db):
    experiment_service.set_tags(["copynet", "seq2seq"])
    assert experiment_service.get_tags() == ["copynet", "seq2seq"]

    # Should be written to file now.
    assert experiment_service.e.meta.path.exists()
    es2 = ExperimentService(experiment_service.get_path())
    assert es2.get_tags() == ["copynet", "seq2seq"]

    # Should be updated in database as well.
    results = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE path = ?",
            (str(experiment_service.get_path()),),
        )
    )
    assert len(results) == 1
    assert results[0]["tags"] == "copynet seq2seq"


def test_get_metrics(experiment_service):
    initial_check(experiment_service.e.metrics)
    metrics = experiment_service.get_metrics()
    assert isinstance(metrics, dict)
    assert metrics["best_epoch"] == 9
    touch_and_check_again(experiment_service.e.metrics)


def test_get_stdout(experiment_service):
    initial_check(experiment_service.e.stdout)
    stdout = experiment_service.get_stdout()
    assert isinstance(stdout, str)
    assert stdout.startswith("2019-11-08 11:37:07,848 - INFO")
    touch_and_check_again(experiment_service.e.stdout)


def test_get_stderr(experiment_service):
    initial_check(experiment_service.e.stderr)
    stderr = experiment_service.get_stderr()
    assert isinstance(stderr, str)
    assert stderr.startswith("/home/epwalsh/.virtualenvs/allennlp/src/allennlp/")
    touch_and_check_again(experiment_service.e.stderr)


def test_get_epochs(experiment_service):
    epochs = experiment_service.get_epochs()
    assert len(epochs) == 10
    assert epochs[0].metrics.data["training_duration"] == "0:00:13.069122"
    assert epochs[9].metrics.data["training_duration"] == "0:02:04.405518"
    assert not epochs[0].metrics.should_read()

    # Now change one of the epoch metric files.
    new_data = deepcopy(epochs[0].metrics.data)
    new_data["training_duration"] = "0:00:12.06"
    with open(epochs[0].metrics.path, "w") as f:
        json.dump(new_data, f)
    epochs = experiment_service.get_epochs()
    assert len(epochs) == 10
    assert epochs[0].metrics.data["training_duration"] == "0:00:12.06"


def test_find_experiments(project):
    exps = list(ExperimentService.find_experiments(project))
    assert len(exps) == 1
    assert exps[0].e.path == Path("test_experiment")


@pytest.fixture(scope="module")
def entries():
    return [
        ("greetings/copynet/run_001", "copynet seq2seq"),
        ("greetings/copynet/run_002", "copynet seq2seq beam-search copy"),
        ("greetings/seq2seq/run_001", "simple-seq2seq beam-search char-level"),
    ]


def test_add_experiments(db, entries):
    init_tables(db, (Tables.EXPERIMENTS.value,))
    ExperimentService.init_db_table(db=db, entries=entries)


def test_custom_func_hasanytags(db):
    rows = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE HasAnyTags(tags, 'copynet', 'copy')"
        )
    )
    assert len(rows) == 2

    rows = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE HasAnyTags(tags, 'copynet', 'beam-search')"
        )
    )
    assert len(rows) == 3

    rows = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE HasAnyTags(tags, 'simple')"
        )
    )
    assert len(rows) == 0


def test_custom_func_hasalltags(db):
    rows = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE HasAllTags(tags, 'copynet', 'copy')"
        )
    )
    assert len(rows) == 1

    rows = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE HasAllTags(tags, 'copynet')"
        )
    )
    assert len(rows) == 2


def test_glob_by_path(db):
    rows = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE path GLOB ?",
            ("greetings/copynet/*",),
        )
    )
    assert len(rows) == 2

    rows = list(
        db.execute(
            f"SELECT * FROM {Tables.EXPERIMENTS.value} WHERE path GLOB ?",
            ("greetings/*/run_001",),
        )
    )
    assert len(rows) == 2
