import typing

import attr
import click

from mallennlp.bin.new import new
from mallennlp.config import ServerConfig, ProjectConfig


def check_types(attribute, option):
    if attribute.type == str or attribute.type == typing.Union[str, type(None)]:
        assert option.type == click.STRING or isinstance(option.type, click.Choice)
    elif attribute.type == int:
        assert option.type == click.INT
    elif attribute.type == bool:
        assert option.type == click.BOOL
    elif attribute.type == float:
        assert option.type == click.FLOAT


def test_project_options_match_config_parameters():
    project_options = {
        opt.name: opt for opt in new.params if not opt.name.startswith("server_")
    }
    for name, attribute in attr.fields_dict(ProjectConfig).items():
        if name.startswith("_"):
            continue
        assert name in project_options
        check_types(attribute, project_options[name])


def test_server_options_match_config_parameters():
    server_options = {
        opt.name[7:]: opt for opt in new.params if opt.name.startswith("server_")
    }
    for name, attribute in attr.fields_dict(ServerConfig).items():
        if name.startswith("_"):
            continue
        assert name in server_options
        check_types(attribute, server_options[name])
