import os

from boardtt.config import LOGGER
from boardtt.marker import get_cards_from_file


def debug_image(
    image_path, card_type, debug=False, target_area="text", show_composite=False
):
    """Вспомогательная функция, используется при объявлении типов карт (создании классов),
    для нахождения координат регионов.

    :param image_path: Путь к скану
    :param card_type: Класс типа карты
    :param debug: Флаг указывающий не необходимость вывода дополнительной отладочной информации.
    :param target_area: Имя отладиваемого региона
    :param show_composite: Флаг, указывающий на то следует ли показывать локализованную версию карты.
    :return:
    """
    card_type.DEBUG = debug
    cards = get_cards_from_file(image_path)
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


def process_image(image_path, card_types):
    """Производит обработку указанного скана, используя
    указанные типы карт.

    :param image_path:
    :param card_types:
    :return:
    """
    LOGGER.info("Image processing started")

    target_dir = os.path.splitext(image_path)[0]
    LOGGER.debug("Target path: %s" % target_dir)
    cards = get_cards_from_file(image_path)

    for card_type in card_types:
        LOGGER.info("Processing using %s ..." % card_type.__name__)
        data = card_type(cards, target_dir)
        data.save_files()

    LOGGER.info("Image processing finished")
