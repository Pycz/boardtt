import os
from typing import TypedDict, Protocol

from PIL import Image

from boardtt.config import CARD_HEIGHT_MM, CARD_WIDTH_MM, CARDS_COLS, CARDS_ROWS, LOGGER
from boardtt.utils import mm_to_pixels


class CardData(TypedDict):
    img: Image
    coords: tuple[float, float, float, float]


CardsData = list[CardData]


class CardMarker(Protocol):
    def get_cards(self, img: Image) -> CardsData:
        ...


class PlanarCardMarker(CardMarker):
    def __init__(self, filepath: str | os.PathLike):
        self.filepath = filepath

    def get_cards(self, img: Image) -> CardsData:
        ...


def open_image_file(fpath):
    """Возвращает открытый Pillow файл с изображением.

    :param fpath:
    :return:
    """
    return Image.open(fpath)


def get_card_coords(row_num, col_num):
    """Возвращает координаты карты по её расположению в ряду, колонке.

    :param row_num: Номер ряда
    :param col_num: Номер колонки
    :return:
    """

    CARD_HEIGHT_PX = mm_to_pixels(CARD_HEIGHT_MM)
    CARD_WIDTH_PX = mm_to_pixels(CARD_WIDTH_MM)

    OFFSET_X_PX = 2
    OFFSET_Y_PX = 2

    x = row_num * CARD_WIDTH_PX + OFFSET_X_PX
    x1 = x + CARD_WIDTH_PX

    y = col_num * CARD_HEIGHT_PX + OFFSET_Y_PX
    y1 = y + CARD_HEIGHT_PX

    return x, y, x1, y1


def get_cards(img):
    """Возвращает список с данными карт с указанного изображения (скана).

    :param img: объект изображения от Pillow
    :return:
    """
    cards = []

    for col_num in range(CARDS_COLS):
        for row_num in range(CARDS_ROWS):
            LOGGER.debug("Getting card %sx%s ..." % (col_num + 1, row_num + 1))
            coords = get_card_coords(row_num, col_num)
            card = img.crop(coords)
            cards.append({"img": card, "coords": coords})

    LOGGER.info("Source image split into %s cards" % len(cards))

    return cards


def get_cards_from_file(fpath):
    """Возвращает данные о картах, изъятых из указанно файла-скана.

    :param fpath:
    :return:
    """
    LOGGER.info("Loading cards from %s" % fpath)
    img = open_image_file(fpath)
    return get_cards(img)
