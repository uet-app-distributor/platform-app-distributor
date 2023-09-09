import logging

from settings import LOG_LEVEL, LOG_FORMAT

log_level_mapping = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
}

logging.basicConfig(
    level=log_level_mapping[LOG_LEVEL],
    format=LOG_FORMAT,
)

logger = logging.getLogger(__name__)
