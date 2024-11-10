from PIL import Image
from pytesseract import pytesseract

from boardtt.exceptions import TesseractException


class TesseractAPI:
    LANG = 'eng'

    def recognize(self, img: Image, as_html: bool = False) -> str:
        """Распознаёт текст на данном изображении.
        """
        try:
            if as_html:
                return pytesseract.image_to_pdf_or_hocr(img, lang=self.LANG, extension='hocr')
            return pytesseract.image_to_string(img, lang=self.LANG)
        except OSError as e:
            raise TesseractException(f'Tessaract error: {e}') from e
