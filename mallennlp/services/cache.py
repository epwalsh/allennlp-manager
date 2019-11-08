from flask_caching import Cache

from mallennlp.services.config import Config


cache = Cache()


def init_app(app, config: Config):
    cache.init_app(
        app,
        config={
            "CACHE_TYPE": "filesystem",
            "CACHE_DEFAULT_TIMEOUT": 60 * 60,
            "CACHE_DIR": str(config.server.cache_path),
            "CACHE_THRESHOLD": 1000,
        },
    )
