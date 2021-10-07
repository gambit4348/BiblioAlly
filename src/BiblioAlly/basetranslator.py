import re


class BaseTranslator:
    @staticmethod
    def documents_from_file(filename):
        return None

    @staticmethod
    def _unbroken(value):
        return re.sub(r'\s+', ' ', value)
