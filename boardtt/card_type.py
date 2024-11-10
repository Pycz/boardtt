import json
import os
import re
from collections import OrderedDict

from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont

from boardtt.card_area import CardArea
from boardtt.logger import LOGGER
from boardtt.tesseract import TesseractAPI


RE_SPACES = re.compile(r"(\s)+", re.MULTILINE)


class CardType:
    """Тип карты характеризуется её внешним видом, а точнее расположением на ней
    регионов с данными. Различные типы карт могут содержать различный набор регионов
    и обрабатываться по различающимся правилам.
    """

    # Псевдоним карты. Используется при именовании директорий локализации.
    alias = None

    # Имя региона карты, содержащего идентификтаор карты.
    # Часто в том или ином месте карты можно отыскать её номер.
    # Распознанное значение из региона будет использовано при именовании директорий локализации.
    card_id_area = None

    # Имя региона карты, значение из которого может служить для определения принадлежности
    # карты к данному типу.
    marker_area = None
    # Значение, которое должно присутствовать в регионе заданном `marker_area`
    # для отнесения карты к данному типу.
    marker_value = None

    # Список имён регионов, значения из которых должны быть нормализованы -
    # приведены к целому.
    norm_numeric = []

    DEBUG = False

    def __init__(self, cards, target_dir=None):
        self.target_dir = target_dir
        self.cards = OrderedDict()

        for idx, card in enumerate(cards):
            if self.marker_area is None or self.has_marker(card["img"]):
                self.cards[idx] = {
                    "img": card["img"],
                    "coords": card["coords"],
                    "areas": self.get_areas(card["img"]),
                }

    def get_file_dir(self, card_id, fname):
        """Возвращает директорию, содержащую материалы для локализации
        для указанной карты.

        :param card_id:
        :param fname:
        :return:
        """
        target_dir = os.path.join(self.target_dir, self.alias, str(card_id))
        try:
            os.makedirs(target_dir)
        except OSError:  # Диретория существует.
            pass
        return os.path.join(target_dir, fname)

    @classmethod
    def get_tr_image(cls, card, idx):
        """Возвращает изображение с оверлейным (локализованным) слоем.

        :param dict card: Словарь с данными карты
        :param int idx: Индекс (номер в последовательности) карты
        :return:
        """

        card_id = cls.get_card_id(idx, card)
        LOGGER.info("Generating localized image for %s ..." % card_id)

        card_coords = card["coords"]
        tr_img = Image.new(
            "RGBA",
            (card_coords[2] - card_coords[0], card_coords[3] - card_coords[1]),
            (255, 255, 255, 0),
        )

        for area_name, area_data in card["areas"].items():
            if area_data["render"]:
                LOGGER.debug("Rendering `%s` area ..." % area_name)

                rotate = area_data["rotate"]
                coords = area_data["coords"]

                height = coords[3] - coords[1]
                width = coords[2] - coords[0]
                img_tr = area_data["img_bg"].copy()

                if rotate is not None:
                    img_tr = img_tr.rotate(rotate)
                    height, width = width, height

                text = area_data["str"]
                (
                    font,
                    text_x,
                    text_y,
                ) = cls.adjust_text_to_box(text, height, width)
                img_tr = cls.render_text(img_tr, text, font, text_x, text_y)

                if rotate is not None:  # Восстанавливаем изначальную ориентацию.
                    abs_ = abs(rotate)
                    img_tr = img_tr.rotate(
                        abs_ if area_data["rotate"] < 0 else 0 - abs_
                    )

                tr_img.paste(img_tr, (coords[0], coords[1]), area_data["img_bg"])
            else:
                LOGGER.debug("Skipping `%s` area ..." % area_name)

        return tr_img

    @classmethod
    def get_composite_image(cls, card_img, tr_img, card_id):
        """Возвращает сведённое локализованное изображение (оверлей + оригинал).

        :param card_img:
        :param tr_img:
        :param card_id:
        :return:
        """
        LOGGER.info("Generating composite image for %s ..." % card_id)
        return Image.alpha_composite(card_img.convert("RGBA"), tr_img)

    @classmethod
    def get_card_id(cls, idx, card):
        """Возвращает идентификатор карты.

        :param int idx:
        :param dict card: Словарь с данными карты
        :return:
        """
        card_id = idx + 1
        if cls.card_id_area is not None:
            card_id = "%s-%s" % (card_id, card["areas"][cls.card_id_area]["str"])
        return card_id

    def save_files(self):
        """Сохраняет файлы проекта локализации."""
        for idx, card in self.cards.items():
            card_id = self.get_card_id(idx, card)

            LOGGER.info("Saving %s card files ..." % card_id)

            json_fname = self.get_file_dir(card_id, "card.json")

            if os.path.exists(json_fname):
                LOGGER.debug("Translation file already exists.")
                LOGGER.info(
                    "Card image files will be changed using data from %s." % json_fname
                )

                with open(json_fname) as f:
                    json_data = json.load(f)

                for area_name, area_data in json_data["areas"].items():
                    card["areas"][area_name]["str"] = area_data["str"]

            else:  # do not overwrite existing files
                card["img"].save(self.get_file_dir(card_id, "card.png"))

                json_data = {"coords": card["coords"], "areas": {}}
                for area_name, area_data in card["areas"].items():
                    json_data["areas"][area_name] = {"str": area_data["str"]}

                LOGGER.info("Generating card translation file %s ..." % json_fname)

                with open(json_fname, "w") as f:
                    json.dump(json_data, f, indent=4)

            img_tr = self.get_tr_image(card, idx)
            img_comp = self.get_composite_image(card["img"], img_tr, card_id)

            img_tr.save(self.get_file_dir(card_id, "card_tr.png"))
            img_comp.save(self.get_file_dir(card_id, "card_comp.png"))

    @classmethod
    def normalize_numeric(cls, val):
        """Нормализует строку, превращает в целое.
        Помогает при ошибках OCR.

        :param val:
        :return:
        """
        val = val.split("\n")[0].replace("o", "0").replace("D", "0")
        return re.sub(r"\D", "", val)

    @classmethod
    def has_marker(cls, card):
        """Возвращает булево, указывающее на то, содержит ли изображение маркер типа
        (принадлежит ли карта к данному типу).

        :param card:
        :return:
        """
        found_value, img, _ = cls.recognize_area(card, getattr(cls, cls.marker_area))
        if cls.DEBUG:
            img.show()
            LOGGER.info(
                "** Marker: expected - `%s`; found - `%s`"
                % (cls.marker_value, found_value.decode("utf-8", "ignore"))
            )
        return found_value.lower() == cls.marker_value.lower()

    @classmethod
    def enhance_img(cls, img):
        """Производит подготовку изображения к распознаванию.

        :param img:
        :return:
        """
        enh = ImageEnhance.Color(img)
        img = enh.enhance(0.0)
        enh = ImageEnhance.Brightness(img)
        img = enh.enhance(1.4)
        enh = ImageEnhance.Contrast(img)
        img = enh.enhance(1.4)

        img = ImageOps.expand(img, border=60, fill="white")

        threshold = 150
        img = img.point(lambda p: p > threshold and 255)

        return img

    @classmethod
    def get_bg_img(cls, img, box_size=6, bg_start=3):
        """Возвращает образец с подложки (фона) региона.

        :param img:
        :param int box_size: Длина стороны квадрата образца
        :param int bg_start: Стартовая позиция, с которой берётся образец
        :return:
        """
        start = img.size[0] - box_size - bg_start
        bg_sprite = img.crop((start, bg_start, start + box_size, bg_start + box_size))

        bg_img = Image.new("RGBA", (img.size[0], img.size[1]), (0, 0, 0, 0))

        for y in range(0, bg_img.size[1], box_size):
            for x in range(0, bg_img.size[0], box_size):
                bg_img.paste(bg_sprite, (x, y))

        return bg_img

    @classmethod
    def render_text(cls, img, text, font, x=10, y=10, color=(0, 0, 0)):
        """Печатает тект на изображении.

        :param img:
        :param text: Текст для печати
        :param font: Шрифт
        :param x: Позиция печати x
        :param y: Позиция печати y
        :param color: Цвет надписи
        :return:
        """
        dr = ImageDraw.Draw(img)

        line_height = font.getbbox("jN")[1] * 1.25

        for line in text.splitlines():
            dr.text((x, y), line, color, font=font)
            y += line_height

        return img

    @classmethod
    def get_font(cls, font_size=40, font_name=None):
        """Возвращает шрифт указанноти типа и размера.

        /usr/share/fonts/truetype/ubuntu/
        /usr/share/fonts/truetype/freefont/
        FreeMono.ttf
        FreeMonoBold.ttf
        FreeMonoBoldOblique.ttf
        FreeMonoOblique.ttf
        FreeSans.ttf
        FreeSansBold.ttf
        FreeSansBoldOblique.ttf
        FreeSansOblique.ttf
        FreeSerif.ttf
        FreeSerifBold.ttf
        FreeSerifBoldItalic.ttf
        FreeSerifItalic.ttf

        :param font_size:
        :param font_name:
        :return:
        """
        if font_name is None:
            font_name = "Ubuntu-M.ttf"

        if "/" not in font_name:
            font_name = f"/usr/share/fonts/truetype/ubuntu/{font_name}"

        return ImageFont.truetype(font_name, font_size)

    @classmethod
    def recognize_area(cls, card, area):
        """Производит попытку распознать регион.
        Возвращает кортеж: (распознанный_текст, изображение_региона_для_распознания, оригинальное_изображение_региона)

        :param card:
        :param area:
        :return:
        """
        marker_coords = area.get_coords()
        img_orig = card.crop(marker_coords)
        img = cls.enhance_img(img_orig)

        if area.rotate is not None:
            img = img.rotate(area.rotate)

        text = TesseractAPI.recognize(img).strip()
        text = re.sub(RE_SPACES, r"\g<0>", text)  # strip consecutive whitespaces

        return text, img, img_orig

    @classmethod
    def adjust_text_to_box(cls, text, height, width):
        """Вписывает текст в пределы, подбирая его размер.

        :param text: Текст
        :param height: Предельная высота
        :param width: Предельная ширина
        :return:
        """
        max_height = int(height / 1.2)
        max_width = int(width / 1.2)

        longest_line = ""
        longest_len = 0

        for line in text.splitlines():
            l = len(line)
            if l > longest_len:
                longest_line = line
                longest_len = l

        lines_quantity = len(text.splitlines())

        def get_size(base_size):
            font = cls.get_font(base_size)
            line_size = font.getbbox(longest_line)

            line_height = line_size[1]

            if lines_quantity > 1:
                line_height = (
                    lines_quantity * line_height
                )  # + ((lines_quantity-1) * line_height)

            if line_height > max_height or line_size[0] > max_width:
                return get_size(base_size - 2)
            return font, line_size

        font, text_size = get_size(100)
        text_x = 4
        text_y = 4  # int((height - text_size[1]) / 2)  # align vertically

        return font, text_x, text_y

    @classmethod
    def get_areas(cls, card):
        """Возвращает словарь с данными регионов карты.

        :param card:
        :return:
        """
        areas = {}
        for name, val in cls.__dict__.items():
            if isinstance(val, CardArea):
                text, img, img_orig = cls.recognize_area(card, val)

                if name in cls.norm_numeric:
                    text = cls.normalize_numeric(text)

                img_bg = None

                if val.render:
                    img_bg = cls.get_bg_img(img_orig, box_size=val.bg_box_size)

                areas[name] = {
                    "str": text,
                    "coords": val.get_coords(),
                    "img_bg": img_bg,
                    "img_orig": img_orig,
                    "img": img,
                    "render": val.render,
                    "rotate": val.rotate,
                }
        return areas
