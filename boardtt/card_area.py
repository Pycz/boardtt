from boardtt.config import Config
from boardtt.utils import mm_to_pixels


class CardArea:
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

    def get_coords(self, config: Config) -> tuple[int, int, int, int]:
        """Возвращает кортеж с координатами региона на карте."""
        return (
            mm_to_pixels(self.x, dpi=config.image_dpi),
            mm_to_pixels(self.y, dpi=config.image_dpi),
            mm_to_pixels(self.x1, dpi=config.image_dpi),
            mm_to_pixels(self.y1, dpi=config.image_dpi),
        )
