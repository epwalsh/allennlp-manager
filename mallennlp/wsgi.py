from mallennlp.app import create_app, create_dash
from mallennlp.services.config import Config


config = Config.from_toml()
application = create_app(config)
dashboard = create_dash(application, config)
