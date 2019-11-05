from pathlib import Path

from mallennlp.app import create_app, create_dash
from mallennlp.config import Config


config = Config.from_toml(Path("/opt/python/app/project"))
application = create_app(config)
dashboard = create_dash(application, config)
