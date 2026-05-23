import re
import unicodedata


class TextNormalizer:
    def __init__(self) -> None:
        pass
    def normalize(self, text: str) -> str:
        return self.collapse_whitespace(self.remove_zero_width_characters(self.basic_normalize(text=text)))

    def basic_normalize(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text)

    def remove_zero_width_characters(self, text: str) -> str:
        clean_normalized_text: list[str] = []
        for char in text:
            unicode_category: str = unicodedata.category(char)
            if unicode_category != "Cf":
                clean_normalized_text.append(char)
        return "".join(clean_normalized_text)

    def collapse_whitespace(self, text: str) -> str:
        return re.sub("  ", " ", text)


