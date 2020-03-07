import logging
import os


LOG_FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
FORMATTER = formatter = logging.Formatter(LOG_FORMAT)


def _is_debug():
    return os.environ.get('DEBUG', '').strip() not in ['', '0', 'false']


class LoggingConfig:
    format = LOG_FORMAT
    formatter = FORMATTER
    date_format = DATE_FORMAT
    level = logging.DEBUG #if _is_debug() else logging.INFO


def setup_logging():
    logging.basicConfig(
        level=LoggingConfig.level,
        format=LoggingConfig.format,
        datefmt=LoggingConfig.date_format)


setup_logging()
