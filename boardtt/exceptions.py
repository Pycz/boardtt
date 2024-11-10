class BGTTException(Exception):
    """Базовое исключение."""


class TesseractException(BGTTException):
    """Исключения взаимодействия с Tesseract."""
