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
@click.option("--skip-db-update", is_flag=True, help="Skip updating the database.")
@requires_config
def serve(config, launch, skip_db_update):
    """
    Serve the dashboard locally.
    """
    monkey.patch_all()

    from mallennlp.app import create_app
    from mallennlp.services.db import get_db_from_cli, init_tables, Tables
    from mallennlp.services.experiment import ExperimentService

    if not skip_db_update:
        db = get_db_from_cli(config)
        click.echo("Updating experiments index...")
        init_tables(db, (Tables.EXPERIMENTS.value,))
        entries = [s.get_db_fields() for s in ExperimentService.find_experiments()]
        if entries:
            click.echo(
                f"Found {click.style(str(len(entries)), fg='green')} experiments"
            )
            ExperimentService.init_db_table(db=db, entries=entries)
        else:
            click.secho("No experiments found", fg="yellow")
        db.close()

    click.secho(
        f"Serving AllenNLP manager for {click.style(config.project.name, bold=True)}",
        fg="green",
    )

    application = create_app(config)

    if launch:
        url = f"http://localhost:{config.server.port}"
        click.launch(url)

    options = {
        "timeout": 300,
        "workers": config.server.workers,
        "worker_class": "gevent",
        "worker_connections": config.server.worker_connections,
        "bind": f":{config.server.port}",
        "loglevel": config.project.loglevel.lower(),
        "preload_app": True,
    }

    StandaloneApplication(application, options).run()
