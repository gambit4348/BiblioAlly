import binascii
import re

pattern = re.compile('[\W_]+', re.UNICODE)


def alphanum(text: str) -> str:
    text = pattern.sub('', text)
    return text


def alphanum_crc32(text: str) -> int:
    text = alphanum(text).lower().encode("utf-8")
    return binascii.crc32(text)
