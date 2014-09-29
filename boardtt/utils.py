# encoding: utf-8
from __future__ import unicode_literals
import os
import re
import json
import ctypes
import logging
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont


LOGGER = logging.getLogger(__name__)


IMAGE_DPI = 600

CARD_HEIGHT_MM = 88
CARD_WIDTH_MM = 62

CARDS_ROWS = 3
CARDS_COLS = 3


def configure(image_dpi=600, card_height_mm=88, card_width_mm=62, cards_rows=3, cards_cols=3, log_level=logging.INFO):
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
    format_str = '%(levelname)s: %(message)s'
    if show_logger_names:
        format_str = '%(name)s\t\t ' + format_str
    logging.basicConfig(format=format_str, level=log_level)


RE_SPACES = re.compile('(\s)+', re.MULTILINE)


class BGTTException(Exception):
    """Базовое исключение."""


class TesseractException(BGTTException):
    """Исключения взаимодействия с Tesseract."""


class TesseractAPI(object):
    """Простой API для распознования текста при помощи Tesseract OCR."""

    def __init__(self):
        lib_tesseract = '/usr/lib/libtesseract.so.3'
        self.tess = ctypes.cdll.LoadLibrary(lib_tesseract)

        self.tess_api = self.tess.TessBaseAPICreate()
        tess_failed = self.tess.TessBaseAPIInit3(self.tess_api, None, 'eng'.encode('ascii'))

        if tess_failed:
            self.tess.TessBaseAPIDelete(self.tess_api)
            raise TesseractException('Unable to initialize Tesseract OCR')

    def recognize(self, img, as_html=False):
        """Распознаёт текст на данном изображении.

        :param img:
        :param as_html:
        :return:
        """
        RGB = 3
        MODE = RGB

        self.tess.TessBaseAPISetImage(self.tess_api, img.tostring(), img.size[0], img.size[1], MODE, MODE*img.size[0])
        tess_failed = self.tess.TessBaseAPIRecognize(self.tess_api, None)

        if tess_failed:
            self.tess.TessBaseAPIDelete(self.tess_api)
            raise TesseractException('Unable to recognize text.')

        if as_html:
            text = self.tess.TessBaseAPIGetHOCRText(self.tess_api)
        else:
            text = self.tess.TessBaseAPIGetUTF8Text(self.tess_api)
        return ctypes.string_at(text)


TESS = TesseractAPI()


def open_image_file(fpath):
    """Возвращает открытый Pillow файл с изображением.

    :param fpath:
    :return:
    """
    return Image.open(fpath)


def mm_to_pixels(mm):
    """Переводит миллиметры в пикселы.

    :param mm:
    :return:
    """
    return int((IMAGE_DPI * mm) / 25.4)


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
            LOGGER.debug('Getting card %sx%s ...' % (col_num+1, row_num+1))
            coords = get_card_coords(row_num, col_num)
            card = img.crop(coords)
            cards.append({
                'img': card,
                'coords': coords
            })

    LOGGER.info('Source image split into %s cards' % len(cards))

    return cards


def get_cards_from_file(fpath):
    """Возвращает данные о картах, изъятых из указанно файла-скана.

    :param fpath:
    :return:
    """
    LOGGER.info('Loading cards from %s' % fpath)
    img = open_image_file(fpath)
    return get_cards(img)


class CardArea(object):

    def __init__(self, x, x1, y, y1, render=True, rotate=None, bg_box_size=13):
        """Описывает регион на карте.

        :param float x: Координата x верхнего левого угла региона
        :param float x1: Координата x верхнего правого угла региона
        :param float y: Координата y верхнего левого угла региона
        :param float y1: Координата y нижнего левого угла региона
        :param bool render: Следует ли выводить регион на локализованном изображении
        :param int|None rotate: Угол разворота. Например, -90, если текст в регоне вдоль карты
        :param int bg_box_size: Длина стороны квадрата для взятия образца подложки региона. В пикселах
        :return:
        """
        self.bg_box_size = bg_box_size
        self.rotate = rotate
        self.render = render
        self.x = x
        self.y = y
        self.x1 = x1
        self.y1 = y1

    def get_coords(self):
        """Возвращает кортеж с координатами региона на карте.

        :return:
        """
        return mm_to_pixels(self.x), mm_to_pixels(self.y), mm_to_pixels(self.x1), mm_to_pixels(self.y1)


