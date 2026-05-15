from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.services.knowledge.config import settings


class Splitter:
    # ---- Constructor ----
    def __init__(self):
        self.chunk_size = settings.ingestion_chunk_size
        self.chunk_overlap = settings.ingestion_chunk_overlap

        # ---- Length function ----
        self.length_function = len

        self._splitter = self._build_splitter()

    # ---- Build Splitter ----
    def _build_splitter(self) -> RecursiveCharacterTextSplitter:
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.length_function,
            is_separator_regex=False,
            separators=[
                "\n# ",
                "\n## ",
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    # ---- Split Text ----
    def split(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        return self._splitter.split_text(text)