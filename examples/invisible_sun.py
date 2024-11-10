from pathlib import Path

from boardtt.manager import ImageProcessingManager
from boardtt.card_type import CardType
from boardtt.card_area import CardArea
from boardtt.config import Config


class Base(CardType):
    pass


class Regular(Base):
    alias = "enhance"
    title = CardArea(10, 60, 10, 25, bg_box_size=3)
    text = CardArea(10, 60, 30, 80, bg_box_size=3)


###################################################################

SOURCE_DIR = Path(__file__).parent.parent / "sources" / Path(__file__).stem
IMAGE_NAMES_IN_DIR = [
    f for f in SOURCE_DIR.iterdir() if f.is_file() and f.suffix in [".jpg", ".png"]
]
FIRST_IMAGE = SOURCE_DIR / IMAGE_NAMES_IN_DIR[0]


for image_name in IMAGE_NAMES_IN_DIR:
    config = Config(
        image_dpi=300,
        card_height_mm=90,
        card_width_mm=75,
        cards_rows=2,
        cards_cols=4,
        offset_from_top_border_mm=17,
        offset_from_left_border_mm=7,
    )
    ImageProcessingManager(
        config=config, image_path=SOURCE_DIR / image_name, card_types=(Regular,)
    ).process()
