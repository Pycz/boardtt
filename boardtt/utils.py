def mm_to_pixels(mm: int | float, dpi: int | float = 300) -> int:
    return int((dpi * mm) / 25.4)
