from boardtt.config import IMAGE_DPI


def mm_to_pixels(mm):
    """Переводит миллиметры в пикселы.

    :param mm:
    :return:
    """
    return int((IMAGE_DPI * mm) / 25.4)