class CardType(object):
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
            if self.marker_area is None or self.has_marker(card['img']):
                self.cards[idx] = {
                    'img': card['img'],
                    'coords': card['coords'],
                    'areas': self.get_areas(card['img'])
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
        LOGGER.info('Generating localized image for %s ...' % card_id)

        card_coords = card['coords']
        tr_img = Image.new('RGBA', (card_coords[2]-card_coords[0], card_coords[3]-card_coords[1]), (255, 255, 255, 0))

        for area_name, area_data in card['areas'].items():
            if area_data['render']:
                LOGGER.debug('Rendering `%s` area ...' % area_name)

                rotate = area_data['rotate']
                coords = area_data['coords']

                height = coords[3] - coords[1]
                width = coords[2] - coords[0]
                img_tr = area_data['img_bg'].copy()

                if rotate is not None:
                    img_tr = img_tr.rotate(rotate)
                    height, width = width, height

                text = area_data['str']
                font, text_x, text_y, = cls.adjust_text_to_box(text, height, width)
                img_tr = cls.render_text(img_tr, text, font, text_x, text_y)

                if rotate is not None:  # Восстанавливаем изначальную ориентацию.
                    abs_ = abs(rotate)
                    img_tr = img_tr.rotate(abs_ if area_data['rotate'] < 0 else 0-abs_)

                tr_img.paste(img_tr, (coords[0], coords[1]), area_data['img_bg'])
            else:
                LOGGER.debug('Skipping `%s` area ...' % area_name)

        return tr_img

    @classmethod
    def get_composite_image(cls, card_img, tr_img, card_id):
        """Возвращает сведённое локализованное изображение (оверлей + оригинал).

        :param card_img:
        :param tr_img:
        :param card_id:
        :return:
        """
        LOGGER.info('Generating composite image for %s ...' % card_id)
        return Image.alpha_composite(card_img.convert('RGBA'), tr_img)

    @classmethod
    def get_card_id(cls, idx, card):
        """Возвращает идентификатор карты.

        :param int idx:
        :param dict card: Словарь с данными карты
        :return:
        """
        card_id = idx + 1
        if cls.card_id_area is not None:
            card_id = '%s-%s' % (card_id, card['areas'][cls.card_id_area]['str'])
        return card_id

    def save_files(self):
        """Сохраняет файлы проекта локализации.

        :return:
        """
        for idx, card in self.cards.items():
            card_id = self.get_card_id(idx, card)

            LOGGER.info('Saving %s card files ...' % card_id)

            json_fname = self.get_file_dir(card_id, 'card.json')

            if os.path.exists(json_fname):

                LOGGER.debug('Translation file already exists.')
                LOGGER.info('Card image files will be changed using data from %s.' % json_fname)

                with open(json_fname) as f:
                    json_data = json.load(f)

                for area_name, area_data in json_data['areas'].items():
                    card['areas'][area_name]['str'] = area_data['str']

            else:  # do not overwrite existing files
                card['img'].save(self.get_file_dir(card_id, 'card.png'))

                json_data = {
                    'coords': card['coords'],
                    'areas': {}
                }
                for area_name, area_data in card['areas'].items():
                    json_data['areas'][area_name] = {'str': area_data['str']}

                LOGGER.info('Generating card translation file %s ...' % json_fname)

                with open(json_fname, 'w') as f:
                    json.dump(json_data, f, indent=4)

            img_tr = self.get_tr_image(card, idx)
            img_comp = self.get_composite_image(card['img'], img_tr, card_id)

            img_tr.save(self.get_file_dir(card_id, 'card_tr.png'))
            img_comp.save(self.get_file_dir(card_id, 'card_comp.png'))

    @classmethod
    def normalize_numeric(cls, val):
        """Нормализует строку, превращает в целое.
        Помогает при ошибках OCR.

        :param val:
        :return:
        """
        val = val.split('\n')[0].replace('o', '0').replace('D', '0')
        return re.sub('\D', '', val)

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
            LOGGER.info('** Marker: expected - `%s`; found - `%s`' % (cls.marker_value, found_value.decode('utf-8', 'ignore')))
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

        img = ImageOps.expand(img, border=60, fill='white')

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
        bg_sprite = img.crop((start, bg_start, start+box_size, bg_start+box_size))

        bg_img = Image.new('RGBA', (img.size[0], img.size[1]), (0, 0, 0, 0))

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

        line_height = font.getsize('jN')[1] * 1.25

        for line in text.splitlines():
            dr.text((x, y), line, color, font=font)
            y += line_height

        return img

    @classmethod
    def get_font(cls, font_size=40, font_name=None):
        """Возвращает шрифт указанноти типа и размера.

        /usr/share/fonts/truetype/ubuntu-font-family/
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
            font_name = 'Ubuntu-M.ttf'

        if '/' not in font_name:
            font_name = '/usr/share/fonts/truetype/ubuntu-font-family/%s' % font_name

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

        text = TESS.recognize(img).strip()
        text = re.sub(RE_SPACES, '\g<0>', text)  # strip consecutive whitespaces

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

        longest_line = ''
        longest_len = 0

        for lines_num, line in enumerate(text.splitlines(), 1):
            l = len(line)
            if l > longest_len:
                longest_line = line
                longest_len = l

        def get_size(base_size):
            font = cls.get_font(base_size)
            line_size = font.getsize(longest_line)

            line_height = line_size[1]

            if lines_num > 1:
                line_height = (lines_num * line_height)  # + ((lines_num-1) * line_height)

            if line_height > max_height or line_size[0] > max_width:
                return get_size(base_size-2)
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
                    'str': text,
                    'coords': val.get_coords(),
                    'img_bg': img_bg,
                    'img_orig': img_orig,
                    'img': img,
                    'render': val.render,
                    'rotate': val.rotate
                }
        return areas


def debug_image(image_path, card_type, debug=False, target_area='text', show_composite=False):
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
            card['img'].show()

    matches = card_type(cards)

    LOGGER.warning('** Card indexes: %s' % matches.cards.keys())

    for idx, card in matches.cards.items():

        if not show_composite:
            LOGGER.warning('** Text in `%s` area: %s' % (target_area, card['areas'][target_area]['str']))
            card['areas'][target_area]['img'].show()
        else:
            card_id = card_type.get_card_id(idx, card)
            img_tr = card_type.get_tr_image(card, idx)
            img_comp = card_type.get_composite_image(card['img'], img_tr, card_id)
            img_comp.show()


def process_image(image_path, card_types):
    """Производит обработку указанного скана, используя
    указанные типы карт.

    :param image_path:
    :param card_types:
    :return:
    """
    LOGGER.info('Image processing started')

    target_dir = os.path.splitext(image_path)[0]
    LOGGER.debug('Target path: %s' % target_dir)
    cards = get_cards_from_file(image_path)

    for card_type in card_types:
        LOGGER.info('Processing using %s ...' % card_type.__name__)
        data = card_type(cards, target_dir)
        data.save_files()

    LOGGER.info('Image processing finished')
