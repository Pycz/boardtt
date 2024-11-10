import logging
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)

IMAGE_DPI = 600
CARD_HEIGHT_MM = 88
CARD_WIDTH_MM = 62
CARDS_ROWS = 3
CARDS_COLS = 3


def configure(
    image_dpi=600,
    card_height_mm=88,
    card_width_mm=62,
    cards_rows=3,
    cards_cols=3,
    log_level=logging.INFO,
):
    """Конфигурирует приложение.

    :param image_dpi: Ращерешение скана. Точки на дюйм.
    :param card_height_mm: Высота карты, мм
    :param card_width_mm: Ширина карты, мм
    :param cards_rows: Кол-во рядов карт на скане
    :param cards_cols: Кол-во столбцов карт на скане
    :param log_level:
    :return:
    """
    global IMAGE_DPI, CARD_HEIGHT_MM, CARD_WIDTH_MM, CARDS_ROWS, CARDS_COLS
    # TODO Можно автоматизировать, скорее всего - автоматом вычислять ширину и высоту карты.

    IMAGE_DPI = image_dpi
    CARD_HEIGHT_MM = card_height_mm
    CARD_WIDTH_MM = card_width_mm
    CARDS_ROWS = cards_rows
    CARDS_COLS = cards_cols

    configure_logging(log_level)


def configure_logging(log_level=logging.INFO, show_logger_names=False):
    """Performs basic logging configuration.

    :param log_level: logging level, e.g. logging.DEBUG
    :param show_logger_names: bool - flag to show logger names in output
    :return:
    """
    format_str = "%(levelname)s: %(message)s"
    if show_logger_names:
        format_str = "%(name)s\t\t " + format_str
    logging.basicConfig(format=format_str, level=log_level)


@dataclass
class Config:
    image_dpi: int = 600
    card_height_mm: int | float = 88
    card_width_mm: int | float = 62
    cards_rows: int = 3
    cards_cols: int = 3
    log_level: int = logging.INFO
