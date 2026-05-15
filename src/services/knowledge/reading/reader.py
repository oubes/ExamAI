# ---- Imports ---- #
import logging
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document



# ---- Logger ---- #
logger = logging.getLogger(__name__)


# ---- Document Loader Implementation ---- #
class PyMuPDFDocumentLoader:
    # ---- Load Method ---- #
    def load(self, file_path: Path) -> list[Document]:
        try:

            if not file_path.exists():
                raise FileNotFoundError(f"{file_path} not found")

            loader = PyMuPDFLoader(str(file_path))
            documents = loader.load()

            logger.debug(f"Loaded {len(documents)} pages from {file_path.name}")

            return documents

        except Exception:
            logger.exception("load_pymupdf failed")
            raise