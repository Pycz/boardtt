from dataclasses import dataclass


@dataclass
class Config:
    cards_rows: int  # сколько рядов карт на скане
    cards_cols: int  # сколько столбцов карт на скане

    image_dpi: int = 300
    offset_from_top_border_mm: int | float = (
        0  # сколько миллиметров от верхнего края до первой карточки
    )
    offset_from_left_border_mm: int | float = (
        0  # сколько миллиметров от левого края до первой карточки
    )
    card_height_mm: int | float = 80  # высота карты в миллиметрах
    card_width_mm: int | float = 60  # ширина карты в миллиметрах
    offset_x_mm: int | float = 1  # отступ между картами по горизонтали
    offset_y_mm: int | float = 1  # отступ между картами по вертикали

    def _mm_to_pixels(self, mm: int | float) -> int:
        return int((self.image_dpi * mm) / 25.4)

    @property
    def card_height_px(self) -> int:
        return self._mm_to_pixels(self.card_height_mm)

    @property
    def card_width_px(self) -> int:
        return self._mm_to_pixels(self.card_width_mm)

    @property
    def offset_x_px(self) -> int:
        return self._mm_to_pixels(self.offset_x_mm)

    @property
    def offset_y_px(self) -> int:
        return self._mm_to_pixels(self.offset_y_mm)

    @property
    def offset_from_top_border_px(self) -> int:
        return self._mm_to_pixels(self.offset_from_top_border_mm)

    @property
    def offset_from_left_border_px(self) -> int:
        return self._mm_to_pixels(self.offset_from_left_border_mm)
