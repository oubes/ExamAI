# ---- Imports ---- #
from pathlib import Path
from src.services.knowledge.reading.reader import PyMuPDFDocumentLoader
from src.services.knowledge.chunking.chunker import chunker


# ---- Pdf Reader ---- #
pdf_reader = PyMuPDFDocumentLoader()

# ---- Knowledge Pipeline ---- #
class KnowledgePipeline:

    # ---- Run ---- #
    async def run(
        self,
        file_path: str,
    ) -> list[dict]:

        # ---- Resolve Path ---- #
        path = Path(file_path)

        # ---- Load Documents ---- #
        docs_loader = pdf_reader.load(file_path=path)


        # ---- Chunk Documents ---- #
        chunks = await chunker.chunk_documents(
            documents=docs_loader,
            doc_name=path.name,
        )

        return chunks


# ---- DI ---- #
knowledge_pipeline = KnowledgePipeline()