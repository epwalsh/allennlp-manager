import click
from gevent import monkey
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
        for key, value in self.options.items():
            if key not in self.cfg.settings:
                raise KeyError(key)
            else:
                self.cfg.set(key, value)

    def load(self):
        return self.application


@click.command()
@click.option("--launch", is_flag=True, help="Launch dashboard in browser.")
@requires_config
def serve(config, launch):
    """
    Serve the dashboard locally.
    """
    monkey.patch_all()
    click.secho(
        f"Serving AllenNLP manager for {click.style(config.project.name, bold=True)}",
        fg="green",
    )
    if launch:
        url = f"http://localhost:{config.server.port}"
        click.launch(url)

    options = {
        "timeout": 300,
        "worker_class": "gevent",
        "worker_connections": config.server.concurrency,
        "bind": f":{config.server.port}",
        "loglevel": config.project.loglevel.lower(),
    }
    from mallennlp.app import create_app

    application = create_app(config)
    StandaloneApplication(application, options).run()
