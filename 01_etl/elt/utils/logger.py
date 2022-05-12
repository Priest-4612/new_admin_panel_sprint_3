import logging
from pathlib import Path

BASE_PATH = Path(__file__).resolve()
PATH_TO_LOG = BASE_PATH.parents[4].joinpath('logs', 'backoff')

_log_format = (
    '%(asctime)s - [%(levelname)s] -  %(name)s - ',
    '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
)

logging.basicConfig(
    level=logging.DEBUG,
    format=_log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            filename=PATH_TO_LOG, mode='a', encoding='utf8',
        ),
    ],
)


def get_logger(name):
    return logging.getLogger(name)
