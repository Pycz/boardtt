import logging


LOGGER = logging.getLogger(__name__)


def configure_logging(log_level=logging.INFO, show_logger_names=False):
    """Performs basic logging configuration.
    """
    format_str = "%(levelname)s: %(message)s"
    if show_logger_names:
        format_str = "%(name)s\t\t " + format_str
    logging.basicConfig(format=format_str, level=log_level)


configure_logging(logging.DEBUG, show_logger_names=True)
