from click.testing import CliRunner
import pytest


@pytest.fixture(scope="module", autouse=True)
def runner():
    yield CliRunner()


@pytest.fixture(scope="module", autouse=True)
def isolated_filesystem(runner):
    with runner.isolated_filesystem() as filesystem:
        yield filesystem


def test_cli_workflow(runner):
    assert True
