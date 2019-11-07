import click
from gunicorn.app.base import BaseApplication

from mallennlp.bin.common import requires_config


class StandaloneApplication(BaseApplication):
    """
    See http://docs.gunicorn.org/en/latest/custom.html.
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict(
            [
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


@click.command()
@click.option("--launch", is_flag=True, help="Launch dashboard in browser.")
@requires_config
def serve(config, launch):
    """
    Serve the dashboard locally.
    """
    click.secho(
        f"Serving AllenNLP manager for {click.style(config.project.name, bold=True)}",
        fg="green",
    )
    if launch:
        url = f"http://localhost:{config.server.port}"
        click.launch(url)

    options = {
        "timeout": 300,
        "worker-class": "gevent",
        "worker-connections": config.server.concurrency,
        "bind": f":{config.server.port}",
    }
    from mallennlp.app import create_app

    application = create_app(config)
    StandaloneApplication(application, options).run()
