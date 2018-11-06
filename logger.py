import logging.config
import sys

FORMAT = "[%(asctime)s] [PID %(process)d] [%(threadName)s] [%(request_id)s] [%(name)s] [%(levelname)s] %(message)s"  # noqa

def setup_logging(level):
    logging.config.dictConfig({
        "disable_existing_loggers": False,
        "version": 1,
        "filters": {
            "request_id": {
                "()": "molten.contrib.request_id.RequestIdFilter",
            }
        },
        "formatters": {
            "console": {
                "format": FORMAT,
            },
        },
        "handlers": {
            "default": {
                "level": level,
                "class": "logging.StreamHandler",
                "stream": sys.stderr,
                "formatter": "console",
                "filters": ["request_id"],
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": level,
                "propagate": False,
            },
        }
    })
