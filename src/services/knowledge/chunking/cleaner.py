# ---- Standard Library ----
import re
import unicodedata


class TextCleaner:
    # ---- Normalize Text ----
    def normalize_text(
        self,
        text: str,
        *,
        lowercase: bool = True,
        remove_accents: bool = True,
    ) -> str:
        text = unicodedata.normalize("NFKC", text)

        if remove_accents:
            text = self._strip_accents(text)

        if lowercase:
            text = text.lower()

        return text

    # ---- Strip Accents ----
    def _strip_accents(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(c for c in normalized if not unicodedata.combining(c))

    # ---- Normalize Whitespace ----
    def normalize_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    # ---- Replace Ampersand ----
    def replace_ampersand(self, text: str) -> str:
        return re.sub(r"\s*&\s*", " and ", text)

    # ---- Remove Special Characters ----
    def remove_special_chars(self, text: str) -> str:
        return re.sub(r"[^\w\s.,;:!?()\-@$%]", "", text)

    # ---- Clean Pipeline (Pre-Split) ----
    def clean(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        text = self.normalize_text(text)
        text = self.normalize_whitespace(text)
        text = self.replace_ampersand(text)
        text = self.remove_special_chars(text)
        text = self.normalize_whitespace(text)

        return text