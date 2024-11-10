import os
from typing import Type, Iterable

from boardtt.card_type import CardType
from boardtt.config import Config
from boardtt.logger import LOGGER
from boardtt.marker import PlanarCardMarker, CardMarker


class ImageProcessingManager:
    def __init__(
        self,
        config: Config,
        image_path: str | os.PathLike,
        card_types: Iterable[Type[CardType]],
    ):
        self.config = config
        self.image_path = image_path
        self.card_types = card_types
        self.card_marker: CardMarker = PlanarCardMarker(image_path)

    def debug_process_card_type(
        self,
        card_type: Type[CardType],
        debug: bool = False,
        target_area: str = "text",
        show_composite: bool = False,
    ) -> None:
        """TODO: Remove this for something better
        Вспомогательная функция, используется при объявлении типов карт (создании классов),
        для нахождения координат регионов.

        :param card_type: Класс типа карты
        :param debug: Флаг указывающий не необходимость вывода дополнительной отладочной информации.
        :param target_area: Имя отладиваемого региона
        :param show_composite: Флаг, указывающий на то следует ли показывать локализованную версию карты.
        """
        card_type.DEBUG = debug

        cards = self.card_marker.get_cards()
        if debug:
            for card in cards:
                card["img"].show()

        matches = card_type(cards)

        LOGGER.warning("** Card indexes: %s" % matches.cards.keys())

        for idx, card in matches.cards.items():
            if not show_composite:
                LOGGER.warning(
                    "** Text in `%s` area: %s"
                    % (target_area, card["areas"][target_area]["str"])
                )
                card["areas"][target_area]["img"].show()
            else:
                card_id = card_type.get_card_id(idx, card)
                img_tr = card_type.get_tr_image(card, idx)
                img_comp = card_type.get_composite_image(card["img"], img_tr, card_id)
                img_comp.show()

    def process(self):
        """Производит обработку указанного скана, используя
        указанные типы карт"""
        LOGGER.info("Image processing started")

        target_dir = os.path.splitext(self.image_path)[0]
        LOGGER.debug("Target path: %s" % target_dir)
        cards = self.card_marker.get_cards()

        for card_type in self.card_types:
            LOGGER.info("Processing using %s ..." % card_type.__name__)
            card = card_type(cards, target_dir)
            card.save_files()

        LOGGER.info("Image processing finished")
