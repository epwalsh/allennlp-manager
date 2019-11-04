import logging
from pathlib import Path

from flask import Flask, Response

from mallennlp.config import Config


def create_app():
    logger = logging.getLogger("gunicorn.error")

    config = Config.from_toml(Path("/opt/python/app/project"))

    application = Flask(__name__)
    application.secret_key = config.server.secret
    application.logger.handlers = logger.handlers
    application.logger.setLevel(logger.level)

    @application.route("/")
    def main():
        return Response("Hello from AllenNLP manager!")

    return application


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
