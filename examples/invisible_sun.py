import logging
import os.path

from boardtt.utils import configure, CardType, CardArea, process_image, debug_image


class Base(CardType):
    pass
    # marker_area = 'type_name'
    # card_id_area = 'card_id'
    # norm_numeric = ('card_id',)


class Regular(Base):
    alias = 'enhance'
    title = CardArea(10, 60, 10, 25, bg_box_size=3)
    text = CardArea(10, 60, 30, 80, bg_box_size=3)



###################################################################

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "sources", __file__[:-3])
IMAGES = os.path.listdir(SOURCE_DIR)
FIRST_IMAGE = os.path.join(SOURCE_DIR, IMAGES[0])

IMAGE_PATH = FIRST_IMAGE  # Put your path here.

configure(image_dpi=300, card_height_mm=90, card_width_mm=75, cards_rows=2, cards_cols=4, log_level=logging.DEBUG)

###################################################################
# Debug example:
#
# handle = StarWarsLureEnhance
# target_area = 'text'
# debug_image(IMAGE_PATH, handle, debug=True)
# debug_image(IMAGE_PATH, handle, target_area=target_area)
# debug_image(IMAGE_PATH, handle, show_composite=True)
###################################################################

process_image(IMAGE_PATH, (
    Regular,
))
