from boardtt.manager import ImageProcessingManager
from boardtt.card_type import CardType
from boardtt.card_area import CardArea
from boardtt.config import Config


class StarWarsLure(CardType):
    """`Lure of The Dark Side` expansion cards deck."""

    marker_area = "type_name"
    card_id_area = "card_id"
    norm_numeric = ("card_id",)


class StarWarsLureEnhance(StarWarsLure):
    alias = "enhance"
    marker_value = "ENHANCE"

    type_name = CardArea(0.8, 7.7, 60.1, 61.5, bg_box_size=3)
    card_id = CardArea(55.4, 60.5, 78, 80.7, render=False)
    title = CardArea(15.4, 54, 3.4, 8.1)
    text = CardArea(13, 61, 63, 78.7)


class StarWarsLureEvent(StarWarsLure):
    alias = "event"
    marker_value = "EVENT"

    type_name = CardArea(2, 7.3, 61.4, 62.7, bg_box_size=2)
    card_id = CardArea(53.8, 59, 79.8, 81.4, render=False)
    title = CardArea(12.7, 54, 56.7, 60.8)
    text = CardArea(3.2, 58, 65.3, 79.5)


class StarWarsLureUnit(StarWarsLure):
    alias = "unit"
    marker_value = "UNIT"

    type_name = CardArea(2.7, 6.2, 47.3, 48.6, bg_box_size=2)
    card_id = CardArea(56.2, 60.7, 76.1, 81.4, render=False)
    title = CardArea(16, 54, 4.2, 8)
    text = CardArea(5, 57, 54.6, 77)


class StarWarsLureFate(StarWarsLure):
    alias = "fate"
    marker_value = "FATE"

    type_name = CardArea(55, 59, 4.4, 5.7)
    card_id = CardArea(56, 60.1, 80.1, 81.7, render=False)
    title = CardArea(13, 48, 5, 9.5)
    text = CardArea(12, 53, 15, 28)


class StarWarsLureObjective(StarWarsLure):
    alias = "objective"
    marker_value = "OBJECTIVE"

    type_name = CardArea(39.3, 40.6, 78, 85.7, rotate=-90)
    card_id = CardArea(53, 54.3, 1, 5.2, render=False, rotate=-90)
    title = CardArea(32.6, 36.4, 23, 71.3, rotate=-90)
    text = CardArea(39.5, 53.2, 6, 76.1, rotate=-90)


###################################################################

IMAGE_PATH = "sw1.png"  # Put your path here.

###################################################################
# Debug example (that's wrong now):
#
# handle = StarWarsLureEnhance
# target_area = 'text'
# debug_image(IMAGE_PATH, handle, debug=True)
# debug_image(IMAGE_PATH, handle, target_area=target_area)
# debug_image(IMAGE_PATH, handle, show_composite=True)
###################################################################

config = Config(
    cards_rows=3,
    cards_cols=3,
    image_dpi=600,
    card_height_mm=88.35,
    card_width_mm=62.1,
)

ImageProcessingManager(
    config,
    IMAGE_PATH,
    (
        StarWarsLureEnhance,
        StarWarsLureEvent,
        StarWarsLureUnit,
        StarWarsLureFate,
        StarWarsLureObjective,
    ),
).process()
