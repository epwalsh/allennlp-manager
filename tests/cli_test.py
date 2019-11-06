import os

from click.testing import CliRunner
import pytest

from mallennlp.bin.main import main
from mallennlp.services.db import get_db_from_cli
from mallennlp.services.config import Config
from mallennlp.services.user import UserService


PROJECT_NAME = "test-project"
USERNAME = "testuser"
PASSWORD = "testing123"
NEW_PASSWORD = "testing124"


@pytest.fixture(scope="module", autouse=True)
def runner():
    return CliRunner()


@pytest.fixture(scope="module", autouse=True)
def isolated_filesystem(runner):
    with runner.isolated_filesystem() as filesystem:
        yield filesystem


def test_create_project(runner):
    result = runner.invoke(
        main,
        [
            "new",
            PROJECT_NAME,
            f"--username={USERNAME}",
            f"--password={PASSWORD}",
            "--loglevel=DEBUG",
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(PROJECT_NAME)
    assert os.path.isdir(PROJECT_NAME)


@pytest.fixture(scope="function", autouse=True)
def project():
    """
    Ensure we are always in the project subdirectory from now on.
    """
    if os.path.exists(PROJECT_NAME):
        os.chdir(PROJECT_NAME)


@pytest.fixture(scope="function")
def config():
    return Config.from_toml()


def test_initial_config(config):
    assert config.project.name == PROJECT_NAME
    assert config.project.loglevel == "DEBUG"


@pytest.fixture(scope="function")
def db(config):
    db = get_db_from_cli(config)
    yield db
    db.close()


@pytest.fixture(scope="function")
def user_service(db):
    return UserService(db)


def test_user_created(user_service):
    user = user_service.find(USERNAME, PASSWORD)
    assert user is not None
    assert user.alt_id == 0


def test_change_password(runner):
    result = runner.invoke(
        main, ["user", "changepw", f"{USERNAME}", f"--password={NEW_PASSWORD}"]
    )
    assert result.exit_code == 0, result.output


def test_user_password_changed(user_service):
    assert user_service.find(USERNAME, PASSWORD) is None
    user = user_service.find(USERNAME, NEW_PASSWORD)
    assert user is not None
    # Alternate id should have been incremented.
    assert user.alt_id == 1
