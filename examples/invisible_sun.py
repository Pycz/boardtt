import logging
from pathlib import Path

from boardtt.utils import configure, CardType, CardArea, process_image


class Base(CardType):
    pass


class Regular(Base):
    alias = 'enhance'
    title = CardArea(10, 60, 10, 25, bg_box_size=3)
    text = CardArea(10, 60, 30, 80, bg_box_size=3)


###################################################################

SOURCE_DIR = Path(__file__).parent.parent / "sources" / Path(__file__).stem
IMAGE_NAMES_IN_DIR = [f for f in SOURCE_DIR.iterdir() if f.is_file() and f.suffix in ['.jpg', '.png']]
FIRST_IMAGE = SOURCE_DIR / IMAGE_NAMES_IN_DIR[0]

configure(image_dpi=300, card_height_mm=90, card_width_mm=75, cards_rows=2, cards_cols=4, log_level=logging.DEBUG)

for image_name in IMAGE_NAMES_IN_DIR:
    process_image(SOURCE_DIR / image_name, (
        Regular,
    ))
