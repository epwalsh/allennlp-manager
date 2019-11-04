import logging
import os

from flask import Flask, Response


logger = logging.getLogger("gunicorn.error")


application = Flask(__name__)
application.secret_key = os.environ["SECRET_KEY"]
application.logger.handlers = logger.handlers
application.logger.setLevel(logger.level)


@application.route("/")
def main():
    return Response("Hello from AllenNLP manager!")


if __name__ == "__main__":
    application.run(debug=True)
