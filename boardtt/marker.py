import os
from typing import TypedDict, Protocol

from PIL import Image

from boardtt.config import Config
from boardtt.logger import LOGGER


class CardData(TypedDict):
    img: Image
    coords: tuple[float, float, float, float]


CardsData = list[CardData]


class CardMarker(Protocol):
    def get_cards(self) -> CardsData: ...


class PlanarCardMarker(CardMarker):
    def __init__(self, config: Config, filepath: str | os.PathLike):
        self.filepath = filepath
        self.config = config

    def _open_image_file(self) -> Image:
        """Возвращает открытый Pillow файл с изображением."""
        return Image.open(self.filepath)

    def _get_card_coords(self, row_num: int, col_num: int) -> tuple[int, int, int, int]:
        """Возвращает координаты карты по её расположению в ряду, колонке."""

        x = self.config.offset_from_left_border_px + (
            row_num * (self.config.card_width_px + self.config.offset_x_px)
        )
        x1 = x + self.config.card_width_px

        y = self.config.offset_from_top_border_px + (
            col_num * (self.config.card_height_px + self.config.offset_y_px)
        )
        y1 = y + self.config.card_height_px

        return x, y, x1, y1

    def get_cards(self) -> CardsData:
        """Возвращает список с данными карт с указанного изображения (скана)."""
        LOGGER.info("Loading cards from %s" % self.filepath)
        img = self._open_image_file()

        cards = []

        for col_num in range(self.config.cards_cols):
            for row_num in range(self.config.cards_rows):
                LOGGER.debug("Getting card %s x %s ..." % (col_num + 1, row_num + 1))
                coords = self._get_card_coords(row_num, col_num)
                card = img.crop(coords)
                cards.append({"img": card, "coords": coords})

        LOGGER.info("Source image split into %s cards" % len(cards))

        return cards
