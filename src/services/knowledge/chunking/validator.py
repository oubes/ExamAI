class TextValidator:
    # ---- Minimum Length Check ----
    def has_min_length(self, text: str, min_length: int) -> bool:
        return bool(text) and len(text) >= min_length

    # ---- Character Diversity Check ----
    def has_enough_char_diversity(self, text: str, min_unique_chars: int = 5) -> bool:
        return len(set(text)) >= min_unique_chars

    # ---- Word Count Check ----
    def has_enough_words(self, text: str, min_words: int = 5) -> bool:
        return len(text.split()) >= min_words

    # ---- Text Validity Pipeline ----
    def is_valid_text(self, text: str, min_length: int = 20) -> bool:
        if not self.has_min_length(text, min_length):
            return False

        if not self.has_enough_char_diversity(text):
            return False

        if not self.has_enough_words(text):
            return False

        return True