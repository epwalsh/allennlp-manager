from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile

from allennlp.common.params import Params
import pytest

from mallennlp.domain.config import ProjectConfig, ServerConfig
from mallennlp.services.config import Config
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
def experiment_service(project):
    return ExperimentService(project / "test_experiment")


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


@pytest.mark.skip()
def test_get_meta(experiment_service):
    # TODO
    pass


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
    assert exps[0].e.path == (project / "test_experiment")
