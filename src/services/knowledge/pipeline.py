# ---- Imports ---- #
from pathlib import Path
from src.services.knowledge.reading.reader import PyMuPDFDocumentLoader
from src.services.knowledge.chunking.chunker import chunker
from src.domain.storage.services.upload_file import UploadService
from src.infra.db.session import session_local
from uuid import UUID


# ---- Pdf Reader ---- #
pdf_reader = PyMuPDFDocumentLoader()

# ---- Upload Service ---- #
upload_service = UploadService()

# ---- Session ---- #
session = session_local()

# ---- Knowledge Pipeline ---- #
class KnowledgePipeline:

    # ---- Run ---- #
    async def run(
        self,
        file_id: str,
    ) -> list[dict]:

        # ---- Resolve Path ---- #
        file_info = upload_service.get_by_id(session, UUID(file_id))
        path = Path(file_info.path) # type: ignore

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