import typing

import attr
import click
import pytest

from mallennlp.bin.new import new, init
from mallennlp.domain.config import ServerConfig, ProjectConfig


def check_types(attribute, option):
    # Crude ad hoc way of comparing CLI types against Config types.
    if attribute.type == str or attribute.type == typing.Union[str, type(None)]:
        assert option.type == click.STRING or isinstance(option.type, click.Choice)
    elif attribute.type == int:
        assert option.type == click.INT
    elif attribute.type == bool:
        assert option.type == click.BOOL
    elif attribute.type == float:
        assert option.type == click.FLOAT
    elif attribute.type == typing.Union[typing.List[str], type(None)]:
        assert option.type == click.STRING
        assert option.multiple


@pytest.mark.parametrize("command, ignore", [(new, []), (init, ["name"])])
def test_project_options_match_config_parameters(command, ignore):
    project_options = {
        opt.name: opt for opt in command.params if not opt.name.startswith("server_")
    }
    for name, attribute in attr.fields_dict(ProjectConfig).items():
        if name.startswith("_") or name in ignore:
            continue
        assert name in project_options
        check_types(attribute, project_options[name])


@pytest.mark.parametrize("command, ignore", [(new, []), (init, [])])
def test_server_options_match_config_parameters(command, ignore):
    server_options = {
        opt.name[7:]: opt for opt in command.params if opt.name.startswith("server_")
    }
    for name, attribute in attr.fields_dict(ServerConfig).items():
        if name.startswith("_") or name in ignore:
            continue
        assert name in server_options
        check_types(attribute, server_options[name])
