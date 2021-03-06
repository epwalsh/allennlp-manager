from pathlib import Path
import tempfile

import pytest

from mallennlp.domain.config import ProjectConfig, ServerConfig
from mallennlp.services.config import Config
from mallennlp.exceptions import NotInProjectError


@pytest.fixture(scope="function")
def tmpdir():
    with tempfile.TemporaryDirectory() as _tmpdirname:
        yield Path(_tmpdirname)


@pytest.fixture(scope="function")
def project_path(tmpdir):
    with open(tmpdir / Config.CONFIG_PATH, "w") as config_file:
        config_file.write(
            "[project]\n" 'name = "my-project"\n' "\n" "[server]\n" "port = 5000\n"
        )
    yield tmpdir


def test_from_toml_raises(tmpdir):
    with pytest.raises(NotInProjectError):
        Config.from_toml(tmpdir)


def test_from_toml(project_path):
    config = Config.from_toml(project_path)
    assert config.project.name == "my-project"
    assert config.server.port == 5000


def test_to_toml(tmpdir):
    config = Config(
        ProjectConfig(tmpdir, name="my-test-project"), ServerConfig(tmpdir, port=8888)
    )
    config.to_toml(tmpdir)
    config = Config.from_toml(tmpdir)
    assert config.project.name == "my-test-project"
    assert config.server.port == 8888
